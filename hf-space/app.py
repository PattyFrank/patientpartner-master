"""
PatientPartner Healthcare Photo Generator — Hugging Face Space

Generates photorealistic healthcare photography using FLUX.1-dev + optional
LoRA fine-tune on ZeroGPU (free). Exposes a Gradio API that the NanoBanana
MCP server can call.

Deploy: https://huggingface.co/new-space → Gradio SDK → ZeroGPU hardware
"""

import os
import spaces
import gradio as gr
import torch
from diffusers import FluxPipeline

# ---------------------------------------------------------------------------
# Brand prompt enhancement (mirrors mcp-servers/image-generator/server.py)
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

SUBJECT_TEMPLATES = {
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

EMOTION_MODIFIERS = {
    "hopeful": "expressing genuine hope and optimism, slight natural smile, bright eyes, uplifting atmosphere",
    "supportive": "showing warmth and support, leaning in attentively, empathetic expression, connected posture",
    "reflective": "in a quiet thoughtful moment, calm and contemplative, peaceful expression, soft ambient light",
    "confident": "projecting quiet confidence, standing tall, assured expression, empowered body language",
    "grateful": "expressing sincere gratitude, warm genuine smile, relaxed and appreciative demeanor",
    "determined": "showing resolve and determination, focused gaze, purposeful posture, strong but approachable",
    "relieved": "expressing relief and comfort, relaxed shoulders, gentle exhale moment, tension releasing",
    "connected": "feeling of human connection, engaged with another person, shared understanding, mutual warmth",
}

SCENE_TEMPLATES = {
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

# Resolution presets: (width, height)
PRESETS = {
    "social_square (1080x1080)": (1024, 1024),
    "social_portrait (1080x1350)": (832, 1024),
    "social_story (1080x1920)": (576, 1024),
    "hero (1920x1080)": (1024, 576),
    "blog (1200x800)": (1024, 680),
}


def enhance_prompt(
    scene: str,
    subject_type: str = "none",
    emotion: str = "none",
    scene_setting: str = "none",
) -> str:
    """Build a brand-consistent, photorealistic prompt."""
    parts = [BRAND_STYLE_PREFIX]

    if scene_setting != "none" and scene_setting in SCENE_TEMPLATES:
        parts.append(SCENE_TEMPLATES[scene_setting])

    if subject_type != "none" and subject_type in SUBJECT_TEMPLATES:
        parts.append(SUBJECT_TEMPLATES[subject_type])

    parts.append(scene)

    if emotion != "none" and emotion in EMOTION_MODIFIERS:
        parts.append(EMOTION_MODIFIERS[emotion])

    parts.append(BRAND_STYLE_SUFFIX)

    # Add LoRA trigger word if a fine-tune is loaded
    trigger = os.getenv("LORA_TRIGGER_WORD", "")
    if trigger:
        parts.insert(0, f"{trigger} style photograph,")

    return ", ".join(parts)


# ---------------------------------------------------------------------------
# Model loading
# ---------------------------------------------------------------------------

HF_TOKEN = os.getenv("HF_TOKEN", None)
LORA_REPO = os.getenv("LORA_REPO", "")  # e.g. "patientpartner/healthcare-lora"
LORA_FILENAME = os.getenv("LORA_FILENAME", "pytorch_lora_weights.safetensors")

print("Loading FLUX.1-dev pipeline...")
pipe = FluxPipeline.from_pretrained(
    "black-forest-labs/FLUX.1-dev",
    torch_dtype=torch.bfloat16,
    token=HF_TOKEN,
)
pipe.to("cuda")

# Load LoRA if configured
if LORA_REPO:
    print(f"Loading LoRA weights from {LORA_REPO}...")
    pipe.load_lora_weights(LORA_REPO, weight_name=LORA_FILENAME)
    print("LoRA loaded.")
else:
    print("No LORA_REPO set — running base FLUX.1-dev (no fine-tune).")


# ---------------------------------------------------------------------------
# Generation function
# ---------------------------------------------------------------------------

@spaces.GPU(duration=120)
def generate(
    scene: str,
    subject_type: str,
    emotion: str,
    scene_setting: str,
    preset: str,
    guidance_scale: float,
    num_steps: int,
    seed: int,
):
    """Generate a PatientPartner healthcare photograph."""
    # Build prompt
    full_prompt = enhance_prompt(scene, subject_type, emotion, scene_setting)

    # Resolve dimensions
    width, height = PRESETS.get(preset, (1024, 680))

    # Seed
    generator = None
    if seed >= 0:
        generator = torch.Generator("cuda").manual_seed(seed)

    # Generate
    image = pipe(
        prompt=full_prompt,
        width=width,
        height=height,
        guidance_scale=guidance_scale,
        num_inference_steps=num_steps,
        generator=generator,
    ).images[0]

    return image, full_prompt


# ---------------------------------------------------------------------------
# Gradio UI
# ---------------------------------------------------------------------------

with gr.Blocks(title="PatientPartner Image Generator") as demo:
    gr.Markdown(
        "# PatientPartner Healthcare Photo Generator\n"
        "Generate photorealistic healthcare photography with brand-aware prompt enhancement.\n"
        "Powered by FLUX.1-dev on free ZeroGPU."
    )

    with gr.Row():
        with gr.Column(scale=1):
            scene_input = gr.Textbox(
                label="Scene Description",
                placeholder="A woman in her 40s discussing her treatment journey with a peer mentor over coffee",
                lines=3,
            )
            subject_type = gr.Dropdown(
                label="Subject Type",
                choices=["none"] + list(SUBJECT_TEMPLATES.keys()),
                value="patient",
            )
            emotion = gr.Dropdown(
                label="Emotion",
                choices=["none"] + list(EMOTION_MODIFIERS.keys()),
                value="hopeful",
            )
            scene_setting = gr.Dropdown(
                label="Scene Setting",
                choices=["none"] + list(SCENE_TEMPLATES.keys()),
                value="none",
            )
            preset = gr.Dropdown(
                label="Resolution Preset",
                choices=list(PRESETS.keys()),
                value="blog (1200x800)",
            )

            with gr.Accordion("Advanced", open=False):
                guidance = gr.Slider(
                    label="Guidance Scale",
                    minimum=1.0, maximum=10.0, value=3.5, step=0.5,
                )
                steps = gr.Slider(
                    label="Inference Steps",
                    minimum=10, maximum=50, value=28, step=1,
                )
                seed_input = gr.Number(
                    label="Seed (-1 for random)",
                    value=-1, precision=0,
                )

            generate_btn = gr.Button("Generate", variant="primary")

        with gr.Column(scale=1):
            output_image = gr.Image(label="Generated Image", type="pil")
            output_prompt = gr.Textbox(label="Enhanced Prompt Used", lines=4)

    generate_btn.click(
        fn=generate,
        inputs=[
            scene_input, subject_type, emotion, scene_setting,
            preset, guidance, steps, seed_input,
        ],
        outputs=[output_image, output_prompt],
    )

    # Examples
    gr.Examples(
        examples=[
            ["A woman in her 40s, warm natural smile, experienced mentor", "mentor", "supportive", "consultation", "blog (1200x800)", 3.5, 28, -1],
            ["A diverse group of patients sharing their healthcare journeys", "group", "connected", "support_group", "hero (1920x1080)", 3.5, 28, -1],
            ["A young man looking hopeful after receiving good news from his doctor", "patient", "hopeful", "hospital", "social_square (1080x1080)", 3.5, 28, -1],
            ["An older couple, one supporting the other through recovery", "caregiver", "grateful", "home", "blog (1200x800)", 3.5, 28, -1],
        ],
        inputs=[
            scene_input, subject_type, emotion, scene_setting,
            preset, guidance, steps, seed_input,
        ],
    )

demo.launch()
