---
name: ziplyne-magic-create
description: >
  AI-powered image pipeline using Google Gemini to generate, enhance, upscale, and optimize
  website images — then compress to WebP/AVIF, upload to Cloudinary, and replace references
  in code. Handles hero images, cards, OG images, favicons, and full site image overhauls.
  Use whenever the user mentions: website images, image optimization, hero images, OG images,
  favicons, image upscaling, Cloudinary upload, placeholder replacement, AI-generated images,
  WebP/AVIF conversion, or "ZipLyne-Magic-Create". Also trigger for "make my site images
  better", "generate images for my page", "create a favicon", or "make OG images".
---

# ZipLyne-Magic-Create

An AI-powered image pipeline that analyzes your website's images, generates or enhances them
using Google Gemini, optimizes them for web performance, uploads to Cloudinary, and wires
everything back into your codebase.

## Required Environment Variables

Before running ANY operation, verify these are set. **Always ask the user for these if missing.**

```
GEMINI_API_KEY=         # Google AI Studio API key for Gemini image generation
CLOUDINARY_CLOUD_NAME=  # Cloudinary cloud name
CLOUDINARY_API_KEY=     # Cloudinary API key
CLOUDINARY_API_SECRET=  # Cloudinary API secret
```

If any are missing, stop and ask the user to provide them. Do not proceed without credentials.

---

## Core Philosophy

**Always ask questions before acting.** This skill deals with brand identity and visual assets —
getting them wrong is costly. Before generating or modifying any image, confirm with the user:

1. What is the business/brand? What industry?
2. What is the visual style? (modern, minimal, corporate, playful, luxury, etc.)
3. Are there brand colors, fonts, or guidelines to follow?
4. Should images be photorealistic, illustrated, or mixed?
5. Does the client have a logo? Where is it? Should it appear in any images?
6. What pages need images? What are they for?

---

## Workflow Overview

The skill operates in several modes. Ask the user which mode they need:

### Mode 1: Analyze & Enhance Existing Images
Scan the website/repo for all images → analyze each one → use Gemini to recreate at higher
quality → compress → convert → upload to Cloudinary → replace references in code.

### Mode 2: Generate New Images from Descriptions
User describes what images they need → generate with Gemini → compress → upload → place in code.

### Mode 3: Replace Placeholders
Detect placeholder/stock images in the site → determine what real images should be there →
generate appropriate replacements → compress → upload → swap in code.

### Mode 4: Open Graph Images
Generate OG images for every page on the site with proper dimensions and branding.

### Mode 5: Favicon Generation
Create a complete favicon set from a logo or brand mark following modern best practices.

### Mode 6: Full Site Image Overhaul
Combination of all above — complete image audit and replacement.

---

## Step 1: Site & Image Audit

Before generating anything, understand what exists. Read `references/image-audit.md` for the
full audit procedure.

**Quick summary:**
1. Scan the project for all image files (jpg, jpeg, png, gif, webp, avif, svg, ico)
2. Scan HTML/JSX/Vue/Svelte templates for `<img>`, `background-image`, OG meta tags, favicon links
3. For each image, determine:
   - Current dimensions and file size
   - Where it's used (hero, card, thumbnail, background, OG, favicon, logo, icon)
   - What aspect ratio and size it SHOULD be (see sizing guide below)
   - Whether it's a placeholder, stock photo, or real brand image
4. Present findings to user and ask what they want to do with each image

---

## Step 2: Image Generation with Gemini

Read `references/gemini-image-guide.md` for comprehensive Gemini API usage.

### Model Selection

| Model | Best For | Notes |
|-------|----------|-------|
| `gemini-3-pro-image-preview` | Professional asset production, complex prompts, text in images | Advanced reasoning ("Thinking"), highest fidelity. Use this as the **primary model**. |
| `gemini-2.5-flash-image` | Fast iteration, high-volume tasks, quick previews | Lower cost, faster. Good for drafts and bulk generation. |

