# PatientPartner Custom Replicate Model — Implementation Plan

## Goal

Build and deploy a custom image generation model on Replicate, fine-tuned for
PatientPartner's healthcare photography needs. The model connects to the
existing NanoBanana MCP server for seamless generation from Claude Code.

---

## Architecture Overview

```
Claude Code
    │
    ▼
NanoBanana MCP (mcp-servers/image-generator/server.py)
    │
    ▼
Replicate API
    │
    ▼
patientpartner/healthcare-photos  ◄── Custom Cog model
    │
    ├── FLUX.1 Dev (base model)
    └── PatientPartner LoRA (healthcare photography style)
```

**Two-layer approach:**

1. **FLUX LoRA fine-tune** — Train a style LoRA on curated healthcare
   photography to get consistent, on-brand outputs
2. **Cog wrapper** — Package the fine-tuned model with PatientPartner
   prompt engineering, presets, and safety guardrails baked in

---

## Phase 1: Training Data Curation

### 1.1 Collect Reference Images (20-40 images)

Source high-quality healthcare photography that represents the PatientPartner
visual identity. These will train the style LoRA.

**Image categories needed:**

| Category | Count | Description |
|----------|-------|-------------|
| Patient portraits | 6-8 | Diverse patients, natural expressions, various ages/ethnicities |
| Mentor interactions | 6-8 | Two people in warm, supportive conversation |
| Healthcare settings | 4-6 | Modern, welcoming clinical environments |
| Support groups | 3-4 | Small groups in community/support settings |
| Home/recovery | 3-4 | Patients in comfortable home environments |
| Virtual meetings | 2-3 | Telehealth/video call settings |

**Image requirements:**
- 1024×1024 or higher resolution
- JPG, PNG, or WebP format
- Varied lighting, angles, and compositions
- Natural, documentary style — no stock photo poses
- Diverse representation (age, ethnicity, gender)

### 1.2 Caption Each Image

Write structured captions for every training image. Format:

```
A [trigger_word] style photograph of [subject description],
[setting/environment], [lighting], [mood/emotion], [composition details]
```

