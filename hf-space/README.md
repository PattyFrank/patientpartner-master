---
title: PatientPartner Healthcare Photo Generator
emoji: 🏥
colorFrom: blue
colorTo: green
sdk: gradio
sdk_version: 5.12.0
app_file: app.py
pinned: false
license: mit
suggested_hardware: zero-a10g
---

# PatientPartner Healthcare Photo Generator

Generates photorealistic healthcare photography using FLUX.1-dev on free ZeroGPU.

## Features

- Brand-aware prompt enhancement for PatientPartner
- Subject types: patient, mentor, caregiver, group, healthcare professional
- Emotion modifiers: hopeful, supportive, reflective, confident, grateful
- Resolution presets: social media, hero images, blog
- Optional LoRA fine-tune support

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `HF_TOKEN` | Yes | Hugging Face token (for gated FLUX model access) |
| `LORA_REPO` | No | HF repo with LoRA weights (e.g. `patientpartner/healthcare-lora`) |
| `LORA_FILENAME` | No | LoRA weights filename (default: `pytorch_lora_weights.safetensors`) |
| `LORA_TRIGGER_WORD` | No | Trigger word for the LoRA (e.g. `PTPTNR`) |

## API Usage

Call from the NanoBanana MCP or any Gradio client:

```python
from gradio_client import Client

client = Client("patientpartner/healthcare-photos", hf_token="hf_...")
result = client.predict(
    scene="A woman in her 40s, warm natural smile",
    subject_type="mentor",
    emotion="supportive",
    scene_setting="consultation",
    preset="blog (1200x800)",
    guidance_scale=3.5,
    num_steps=28,
    seed=-1,
    api_name="/generate",
)
image_path = result[0]  # local path to generated image
prompt_used = result[1]  # enhanced prompt
```