**Default to `gemini-3-pro-image-preview`** unless the user asks for speed/cost optimization.

### API Call Pattern

```python
import google.generativeai as genai
import base64
from pathlib import Path

genai.configure(api_key=os.environ["GEMINI_API_KEY"])

# For generating a NEW image
response = client.models.generate_content(
    model="gemini-3-pro-image-preview",
    contents="YOUR DETAILED PROMPT HERE",
    config=types.GenerateContentConfig(
        response_modalities=["TEXT", "IMAGE"]
    ),
)

# For ENHANCING an existing image (pass it as input)
with open("existing_image.jpg", "rb") as f:
    image_data = base64.b64encode(f.read()).decode()

response = client.models.generate_content(
    model="gemini-3-pro-image-preview",
    contents=[
        {"text": "Recreate this image at much higher quality. Maintain the same composition, subject, and mood but enhance resolution, lighting, detail, and overall professional quality. Make it look like a premium commercial photograph."},
        {"inline_data": {"mime_type": "image/jpeg", "data": image_data}}
    ],
    config=types.GenerateContentConfig(
        response_modalities=["TEXT", "IMAGE"]
    ),
)

# Extract and save the generated image
for part in response.candidates[0].content.parts:
    if hasattr(part, 'inline_data') and part.inline_data:
        img_bytes = base64.b64decode(part.inline_data.data)
        with open("output.png", "wb") as f:
            f.write(img_bytes)
```

### Prompt Engineering for Best Results

The quality of your Gemini prompt determines everything. Follow these principles:

1. **Be extremely specific** — describe composition, lighting, color palette, mood, camera angle
2. **Specify the use case** — "This is a hero image for a trucking company website"
3. **Include the aspect ratio you determined from the site** — after analyzing the container/layout (see Step 3)
4. **Reference style** — "Clean, modern corporate style with warm lighting"
5. **For brand consistency** — Include brand colors and style across all prompts for the same site

**Prompt template for enhancement:**
```
Recreate this image as a premium, professional [INDUSTRY] photograph.
Enhance: resolution, lighting, color vibrancy, detail, and sharpness.
Style: [STYLE DESCRIPTION]
Mood: [MOOD]
Maintain the same subject, composition, and visual intent.
This will be used as a [DESCRIBE WHERE ON THE SITE] on a [INDUSTRY] website.
Aspect ratio: [RATIO YOU DETERMINED FROM ANALYZING THE LAYOUT]
Output should look like it was shot by a professional photographer with high-end equipment.
```

**Prompt template for new generation:**
```
Create a professional [STYLE] image for a [INDUSTRY] company website.
Subject: [WHAT THE IMAGE SHOWS]
Composition: [LAYOUT - centered, rule of thirds, etc.]
Lighting: [LIGHTING TYPE]
Color palette: [COLORS that match the brand]
Mood: [EMOTIONAL TONE]
This will be used as: [DESCRIBE WHERE — e.g. "the main image in the hero section",
"a card in a 3-column service grid", "a full-width divider between sections"]
Aspect ratio: [RATIO YOU DETERMINED FROM ANALYZING THE LAYOUT]
The image should look authentic, not AI-generated. Professional commercial photography quality.
```

### Logo Integration

If the user's site has a logo and an image needs it:
1. Download/locate the logo from the site
2. Pass both the logo and the prompt to Gemini
3. Instruct Gemini to incorporate the logo naturally
4. Only use logos in images where it makes sense (branded graphics, OG images, etc.)
5. Most standard photos do NOT need a logo

---

## Step 3: Figuring Out Image Sizes

**Do NOT use a fixed size chart.** Every site is different. The AI must determine the right
size and aspect ratio for each image by analyzing the actual site context.

### How to Determine the Right Size

