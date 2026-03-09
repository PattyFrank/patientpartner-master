"""
PatientPartner Image Generator MCP Server

Generates photorealistic healthcare photography for PatientPartner.com.
Brand-aware prompt enhancement + multi-backend image generation.

Backends (in priority order):
  1. Google Gemini (free)    — Gemini 2.0 Flash image gen via generativelanguage.googleapis.com
  2. HF Inference API (free) — FLUX.1-schnell via huggingface.co API
  3. HF Space (free)         — Custom Gradio Space with LoRA support
  4. Replicate (paid)        — NanoBanana2 / Imagen 4
  5. Prompt-only (fallback)  — Returns enhanced prompt, no image

Setup (free path — only needs one env var):
    GOOGLE_API_KEY=your_key   # get free at aistudio.google.com

Usage:
    python server.py   # stdio transport for Claude Code
"""

import asyncio
import base64
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import httpx
from dotenv import load_dotenv
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    TextContent,
    Tool,
)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
HF_TOKEN = os.getenv("HF_TOKEN", "")
HF_SPACE_ID = os.getenv("HF_SPACE_ID", "")
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN", "")
LOCAL_TEST = os.getenv("LOCAL_TEST", "").lower() in ("1", "true", "yes")

# Determine active backend (priority order)
if LOCAL_TEST:
    BACKEND = "local_pil"
elif GOOGLE_API_KEY:
    BACKEND = "google_gemini"
elif HF_TOKEN:
    BACKEND = "hf_inference"
elif HF_SPACE_ID:
    BACKEND = "hf_space"
elif REPLICATE_API_TOKEN:
    BACKEND = "replicate"
else:
    BACKEND = "prompt_only"

OUTPUT_DIR = Path(os.getenv(
    "IMAGE_OUTPUT_DIR",
    os.path.join(os.getcwd(), "creative-output", "generated-images"),
))

logger = logging.getLogger("image-generator-mcp")
logging.basicConfig(level=logging.INFO, stream=sys.stderr)

logger.info(f"Backend: {BACKEND}")

# ---------------------------------------------------------------------------
# Resolution presets
# ---------------------------------------------------------------------------

RESOLUTION_PRESETS: dict[str, dict[str, Any]] = {
    "social_square": {
        "aspect_ratio": "1:1",
        "width": 1024,
        "height": 1024,
        "description": "Social media square (1080×1080) — Instagram feed, LinkedIn, Facebook",
    },
    "social_portrait": {
        "aspect_ratio": "4:5",
        "width": 832,
        "height": 1024,
        "description": "Social media portrait (1080×1350) — Instagram feed optimal, Facebook ads",
    },
    "social_story": {
        "aspect_ratio": "9:16",
        "width": 576,
        "height": 1024,
        "description": "Social stories/reels (1080×1920) — Instagram Stories, TikTok, Reels",
    },
    "hero": {
        "aspect_ratio": "16:9",
        "width": 1024,
        "height": 576,
        "description": "Website hero image (1920×1080) — Landing pages, hero sections, OG images",
    },
    "blog": {
        "aspect_ratio": "3:2",
        "width": 1024,
        "height": 680,
        "description": "Blog image (1200×800) — Blog posts, articles, editorial content",
    },
    "blog_wide": {
        "aspect_ratio": "16:9",
        "width": 1024,
        "height": 576,
        "description": "Wide blog image (1200×675) — Blog headers, newsletter banners",
    },
}

# ---------------------------------------------------------------------------
# Brand-aware prompt enhancement
# ---------------------------------------------------------------------------

BRAND_STYLE_PREFIX = (
    "Professional documentary-style healthcare photography, "
    "natural lighting, authentic and warm, "
    "shot on Canon EOS R5 with 85mm lens, shallow depth of field, "
    "soft bokeh background"
)

BRAND_STYLE_SUFFIX = (
    "The image should feel genuine and trustworthy, like real documentary photography. "
    "Diverse representation in age, ethnicity, and background. "
    "No exaggerated facial features, no plastic skin textures, no cartoon-like appearance. "
    "Natural skin tones, realistic clothing, believable environment."
)

SUBJECT_TEMPLATES: dict[str, str] = {
    "patient": (
        "a real patient in a healthcare setting, "
        "wearing everyday clothing, natural posture and expression, "
        "relatable and authentic appearance"
    ),
    "mentor": (
        "a patient mentor or peer supporter, warm and approachable demeanor, "
        "making eye contact, conveying experience and empathy, "
        "dressed in smart casual attire"
    ),
    "caregiver": (
        "a caregiver or family member providing support, "
        "gentle and attentive, natural body language showing care, "
        "in a comfortable home or healthcare environment"
    ),
    "healthcare_professional": (
        "a healthcare professional in a clinical setting, "
        "wearing appropriate medical attire, professional yet approachable, "
        "conveying competence and warmth"
    ),
    "patient_and_mentor": (
        "a patient and their peer mentor sitting together, "
        "engaged in genuine conversation, warm supportive interaction, "
        "both looking comfortable and connected"
    ),
    "group": (
        "a small support group of diverse patients, "
        "sitting together in a circle or at a table, "
        "engaged and supportive, community feeling"
    ),
}

