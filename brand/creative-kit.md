# PatientPartner — Creative Kit

> Read by all image generation skills and the content-atomizer.
> Source of truth for visual brand identity across all AI-generated assets.
> Last updated: 2026-03-05

---

## Brand Colors

| Name | Hex | Usage |
|---|---|---|
| Primary Teal | `#74CCD3` | CTAs, design elements, accent headers |
| Dark Navy | `#314D69` | Text, dark backgrounds, primary CTA buttons |
| Light Teal | `#DDF7F9` | Backgrounds, slide fills, section blocks |
| Extra Teal | `#188F8B` | Design elements, icon accents |
| Extra Teal Dark | `#16837F` | Accessible dark backgrounds |
| Icon Teal | `#59B6BE` | Illustrations, outline icons |

**Primary palette for image generation:** Dark navy backgrounds (`#314D69`) with teal accents (`#74CCD3`). Light sections use `#DDF7F9` as background.

---

## Typography Direction

| Level | Style | Notes |
|---|---|---|
| Headlines | Utopia Std (serif), bold | Warm, premium serif. Use for pull quotes and slide headlines. |
| Body | HK Grotesk (sans-serif), regular | Clean and modern. All body text. |
| Data/Stats | HK Grotesk, bold | Large numerics (68%, 90%, 29%). High contrast. |
| CTAs | HK Grotesk, bold | Teal or white on dark background. |

**For AI image text rendering:** Specify bold serif for headlines, clean sans-serif for data. Always high contrast (white on navy, or navy on light teal).

---

## Visual Style

**Photography preference:**
- Real patients and real people — not models or stock photo actors
- Warm, natural lighting (not studio flash)
- Approachable and humanizing — healthcare adjacent without clinical coldness
- Diverse representation across age, race, background
- Settings: home/community environments, NOT hospitals or clinical settings
- Two-person interactions preferred (mentor + patient dynamic)
- Emotion: hope, relief, connection, empowerment

**Illustration style:**
- Flat vector with subtle gradients and soft shadows
- Outline icons: 3px stroke, colored `#59B6BE`
- Sourced from undraw.co pattern (set color picker to `#59B6BE`)
- No clip art, no cartoon characters

**Data visualizations:**
- Clean, minimal, high-contrast
- Navy background with teal chart elements
- White text for numbers and labels
- Show the stat large — 68%, 90%, 29%, 133.5 days

**Overall mood:** 
Confident, warm, evidence-based. Professional but never cold. The visual equivalent of "a trusted colleague who's also a warm human being."

---

## What to Avoid

- Generic stock photo aesthetics (posed corporate handshakes, blue-sky business)
- Clinical hospital settings (sterile, white, cold)
- Dark or gothic moods
- Neon or fluorescent colors
- Cartoon or illustrated humans (use photography style)
- Logos of pharmaceutical brands on anything visual
- Patient in distress or suffering imagery — always forward-looking
- Overly saturated or HDR processing

---

## Logo

- **Path:** `brand/logos/` (request SVG/PNG exports from Figma)
- **Horizontal:** Primary use — most contexts
- **Vertical:** When horizontal space is constrained
- **Stamp (icon only):** Avatar, small format, favicon
- **On light:** Black version
- **On dark:** White version
- **On brand teal:** Contrasting brand color version
- **Clear space:** Minimum 100% logo height on all sides

---

## Platform Specs (LinkedIn Only)

| Format | Dimensions | Notes |
|---|---|---|
| Post header / link preview | 1200×628px (16:9) | Primary LinkedIn post image |
| Carousel slides | 1080×1350px (4:5 portrait) | Best for dwell time |
| Square post | 1080×1080px (1:1) | Single stat graphics |
| Profile / company banner | 1584×396px | Wide landscape |

**All images should work at small preview size.** Text must be readable at 200px width.

---

## Image Generation Prompt Base

Use this template for every AI-generated image. Fill in `[SUBJECT]` and `[COMPOSITION NOTES]`.

```
[SUBJECT], PatientPartner brand aesthetic, 
teal and navy color palette, primary teal #74CCD3, dark navy #314D69,
warm natural light, approachable professional mood,
diverse real people, healthcare-adjacent setting without clinical coldness,
clean modern composition, subtle soft shadows,
[COMPOSITION NOTES],
photorealistic high resolution

Negative prompt: cartoon, clipart, generic stock photo, 
cold sterile hospital, fluorescent lighting, dark moody,
overly saturated, HDR, posed corporate handshake
```

### Example Prompts by Use Case

**Carousel slide background (data/stats):**
```
Abstract fluid data visualization with flowing connection lines,
PatientPartner brand aesthetic, dark navy #314D69 background,
teal accent lines #74CCD3 and #188F8B,
clean modern minimal, leaves space for text overlay center,
subtle geometric particle network suggesting patient-to-patient connection,
no text, no faces, 1080x1350 portrait
```

**Human connection / lifestyle:**
```
Two people in warm conversation, one older patient one younger mentor,
outdoor or home setting, warm golden hour natural light,
genuine emotion, hope and trust visible,
PatientPartner brand aesthetic, teal accent clothing details,
diverse representation, NOT clinical, NOT hospital,
photorealistic, 1080x1350 portrait
```

**Stat graphic header:**
```
Bold typographic layout showing "68%" in large white serif font,
dark navy background #314D69,
subtle teal gradient accent #74CCD3,
clean minimal design with thin decorative lines,
professional medical data aesthetic,
1200x628 landscape
```

---

## Model Selection for PatientPartner

| Asset Type | Recommended Model | Why |
|---|---|---|
| Human photography / lifestyle | **Flux.2 Pro** (via FAL.ai or Replicate) | Best photorealism + multi-reference brand lock |
| Text-heavy slides / data graphics | **GPT-image-1** (OpenAI) | Best text rendering, HEX support |
| Vector / icons / diagrams | **Recraft V4** (via FAL.ai) | Best vector quality |
| Background / abstract textures | **Flux.2 Pro** | Consistent style |

---

## LoRA Status

| LoRA | Status | Path | Trigger Word |
|---|---|---|---|
| PatientPartner Brand Style | ✗ not yet trained | — | `patientpartner style` |

**To train:** Collect 25–35 brand images → upload to FAL.ai → see `brand/image-gen-strategy.md`

Once trained, add the trigger word `patientpartner style` to every image prompt for automatic brand alignment.

---

## Competitor Visual References

| Competitor | Learn | Avoid |
|---|---|---|
| HealthUnlocked | Community warmth, peer photography | Generic web forum look |
| Inspire | Real patient stories aesthetic | Too text-heavy, dated UI |
| Cerner / Epic (enterprise) | Clean data design | Corporate coldness |

PatientPartner differentiator: **Human warmth + clinical credibility in the same frame.**

---

## Connected APIs

| API | Status | Key Location |
|---|---|---|
| FAL.ai (Flux.2 Pro) | ✗ not connected | `.env` → `FAL_KEY=` |
| Replicate (all models) | ✗ not connected | `.env` → `REPLICATE_API_TOKEN=` |
| OpenAI (GPT-image-1) | ✗ not connected | `.env` → `OPENAI_API_KEY=` |

**Setup guide:** See `brand/image-gen-strategy.md → Implementation Roadmap`
