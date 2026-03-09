"""
PatientPartner Image Generator MCP Server

Generates photorealistic images of people for PatientPartner.com.

Supports two backends:
  1. HF Space (free) — FLUX.1-dev on ZeroGPU via Gradio API
  2. Replicate (paid) — NanoBanana2 / Imagen 4 via Replicate API

Backend selection:
  - Set HF_SPACE_ID to use the free HF Space backend (e.g. "patientpartner/healthcare-photos")
  - Set REPLICATE_API_TOKEN to use the Replicate backend
  - If both are set, HF Space is preferred (free first)

Usage:
    python server.py                    # stdio transport (default for Claude Code)
"""

import asyncio
import json
import logging
import os
import sys
import time
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

# Backend: HF Space (free) or Replicate (paid)
HF_SPACE_ID = os.getenv("HF_SPACE_ID", "")  # e.g. "patientpartner/healthcare-photos"
HF_TOKEN = os.getenv("HF_TOKEN", "")

REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN", "")
MODEL_ID = "google/nano-banana-2"
FALLBACK_MODEL_ID = "google/nano-banana-pro"
REPLICATE_BASE = "https://api.replicate.com/v1"

# Determine active backend
BACKEND = "hf_space" if HF_SPACE_ID else ("replicate" if REPLICATE_API_TOKEN else "prompt_only")

OUTPUT_DIR = Path(os.getenv(
    "IMAGE_OUTPUT_DIR",
    os.path.join(os.getcwd(), "creative-output", "generated-images"),
))

POLL_INTERVAL = 5        # seconds between status checks
MAX_POLL_ATTEMPTS = 60   # 5 minutes max wait

logger = logging.getLogger("image-generator-mcp")
logging.basicConfig(level=logging.INFO, stream=sys.stderr)

# ---------------------------------------------------------------------------
# Resolution presets
# ---------------------------------------------------------------------------