EMOTION_MODIFIERS: dict[str, str] = {
    "hopeful": "expressing genuine hope and optimism, slight natural smile, bright eyes, uplifting atmosphere",
    "supportive": "showing warmth and support, leaning in attentively, empathetic expression, connected posture",
    "reflective": "in a quiet thoughtful moment, calm and contemplative, peaceful expression, soft ambient light",
    "confident": "projecting quiet confidence, standing tall, assured expression, empowered body language",
    "grateful": "expressing sincere gratitude, warm genuine smile, relaxed and appreciative demeanor",
    "determined": "showing resolve and determination, focused gaze, purposeful posture, strong but approachable",
    "relieved": "expressing relief and comfort, relaxed shoulders, gentle exhale moment, tension releasing",
    "connected": "feeling of human connection, engaged with another person, shared understanding, mutual warmth",
}

SCENE_TEMPLATES: dict[str, str] = {
    "consultation": "in a modern, welcoming medical consultation room with natural light from large windows",
    "waiting_room": "in a bright, comfortable healthcare waiting area with plants and natural decor",
    "home": "in a warm, inviting living room at home, natural afternoon light through windows",
    "outdoors": "outdoors in a park or garden setting, soft natural daylight, greenery in background",
    "hospital": "in a modern hospital corridor or room, clean and well-lit, not sterile-looking",
    "support_group": "in a comfortable community room set up for a support group meeting, warm lighting",
    "virtual": "at a desk during a virtual mentorship call, laptop visible, home office background",
    "pharmacy": "at a friendly neighborhood pharmacy counter, warm lighting, approachable setting",
    "recovery": "in a recovery or rehabilitation setting, encouraging atmosphere, natural light",
}


def enhance_prompt(
    scene: str,
    subject_type: str | None = None,
    emotion: str | None = None,
    scene_setting: str | None = None,
    additional_details: str | None = None,
) -> str:
    """Build a brand-consistent, photorealistic prompt from user inputs."""
    parts: list[str] = [BRAND_STYLE_PREFIX]

    if scene_setting and scene_setting in SCENE_TEMPLATES:
        parts.append(SCENE_TEMPLATES[scene_setting])

    if subject_type and subject_type in SUBJECT_TEMPLATES:
        parts.append(SUBJECT_TEMPLATES[subject_type])

    parts.append(scene)

    if emotion and emotion in EMOTION_MODIFIERS:
        parts.append(EMOTION_MODIFIERS[emotion])

    if additional_details:
        parts.append(additional_details)

    parts.append(BRAND_STYLE_SUFFIX)

    return ", ".join(parts)


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

async def download_image(image_url: str, filename: str) -> str:
    """Download an image from URL and save locally."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    filepath = OUTPUT_DIR / filename

    async with httpx.AsyncClient(timeout=60, follow_redirects=True) as client:
        resp = await client.get(image_url)
        if resp.status_code != 200:
            raise RuntimeError(f"Failed to download image: HTTP {resp.status_code}")
        filepath.write_bytes(resp.content)

    return str(filepath)


def save_image_bytes(image_bytes: bytes, filename: str) -> str:
    """Save raw image bytes to a local file."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    filepath = OUTPUT_DIR / filename
    filepath.write_bytes(image_bytes)
    return str(filepath)


def _generate_filename(
    asset_type: str, descriptor: str, aspect_ratio: str, fmt: str
) -> str:
    """Generate a filename following PatientPartner naming conventions."""
    ratio_str = aspect_ratio.replace(":", "x")
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    return f"{asset_type}-{descriptor}-{ratio_str}-{timestamp}.{fmt}"


# ---------------------------------------------------------------------------
# Backend 0: Local PIL generator (no network — for sandbox / offline testing)
# Generates a styled branded image with the prompt embedded. Full pipeline demo.
# ---------------------------------------------------------------------------

# PatientPartner brand colors
PP_TEAL = (0, 171, 169)        # #00ABA9
PP_DARK = (30, 47, 69)         # #1E2F45
PP_WARM = (248, 243, 237)      # #F8F3ED
PP_ACCENT = (255, 107, 53)     # #FF6B35


