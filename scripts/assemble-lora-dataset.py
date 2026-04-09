#!/usr/bin/env python3
"""
Assemble PatientPartner LoRA training dataset.
Scrapes patientpartner.com for brand images, downloads them, creates caption files,
and zips everything for FAL Flux 2 Trainer upload.
"""

import os
import re
import urllib.request
import urllib.parse
from pathlib import Path

# Pages to scrape for images
PAGES = [
    "https://www.patientpartner.com",
    "https://www.patientpartner.com/about-us",
    "https://www.patientpartner.com/how-patientpartner-works",
    "https://www.patientpartner.com/pharma-engagment-software",
]

# Skip patterns (logos, tracking, tiny thumbnails, UI buttons)
SKIP_PATTERNS = [
    r"linkedin\.com",
    r"px\.ads",
    r"-p-500\.",  # Webflow small thumbnails
    r"logo\.webp",
    r"logo\.avif",
    r"Button\.webp",
    r"g12\.webp",
    r"Ellipse",  # Decorative circles
]

# Prefer these (hero, lifestyle, screenshots)
PREFER_PATTERNS = [
    r"hero",
    r"website\.webp",
    r"Frame",
    r"Benchmark",
    r"fi_\d+",  # Illustration IDs
]

TRIGGER_PHRASE = "patientpartner style"
DEFAULT_CAPTION = (
    "PatientPartner brand style, warm natural lighting, teal and navy color palette "
    "#74CCD3 and #314D69, professional approachable mood, healthcare-adjacent "
    "without clinical coldness, diverse representation, clean modern composition."
)


def fetch_html(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"})
    with urllib.request.urlopen(req, timeout=15) as r:
        return r.read().decode(errors="replace")


def extract_image_urls(html: str, base_url: str) -> set[str]:
    urls = set()
    # img src
    for m in re.finditer(r'<img[^>]+src=["\']([^"\']+)["\']', html, re.I):
        urls.add(m.group(1))
    # srcset (take first/largest)
    for m in re.finditer(r'srcset=["\']([^"\']+)["\']', html, re.I):
        for part in m.group(1).split(","):
            u = part.strip().split()[0]
            urls.add(u)
    # data-src
    for m in re.finditer(r'data-src=["\']([^"\']+)["\']', html, re.I):
        urls.add(m.group(1))
    # Resolve relative URLs
    base = urllib.parse.urlparse(base_url)
    resolved = set()
    for u in urls:
        if u.startswith("//"):
            resolved.add("https:" + u)
        elif u.startswith("/"):
            resolved.add(f"{base.scheme}://{base.netloc}{u}")
        elif u.startswith("http"):
            resolved.add(u)
    return resolved


def should_skip(url: str) -> bool:
    url_lower = url.lower()
    for pat in SKIP_PATTERNS:
        if re.search(pat, url_lower):
            return True
    return False


def score_url(url: str) -> int:
    """Higher = better for LoRA training."""
    url_lower = url.lower()
    score = 0
    for pat in PREFER_PATTERNS:
        if re.search(pat, url_lower):
            score += 2
    # Prefer larger images (avoid -p-500, -p-800)
    if "-p-500" in url or "-p-800" in url:
        score -= 5
    if ".avif" in url or ".webp" in url:
        score += 1
    return score


def download_image(url: str, out_path: Path) -> bool:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=20) as r:
            data = r.read()
        if len(data) < 1000:  # Skip tiny images
            return False
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "wb") as f:
            f.write(data)
        return True
    except Exception as e:
        print(f"  Skip {url[:60]}...: {e}")
        return False


def main():
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    output_dir = project_root / "brand" / "lora-dataset" / "patientpartner-photos"
    output_dir.mkdir(parents=True, exist_ok=True)

    print("Fetching pages and extracting image URLs...")
    all_urls = set()
    for page in PAGES:
        try:
            html = fetch_html(page)
            urls = extract_image_urls(html, page)
            all_urls.update(urls)
            print(f"  {page}: {len(urls)} images")
        except Exception as e:
            print(f"  Error {page}: {e}")

    # Filter and score
    candidates = [(u, score_url(u)) for u in all_urls if not should_skip(u)]
    candidates.sort(key=lambda x: -x[1])
    # Take top 35 (aim for 20-40)
    selected = [u for u, s in candidates[:35] if s >= -2]

    print(f"\nSelected {len(selected)} images for download.")

    # Download and create captions
    for i, url in enumerate(selected, 1):
        ext = ".png"
        if ".webp" in url:
            ext = ".webp"
        elif ".avif" in url:
            ext = ".avif"
        elif ".jpg" in url or ".jpeg" in url:
            ext = ".jpg"

        base_name = f"patientpartner_{i:02d}"
        img_path = output_dir / f"{base_name}{ext}"
        txt_path = output_dir / f"{base_name}.txt"

        if download_image(url, img_path):
            with open(txt_path, "w") as f:
                f.write(DEFAULT_CAPTION)
            print(f"  {base_name}{ext} + .txt")
        else:
            if img_path.exists():
                img_path.unlink()

    # Count successful downloads
    images = list(output_dir.glob("patientpartner_*.png")) + list(output_dir.glob("patientpartner_*.webp")) + list(output_dir.glob("patientpartner_*.avif")) + list(output_dir.glob("patientpartner_*.jpg"))
    txts = list(output_dir.glob("patientpartner_*.txt"))

    if len(images) < 10:
        print(f"\nWarning: Only {len(images)} images downloaded. LoRA training recommends 20-40.")
        print("You may need to add more images manually (LinkedIn, brand guidelines).")
    else:
        print(f"\nDownloaded {len(images)} images, {len(txts)} captions.")

    # Create zip
    zip_path = project_root / "brand" / "lora-dataset" / "patientpartner-lora-dataset.zip"
    import zipfile
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in output_dir.iterdir():
            if f.is_file():
                zf.write(f, f.name)

    print(f"\nCreated: {zip_path}")
    print(f"Size: {zip_path.stat().st_size / 1024:.1f} KB")
    print("\nNext: Upload to https://fal.ai/models/fal-ai/flux-2-trainer")
    print("Default caption (if needed):", DEFAULT_CAPTION[:80] + "...")


if __name__ == "__main__":
    main()