**Trigger word:** `PTPTNR` (unique, won't conflict with existing tokens)

**Example captions:**
```
A PTPTNR style photograph of a middle-aged woman and her peer mentor
having a warm conversation in a modern healthcare consultation room,
soft natural window light, hopeful and supportive mood, medium shot
with shallow depth of field

A PTPTNR style photograph of a diverse support group sitting in a
circle in a bright community room, natural overhead lighting mixed
with window light, connected and engaged expressions, wide shot
showing the full group dynamic
```

### 1.3 Prepare Training ZIP

```
training-data/
├── image_001.jpg
├── image_001.txt    # caption file (same name, .txt extension)
├── image_002.jpg
├── image_002.txt
└── ...
```

---

## Phase 2: LoRA Training on Replicate

### 2.1 Train via Replicate Fast Flux Trainer

```bash
# Upload training data and start training
curl -s -X POST "https://api.replicate.com/v1/models/replicate/fast-flux-trainer/versions/{version}/trainings" \
  -H "Authorization: Bearer $REPLICATE_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "destination": "patientpartner/healthcare-photos",
    "input": {
      "input_images": "https://your-storage.com/training-data.zip",
      "trigger_word": "PTPTNR",
      "lora_type": "style",
      "training_steps": 1000,
      "learning_rate": 0.0004,
      "resolution": "1024"
    }
  }'
```

**Training parameters:**
- **lora_type:** `style` (not subject — we want the healthcare photography aesthetic)
- **trigger_word:** `PTPTNR`
- **steps:** 1000 (default, proven sweet spot)
- **learning_rate:** 0.0004 (default)
- **Cost:** ~$1.50 per training run (2 min on 8x H100s)

### 2.2 Test the Fine-Tune

Run test predictions with the trained model:

```bash
curl -s -X POST "https://api.replicate.com/v1/models/patientpartner/healthcare-photos/predictions" \
  -H "Authorization: Bearer $REPLICATE_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "prompt": "A PTPTNR style photograph of a patient and mentor having a warm conversation in a modern consultation room, natural lighting, hopeful expression",
      "aspect_ratio": "3:2",
      "output_format": "jpg"
    }
  }'
```

**Validation checklist:**
- [ ] Trigger word activates the healthcare photography style
- [ ] People look photorealistic (no AI artifacts on faces/hands)
- [ ] Lighting matches documentary style
- [ ] Settings feel like real healthcare environments
- [ ] Diversity in outputs when not specified

---

## Phase 3: Cog Wrapper Model

Package the fine-tuned model with PatientPartner-specific logic as a Cog
model. This adds brand guardrails, preset prompts, and simplified inputs
directly into the Replicate model API.

### 3.1 Project Structure

```
replicate-model/
├── cog.yaml              # Environment and dependency config
├── predict.py            # Prediction interface with brand logic
├── brand_config.py       # Brand constants, presets, prompt templates
└── weights/              # LoRA weights (loaded at setup)
```

### 3.2 cog.yaml

```yaml
build:
  gpu: true
  python_version: "3.11"
  python_packages:
    - "torch>=2.1"
    - "diffusers>=0.28"
    - "transformers>=4.40"
    - "accelerate>=0.30"
    - "safetensors>=0.4"
    - "peft>=0.10"
    - "pillow>=10.0"
    - "sentencepiece>=0.2"

predict: "predict.py:Predictor"
```

### 3.3 predict.py (Prediction Interface)

```python
from cog import BasePredictor, Input, Path
from brand_config import enhance_prompt, PRESETS, SUBJECTS, EMOTIONS

class Predictor(BasePredictor):
    def setup(self):
        """Load FLUX.1 Dev + PatientPartner LoRA into memory."""
        # Load base model + LoRA weights
        # Cache on GPU for fast inference

    def predict(
        self,
        scene: str = Input(description="Scene description"),
        subject_type: str = Input(
            description="Subject type",
            choices=["patient", "mentor", "caregiver", "group",
                     "patient_and_mentor", "healthcare_professional"],
            default="patient",
        ),
        emotion: str = Input(
            description="Emotional tone",
            choices=["hopeful", "supportive", "reflective",
                     "confident", "grateful", "connected"],
            default="hopeful",
        ),
        preset: str = Input(
            description="Resolution preset",
            choices=["social_square", "social_portrait",
                     "social_story", "hero", "blog"],
            default="blog",
        ),
        output_format: str = Input(
            description="Output format",
            choices=["jpg", "png", "webp"],
            default="jpg",
        ),
        guidance_scale: float = Input(
            description="Prompt adherence strength",
            default=3.5, ge=1.0, le=10.0,
        ),
        seed: int = Input(
            description="Random seed for reproducibility",
            default=None,
        ),
    ) -> Path:
        """Generate a PatientPartner healthcare photograph."""
        # 1. Build enhanced prompt with brand context
        full_prompt = enhance_prompt(scene, subject_type, emotion)

        # 2. Resolve aspect ratio from preset
        aspect_ratio = PRESETS[preset]["aspect_ratio"]
        width, height = PRESETS[preset]["dimensions"]

        # 3. Run inference with FLUX + LoRA
        image = self.pipeline(
            prompt=full_prompt,
            width=width,
            height=height,
            guidance_scale=guidance_scale,
            num_inference_steps=28,
            generator=seed,
        ).images[0]

        # 4. Save and return
        output_path = f"/tmp/output.{output_format}"
        image.save(output_path)
        return Path(output_path)
```

### 3.4 brand_config.py

Extracted from the MCP server's prompt enhancement logic — same subject
templates, emotion modifiers, scene settings, and brand style prefix/suffix.
Single source of truth shared between the Cog model and MCP server.

---

## Phase 4: Deploy to Replicate

### 4.1 Create the Model on Replicate

```bash
# Create model (one-time)
curl -s -X POST "https://api.replicate.com/v1/models" \
  -H "Authorization: Bearer $REPLICATE_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "owner": "patientpartner",
    "name": "healthcare-photos",
    "visibility": "private",
    "hardware": "gpu-a40-large",
    "description": "Photorealistic healthcare photography for PatientPartner. Generates diverse, authentic patient and mentor imagery."
  }'
```

### 4.2 Push with Cog

```bash
cd replicate-model
cog login
cog push r8.im/patientpartner/healthcare-photos
```

### 4.3 Create a Deployment (Production)

```bash
# Create dedicated deployment for stable production use
curl -s -X POST "https://api.replicate.com/v1/deployments" \
  -H "Authorization: Bearer $REPLICATE_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "pp-image-gen",
    "model": "patientpartner/healthcare-photos",
    "hardware": "gpu-a40-large",
    "min_instances": 0,
    "max_instances": 2
  }'
```

---

## Phase 5: Connect to NanoBanana MCP

### 5.1 Update MCP Server

Update `mcp-servers/image-generator/server.py` to use the custom model:

```python
# Model priority:
# 1. PatientPartner custom model (fine-tuned)
# 2. Imagen 4 Ultra (fallback)
# 3. Nano Banana Pro (legacy fallback)

MODEL_ID = "patientpartner/healthcare-photos"
FALLBACK_MODEL_ID = "google/imagen-4-ultra"
LEGACY_FALLBACK_ID = "google/nano-banana-pro"
```

The MCP server already handles the Replicate async API pattern (create
prediction → poll → download). Only the model ID and input parameters
need updating.

### 5.2 Update .mcp.json

No changes needed — same server, same config. The model switch is internal.

---

## Phase 6: Validation & Iteration

### 6.1 Test Matrix

Generate and review images across all combinations:

| Subject | Emotion | Preset | Pass? |
|---------|---------|--------|-------|
| patient | hopeful | blog | |
| patient | reflective | hero | |
| mentor | supportive | blog | |
| mentor | confident | social_square | |
| patient_and_mentor | connected | hero | |
| group | hopeful | social_portrait | |
| caregiver | grateful | blog | |
| healthcare_professional | confident | social_square | |

### 6.2 Quality Criteria

- [ ] Faces are photorealistic (no uncanny valley)
- [ ] Hands are correct (5 fingers, natural positioning)
- [ ] Skin tones are natural and diverse
- [ ] Healthcare settings look authentic
- [ ] Lighting feels documentary/editorial
- [ ] No stock photo stiffness
- [ ] Brand tone is warm, trustworthy, human

### 6.3 Iterate

If quality is inconsistent:
- Add more training images in weak categories
- Adjust training steps (try 1200-1500)
- Refine captions for more precision
- Re-train (~$1.50 per attempt)

---

## Cost Summary

| Item | Cost | Frequency |
|------|------|-----------|
| LoRA training | ~$1.50 | Per training run |
| Test predictions | ~$0.03-0.05/image | During validation |
| Production predictions | ~$0.03-0.05/image | Per generation |
| Deployment (idle) | $0/hr (min_instances=0) | When not in use |
| Deployment (active) | ~$0.60-1.00/hr | While generating |

**Total to launch:** ~$5-10 (training + validation images)
**Per-image cost in production:** ~$0.03-0.05

---

## Timeline

| Phase | Duration | Dependency |
|-------|----------|------------|
| Phase 1: Data curation | 1-2 days | Need photography assets |
| Phase 2: LoRA training | 5 minutes | Training data ready |
| Phase 3: Cog wrapper | 2-3 hours | Training validated |
| Phase 4: Deploy | 30 minutes | Cog model built |
| Phase 5: MCP connection | 15 minutes | Model deployed |
| Phase 6: Validation | 1-2 hours | Everything connected |

---

## Files to Create

```
replicate-model/
├── cog.yaml
├── predict.py
└── brand_config.py

training-data/
├── README.md           # Guidelines for image collection
├── captions/           # Caption templates and examples
└── images/             # Training images (not committed)
```

## Files to Modify

```
mcp-servers/image-generator/server.py    # Update MODEL_ID + fallback chain
```