def generate_local_pil_image(
    prompt: str,
    width: int = 1024,
    height: int = 680,
    subject_type: str | None = None,
    emotion: str | None = None,
) -> bytes:
    """
    Generate a branded placeholder image using Pillow only — no network needed.
    Demonstrates the full MCP pipeline (prompt → file → naming conventions).
    Replace with a real backend for production use.
    """
    from PIL import Image, ImageDraw, ImageFont, ImageFilter
    import math, random, io

    rng = random.Random(abs(hash(prompt)) % (2**31))

    img = Image.new("RGB", (width, height), PP_WARM)
    draw = ImageDraw.Draw(img)

    # Gradient background
    for y in range(height):
        t = y / height
        r = int(PP_WARM[0] * (1 - t) + PP_DARK[0] * t * 0.15)
        g = int(PP_WARM[1] * (1 - t) + PP_DARK[1] * t * 0.15)
        b = int(PP_WARM[2] * (1 - t) + PP_DARK[2] * t * 0.25)
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    # Organic circles — suggest people/bokeh
    circle_configs = [
        (0.15, 0.4, 0.28, PP_TEAL, 40),
        (0.72, 0.35, 0.22, PP_DARK, 35),
        (0.45, 0.65, 0.18, PP_TEAL, 50),
        (0.85, 0.7, 0.15, PP_ACCENT, 30),
        (0.08, 0.75, 0.12, PP_ACCENT, 25),
    ]
    for cx_r, cy_r, r_r, color, alpha in circle_configs:
        cx = int(cx_r * width)
        cy = int(cy_r * height)
        radius = int(r_r * min(width, height))
        jitter = int(rng.uniform(-0.03, 0.03) * min(width, height))
        overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        ov_draw = ImageDraw.Draw(overlay)
        ov_draw.ellipse(
            [cx - radius + jitter, cy - radius + jitter,
             cx + radius + jitter, cy + radius + jitter],
            fill=(*color, alpha),
        )
        img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
        draw = ImageDraw.Draw(img)

    img = img.filter(ImageFilter.GaussianBlur(radius=2))
    draw = ImageDraw.Draw(img)

    # Teal header bar
    bar_h = max(60, height // 9)
    draw.rectangle([(0, 0), (width, bar_h)], fill=PP_TEAL)

    # PatientPartner wordmark
    font_size_brand = max(18, bar_h // 2)
    try:
        font_brand = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size_brand)
        font_body = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", max(14, height // 42))
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", max(11, height // 56))
    except Exception:
        font_brand = ImageFont.load_default()
        font_body = font_brand
        font_small = font_brand

    draw.text((20, bar_h // 2 - font_size_brand // 2), "PatientPartner", font=font_brand, fill="white")

    # Teal dot separator
    dot_x = 20 + draw.textlength("PatientPartner", font=font_brand) + 16
    dot_y = bar_h // 2
    draw.ellipse([dot_x - 5, dot_y - 5, dot_x + 5, dot_y + 5], fill=PP_ACCENT)

    badge_text = (subject_type or "generated").replace("_", " ").upper()
    draw.text((dot_x + 18, bar_h // 2 - font_size_brand // 2), badge_text, font=font_brand, fill=PP_WARM)

    # Emotion ribbon
    if emotion:
        emo_text = f"  {emotion.upper()}  "
        ribbon_w = int(draw.textlength(emo_text, font=font_small)) + 4
        ribbon_h = max(22, height // 28)
        ribbon_y = bar_h + 16
        ribbon_x = width - ribbon_w - 20
        draw.rounded_rectangle(
            [ribbon_x, ribbon_y, ribbon_x + ribbon_w, ribbon_y + ribbon_h],
            radius=ribbon_h // 2,
            fill=PP_ACCENT,
        )
        draw.text((ribbon_x + 2, ribbon_y + (ribbon_h - font_small.size) // 2), emo_text, font=font_small, fill="white")

    # Prompt text — wrapped
    margin = 32
    text_y = bar_h + max(48, height // 10)
    max_line_w = width - margin * 2
    words = prompt.split()
    lines: list[str] = []
    current = ""
    for word in words:
        test = (current + " " + word).strip()
        if draw.textlength(test, font=font_body) <= max_line_w:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
        if len(lines) >= 6:
            break
    if current and len(lines) < 6:
        lines.append(current)

    line_h = max(20, height // 28)
    for line in lines:
        draw.text((margin, text_y), line, font=font_body, fill=PP_DARK)
        text_y += line_h + 4

    # Bottom bar
    bottom_bar_y = height - max(36, height // 16)
    draw.rectangle([(0, bottom_bar_y), (width, height)], fill=PP_DARK)
    draw.text(
        (20, bottom_bar_y + (height - bottom_bar_y - max(14, height // 44)) // 2),
        "Generated by PatientPartner Image Generator MCP  ·  Peer-to-Peer Beats Everything",
        font=font_small,
        fill=(*PP_TEAL, 220),
    )

    # Subtle noise texture
    for _ in range(width * height // 60):
        px = rng.randint(0, width - 1)
        py = rng.randint(bar_h, bottom_bar_y - 1)
        v = rng.randint(-12, 12)
        px_color = img.getpixel((px, py))
        noisy = tuple(max(0, min(255, c + v)) for c in px_color)
        img.putpixel((px, py), noisy)

    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=92)
    return buf.getvalue()


# ---------------------------------------------------------------------------
# Backend 1: Google Gemini image generation (free — works in all environments)
# Uses generativelanguage.googleapis.com — accessible from any network
# ---------------------------------------------------------------------------

GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent"


async def generate_via_google_gemini(prompt: str) -> bytes:
    """Generate image via Gemini 2.0 Flash. Returns raw image bytes."""
    payload = {
        "contents": [
            {"parts": [{"text": prompt}]}
        ],
        "generationConfig": {
            "responseModalities": ["IMAGE", "TEXT"],
        },
    }

    async with httpx.AsyncClient(timeout=120) as client:
        resp = await client.post(
            f"{GEMINI_URL}?key={GOOGLE_API_KEY}",
            json=payload,
        )

        if resp.status_code != 200:
            raise RuntimeError(
                f"Google Gemini API error {resp.status_code}: {resp.text[:500]}"
            )

        data = resp.json()
        parts = data.get("candidates", [{}])[0].get("content", {}).get("parts", [])
        for part in parts:
            if "inlineData" in part:
                mime = part["inlineData"].get("mimeType", "image/png")
                img_bytes = base64.b64decode(part["inlineData"]["data"])
                return img_bytes

        raise RuntimeError(
            f"Gemini returned no image. Parts: {[list(p.keys()) for p in parts]}"
        )


# ---------------------------------------------------------------------------
# Backend 2: HF Inference API (free — just needs HF_TOKEN)
# ---------------------------------------------------------------------------

HF_INFERENCE_URL = "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-schnell"


async def generate_via_hf_inference(
    prompt: str,
    width: int = 1024,
    height: int = 680,
    num_steps: int = 4,
    guidance_scale: float = 0.0,
    seed: int = -1,
) -> bytes:
    """Call FLUX.1-schnell via the free HF Inference API. Returns image bytes."""
    headers = {
        "Authorization": f"Bearer {HF_TOKEN}",
        "Content-Type": "application/json",
    }

    payload: dict[str, Any] = {
        "inputs": prompt,
        "parameters": {
            "width": width,
            "height": height,
            "num_inference_steps": num_steps,
            "guidance_scale": guidance_scale,
        },
    }
    if seed >= 0:
        payload["parameters"]["seed"] = seed

    async with httpx.AsyncClient(timeout=120) as client:
        resp = await client.post(HF_INFERENCE_URL, headers=headers, json=payload)

        # Model loading: HF returns 503 while the model warms up
        if resp.status_code == 503:
            estimated_time = resp.json().get("estimated_time", 60)
            logger.info(f"Model loading, waiting {estimated_time:.0f}s...")
            await asyncio.sleep(min(estimated_time, 120))
            # Retry once
            resp = await client.post(HF_INFERENCE_URL, headers=headers, json=payload)

        if resp.status_code != 200:
            error_text = resp.text[:500]
            raise RuntimeError(
                f"HF Inference API error {resp.status_code}: {error_text}"
            )

        content_type = resp.headers.get("content-type", "")
        if "image" not in content_type and "octet-stream" not in content_type:
            raise RuntimeError(
                f"HF Inference API returned unexpected content-type: {content_type}. "
                f"Body: {resp.text[:300]}"
            )

        return resp.content


# ---------------------------------------------------------------------------
# Backend 2: HF Space (free — for custom LoRA / advanced config)
# ---------------------------------------------------------------------------

HF_PRESET_MAP = {
    "social_square": "social_square (1080x1080)",
    "social_portrait": "social_portrait (1080x1350)",
    "social_story": "social_story (1080x1920)",
    "hero": "hero (1920x1080)",
    "blog": "blog (1200x800)",
    "blog_wide": "hero (1920x1080)",
}


async def generate_via_hf_space(
    scene: str,
    subject_type: str | None = None,
    emotion: str | None = None,
    scene_setting: str | None = None,
    preset: str | None = None,
) -> dict[str, Any]:
    """Call the PatientPartner HF Space via Gradio API."""
    hf_preset = HF_PRESET_MAP.get(preset or "blog", "blog (1200x800)")
    space_host = f"https://{HF_SPACE_ID.replace('/', '-')}.hf.space"

    data = [
        scene,
        subject_type or "none",
        emotion or "none",
        scene_setting or "none",
        hf_preset,
        0.0,   # guidance_scale (schnell)
        4,     # num_steps
        -1,    # seed
    ]

    headers: dict[str, str] = {"Content-Type": "application/json"}
    if HF_TOKEN:
        headers["Authorization"] = f"Bearer {HF_TOKEN}"

    async with httpx.AsyncClient(timeout=300) as client:
        # Gradio 4+ /call endpoint
        resp = await client.post(
            f"{space_host}/call/generate",
            headers=headers,
            json={"data": data},
        )
        if resp.status_code != 200:
            raise RuntimeError(f"HF Space error {resp.status_code}: {resp.text}")

        event_id = resp.json().get("event_id")
        if not event_id:
            raise RuntimeError("HF Space did not return an event_id")

        # Poll SSE result
        for _ in range(120):
            await asyncio.sleep(5)
            result_resp = await client.get(
                f"{space_host}/call/generate/{event_id}",
                headers=headers,
            )
            if result_resp.status_code == 200:
                for line in result_resp.text.strip().split("\n"):
                    if line.startswith("data:"):
                        result_data = json.loads(line[5:].strip())
                        image_info = result_data[0]
                        return {
                            "image_url": image_info.get("url", "") if isinstance(image_info, dict) else image_info,
                            "prompt_used": result_data[1] if len(result_data) > 1 else "",
                            "model_used": f"hf-space:{HF_SPACE_ID}",
                        }
                if "event: complete" in result_resp.text:
                    raise RuntimeError("HF Space completed without image data")

        raise RuntimeError("HF Space generation timed out")


# ---------------------------------------------------------------------------
# Backend 3: Replicate (paid)
# ---------------------------------------------------------------------------

REPLICATE_MODEL_ID = "google/nano-banana-2"
REPLICATE_FALLBACK = "google/nano-banana-pro"
REPLICATE_BASE = "https://api.replicate.com/v1"
POLL_INTERVAL = 5
MAX_POLL_ATTEMPTS = 60


async def generate_via_replicate(
    prompt: str,
    aspect_ratio: str = "3:2",
    output_format: str = "jpg",
    reference_images: list[str] | None = None,
) -> dict[str, Any]:
    """Create and poll a Replicate prediction. Returns result dict."""
    headers = {
        "Authorization": f"Bearer {REPLICATE_API_TOKEN}",
        "Content-Type": "application/json",
    }

    payload: dict[str, Any] = {
        "input": {
            "prompt": prompt,
            "aspect_ratio": aspect_ratio,
            "output_format": output_format,
            "resolution": "2K",
        }
    }
    if reference_images:
        payload["input"]["image_input"] = reference_images

    model_id = REPLICATE_MODEL_ID
    async with httpx.AsyncClient(timeout=30) as client:
        url = f"{REPLICATE_BASE}/models/{model_id}/predictions"
        resp = await client.post(url, headers=headers, json=payload)

        if resp.status_code == 404:
            logger.warning(f"Model {model_id} not found, trying {REPLICATE_FALLBACK}")
            model_id = REPLICATE_FALLBACK
            url = f"{REPLICATE_BASE}/models/{model_id}/predictions"
            resp = await client.post(url, headers=headers, json=payload)

        if resp.status_code not in (200, 201):
            raise RuntimeError(f"Replicate API error {resp.status_code}: {resp.text}")

        prediction = resp.json()
        prediction_id = prediction["id"]

    # Poll for completion
    async with httpx.AsyncClient(timeout=30) as client:
        for _ in range(MAX_POLL_ATTEMPTS):
            resp = await client.get(
                f"{REPLICATE_BASE}/predictions/{prediction_id}",
                headers=headers,
            )
            if resp.status_code != 200:
                raise RuntimeError(f"Replicate poll error {resp.status_code}: {resp.text}")

            data = resp.json()
            status = data.get("status")

            if status == "succeeded":
                output = data.get("output")
                image_url = output if isinstance(output, str) else output[0]
                return {
                    "image_url": image_url,
                    "model_used": model_id,
                    "prediction_id": prediction_id,
                }
            elif status in ("failed", "canceled"):
                raise RuntimeError(f"Replicate generation {status}: {data.get('error', 'Unknown')}")

            await asyncio.sleep(POLL_INTERVAL)

    raise RuntimeError(f"Replicate timed out after {MAX_POLL_ATTEMPTS * POLL_INTERVAL}s")


# ---------------------------------------------------------------------------
# Core generation logic
# ---------------------------------------------------------------------------

async def _do_generate(
    scene: str,
    subject_type: str | None = None,
    emotion: str | None = None,
    scene_setting: str | None = None,
    preset: str | None = None,
    aspect_ratio: str | None = None,
    output_format: str = "jpg",
    additional_details: str | None = None,
    reference_images: list[str] | None = None,
    save_locally: bool = True,
    asset_type: str = "photo",
    descriptor: str = "generated",
) -> list[TextContent]:
    """Route to the active backend and return results."""

    # Resolve dimensions
    preset_data = RESOLUTION_PRESETS.get(preset, {}) if preset else {}
    ar = preset_data.get("aspect_ratio") or aspect_ratio or "3:2"
    width = preset_data.get("width", 1024)
    height = preset_data.get("height", 680)

    # Build enhanced prompt
    full_prompt = enhance_prompt(
        scene=scene,
        subject_type=subject_type,
        emotion=emotion,
        scene_setting=scene_setting,
        additional_details=additional_details,
    )

    logger.info(f"Backend: {BACKEND} | {ar} {width}x{height} {output_format}")
    logger.info(f"Prompt: {full_prompt[:200]}...")

    # ── Local PIL (sandbox / offline — no network required) ──
    if BACKEND == "local_pil":
        logger.info("Generating locally with PIL (sandbox mode)...")
        import asyncio as _asyncio
        image_bytes = await _asyncio.get_event_loop().run_in_executor(
            None,
            lambda: generate_local_pil_image(
                prompt=full_prompt,
                width=width,
                height=height,
                subject_type=subject_type,
                emotion=emotion,
            ),
        )

        response: dict[str, Any] = {
            "status": "success",
            "backend": "local_pil (sandbox demo)",
            "model": "pillow-local",
            "note": (
                "Sandbox mode: generated a branded placeholder. "
                "Set GOOGLE_API_KEY or HF_TOKEN for real AI-generated images."
            ),
            "prompt_used": full_prompt,
            "settings": {"aspect_ratio": ar, "width": width, "height": height},
        }

        filename = _generate_filename(asset_type, descriptor, ar, output_format)
        try:
            local_path = save_image_bytes(image_bytes, filename)
            response["local_path"] = local_path
            response["filename"] = filename
            logger.info(f"Saved: {local_path}")
        except Exception as e:
            response["save_error"] = str(e)

        return [TextContent(type="text", text=json.dumps(response, indent=2))]

    # ── Google Gemini (primary — works everywhere googleapis.com is reachable) ──
    if BACKEND == "google_gemini":
        logger.info("Generating via Google Gemini 2.0 Flash...")
        image_bytes = await generate_via_google_gemini(full_prompt)

        response: dict[str, Any] = {
            "status": "success",
            "backend": "google_gemini (free)",
            "model": "gemini-2.0-flash-exp",
            "prompt_used": full_prompt,
            "settings": {"aspect_ratio": ar, "width": width, "height": height},
        }

        if save_locally:
            filename = _generate_filename(asset_type, descriptor, ar, output_format)
            try:
                local_path = save_image_bytes(image_bytes, filename)
                response["local_path"] = local_path
                response["filename"] = filename
                logger.info(f"Saved: {local_path}")
            except Exception as e:
                response["save_error"] = str(e)
        else:
            response["image_base64"] = base64.b64encode(image_bytes).decode()

        return [TextContent(type="text", text=json.dumps(response, indent=2))]

    # ── Prompt-only fallback ──
    if BACKEND == "prompt_only":
        return [TextContent(type="text", text=json.dumps({
            "status": "prompt_only",
            "message": (
                "No API tokens configured. Set HF_TOKEN (free) in .env to enable "
                "image generation. Get one at https://huggingface.co/settings/tokens"
            ),
            "prompt": full_prompt,
            "settings": {"aspect_ratio": ar, "width": width, "height": height},
        }, indent=2))]

    # ── HF Inference API (free, primary) ──
    if BACKEND == "hf_inference":
        logger.info("Generating via HF Inference API (FLUX.1-schnell)...")
        image_bytes = await generate_via_hf_inference(
            prompt=full_prompt,
            width=width,
            height=height,
        )

        response: dict[str, Any] = {
            "status": "success",
            "backend": "hf_inference (free)",
            "model": "black-forest-labs/FLUX.1-schnell",
            "prompt_used": full_prompt,
            "settings": {"aspect_ratio": ar, "width": width, "height": height},
        }

        # Save locally
        if save_locally:
            filename = _generate_filename(asset_type, descriptor, ar, output_format)
            try:
                local_path = save_image_bytes(image_bytes, filename)
                response["local_path"] = local_path
                response["filename"] = filename
                logger.info(f"Saved: {local_path}")
            except Exception as e:
                response["save_error"] = str(e)
                logger.warning(f"Failed to save: {e}")
        else:
            # Return as base64 if not saving
            response["image_base64"] = base64.b64encode(image_bytes).decode()

        return [TextContent(type="text", text=json.dumps(response, indent=2))]

    # ── HF Space (free, custom LoRA) ──
    if BACKEND == "hf_space":
        logger.info(f"Generating via HF Space: {HF_SPACE_ID}...")
        hf_result = await generate_via_hf_space(
            scene=scene,
            subject_type=subject_type,
            emotion=emotion,
            scene_setting=scene_setting,
            preset=preset or "blog",
        )

        response = {
            "status": "success",
            "backend": "hf_space (free)",
            "model": hf_result.get("model_used", f"hf-space:{HF_SPACE_ID}"),
            "image_url": hf_result["image_url"],
            "prompt_used": hf_result.get("prompt_used", full_prompt),
            "settings": {"aspect_ratio": ar, "width": width, "height": height},
        }

        if save_locally and hf_result.get("image_url"):
            filename = _generate_filename(asset_type, descriptor, ar, output_format)
            try:
                local_path = await download_image(hf_result["image_url"], filename)
                response["local_path"] = local_path
                response["filename"] = filename
            except Exception as e:
                response["download_error"] = str(e)

        return [TextContent(type="text", text=json.dumps(response, indent=2))]

    # ── Replicate (paid) ──
    logger.info("Generating via Replicate...")
    rep_result = await generate_via_replicate(
        prompt=full_prompt,
        aspect_ratio=ar,
        output_format=output_format,
        reference_images=reference_images,
    )

    response = {
        "status": "success",
        "backend": "replicate (paid)",
        "model": rep_result["model_used"],
        "image_url": rep_result["image_url"],
        "prediction_id": rep_result["prediction_id"],
        "prompt_used": full_prompt,
        "settings": {"aspect_ratio": ar, "output_format": output_format},
    }

    if save_locally:
        filename = _generate_filename(asset_type, descriptor, ar, output_format)
        try:
            local_path = await download_image(rep_result["image_url"], filename)
            response["local_path"] = local_path
            response["filename"] = filename
        except Exception as e:
            response["download_error"] = str(e)

    return [TextContent(type="text", text=json.dumps(response, indent=2))]


# ---------------------------------------------------------------------------
# MCP Server — Tools
# ---------------------------------------------------------------------------

server = Server("patientpartner-image-generator")


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available image generation tools."""

    backend_note = {
        "local_pil": "LOCAL SANDBOX MODE — generates branded placeholder (set GOOGLE_API_KEY for real images)",
        "google_gemini": "Using Gemini 2.0 Flash image generation (free)",
        "hf_inference": "Using FLUX.1-schnell via HF Inference API (free)",
        "hf_space": f"Using custom HF Space: {HF_SPACE_ID} (free)",
        "replicate": "Using NanoBanana2 via Replicate (paid)",
        "prompt_only": "No backend configured. Set GOOGLE_API_KEY (free at aistudio.google.com).",
    }[BACKEND]

    return [
        Tool(
            name="generate_image",
            description=(
                f"Generate a photorealistic healthcare image for PatientPartner.com. "
                f"Auto-enhances prompts with brand context. {backend_note}"
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "scene": {
                        "type": "string",
                        "description": (
                            "Describe the scene. Be specific about people, setting, action. "
                            "Example: 'A woman in her 50s discussing her treatment journey "
                            "with a younger peer mentor over coffee'"
                        ),
                    },
                    "subject_type": {
                        "type": "string",
                        "enum": list(SUBJECT_TEMPLATES.keys()),
                        "description": "Type of subject — adds appropriate appearance details.",
                    },
                    "emotion": {
                        "type": "string",
                        "enum": list(EMOTION_MODIFIERS.keys()),
                        "description": "Emotional tone of the image.",
                    },
                    "scene_setting": {
                        "type": "string",
                        "enum": list(SCENE_TEMPLATES.keys()),
                        "description": "Pre-defined environment/setting.",
                    },
                    "preset": {
                        "type": "string",
                        "enum": list(RESOLUTION_PRESETS.keys()),
                        "description": "Resolution preset. Overrides aspect_ratio.",
                    },
                    "aspect_ratio": {
                        "type": "string",
                        "enum": ["1:1", "16:9", "9:16", "4:3", "3:4", "3:2", "2:3", "4:5", "5:4"],
                        "description": "Custom aspect ratio (ignored if preset is set).",
                    },
                    "output_format": {
                        "type": "string",
                        "enum": ["jpg", "png", "webp"],
                        "default": "jpg",
                    },
                    "additional_details": {
                        "type": "string",
                        "description": "Extra details: clothing, props, background elements.",
                    },
                    "reference_images": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Reference image URLs (Replicate backend only).",
                    },
                    "save_locally": {
                        "type": "boolean",
                        "default": True,
                        "description": "Save image to creative-output/generated-images/.",
                    },
                },
                "required": ["scene"],
            },
        ),
        Tool(
            name="generate_patient_photo",
            description=(
                "Quick: Generate a patient photo. Just describe the patient. "
                f"{backend_note}"
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "description": {
                        "type": "string",
                        "description": "Describe the patient. Example: 'A middle-aged man looking hopeful after consultation'",
                    },
                    "emotion": {
                        "type": "string",
                        "enum": list(EMOTION_MODIFIERS.keys()),
                        "default": "hopeful",
                    },
                    "preset": {
                        "type": "string",
                        "enum": list(RESOLUTION_PRESETS.keys()),
                        "default": "blog",
                    },
                },
                "required": ["description"],
            },
        ),
        Tool(
            name="generate_mentor_photo",
            description=(
                "Quick: Generate a peer mentor/supporter photo. "
                f"{backend_note}"
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "description": {
                        "type": "string",
                        "description": "Describe the mentor. Example: 'A warm woman in her 60s sharing her recovery story'",
                    },
                    "emotion": {
                        "type": "string",
                        "enum": list(EMOTION_MODIFIERS.keys()),
                        "default": "supportive",
                    },
                    "preset": {
                        "type": "string",
                        "enum": list(RESOLUTION_PRESETS.keys()),
                        "default": "blog",
                    },
                },
                "required": ["description"],
            },
        ),
        Tool(
            name="generate_hero_image",
            description=(
                "Quick: Generate a 16:9 hero image for landing pages. "
                f"{backend_note}"
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "description": {
                        "type": "string",
                        "description": "Describe the hero scene.",
                    },
                    "subject_type": {
                        "type": "string",
                        "enum": list(SUBJECT_TEMPLATES.keys()),
                    },
                    "emotion": {
                        "type": "string",
                        "enum": list(EMOTION_MODIFIERS.keys()),
                        "default": "hopeful",
                    },
                },
                "required": ["description"],
            },
        ),
        Tool(
            name="generate_social_image",
            description=(
                "Quick: Generate a social media image. Auto-sizes per platform. "
                f"{backend_note}"
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "description": {
                        "type": "string",
                        "description": "Describe the social media image content.",
                    },
                    "platform": {
                        "type": "string",
                        "enum": ["instagram_feed", "instagram_story", "linkedin", "facebook", "twitter"],
                        "default": "instagram_feed",
                    },
                    "subject_type": {
                        "type": "string",
                        "enum": list(SUBJECT_TEMPLATES.keys()),
                    },
                    "emotion": {
                        "type": "string",
                        "enum": list(EMOTION_MODIFIERS.keys()),
                        "default": "hopeful",
                    },
                },
                "required": ["description"],
            },
        ),
        Tool(
            name="list_presets",
            description="List all resolution presets, subject types, emotions, and settings.",
            inputSchema={"type": "object", "properties": {}},
        ),
    ]


# ---------------------------------------------------------------------------
# Tool handlers
# ---------------------------------------------------------------------------

PLATFORM_PRESETS: dict[str, str] = {
    "instagram_feed": "social_square",
    "instagram_story": "social_story",
    "linkedin": "social_square",
    "facebook": "social_square",
    "twitter": "hero",
}


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Route tool calls."""

    if name == "list_presets":
        return [TextContent(type="text", text=json.dumps({
            "active_backend": BACKEND,
            "resolution_presets": {
                k: v["description"] for k, v in RESOLUTION_PRESETS.items()
            },
            "subject_types": list(SUBJECT_TEMPLATES.keys()),
            "emotions": list(EMOTION_MODIFIERS.keys()),
            "scene_settings": list(SCENE_TEMPLATES.keys()),
            "output_formats": ["jpg", "png", "webp"],
        }, indent=2))]

    if name == "generate_image":
        return await _do_generate(
            scene=arguments["scene"],
            subject_type=arguments.get("subject_type"),
            emotion=arguments.get("emotion"),
            scene_setting=arguments.get("scene_setting"),
            preset=arguments.get("preset"),
            aspect_ratio=arguments.get("aspect_ratio"),
            output_format=arguments.get("output_format", "jpg"),
            additional_details=arguments.get("additional_details"),
            reference_images=arguments.get("reference_images"),
            save_locally=arguments.get("save_locally", True),
        )

    if name == "generate_patient_photo":
        return await _do_generate(
            scene=arguments["description"],
            subject_type="patient",
            emotion=arguments.get("emotion", "hopeful"),
            preset=arguments.get("preset", "blog"),
            asset_type="patient",
            descriptor="portrait",
        )

    if name == "generate_mentor_photo":
        return await _do_generate(
            scene=arguments["description"],
            subject_type="mentor",
            emotion=arguments.get("emotion", "supportive"),
            preset=arguments.get("preset", "blog"),
            asset_type="mentor",
            descriptor="portrait",
        )

    if name == "generate_hero_image":
        return await _do_generate(
            scene=arguments["description"],
            subject_type=arguments.get("subject_type"),
            emotion=arguments.get("emotion", "hopeful"),
            preset="hero",
            asset_type="hero",
            descriptor="landing",
        )

    if name == "generate_social_image":
        platform = arguments.get("platform", "instagram_feed")
        return await _do_generate(
            scene=arguments["description"],
            subject_type=arguments.get("subject_type"),
            emotion=arguments.get("emotion", "hopeful"),
            preset=PLATFORM_PRESETS.get(platform, "social_square"),
            asset_type="social",
            descriptor=platform.replace("_", "-"),
        )

    raise ValueError(f"Unknown tool: {name}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

async def main():
    """Run the MCP server via stdio."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


if __name__ == "__main__":
    asyncio.run(main())