1. **Read the code.** Look at the CSS/Tailwind/styles for the image container. What are
   the `width`, `height`, `max-width`, `aspect-ratio`, `object-fit` values? What does the
   layout actually render at in the browser?
2. **Check existing images.** If there's already an image in that slot, what dimensions is it?
   Is it working well or is it stretched/cropped badly?
3. **Look at the component.** Is this a full-bleed hero spanning the viewport? A small card
   in a grid? A circular avatar? A sidebar image? The component context tells you the shape.
4. **Consider the layout.** A hero section with text overlay on the left needs different
   proportions than a centered hero with text below. A card grid with 3 columns needs
   different images than a 2-column feature section.
5. **Check for responsive behavior.** Does the container change aspect ratio at different
   breakpoints? If so, you may need to generate different crops or use `object-fit: cover`
   with a size that works across breakpoints.

### Decision-Making Process

For each image, think through this:

```
What container is this image in?
  → What are its dimensions / aspect ratio at desktop? Tablet? Mobile?
  → Is it cropped via object-fit:cover, or displayed at natural size?
  → Does text overlay it (needs space for text)?

What would look best here?
  → Would a different aspect ratio actually improve this section?
  → Is the current layout optimal, or could a size change make it better?
  → Does the design feel cramped or too spread out?
```

### When to Suggest a Different Size

Sometimes the current image slot isn't ideal. If you notice an opportunity to improve the
layout by using a different image size, **suggest it to the user** — don't just silently
change things. For example:

- "The hero section is using a 4:3 image but the container is full-width 16:9 — the image
  is being heavily cropped. I'd recommend generating a wider image and adjusting the CSS
  so you see the full composition."
- "These service cards use square images but they'd look more professional with 3:2
  landscape images. Want me to generate those and update the card component?"
- "The team section has inconsistent image sizes. I can generate all portraits at the same
  aspect ratio so the grid looks clean."

Only suggest changes when it genuinely improves the design. Don't change things just to change them.

### General Principles (Not Rules)

- **Generate high resolution.** Whatever size you determine, generate at 2x the display
  size minimum so it's crisp on retina screens. If a hero renders at 1440px wide, generate
  at least 2880px wide.
- **OG images are an exception** — these have a fixed spec: **1200×630** at ~1.91:1.
  Social platforms expect this exact size. Don't deviate.
- **Favicons are an exception** — the source should be **512×512** square. The generation
  script handles all the required sizes from there.
- **Logos** — prefer SVG. If raster, generate large (500×500+) and let CSS scale down.
- For everything else, let the site's actual layout drive the decision.

---

## Step 4: Compression & Format Conversion

After generating images, optimize them aggressively for web performance.

Read `references/compression-guide.md` for detailed instructions.

**Quick process:**

```bash
# Install tools
pip install Pillow pillow-avif-plugin --break-system-packages
npm install -g sharp-cli  # or use sharp in Node.js

# Python compression script (see scripts/compress.py)
# Converts to WebP/AVIF, applies appropriate quality settings
```

### Format Selection

| Format | Use When | Quality Setting |
|--------|----------|----------------|
| **WebP** | Default for all web images. Best balance of quality/size. | 80-85 for photos, 90 for graphics |
| **AVIF** | When maximum compression needed AND browser support is acceptable | 65-75 for photos |
| **PNG** | Transparency needed, OG images, favicons | Lossless or near-lossless |
| **SVG** | Logos, icons, simple graphics | N/A (vector) |
| **ICO** | favicon.ico specifically | Contains 16x16 and 32x32 |

### Compression Targets

Don't aim for fixed file sizes per category — the right target depends on the actual
image dimensions and content complexity. Instead, use these principles:

- **Compress until you notice quality loss, then back off one notch.** Start at quality 80
  for WebP and check visually. If it looks fine, try 75. If artifacts appear, go back to 80.
- **Large images above the fold** (heroes, banners) can be a bit larger — up to 200-400KB
  is acceptable for a full-viewport image since it loads first and has the most visual impact.
