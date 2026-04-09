# Image Generation Strategy — PatientPartner
**Research date:** 2026-03-05  
**Scope:** On-brand image generation integrated with the content-atomizer skill  
**Platform:** LinkedIn only (per brand rules)

---

## The Goal

Every piece of content produced by the content-atomizer skill should optionally trigger image generation that is:

1. Aligned with PatientPartner's visual brand (teal/navy palette, warm human photography, clean data graphics)
2. Platform-sized correctly (LinkedIn: 1200×628px post headers, 1080×1350px carousel slides)
3. Generated at the time content is written — no separate design step required
4. Consistently on-brand across campaigns, not random AI aesthetics

---

## Research Findings: Best Image Generation Stack for 2026

### Tier 1 — Primary Recommendation: Flux.2 Pro via FAL.ai

**Why Flux.2 Pro wins for PatientPartner:**

| Capability | Why it matters for PatientPartner |
|---|---|
| **Multi-reference synthesis (up to 4 images)** | Feed in existing brand photos + design examples → model generates new images matching that look |
| **HEX color precision** | Exact `#74CCD3`, `#314D69`, `#DDF7F9` color matching — no approximation |
| **4MP resolution output** | LinkedIn-quality assets at full resolution |
| **LoRA training** | Train a custom "PatientPartner LoRA" on brand photos → permanent style lock |
| **Sub-second generation on FAL infrastructure** | Fast enough for real-time content workflows |