RESOLUTION_PRESETS: dict[str, dict[str, str]] = {
    "social_square": {
        "aspect_ratio": "1:1",
        "description": "Social media square (1080x1080) — Instagram feed, LinkedIn, Facebook",
    },
    "social_portrait": {
        "aspect_ratio": "4:5",
        "description": "Social media portrait (1080x1350) — Instagram feed optimal, Facebook ads",
    },
    "social_story": {
        "aspect_ratio": "9:16",
        "description": "Social stories/reels (1080x1920) — Instagram Stories, TikTok, Reels",
    },
    "hero": {
        "aspect_ratio": "16:9",
        "description": "Website hero image (1920x1080) — Landing pages, hero sections, OG images",
    },
    "blog": {
        "aspect_ratio": "3:2",
        "description": "Blog image (1200x800) — Blog posts, articles, editorial content",
    },
    "blog_wide": {
        "aspect_ratio": "16:9",
        "description": "Wide blog image (1200x675) — Blog headers, newsletter banners",
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

    # Scene setting
    if scene_setting and scene_setting in SCENE_TEMPLATES:
        parts.append(SCENE_TEMPLATES[scene_setting])

    # Subject type
    if subject_type and subject_type in SUBJECT_TEMPLATES:
        parts.append(SUBJECT_TEMPLATES[subject_type])

    # Core scene description from user
    parts.append(scene)

    # Emotion
    if emotion and emotion in EMOTION_MODIFIERS:
        parts.append(EMOTION_MODIFIERS[emotion])

    # Additional user details
    if additional_details:
        parts.append(additional_details)

    # Brand suffix
    parts.append(BRAND_STYLE_SUFFIX)

    return ", ".join(parts)


# ---------------------------------------------------------------------------
# Replicate API client
# ---------------------------------------------------------------------------

async def _replicate_headers() -> dict[str, str]:
    if not REPLICATE_API_TOKEN:
        raise ValueError(
            "REPLICATE_API_TOKEN is not set. "
            "Add it to your .env file or export it as an environment variable. "
            "Get a token at https://replicate.com/account/api-tokens"
        )
    return {
        "Authorization": f"Bearer {REPLICATE_API_TOKEN}",
        "Content-Type": "application/json",
    }


async def create_prediction(
    prompt: str,
    aspect_ratio: str = "1:1",
    output_format: str = "jpg",
    resolution: str = "2K",
    image_input: list[str] | None = None,
) -> dict[str, Any]:
    """Create a Replicate prediction for image generation."""
    headers = await _replicate_headers()

    payload: dict[str, Any] = {
        "input": {
            "prompt": prompt,
            "aspect_ratio": aspect_ratio,
            "output_format": output_format,
            "resolution": resolution,
        }
    }

    if image_input:
        payload["input"]["image_input"] = image_input

    # Try NanoBanana2 first, fall back to Nano Banana Pro
    model_id = MODEL_ID
    async with httpx.AsyncClient(timeout=30) as client:
        url = f"{REPLICATE_BASE}/models/{model_id}/predictions"
        resp = await client.post(url, headers=headers, json=payload)

        if resp.status_code == 404:
            logger.warning(
                f"Model {model_id} not found, falling back to {FALLBACK_MODEL_ID}"
            )
            model_id = FALLBACK_MODEL_ID
            url = f"{REPLICATE_BASE}/models/{model_id}/predictions"
            resp = await client.post(url, headers=headers, json=payload)

        if resp.status_code not in (200, 201):
            raise RuntimeError(
                f"Replicate API error {resp.status_code}: {resp.text}"
            )

        result = resp.json()
        result["_model_used"] = model_id
        return result


async def poll_prediction(prediction_id: str) -> dict[str, Any]:
    """Poll a Replicate prediction until it completes or fails."""
    headers = await _replicate_headers()
    url = f"{REPLICATE_BASE}/predictions/{prediction_id}"

    async with httpx.AsyncClient(timeout=30) as client:
        for attempt in range(MAX_POLL_ATTEMPTS):
            resp = await client.get(url, headers=headers)
            if resp.status_code != 200:
                raise RuntimeError(
                    f"Replicate poll error {resp.status_code}: {resp.text}"
                )

            data = resp.json()
            status = data.get("status")

            if status == "succeeded":
                return data
            elif status == "failed":
                error = data.get("error", "Unknown error")
                raise RuntimeError(f"Image generation failed: {error}")
            elif status == "canceled":
                raise RuntimeError("Image generation was canceled")

            await asyncio.sleep(POLL_INTERVAL)

    raise RuntimeError(
        f"Image generation timed out after {MAX_POLL_ATTEMPTS * POLL_INTERVAL}s"
    )


async def download_image(image_url: str, filename: str) -> str:
    """Download a generated image and save it locally."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    filepath = OUTPUT_DIR / filename

    async with httpx.AsyncClient(timeout=60, follow_redirects=True) as client:
        resp = await client.get(image_url)
        if resp.status_code != 200:
            raise RuntimeError(f"Failed to download image: HTTP {resp.status_code}")
        filepath.write_bytes(resp.content)

    return str(filepath)


def _generate_filename(
    asset_type: str, descriptor: str, aspect_ratio: str, fmt: str
) -> str:
    """Generate a filename following PatientPartner naming conventions."""
    ratio_str = aspect_ratio.replace(":", "x")
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    return f"{asset_type}-{descriptor}-{ratio_str}-{timestamp}.{fmt}"


# ---------------------------------------------------------------------------
# HF Space backend (free)
# ---------------------------------------------------------------------------

# Preset name mapping: MCP preset → HF Space dropdown value
HF_PRESET_MAP = {
    "social_square": "social_square (1080x1080)",
    "social_portrait": "social_portrait (1080x1350)",
    "social_story": "social_story (1080x1920)",
    "hero": "hero (1920x1080)",
    "blog": "blog (1200x800)",
    "blog_wide": "hero (1920x1080)",  # closest match
}


async def generate_via_hf_space(
    scene: str,
    subject_type: str | None = None,
    emotion: str | None = None,
    scene_setting: str | None = None,
    preset: str | None = None,
    guidance_scale: float = 3.5,
    num_steps: int = 28,
    seed: int = -1,
) -> dict[str, Any]:
    """Generate an image via the free HF Space Gradio API."""
    hf_preset = HF_PRESET_MAP.get(preset or "blog", "blog (1200x800)")

    # Build the Gradio API request
    # The HF Space exposes /generate with positional args matching the Gradio UI
    api_url = f"https://{HF_SPACE_ID.replace('/', '-')}.hf.space/api/predict"

    payload = {
        "fn_index": 0,
        "data": [
            scene,
            subject_type or "none",
            emotion or "none",
            scene_setting or "none",
            hf_preset,
            guidance_scale,
            num_steps,
            seed,
        ],
    }

    headers: dict[str, str] = {"Content-Type": "application/json"}
    if HF_TOKEN:
        headers["Authorization"] = f"Bearer {HF_TOKEN}"

    async with httpx.AsyncClient(timeout=300) as client:
        # Gradio SSE/queue pattern: join queue, then poll
        # Try the simple /call endpoint first (Gradio 4+)
        call_url = f"https://{HF_SPACE_ID.replace('/', '-')}.hf.space/call/generate"
        resp = await client.post(call_url, headers=headers, json={
            "data": payload["data"],
        })

        if resp.status_code != 200:
            raise RuntimeError(
                f"HF Space API error {resp.status_code}: {resp.text}"
            )

        event_id = resp.json().get("event_id")
        if not event_id:
            raise RuntimeError("HF Space did not return an event_id")

        # Poll for result
        result_url = f"https://{HF_SPACE_ID.replace('/', '-')}.hf.space/call/generate/{event_id}"
        for _ in range(120):  # up to 10 minutes
            await asyncio.sleep(5)
            result_resp = await client.get(result_url, headers=headers)
            if result_resp.status_code == 200:
                text = result_resp.text
                # Parse SSE-style response
                for line in text.strip().split("\n"):
                    if line.startswith("data:"):
                        data = json.loads(line[5:].strip())
                        return {
                            "image_url": data[0].get("url", "") if isinstance(data[0], dict) else data[0],
                            "prompt_used": data[1] if len(data) > 1 else "",
                            "model_used": f"hf-space:{HF_SPACE_ID}",
                            "backend": "hf_space",
                        }
                # If "complete" event found without data
                if "event: complete" in text:
                    raise RuntimeError("HF Space returned complete but no image data")

        raise RuntimeError("HF Space generation timed out")


# ---------------------------------------------------------------------------
# MCP Server
# ---------------------------------------------------------------------------

server = Server("patientpartner-image-generator")


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available image generation tools."""
    return [
        Tool(
            name="generate_image",
            description=(
                "Generate a photorealistic image of people for PatientPartner.com. "
                "Automatically enhances prompts with healthcare brand context, "
                "documentary-style photography direction, and diversity guidelines. "
                "Uses NanoBanana2 (Google Gemini 3.1 Flash Image) via Replicate API."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "scene": {
                        "type": "string",
                        "description": (
                            "Description of the scene to generate. Be specific about "
                            "what is happening, who is in the scene, and the setting. "
                            "Example: 'A woman in her 50s discussing her treatment journey "
                            "with a younger peer mentor over coffee'"
                        ),
                    },
                    "subject_type": {
                        "type": "string",
                        "enum": list(SUBJECT_TEMPLATES.keys()),
                        "description": (
                            "Type of subject in the image. Automatically adds "
                            "appropriate appearance and context details."
                        ),
                    },
                    "emotion": {
                        "type": "string",
                        "enum": list(EMOTION_MODIFIERS.keys()),
                        "description": "Emotional tone of the image.",
                    },
                    "scene_setting": {
                        "type": "string",
                        "enum": list(SCENE_TEMPLATES.keys()),
                        "description": "Pre-defined scene setting/environment.",
                    },
                    "preset": {
                        "type": "string",
                        "enum": list(RESOLUTION_PRESETS.keys()),
                        "description": (
                            "Resolution preset. Overrides aspect_ratio if set. "
                            "Options: social_square (1080x1080), social_portrait (1080x1350), "
                            "social_story (1080x1920), hero (1920x1080), blog (1200x800), "
                            "blog_wide (1200x675)."
                        ),
                    },
                    "aspect_ratio": {
                        "type": "string",
                        "enum": [
                            "1:1", "16:9", "9:16", "4:3", "3:4",
                            "3:2", "2:3", "4:5", "5:4", "21:9",
                        ],
                        "description": (
                            "Custom aspect ratio. Ignored if 'preset' is provided."
                        ),
                    },
                    "output_format": {
                        "type": "string",
                        "enum": ["jpg", "png", "webp"],
                        "default": "jpg",
                        "description": "Output image format.",
                    },
                    "additional_details": {
                        "type": "string",
                        "description": (
                            "Any additional details to include in the prompt. "
                            "Use for specific clothing, props, background elements, etc."
                        ),
                    },
                    "reference_images": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": (
                            "URLs of reference images for style transfer or editing. "
                            "Supports up to 14 images."
                        ),
                    },
                    "save_locally": {
                        "type": "boolean",
                        "default": True,
                        "description": "Whether to download and save the image locally.",
                    },
                },
                "required": ["scene"],
            },
        ),
        Tool(
            name="generate_patient_photo",
            description=(
                "Quick preset: Generate a photorealistic patient image for PatientPartner. "
                "Simplified interface — just describe the patient and their situation."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "description": {
                        "type": "string",
                        "description": (
                            "Describe the patient. Age, gender, what they are doing or feeling. "
                            "Example: 'A middle-aged man looking hopeful after a consultation'"
                        ),
                    },
                    "emotion": {
                        "type": "string",
                        "enum": list(EMOTION_MODIFIERS.keys()),
                        "default": "hopeful",
                        "description": "Emotional tone.",
                    },
                    "preset": {
                        "type": "string",
                        "enum": list(RESOLUTION_PRESETS.keys()),
                        "default": "blog",
                        "description": "Resolution preset.",
                    },
                    "output_format": {
                        "type": "string",
                        "enum": ["jpg", "png", "webp"],
                        "default": "jpg",
                    },
                },
                "required": ["description"],
            },
        ),
        Tool(
            name="generate_mentor_photo",
            description=(
                "Quick preset: Generate a photorealistic mentor/peer supporter image. "
                "Optimized for the PatientPartner peer-to-peer mentorship context."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "description": {
                        "type": "string",
                        "description": (
                            "Describe the mentor and their interaction. "
                            "Example: 'A warm, experienced woman in her 60s sharing her recovery story'"
                        ),
                    },
                    "emotion": {
                        "type": "string",
                        "enum": list(EMOTION_MODIFIERS.keys()),
                        "default": "supportive",
                        "description": "Emotional tone.",
                    },
                    "preset": {
                        "type": "string",
                        "enum": list(RESOLUTION_PRESETS.keys()),
                        "default": "blog",
                        "description": "Resolution preset.",
                    },
                    "output_format": {
                        "type": "string",
                        "enum": ["jpg", "png", "webp"],
                        "default": "jpg",
                    },
                },
                "required": ["description"],
            },
        ),
        Tool(
            name="generate_hero_image",
            description=(
                "Quick preset: Generate a website hero image (1920x1080, 16:9). "
                "Optimized for PatientPartner landing pages and hero sections."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "description": {
                        "type": "string",
                        "description": (
                            "Describe the hero scene. "
                            "Example: 'A diverse group of patients and mentors in a bright, "
                            "modern healthcare facility, conveying community and support'"
                        ),
                    },
                    "subject_type": {
                        "type": "string",
                        "enum": list(SUBJECT_TEMPLATES.keys()),
                        "description": "Primary subject type.",
                    },
                    "emotion": {
                        "type": "string",
                        "enum": list(EMOTION_MODIFIERS.keys()),
                        "default": "hopeful",
                        "description": "Emotional tone.",
                    },
                    "output_format": {
                        "type": "string",
                        "enum": ["jpg", "png", "webp"],
                        "default": "jpg",
                    },
                },
                "required": ["description"],
            },
        ),
        Tool(
            name="generate_social_image",
            description=(
                "Quick preset: Generate a social media image. "
                "Choose from square (1:1), portrait (4:5), or story (9:16) formats."
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
                        "description": "Target social media platform.",
                    },
                    "subject_type": {
                        "type": "string",
                        "enum": list(SUBJECT_TEMPLATES.keys()),
                        "description": "Primary subject type.",
                    },
                    "emotion": {
                        "type": "string",
                        "enum": list(EMOTION_MODIFIERS.keys()),
                        "default": "hopeful",
                        "description": "Emotional tone.",
                    },
                    "output_format": {
                        "type": "string",
                        "enum": ["jpg", "png", "webp"],
                        "default": "jpg",
                    },
                },
                "required": ["description"],
            },
        ),
        Tool(
            name="list_presets",
            description=(
                "List all available resolution presets, subject types, emotions, "
                "and scene settings for the image generator."
            ),
            inputSchema={
                "type": "object",
                "properties": {},
            },
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
    """Core generation logic shared by all tools."""

    # Resolve aspect ratio
    if preset and preset in RESOLUTION_PRESETS:
        ar = RESOLUTION_PRESETS[preset]["aspect_ratio"]
    elif aspect_ratio:
        ar = aspect_ratio
    else:
        ar = "3:2"  # default to blog size

    # Build enhanced prompt
    full_prompt = enhance_prompt(
        scene=scene,
        subject_type=subject_type,
        emotion=emotion,
        scene_setting=scene_setting,
        additional_details=additional_details,
    )

    logger.info(f"Backend: {BACKEND} | Generating image: {ar} {output_format}")
    logger.info(f"Enhanced prompt: {full_prompt[:200]}...")

    # ----- Backend: Prompt-only mode -----
    if BACKEND == "prompt_only":
        return [
            TextContent(
                type="text",
                text=json.dumps({
                    "status": "prompt_only",
                    "message": (
                        "No HF_SPACE_ID or REPLICATE_API_TOKEN set. "
                        "Running in prompt-only mode. Set either in .env to enable live generation."
                    ),
                    "prompt": full_prompt,
                    "model": MODEL_ID,
                    "settings": {
                        "aspect_ratio": ar,
                        "output_format": output_format,
                        "resolution": "2K",
                    },
                    "api_payload": {
                        "input": {
                            "prompt": full_prompt,
                            "aspect_ratio": ar,
                            "output_format": output_format,
                            "resolution": "2K",
                        }
                    },
                }, indent=2),
            )
        ]

    # ----- Backend: HF Space (free) -----
    if BACKEND == "hf_space":
        logger.info(f"Using HF Space: {HF_SPACE_ID}")
        hf_result = await generate_via_hf_space(
            scene=scene,
            subject_type=subject_type,
            emotion=emotion,
            scene_setting=scene_setting,
            preset=preset or "blog",
        )

        image_url = hf_result["image_url"]
        response: dict[str, Any] = {
            "status": "success",
            "backend": "hf_space (free)",
            "image_url": image_url,
            "model_used": hf_result.get("model_used", f"hf-space:{HF_SPACE_ID}"),
            "settings": {
                "aspect_ratio": ar,
                "output_format": output_format,
                "preset": preset,
            },
            "prompt_used": hf_result.get("prompt_used", full_prompt),
        }

        if save_locally and image_url:
            filename = _generate_filename(asset_type, descriptor, ar, output_format)
            try:
                local_path = await download_image(image_url, filename)
                response["local_path"] = local_path
                response["filename"] = filename
                logger.info(f"Image saved: {local_path}")
            except Exception as e:
                response["download_error"] = str(e)
                logger.warning(f"Failed to save locally: {e}")

        return [
            TextContent(type="text", text=json.dumps(response, indent=2))
        ]

    # ----- Backend: Replicate (paid) -----
    prediction = await create_prediction(
        prompt=full_prompt,
        aspect_ratio=ar,
        output_format=output_format,
        resolution="2K",
        image_input=reference_images,
    )

    prediction_id = prediction["id"]
    model_used = prediction.get("_model_used", MODEL_ID)
    logger.info(f"Prediction created: {prediction_id} (model: {model_used})")

    # Poll for completion
    result = await poll_prediction(prediction_id)
    output = result.get("output")

    if not output:
        return [
            TextContent(
                type="text",
                text=json.dumps({
                    "status": "error",
                    "message": "Generation succeeded but no output was returned.",
                    "prediction_id": prediction_id,
                }, indent=2),
            )
        ]

    # Handle output (can be a string URL or list of URLs)
    image_url = output if isinstance(output, str) else output[0]

    response = {
        "status": "success",
        "backend": "replicate (paid)",
        "image_url": image_url,
        "model_used": model_used,
        "prediction_id": prediction_id,
        "settings": {
            "aspect_ratio": ar,
            "output_format": output_format,
            "resolution": "2K",
            "preset": preset,
        },
        "prompt_used": full_prompt,
    }

    # Download locally
    if save_locally:
        filename = _generate_filename(asset_type, descriptor, ar, output_format)
        try:
            local_path = await download_image(image_url, filename)
            response["local_path"] = local_path
            response["filename"] = filename
            logger.info(f"Image saved: {local_path}")
        except Exception as e:
            response["download_error"] = str(e)
            logger.warning(f"Failed to save locally: {e}")

    return [
        TextContent(
            type="text",
            text=json.dumps(response, indent=2),
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Handle tool calls."""

    if name == "list_presets":
        return [
            TextContent(
                type="text",
                text=json.dumps({
                    "resolution_presets": {
                        k: v["description"] for k, v in RESOLUTION_PRESETS.items()
                    },
                    "subject_types": list(SUBJECT_TEMPLATES.keys()),
                    "emotions": list(EMOTION_MODIFIERS.keys()),
                    "scene_settings": list(SCENE_TEMPLATES.keys()),
                    "output_formats": ["jpg", "png", "webp"],
                    "aspect_ratios": [
                        "1:1", "16:9", "9:16", "4:3", "3:4",
                        "3:2", "2:3", "4:5", "5:4", "21:9",
                    ],
                }, indent=2),
            )
        ]

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
            asset_type="photo",
            descriptor="custom",
        )

    if name == "generate_patient_photo":
        return await _do_generate(
            scene=arguments["description"],
            subject_type="patient",
            emotion=arguments.get("emotion", "hopeful"),
            preset=arguments.get("preset", "blog"),
            output_format=arguments.get("output_format", "jpg"),
            asset_type="patient",
            descriptor="portrait",
        )

    if name == "generate_mentor_photo":
        return await _do_generate(
            scene=arguments["description"],
            subject_type="mentor",
            emotion=arguments.get("emotion", "supportive"),
            preset=arguments.get("preset", "blog"),
            output_format=arguments.get("output_format", "jpg"),
            asset_type="mentor",
            descriptor="portrait",
        )

    if name == "generate_hero_image":
        return await _do_generate(
            scene=arguments["description"],
            subject_type=arguments.get("subject_type"),
            emotion=arguments.get("emotion", "hopeful"),
            preset="hero",
            output_format=arguments.get("output_format", "jpg"),
            asset_type="hero",
            descriptor="landing",
        )

    if name == "generate_social_image":
        platform = arguments.get("platform", "instagram_feed")
        preset = PLATFORM_PRESETS.get(platform, "social_square")
        return await _do_generate(
            scene=arguments["description"],
            subject_type=arguments.get("subject_type"),
            emotion=arguments.get("emotion", "hopeful"),
            preset=preset,
            output_format=arguments.get("output_format", "jpg"),
            asset_type="social",
            descriptor=platform.replace("_", "-"),
        )

    raise ValueError(f"Unknown tool: {name}")


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

async def main():
    """Run the MCP server with stdio transport."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


if __name__ == "__main__":
    asyncio.run(main())