- **Small images and anything below the fold** should be as lean as possible — under 80KB
  ideally, since they'll be lazy-loaded and users may never scroll to them.
- **OG images** are a special case: keep under 100KB PNG for fast social preview loading.
- **Favicon PNGs** should be tiny — under 10KB each.
- When using Cloudinary with `f_auto,q_auto`, Cloudinary handles format and quality
  automatically per browser. You can skip generating multiple formats locally and let
  Cloudinary do the work.

Always generate both WebP and a fallback (JPEG/PNG). Use `<picture>` element for format selection.

---

## Step 5: Upload to Cloudinary

After compression, upload everything to Cloudinary organized by project.

Read `references/cloudinary-guide.md` for detailed API usage.

**Quick process:**

```python
import cloudinary
import cloudinary.uploader

cloudinary.config(
    cloud_name=os.environ["CLOUDINARY_CLOUD_NAME"],
    api_key=os.environ["CLOUDINARY_API_KEY"],
    api_secret=os.environ["CLOUDINARY_API_SECRET"],
    secure=True
)

# Upload with project folder organization
result = cloudinary.uploader.upload(
    "path/to/image.webp",
    folder=f"{project_name}/{image_category}",    # e.g., "acme-trucking/heroes"
    public_id="hero-main",                         # descriptive name
    resource_type="image",
    overwrite=True,
    quality="auto:best",                           # Cloudinary can also optimize
    fetch_format="auto"                            # Serve best format per browser
)

cloudinary_url = result["secure_url"]
```

### Folder Structure in Cloudinary

```
{project-name}/
├── heroes/
├── cards/
├── backgrounds/
├── team/
├── products/
├── og-images/
├── favicons/
├── logos/
└── misc/
```

---

## Step 6: Update Code References

After uploading, replace all image references in the codebase with Cloudinary URLs.

1. Map each uploaded image to its original reference in the code
2. Search for the old image path/URL across all files
3. Replace with the Cloudinary URL
4. For responsive images, use Cloudinary's transformation URLs:
   ```html
   <!-- Cloudinary auto-format and auto-quality -->
   <img src="https://res.cloudinary.com/{cloud}/image/upload/f_auto,q_auto/{folder}/{image}"
        srcset="https://res.cloudinary.com/{cloud}/image/upload/f_auto,q_auto,w_400/{folder}/{image} 400w,
                https://res.cloudinary.com/{cloud}/image/upload/f_auto,q_auto,w_800/{folder}/{image} 800w,
                https://res.cloudinary.com/{cloud}/image/upload/f_auto,q_auto,w_1200/{folder}/{image} 1200w"
        sizes="(max-width: 768px) 100vw, 50vw"
        alt="Descriptive alt text"
        loading="lazy" />
   ```
5. **Always ask user to confirm** before making code changes

---

## Open Graph Image Generation

For every page that needs an OG image:

1. Identify all pages on the site
2. For each page, determine what the OG image should show
3. Generate using Gemini with this template prompt:
   ```
   Create a professional Open Graph social sharing image (1200x630 pixels).
   Brand: [BRAND NAME]
   Brand colors: [COLORS]
   Page title: [PAGE TITLE]
   Page purpose: [WHAT THE PAGE IS ABOUT]
   Style: Clean, modern, professional. Include the brand name prominently.
   The text should be large, legible, and centered.
   Background should be visually appealing but not distract from the text.
   ```
4. Compress as PNG (max 100KB)
5. Upload to Cloudinary under `{project}/og-images/`
6. Add/update `<meta property="og:image">` tags in each page

---

## Favicon Generation

Follow the modern minimal favicon set (based on current best practices):

### Required Files