**API:** [fal.ai/models/fal-ai/flux-pro/v1.1](https://fal.ai/models/fal-ai/flux-pro/v1.1)  
**Cost:** ~$0.04–0.08 per image (4MP)  
**MCP:** FAL.ai has an MCP server, or use Replicate which hosts Flux.2

### Tier 2 — Text-Heavy Assets: GPT-image-1 (OpenAI)

**Why GPT-image-1 is the second tool in the stack:**

| Capability | Why it matters for PatientPartner |
|---|---|
| **Best-in-class text rendering** | Stats like "68% adherence lift", pull quotes, data visualizations |
| **Multi-turn conversation** | Refine images in chat — "make the teal darker", "move the text right" |
| **Reference image input** | Upload brand samples for style direction |
| **Context-aware generation** | Understands brand language and generates imagery consistent with the prompt |

Use GPT-image-1 for: carousel slides with text overlays, stat graphics, pull quote cards.  
Use Flux.2 Pro for: human photography, lifestyle scenes, background/header images.

**API:** `gpt-image-1` via `api.openai.com/v1/images/generations`  
**Cost:** ~$0.04 per image (standard quality)  

### Tier 3 — Vector/Design Assets: Recraft V4 via FAL.ai

For: icons, geometric design elements, brand graphic flourishes, diagrams.

**API:** [fal.ai/models/recraft-ai/recraft-v3](https://fal.ai/models/recraft-ai/recraft-v3)  
**Cost:** ~$0.02 per image

### Ranked Comparison (LM Arena, December 2025)

| Rank | Model | Elo Score | Best For |
|---|---|---|---|
| #1 | GPT Image 1.5 (OpenAI) | 1,284 | Text rendering, multi-turn |
| #2 | Flux.2 Pro (Black Forest Labs) | ~1,260 | Photorealism, brand consistency, LoRA |
| #3 | Nano Banana Pro (Google) | ~1,240 | General quality |
| #4 | Recraft V4 | ~1,200 | Vector, design, brand graphics |
| #5 | Midjourney v7 | ~1,190 | Artistic (no API) |

**PatientPartner recommendation: Flux.2 Pro as primary + GPT-image-1 for text-heavy assets.**

---

## MCP Options — What to Add to Cursor

### Option A: Replicate MCP (Recommended — Broadest Model Access)

Replicate's official MCP server gives access to all models (Flux.2, Nano Banana Pro, etc.) via natural language in Cursor.

```json
{
  "mcpServers": {
    "replicate": {
      "command": "npx",
      "args": ["replicate-mcp"],
      "env": {
        "REPLICATE_API_TOKEN": "your_token_here"
      }
    }
  }
}
```

**Docs:** [replicate.com/docs/reference/mcp](https://replicate.com/docs/reference/mcp)  
**Install:** `npm install -g replicate-mcp`  
**Cost:** ~$0.02–0.08/image depending on model

**What you can do with this in Cursor:**
- "Generate a LinkedIn header image for this carousel using PatientPartner brand colors"
- "Create 5 carousel slide backgrounds in teal and navy"
- "Generate a warm human photography scene of a patient mentor meeting"

### Option B: FAL.ai MCP (Recommended for Flux.2 Speed)

FAL runs Flux.2 at sub-second speeds — dramatically faster than Replicate for high-volume generation.

```json
{
  "mcpServers": {
    "fal-image-gen": {
      "command": "npx",
      "args": ["fal-ai-mcp"],
      "env": {
        "FAL_KEY": "your_fal_api_key"
      }
    }
  }
}
```

**Docs:** [fal.ai/docs](https://fal.ai/docs)  
**Sign up:** [fal.ai](https://fal.ai) — free tier available  
**Cost:** ~$0.01–0.04/image (faster, cheaper than Replicate for Flux)

### Option C: Multi-Provider MCP (Fallback Architecture)

The `marc-shade/image-gen-mcp` server supports Replicate + Together + Cloudflare + HuggingFace with automatic fallback. Good for resilience.

**Best approach: Add both Replicate MCP + FAL.ai MCP** — use FAL for speed on Flux.2, Replicate as fallback and for video models.

---

## The LoRA Path: Locking PatientPartner's Visual DNA

The single highest-ROI investment for long-term brand consistency is training a **PatientPartner LoRA on Flux.2 Dev**. This creates a custom model that has internalized your brand's visual language.

### What a LoRA Does

A LoRA (Low-Rank Adaptation) fine-tunes Flux.2 on your brand images. After training, every generation automatically applies your brand's:
- Color treatment (your teal/navy palette)
- Photography style (warm, human, natural light)
- Composition aesthetic (approachable, diverse, healthcare-adjacent)
- Overall mood (professional but warm)

### Training Requirements

| Parameter | Requirement |
|---|---|
| Images needed | 20–40 high-quality brand photos |
| Image sources | Website screenshots, LinkedIn posts, existing brand photography |
| Training time | ~30–60 minutes via FAL.ai cloud training |
| Cost | ~$2–5 for training on FAL.ai |
| Re-use | Every future image generation costs the same as normal |

### Image Sources for PatientPartner LoRA

1. **patientpartner.com** — Screenshot hero images, lifestyle photography, UI screenshots
2. **PatientPartner LinkedIn page** — Existing social content posts
3. **Brand Guidelines PDF** — Photography examples from pages 18–21
4. **Existing campaign assets** — Any graphics already produced

### Training Workflow (via FAL.ai)

```bash
# Install FAL CLI
pip install fal-client

# Prepare: collect 20-40 images into a zip
zip patientpartner-brand-photos.zip brand-photos/*.jpg

# Upload dataset and start training
fal run fal-ai/flux-lora-fast-training \
  --data patientpartner-brand-photos.zip \
  --trigger-word "patientpartner style" \
  --steps 1000

# Output: a .safetensors LoRA file you add to all future prompts
```

Once trained, every prompt appended with "patientpartner style" generates on-brand imagery.

---

## Integration with Content Atomizer

### The Current Handoff

The content-atomizer already has a built-in handoff to `/creative`:

```
→ /creative    Generate platform visuals —
               carousel graphics, thumbnails,
               video assets (~15 min)
```

### The New Workflow

When content-atomizer produces a LinkedIn carousel or post, it should now also:

1. **Extract image briefs** from the content — one brief per carousel slide, one for the post header
2. **Build brand-consistent prompts** using the PatientPartner creative-kit.md
3. **Call the image generation API** (Flux.2 Pro via FAL/Replicate MCP)
4. **Save images** to `./campaigns/{slug}/social/linkedin/images/`
5. **Reference images in content files** so copy and visuals are delivered together

### Image Brief Format (per Carousel Slide)

```yaml
image_brief:
  slide: 2
  text_overlay: "68% higher adherence"
  background: "deep navy #314D69"
  mood: "data visualization, confident, clinical credibility"
  subject: "abstract patient data flow, human connection"
  avoid: "clinical sterility, stock photo, cartoon"
  dimensions: "1080x1350"
  model: "flux-2-pro"  # or "gpt-image-1" for text-heavy slides
```

### Prompt Template for PatientPartner Images

Every generated image should use this base prompt structure:

```
[SUBJECT DESCRIPTION], PatientPartner brand style, 
teal color palette (#74CCD3 primary, #314D69 navy secondary, #DDF7F9 light teal), 
warm natural lighting, professional yet approachable, 
diverse real patients, healthcare adjacent without clinical coldness, 
clean modern composition, soft shadows,
[PLATFORM SPEC: 1080x1350 portrait / 1200x628 landscape],
photorealistic, high resolution

Negative prompt: cartoon, clipart, generic stock photo, 
cold clinical hospital setting, overly saturated, 
fluorescent lighting, dark moody tone
```

---

## Implementation Roadmap

### Phase 1 — Foundation (1–2 hours)

**Step 1:** Get API keys
- [FAL.ai](https://fal.ai) — sign up, get API key (free tier included)
- [Replicate](https://replicate.com) — sign up, get API token (pay-per-use, ~$5 to start)
- (Optional) OpenAI API key for GPT-image-1 (if you have one already)

**Step 2:** Add Replicate MCP to Cursor settings
- Open Cursor Settings → MCP tab
- Add the Replicate MCP configuration (see Option A above)
- Test with: "Generate a test image using flux-schnell"

**Step 3:** Add keys to `.env` file
```
REPLICATE_API_TOKEN=r8_your_token
FAL_KEY=your_fal_key
OPENAI_API_KEY=sk_your_key (optional)
```

**Step 4:** Update `brand/stack.md` with connected status

### Phase 2 — Brand Kit (30 minutes)

Create `brand/creative-kit.md` using the PatientPartner-specific template at the bottom of this file. This file is read by every creative generation to ensure brand consistency.

### Phase 3 — LoRA Training (1–2 hours, one-time)

1. Collect 25–35 PatientPartner brand images (website + LinkedIn)
2. Upload to FAL.ai and train the LoRA
3. Add the LoRA path to `creative-kit.md`
4. All future images will auto-apply the PatientPartner aesthetic

### Phase 4 — Content-Atomizer Integration (30 minutes)

Update the content-atomizer skill to automatically generate image briefs alongside written content, so every LinkedIn carousel delivered includes both copy AND image prompts (or actual generated images if API is connected).

---

## Cost Estimate

| Volume | Flux.2 Pro (FAL.ai) | GPT-image-1 | Monthly Total |
|---|---|---|---|
| 10 posts/month | $0.08–0.40 | $0.40 | ~$1–2/month |
| 50 posts/month | $0.40–2.00 | $2.00 | ~$5–10/month |
| 200 posts/month | $1.60–8.00 | $8.00 | ~$20–40/month |

LoRA training (one-time): ~$3–5

**Verdict:** This is effectively free at PatientPartner's current content volume.

---

## Files to Create/Update

| File | Action | Purpose |
|---|---|---|
| `brand/creative-kit.md` | **CREATE** | PatientPartner visual identity for all image generation |
| `brand/stack.md` | **UPDATE** | Add FAL.ai + Replicate API status |
| `~/.cursor/mcp.json` | **UPDATE** | Add Replicate MCP server |
| `brand/skills-v2/creative/references/MODEL_REGISTRY.md` | **UPDATE** | Add Flux.2 Pro and GPT-image-1 payloads |
| `brand/skills-v2/creative/SKILL.md` | **NOTE** | Already supports Replicate — just needs keys connected |

---

## PatientPartner Creative Kit Template

See `brand/creative-kit.md` (created alongside this file).
