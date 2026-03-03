#!/usr/bin/env python3
"""
Convert all PDFs in PatientPartner Master to Markdown.
Output: ./reference-extracted/ mirrors folder structure with .md files.
Markdown is optimized for Cursor and Claude AI context—both read .md natively.
"""

import os
import sys
from pathlib import Path

# Add project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

try:
    import pymupdf4llm
except ImportError:
    print("Run: pip install pymupdf4llm")
    sys.exit(1)


def find_pdfs(root: Path) -> list[tuple[Path, Path]]:
    """Find all PDFs and return (pdf_path, output_md_path) tuples."""
    root = Path(root)
    extracted_root = root / "reference-extracted"
    pairs = []
    
    for pdf_path in root.rglob("*.pdf"):
        if ".venv" in str(pdf_path) or "reference-extracted" in str(pdf_path):
            continue
        rel = pdf_path.relative_to(root)
        md_path = extracted_root / rel.with_suffix(".md")
        pairs.append((pdf_path, md_path))
    
    return pairs


def convert_pdf(pdf_path: Path, md_path: Path) -> bool:
    """Convert single PDF to Markdown. Returns True on success."""
    try:
        md_text = pymupdf4llm.to_markdown(str(pdf_path))
        md_path.parent.mkdir(parents=True, exist_ok=True)
        md_path.write_text(md_text, encoding="utf-8")
        return True
    except Exception as e:
        print(f"  ERROR: {e}")
        return False


def main():
    root = PROJECT_ROOT
    pairs = find_pdfs(root)
    
    if not pairs:
        print("No PDFs found.")
        return 1
    
    print(f"Converting {len(pairs)} PDFs to Markdown...")
    success = 0
    for pdf_path, md_path in pairs:
        rel = pdf_path.relative_to(root)
        print(f"  {rel} -> reference-extracted/{rel.with_suffix('.md').name}")
        if convert_pdf(pdf_path, md_path):
            success += 1
    
    print(f"\nDone: {success}/{len(pairs)} converted.")
    return 0 if success == len(pairs) else 1


if __name__ == "__main__":
    sys.exit(main())