| File | Size | Purpose |
|------|------|---------|
| `favicon.ico` | 32×32 (contains 16×16) | Universal browser fallback |
| `favicon.svg` | Vector | Modern browsers, supports dark mode |
| `apple-touch-icon.png` | 180×180 | iOS home screen |
| `android-chrome-192x192.png` | 192×192 | Android home screen |
| `android-chrome-512x512.png` | 512×512 | PWA splash screen |

### HTML to Add

```html
<link rel="icon" href="/favicon.ico" sizes="32x32">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/apple-touch-icon.png"><!-- 180×180 -->
<link rel="manifest" href="/manifest.webmanifest">
```

### manifest.webmanifest

```json
{
  "name": "Brand Name",
  "icons": [
    { "src": "/android-chrome-192x192.png", "sizes": "192x192", "type": "image/png" },
    { "src": "/android-chrome-512x512.png", "sizes": "512x512", "type": "image/png" }
  ]
}
```

### Process

1. Get the logo or brand mark (ask user, or extract from the website)
2. If no logo exists, ask what the favicon should represent
3. Generate a clean, simple 512×512 icon using Gemini (simple, bold, high contrast)
4. Use sharp/Pillow to generate all required sizes from the 512×512 source
5. For SVG: Ask designer or create a simplified vector version
6. For ICO: Use Pillow to create multi-size ICO from PNGs
7. Upload all to Cloudinary AND place in the project's public/static directory
8. Add the HTML tags to the site's `<head>`

```python
# Generate favicon sizes from source
from PIL import Image

source = Image.open("favicon-512.png")

# Generate all sizes
sizes = {
    "favicon-16x16.png": (16, 16),
    "favicon-32x32.png": (32, 32),
    "apple-touch-icon.png": (180, 180),
    "android-chrome-192x192.png": (192, 192),
    "android-chrome-512x512.png": (512, 512),
}

for filename, size in sizes.items():
    resized = source.resize(size, Image.Resampling.LANCZOS)
    resized.save(filename, "PNG", optimize=True)

# Create ICO file
icon_16 = source.resize((16, 16), Image.Resampling.LANCZOS)
icon_32 = source.resize((32, 32), Image.Resampling.LANCZOS)
icon_32.save("favicon.ico", format="ICO", sizes=[(16, 16), (32, 32)])
```

---

## Important Behavioral Rules

1. **ALWAYS ask questions** before generating images. Never assume what the user wants.
2. **Show a plan first.** Before generating, present what you'll create, sizes, and styles. Get approval.
3. **Generate one sample first.** Don't batch-generate 20 images without showing the user the first one for approval and style calibration.
4. **Maintain consistency.** All images for a site should share a cohesive visual style.
5. **Check the logo.** Look for a logo on the site. Download it. Ask if it should be used.
6. **Never overwrite** original images without explicit user confirmation.
7. **Always provide before/after** comparisons when enhancing existing images.
8. **Track everything.** Keep a manifest of what was generated, where it was uploaded, and what code was changed.
9. **Alt text matters.** When placing images, always include descriptive alt text.
10. **Lazy load.** Add `loading="lazy"` to images below the fold.

---

## Reference Files

- `references/gemini-image-guide.md` — Detailed Gemini API parameters, prompt engineering, and model comparison
- `references/compression-guide.md` — Image compression scripts and format conversion details
- `references/cloudinary-guide.md` — Cloudinary API usage, transformations, and folder organization
- `references/image-audit.md` — How to audit a site's images and determine what needs work

## Script Files

- `scripts/audit_images.py` — Scan a project directory for all images and their usage
- `scripts/generate_image.py` — Generate/enhance images via Gemini API
- `scripts/compress_images.py` — Compress and convert images to optimal web formats
- `scripts/upload_cloudinary.py` — Upload images to Cloudinary with proper organization
- `scripts/generate_favicons.py` — Generate complete favicon set from a source image
- `scripts/generate_og_images.py` — Generate OG images for site pages
- `scripts/update_references.py` — Find and replace image references in codebase
