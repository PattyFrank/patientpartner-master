"""
PatientPartner Image Generator MCP Server

Generates photorealistic images of real-looking people for PatientPartner.com.
Prompts are engineered to produce actual portraits — not abstract, not illustrated.

Backends (tried in order, auto-fallback on failure):
  1. Replicate       — google/nano-banana-2      (REPLICATE_API_TOKEN)
  2. Google Imagen 3 — imagen-3.0-generate-002   (GOOGLE_API_KEY, google-genai SDK)
  3. Google Gemini   — gemini-2.0-flash-exp      (GOOGLE_API_KEY, google-genai SDK)
  4. HF Inference    — FLUX.1-schnell            (HF_TOKEN)
  5. HF Space        — Custom Gradio Space       (HF_SPACE_ID)
  6. Prompt-only     — Returns prompt only, no image

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
from mcp.types import TextContent, Tool

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

load_dotenv()

GOOGLE_API_KEY      = os.getenv("GOOGLE_API_KEY", "")
HF_TOKEN            = os.getenv("HF_TOKEN", "")
HF_SPACE_ID         = os.getenv("HF_SPACE_ID", "")
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN", "")

# Build ordered list of available backends (tried in this order)
AVAILABLE_BACKENDS: list[str] = []
if REPLICATE_API_TOKEN:
    AVAILABLE_BACKENDS.append("replicate")       # Nano Banana 2 — primary
if GOOGLE_API_KEY:
    AVAILABLE_BACKENDS.append("google_imagen")   # Imagen 3 — fallback
    AVAILABLE_BACKENDS.append("google_gemini")   # Gemini Flash — fallback
if HF_TOKEN:
    AVAILABLE_BACKENDS.append("hf_inference")
if HF_SPACE_ID:
    AVAILABLE_BACKENDS.append("hf_space")
if not AVAILABLE_BACKENDS:
    AVAILABLE_BACKENDS.append("prompt_only")

BACKEND = AVAILABLE_BACKENDS[0]  # primary, for display

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
        "width": 1024, "height": 1024,
        "description": "Square (1080×1080) — Instagram feed, LinkedIn, Facebook",
    },
    "social_portrait": {
        "aspect_ratio": "4:5",
        "width": 832, "height": 1040,
        "description": "Portrait (1080×1350) — Instagram feed optimal, Facebook ads",
    },
    "social_story": {
        "aspect_ratio": "9:16",
        "width": 576, "height": 1024,
        "description": "Vertical (1080×1920) — Instagram Stories, TikTok, Reels",
    },
    "hero": {
        "aspect_ratio": "16:9",
        "width": 1344, "height": 768,
        "description": "Wide (1920×1080) — Website hero sections, landing pages",
    },
    "blog": {
        "aspect_ratio": "3:2",
        "width": 1216, "height": 832,
        "description": "Landscape (1200×800) — Blog posts, articles",
    },
    "blog_wide": {
        "aspect_ratio": "16:9",
        "width": 1344, "height": 768,
        "description": "Wide landscape (1200×675) — Blog headers, newsletter banners",
    },
}

# ---------------------------------------------------------------------------
# Prompt engineering — tuned for photorealistic portrait generation
#
# Design principle: describe what you SEE in the final photo.
# Lead with the person, their physical presence, what they're doing.
# Technical photography modifiers come last as quality anchors.
# ---------------------------------------------------------------------------

# What the camera sees — physical presence, not character notes
SUBJECT_LOOKS: dict[str, str] = {
    "patient": (
        "a real person sitting in a healthcare setting, "
        "wearing casual everyday clothes, natural relaxed posture"
    ),
    "mentor": (
        "a warm person in their 50s or 60s with kind eyes and a genuine smile, "
        "leaning forward slightly, engaged and present"
    ),
    "caregiver": (
        "a caring person gently beside someone else, "
        "attentive body language, hand near the other person, natural and tender"
    ),
    "healthcare_professional": (
        "a healthcare professional in a white coat or scrubs, "
        "confident posture, approachable expression, in a clinic or hospital"
    ),
    "patient_and_mentor": (
        "two people sitting together at a table, one older and one younger, "
        "both leaning in, mid-conversation, genuine eye contact between them"
    ),
    "group": (
        "three to five diverse people sitting in a circle or around a table, "
        "relaxed and engaged with each other, warm communal energy"
    ),
}

# What the expression looks like — concrete, visible, not abstract
EXPRESSION_LOOKS: dict[str, str] = {
    "hopeful":    "soft genuine smile, bright eyes looking up slightly, relaxed brow",
    "supportive": "warm attentive expression, leaning in, eyes fully on the other person",
    "reflective": "quiet calm face, looking slightly down or into distance, soft neutral mouth",
    "confident":  "direct eye contact with camera, subtle assured smile, shoulders back",
    "grateful":   "full warm smile reaching the eyes, head tilted slightly, relaxed jaw",
    "determined": "focused steady gaze, firm set jaw, purposeful composed expression",
    "relieved":   "exhale expression, closed-eye smile or gentle laugh, shoulders dropped",
    "connected":  "laughing or smiling at another person, shared moment, turned toward them",
}

# Specific locations — concrete visual environments
SETTING_LOOKS: dict[str, str] = {
    "consultation":  "bright modern medical office, large window, plants, two chairs facing each other",
    "waiting_room":  "comfortable healthcare waiting area, warm light, wooden chairs, magazines on table",
    "home":          "cozy living room, natural afternoon window light, bookshelf or couch visible",
    "outdoors":      "outdoor park bench or garden, dappled sunlight through trees, green background",
    "hospital":      "clean modern hospital room or corridor, soft overhead light, white and warm tones",
    "support_group": "community center meeting room, circle of chairs, warm interior lighting",
    "virtual":       "home office desk, laptop open on video call, soft ring light, bookshelves",
    "pharmacy":      "pharmacy counter, warm fluorescent light, shelves of medication behind",
    "recovery":      "rehab or wellness room, exercise equipment in background, encouraging space",
}

# Photography anchors — kept short to not overwhelm the subject description
PHOTO_QUALITY = (
    "RAW photo, 85mm lens, f/1.8 aperture, shallow depth of field, "
    "natural light, photorealistic, highly detailed skin texture, "
    "real person, documentary photography"
)

NEGATIVE_PROMPT = (
    "illustration, painting, cartoon, anime, CGI, 3D render, "
    "plastic skin, smooth unrealistic skin, fake smile, stock photo pose, "
    "text, watermark, logo, border, frame"
)


def _has_overlap(scene_lower: str, template: str, threshold: int = 2) -> bool:
    """Check if enough words from the template already appear in the scene."""
    keywords = [w for w in template.lower().split() if len(w) > 3]
    if not keywords:
        return False
    hits = sum(1 for w in keywords if w in scene_lower)
    return hits >= threshold


def build_prompt(
    scene: str,
    subject_type: str | None = None,
    emotion: str | None = None,
    scene_setting: str | None = None,
    additional_details: str | None = None,
) -> str:
    """
    Build a photorealistic portrait prompt.

    The user's scene description ALWAYS leads. Template data is only added
    when it provides genuinely new visual information not already in the scene.
    This prevents duplication like "leaning in ... leaning in" or
    "a warm person in their 50s ... a Latino man in his 60s".

    Structure: [scene] [+ subject if new] [+ setting if new] [+ expression if new] [photo tech]
    """
    scene_lower = scene.lower()
    parts: list[str] = []

    # 1. User's scene description — always first, always included
    parts.append(scene)

    # 2. Subject template — only if it adds info the scene doesn't already cover
    if subject_type and subject_type in SUBJECT_LOOKS:
        template = SUBJECT_LOOKS[subject_type]
        if not _has_overlap(scene_lower, template):
            parts.append(template)

    # 3. Setting — only if scene doesn't already describe the environment
    if scene_setting and scene_setting in SETTING_LOOKS:
        template = SETTING_LOOKS[scene_setting]
        if not _has_overlap(scene_lower, template):
            parts.append(template)

    # 4. Expression — only if scene doesn't already describe the face/body
    if emotion and emotion in EXPRESSION_LOOKS:
        template = EXPRESSION_LOOKS[emotion]
        if not _has_overlap(scene_lower, template):
            parts.append(template)

    # 5. Extra details from user
    if additional_details:
        parts.append(additional_details)

    # 6. Photography quality anchor — always included
    parts.append(PHOTO_QUALITY)

    return ", ".join(parts)


# ---------------------------------------------------------------------------
# File helpers
# ---------------------------------------------------------------------------

def save_image_bytes(image_bytes: bytes, filename: str) -> str:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    filepath = OUTPUT_DIR / filename
    filepath.write_bytes(image_bytes)
    return str(filepath)


async def download_image(url: str, filename: str) -> str:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    filepath = OUTPUT_DIR / filename
    async with httpx.AsyncClient(timeout=60, follow_redirects=True) as client:
        resp = await client.get(url)
        if resp.status_code != 200:
            raise RuntimeError(f"Download failed: HTTP {resp.status_code}")
        filepath.write_bytes(resp.content)
    return str(filepath)


def _filename(asset_type: str, descriptor: str, aspect_ratio: str, fmt: str) -> str:
    ratio_str = aspect_ratio.replace(":", "x")
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    return f"{asset_type}-{descriptor}-{ratio_str}-{ts}.{fmt}"


# ---------------------------------------------------------------------------
# Backend: Google (via google-genai SDK)
#   - Imagen 3: imagen-3.0-generate-002 (best photorealism for people)
#   - Gemini Flash: gemini-2.0-flash-exp (multimodal, image output)
# ---------------------------------------------------------------------------

_google_client = None


def _get_google_client():
    global _google_client
    if _google_client is None:
        from google import genai  # lazy import — only if backend is used
        _google_client = genai.Client(api_key=GOOGLE_API_KEY)
    return _google_client


async def _imagen_generate(prompt: str) -> bytes:
    """Generate with Imagen 3 — best for photorealistic people."""
    from google.genai import types
    client = _get_google_client()
    # Run sync SDK call in thread to not block event loop
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, lambda: client.models.generate_images(
        model="imagen-3.0-generate-002",
        prompt=prompt,
        config=types.GenerateImagesConfig(
            number_of_images=1,
            aspect_ratio="3:2",
        ),
    ))
    if not result.generated_images:
        raise RuntimeError("Imagen 3 returned no images")
    return result.generated_images[0].image.image_bytes


async def _gemini_generate(prompt: str) -> bytes:
    """Generate with Gemini 2.0 Flash — multimodal image output."""
    from google.genai import types
    client = _get_google_client()
    loop = asyncio.get_event_loop()
    response = await loop.run_in_executor(None, lambda: client.models.generate_content(
        model="gemini-2.0-flash-exp",
        contents=f"Generate a photorealistic photograph: {prompt}",
        config=types.GenerateContentConfig(response_modalities=["IMAGE", "TEXT"]),
    ))
    for part in response.candidates[0].content.parts:
        if part.inline_data:
            return part.inline_data.data
    raise RuntimeError("Gemini returned no image data")


# ---------------------------------------------------------------------------
# Backend: HF Inference API (FLUX.1-schnell)
# ---------------------------------------------------------------------------

HF_URL = "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-schnell"


async def _hf_generate(prompt: str, width: int, height: int) -> bytes:
    headers = {"Authorization": f"Bearer {HF_TOKEN}", "Content-Type": "application/json"}
    payload = {
        "inputs": prompt,
        "parameters": {"width": width, "height": height, "num_inference_steps": 4},
    }
    async with httpx.AsyncClient(timeout=120) as client:
        resp = await client.post(HF_URL, headers=headers, json=payload)
        if resp.status_code == 503:
            wait = resp.json().get("estimated_time", 30)
            logger.info(f"HF model loading, waiting {wait:.0f}s...")
            await asyncio.sleep(min(wait, 60))
            resp = await client.post(HF_URL, headers=headers, json=payload)
        if resp.status_code != 200:
            raise RuntimeError(f"HF Inference {resp.status_code}: {resp.text[:400]}")
        return resp.content


# ---------------------------------------------------------------------------
# Backend: HF Space (Gradio 4+)
# ---------------------------------------------------------------------------

async def _hf_space_generate(scene: str, subject_type: str | None, emotion: str | None,
                               scene_setting: str | None, width: int, height: int) -> dict[str, Any]:
    space_host = f"https://{HF_SPACE_ID.replace('/', '-')}.hf.space"
    headers = {"Content-Type": "application/json"}
    if HF_TOKEN:
        headers["Authorization"] = f"Bearer {HF_TOKEN}"

    data = [scene, subject_type or "none", emotion or "none",
            scene_setting or "none", width, height]

    async with httpx.AsyncClient(timeout=300) as client:
        resp = await client.post(f"{space_host}/call/generate", headers=headers, json={"data": data})
        if resp.status_code != 200:
            raise RuntimeError(f"HF Space {resp.status_code}: {resp.text}")
        event_id = resp.json().get("event_id")
        if not event_id:
            raise RuntimeError("HF Space returned no event_id")

        for _ in range(120):
            await asyncio.sleep(5)
            r = await client.get(f"{space_host}/call/generate/{event_id}", headers=headers)
            if r.status_code == 200:
                for line in r.text.strip().split("\n"):
                    if line.startswith("data:"):
                        d = json.loads(line[5:].strip())
                        img = d[0]
                        return {
                            "image_url": img.get("url", "") if isinstance(img, dict) else img,
                            "model": f"hf-space:{HF_SPACE_ID}",
                        }

    raise RuntimeError("HF Space timed out")


# ---------------------------------------------------------------------------
# Backend: Replicate — Nano Banana 2 (google/nano-banana-2)
#   Google's Gemini 3.1 Flash Image model. Best photorealism + speed.
#   Supports: prompt, aspect_ratio, resolution, output_format, image_input
# ---------------------------------------------------------------------------

REPLICATE_MODEL = "google/nano-banana-2"
REPLICATE_BASE  = "https://api.replicate.com/v1"

# Map our aspect ratios to Nano Banana 2 supported values
_NB2_ASPECT_RATIOS = {
    "1:1", "2:3", "3:2", "3:4", "4:3", "4:5", "5:4", "9:16", "16:9", "21:9",
    "1:4", "4:1", "1:8", "8:1",
}


async def _replicate_generate(prompt: str, aspect_ratio: str, output_format: str) -> dict[str, Any]:
    headers = {
        "Authorization": f"Bearer {REPLICATE_API_TOKEN}",
        "Content-Type": "application/json",
        "Prefer": "wait",  # sync mode — blocks until complete (up to 60s)
    }
    ar = aspect_ratio if aspect_ratio in _NB2_ASPECT_RATIOS else "3:2"
    fmt = output_format if output_format in ("jpg", "png") else "jpg"

    payload = {
        "input": {
            "prompt": prompt,
            "aspect_ratio": ar,
            "output_format": fmt,
            "resolution": "2K",
        }
    }

    # Try sync mode first (Prefer: wait), fall back to polling
    async with httpx.AsyncClient(timeout=120) as client:
        resp = await client.post(
            f"{REPLICATE_BASE}/models/{REPLICATE_MODEL}/predictions",
            headers=headers, json=payload,
        )
        if resp.status_code not in (200, 201):
            raise RuntimeError(f"Replicate {resp.status_code}: {resp.text[:400]}")

        data = resp.json()
        prediction_id = data["id"]

        # If sync mode returned a completed prediction
        if data.get("status") == "succeeded" and data.get("output"):
            output = data["output"]
            return {
                "image_url": output if isinstance(output, str) else output[0],
                "prediction_id": prediction_id,
                "model": REPLICATE_MODEL,
            }

    # Poll for completion (if sync mode didn't finish in time)
    poll_headers = {
        "Authorization": f"Bearer {REPLICATE_API_TOKEN}",
        "Content-Type": "application/json",
    }
    async with httpx.AsyncClient(timeout=30) as client:
        for attempt in range(60):
            await asyncio.sleep(3 if attempt < 10 else 5)
            r = await client.get(
                f"{REPLICATE_BASE}/predictions/{prediction_id}",
                headers=poll_headers,
            )
            data = r.json()
            if data["status"] == "succeeded":
                output = data["output"]
                return {
                    "image_url": output if isinstance(output, str) else output[0],
                    "prediction_id": prediction_id,
                    "model": REPLICATE_MODEL,
                }
            elif data["status"] in ("failed", "canceled"):
                raise RuntimeError(f"Replicate {data['status']}: {data.get('error')}")

    raise RuntimeError("Replicate timed out after 5 minutes")


# ---------------------------------------------------------------------------
# Core generation
# ---------------------------------------------------------------------------

async def _generate(
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

    preset_data = RESOLUTION_PRESETS.get(preset or "", {})
    ar     = preset_data.get("aspect_ratio") or aspect_ratio or "3:2"
    width  = preset_data.get("width",  1216)
    height = preset_data.get("height", 832)

    prompt = build_prompt(
        scene=scene,
        subject_type=subject_type,
        emotion=emotion,
        scene_setting=scene_setting,
        additional_details=additional_details,
    )

    logger.info(f"Backends available: {AVAILABLE_BACKENDS}")
    logger.info(f"{ar} {width}×{height} — {prompt[:120]}...")

    # ── Prompt-only ──
    if AVAILABLE_BACKENDS == ["prompt_only"]:
        return [TextContent(type="text", text=json.dumps({
            "status": "prompt_only",
            "message": "No API keys set. Add GOOGLE_API_KEY or HF_TOKEN to .env to generate images.",
            "prompt": prompt,
            "negative_prompt": NEGATIVE_PROMPT,
            "settings": {"aspect_ratio": ar, "width": width, "height": height},
        }, indent=2))]

    # ── Try each backend in order, fallback on failure ──
    errors: list[str] = []

    for backend in AVAILABLE_BACKENDS:
        if backend == "prompt_only":
            continue

        logger.info(f"Trying backend: {backend}")
        try:
            image_bytes: bytes | None = None
            image_url: str | None = None
            model_name = backend
            extra: dict[str, Any] = {}

            if backend == "google_imagen":
                image_bytes = await _imagen_generate(prompt)
                model_name = "imagen-3.0-generate-002"

            elif backend == "google_gemini":
                image_bytes = await _gemini_generate(prompt)
                model_name = "gemini-2.0-flash-exp"

            elif backend == "hf_inference":
                image_bytes = await _hf_generate(prompt, width, height)
                model_name = "FLUX.1-schnell"

            elif backend == "hf_space":
                hf = await _hf_space_generate(scene, subject_type, emotion, scene_setting, width, height)
                image_url = hf.get("image_url", "")
                model_name = hf.get("model", f"hf-space:{HF_SPACE_ID}")

            elif backend == "replicate":
                rep = await _replicate_generate(prompt, ar, output_format)
                image_url = rep.get("image_url", "")
                model_name = rep.get("model", REPLICATE_MODEL)
                extra["prediction_id"] = rep.get("prediction_id")

            # Build result
            result: dict[str, Any] = {
                "status": "success",
                "backend": backend,
                "model": model_name,
                "prompt": prompt,
                "negative_prompt": NEGATIVE_PROMPT,
                "settings": {"aspect_ratio": ar, "width": width, "height": height},
            }
            result.update({k: v for k, v in extra.items() if v})

            if image_bytes and save_locally:
                fname = _filename(asset_type, descriptor, ar, output_format)
                result["local_path"] = save_image_bytes(image_bytes, fname)
                result["filename"] = fname
            elif image_bytes:
                result["image_base64"] = base64.b64encode(image_bytes).decode()
            elif image_url:
                result["image_url"] = image_url
                if save_locally:
                    fname = _filename(asset_type, descriptor, ar, output_format)
                    result["local_path"] = await download_image(image_url, fname)
                    result["filename"] = fname

            if errors:
                result["fallback_note"] = f"Fell through {len(errors)} backend(s): {', '.join(errors)}"

            logger.info(f"Success with {backend}")
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        except Exception as e:
            err_msg = f"{backend}: {e}"
            logger.warning(f"Backend failed — {err_msg}")
            errors.append(err_msg)
            continue

    # All backends failed — return prompt + errors so user can debug
    return [TextContent(type="text", text=json.dumps({
        "status": "all_backends_failed",
        "errors": errors,
        "message": "All image backends failed. The prompt is still valid — try running locally.",
        "prompt": prompt,
        "negative_prompt": NEGATIVE_PROMPT,
        "settings": {"aspect_ratio": ar, "width": width, "height": height},
    }, indent=2))]


# ---------------------------------------------------------------------------
# MCP Server
# ---------------------------------------------------------------------------

server = Server("patientpartner-image-generator")

PLATFORM_TO_PRESET = {
    "instagram_feed":  "social_square",
    "instagram_story": "social_story",
    "linkedin":        "social_square",
    "facebook":        "social_square",
    "twitter":         "hero",
}

_BACKEND_NAMES = {
    "replicate":     "Nano Banana 2 (Replicate)",
    "google_imagen": "Imagen 3",
    "google_gemini": "Gemini 2.0 Flash",
    "hf_inference":  "FLUX.1-schnell (HF)",
    "hf_space":      f"HF Space: {HF_SPACE_ID}",
    "prompt_only":   "prompt-only",
}
_backend_label = " → ".join(_BACKEND_NAMES.get(b, b) for b in AVAILABLE_BACKENDS)


@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="generate_image",
            description=(
                f"Generate a photorealistic photo of a person for PatientPartner.com. "
                f"Describe the person and scene — the MCP handles prompt engineering. "
                f"Active backend: {_backend_label}"
            ),
            inputSchema={
                "type": "object",
                "required": ["scene"],
                "properties": {
                    "scene": {
                        "type": "string",
                        "description": (
                            "Describe the person and what they are doing. "
                            "Example: 'A woman in her 50s sitting across from a younger patient, "
                            "having a warm conversation about her treatment journey'"
                        ),
                    },
                    "subject_type": {
                        "type": "string",
                        "enum": list(SUBJECT_LOOKS.keys()),
                        "description": "Who is in the image.",
                    },
                    "emotion": {
                        "type": "string",
                        "enum": list(EXPRESSION_LOOKS.keys()),
                        "description": "Visible expression and emotional tone.",
                    },
                    "scene_setting": {
                        "type": "string",
                        "enum": list(SETTING_LOOKS.keys()),
                        "description": "Where the scene takes place.",
                    },
                    "preset": {
                        "type": "string",
                        "enum": list(RESOLUTION_PRESETS.keys()),
                        "description": "Output size preset.",
                    },
                    "aspect_ratio": {
                        "type": "string",
                        "enum": ["1:1", "16:9", "9:16", "4:3", "3:4", "3:2", "2:3", "4:5"],
                        "description": "Custom aspect ratio (ignored if preset is set).",
                    },
                    "output_format": {
                        "type": "string",
                        "enum": ["jpg", "png", "webp"],
                        "default": "jpg",
                    },
                    "additional_details": {
                        "type": "string",
                        "description": "Extra specifics: hair color, clothing, props, background elements.",
                    },
                    "save_locally": {
                        "type": "boolean",
                        "default": True,
                        "description": "Save to creative-output/generated-images/",
                    },
                },
            },
        ),
        Tool(
            name="generate_patient_photo",
            description=f"Quick: photorealistic patient photo. Describe the person. Backend: {_backend_label}",
            inputSchema={
                "type": "object",
                "required": ["description"],
                "properties": {
                    "description": {
                        "type": "string",
                        "description": "Describe the patient. Example: 'A Black woman in her 40s sitting in a clinic waiting room, looking calm and hopeful'",
                    },
                    "emotion": {"type": "string", "enum": list(EXPRESSION_LOOKS.keys()), "default": "hopeful"},
                    "scene_setting": {"type": "string", "enum": list(SETTING_LOOKS.keys())},
                    "preset": {"type": "string", "enum": list(RESOLUTION_PRESETS.keys()), "default": "blog"},
                    "output_format": {"type": "string", "enum": ["jpg", "png", "webp"], "default": "jpg"},
                },
            },
        ),
        Tool(
            name="generate_mentor_photo",
            description=f"Quick: photorealistic peer mentor photo. Backend: {_backend_label}",
            inputSchema={
                "type": "object",
                "required": ["description"],
                "properties": {
                    "description": {
                        "type": "string",
                        "description": "Describe the mentor. Example: 'A Latino man in his 60s with a warm expression, sitting across from a younger person'",
                    },
                    "emotion": {"type": "string", "enum": list(EXPRESSION_LOOKS.keys()), "default": "supportive"},
                    "scene_setting": {"type": "string", "enum": list(SETTING_LOOKS.keys())},
                    "preset": {"type": "string", "enum": list(RESOLUTION_PRESETS.keys()), "default": "blog"},
                    "output_format": {"type": "string", "enum": ["jpg", "png", "webp"], "default": "jpg"},
                },
            },
        ),
        Tool(
            name="generate_hero_image",
            description=f"Quick: 16:9 hero image for landing pages. Backend: {_backend_label}",
            inputSchema={
                "type": "object",
                "required": ["description"],
                "properties": {
                    "description": {
                        "type": "string",
                        "description": "Describe the hero scene. Example: 'A diverse group of three patients and a mentor in a bright modern clinic, all smiling'",
                    },
                    "subject_type": {"type": "string", "enum": list(SUBJECT_LOOKS.keys())},
                    "emotion": {"type": "string", "enum": list(EXPRESSION_LOOKS.keys()), "default": "hopeful"},
                    "output_format": {"type": "string", "enum": ["jpg", "png", "webp"], "default": "jpg"},
                },
            },
        ),
        Tool(
            name="generate_social_image",
            description=f"Quick: social media photo, auto-sized per platform. Backend: {_backend_label}",
            inputSchema={
                "type": "object",
                "required": ["description"],
                "properties": {
                    "description": {"type": "string", "description": "Describe the person and scene."},
                    "platform": {
                        "type": "string",
                        "enum": ["instagram_feed", "instagram_story", "linkedin", "facebook", "twitter"],
                        "default": "instagram_feed",
                    },
                    "subject_type": {"type": "string", "enum": list(SUBJECT_LOOKS.keys())},
                    "emotion": {"type": "string", "enum": list(EXPRESSION_LOOKS.keys()), "default": "hopeful"},
                    "output_format": {"type": "string", "enum": ["jpg", "png", "webp"], "default": "jpg"},
                },
            },
        ),
        Tool(
            name="list_presets",
            description="List all available options: presets, subject types, emotions, scene settings.",
            inputSchema={"type": "object", "properties": {}},
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:

    if name == "list_presets":
        return [TextContent(type="text", text=json.dumps({
            "active_backend": BACKEND,
            "backend_label": _backend_label,
            "resolution_presets": {k: v["description"] for k, v in RESOLUTION_PRESETS.items()},
            "subject_types": {k: v for k, v in SUBJECT_LOOKS.items()},
            "emotions": {k: v for k, v in EXPRESSION_LOOKS.items()},
            "scene_settings": {k: v for k, v in SETTING_LOOKS.items()},
            "output_formats": ["jpg", "png", "webp"],
        }, indent=2))]

    if name == "generate_image":
        return await _generate(
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
        return await _generate(
            scene=arguments["description"],
            subject_type="patient",
            emotion=arguments.get("emotion", "hopeful"),
            scene_setting=arguments.get("scene_setting"),
            preset=arguments.get("preset", "blog"),
            output_format=arguments.get("output_format", "jpg"),
            asset_type="patient",
            descriptor="portrait",
        )

    if name == "generate_mentor_photo":
        return await _generate(
            scene=arguments["description"],
            subject_type="mentor",
            emotion=arguments.get("emotion", "supportive"),
            scene_setting=arguments.get("scene_setting"),
            preset=arguments.get("preset", "blog"),
            output_format=arguments.get("output_format", "jpg"),
            asset_type="mentor",
            descriptor="portrait",
        )

    if name == "generate_hero_image":
        return await _generate(
            scene=arguments["description"],
            subject_type=arguments.get("subject_type", "group"),
            emotion=arguments.get("emotion", "hopeful"),
            preset="hero",
            output_format=arguments.get("output_format", "jpg"),
            asset_type="hero",
            descriptor="landing",
        )

    if name == "generate_social_image":
        platform = arguments.get("platform", "instagram_feed")
        return await _generate(
            scene=arguments["description"],
            subject_type=arguments.get("subject_type"),
            emotion=arguments.get("emotion", "hopeful"),
            preset=PLATFORM_TO_PRESET.get(platform, "social_square"),
            output_format=arguments.get("output_format", "jpg"),
            asset_type="social",
            descriptor=platform.replace("_", "-"),
        )

    raise ValueError(f"Unknown tool: {name}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
