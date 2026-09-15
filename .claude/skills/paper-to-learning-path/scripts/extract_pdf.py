#!/usr/bin/env python3
"""
extract_pdf.py — Extract text blocks, math expressions, and images from a PDF.

Usage:
    python extract_pdf.py --pdf path/to/paper.pdf --out-dir ./output/assets

Output:
    <out-dir>/../extracted.json   — structured document JSON
    <out-dir>/img_NNN.png         — extracted images (PNG)
"""

import argparse
import base64
import json
import os
import re
import sys
from pathlib import Path

try:
    import fitz  # PyMuPDF
except ImportError:
    print("ERROR: PyMuPDF not installed. Run: pip install pymupdf")
    sys.exit(1)

# ---------------------------------------------------------------------------
# Math detection heuristics
# ---------------------------------------------------------------------------
MATH_PATTERNS = [
    # Display math
    re.compile(r"\\\[.*?\\\]", re.DOTALL),
    re.compile(r"\$\$.*?\$\$", re.DOTALL),
    # Inline math
    re.compile(r"\$[^$\n]{1,200}\$"),
    # Common LaTeX commands
    re.compile(r"\\(?:frac|sum|int|prod|lim|infty|alpha|beta|gamma|delta|theta"
               r"|sigma|omega|nabla|partial|sqrt|mathbf|mathbb|mathrm|text"
               r"|begin|end|left|right|cdot|times|leq|geq|neq|approx|equiv"
               r"|forall|exists|in|notin|subset|supset|cup|cap|emptyset)\b"),
]


def looks_like_math(text: str) -> bool:
    """Return True if the text appears to be a math/equation block."""
    stripped = text.strip()
    # Short text with many symbols
    symbol_ratio = sum(1 for c in stripped if c in "+-*/=<>^_{}\\$") / max(len(stripped), 1)
    if symbol_ratio > 0.25 and len(stripped) < 300:
        return True
    for pat in MATH_PATTERNS:
        if pat.search(stripped):
            return True
    return False


def classify_block(block_text: str, flags: int = 0) -> str:
    """Classify a text block into a section type."""
    stripped = block_text.strip()
    if not stripped:
        return None
    if looks_like_math(stripped):
        return "math_block"
    words = stripped.split()
    # Headings: short, may end without period, often ALL CAPS or Title Case
    if len(words) <= 10 and not stripped.endswith("."):
        if stripped.isupper() or stripped.istitle() or re.match(r"^\d+[\.\s]+[A-Z]", stripped):
            return "heading"
    # Captions: start with "Figure", "Table", "Fig.", etc.
    if re.match(r"^(Figure|Fig\.|Table|Tab\.|Algorithm|Listing)\s*\d+", stripped, re.IGNORECASE):
        return "caption"
    # Lists
    if re.match(r"^[\•\-\*\d]+[\.\)]\s", stripped):
        return "list"
    return "paragraph"


# ---------------------------------------------------------------------------
# Main extraction
# ---------------------------------------------------------------------------

def extract(pdf_path: str, out_dir: str, dpi: int = 120) -> dict:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    doc = fitz.open(pdf_path)

    metadata = {
        "title": doc.metadata.get("title", ""),
        "authors": doc.metadata.get("author", ""),
        "subject": doc.metadata.get("subject", ""),
        "pages": doc.page_count,
        "source_file": str(Path(pdf_path).name),
    }

    sections = []
    images = []
    img_counter = 0

    for page_num, page in enumerate(doc, start=1):
        # --- Text blocks ---
        blocks = page.get_text("blocks", sort=True)
        for b in blocks:
            x0, y0, x1, y1, text, block_no, block_type = b
            if block_type != 0:  # 0 = text; 1 = image (handled separately)
                continue
            text = text.strip()
            if not text:
                continue
            btype = classify_block(text)
            if btype is None:
                continue
            sections.append({
                "type": btype,
                "text": text,
                "page": page_num,
                "bbox": [round(x0, 1), round(y0, 1), round(x1, 1), round(y1, 1)],
            })

        # --- Images ---
        for img_info in page.get_images(full=True):
            xref = img_info[0]
            try:
                base_img = doc.extract_image(xref)
            except Exception:
                continue
            img_bytes = base_img["image"]
            img_ext = base_img.get("ext", "png")

            img_counter += 1
            img_id = f"img_{img_counter:03d}"
            img_filename = f"{img_id}.png"
            img_path = out_dir / img_filename

            # Save raw image
            if img_ext.lower() in ("png", "jpeg", "jpg"):
                with open(img_path, "wb") as f:
                    f.write(img_bytes)
            else:
                # Convert to PNG via fitz pixmap
                pix = fitz.Pixmap(doc, xref)
                if pix.n > 4:
                    pix = fitz.Pixmap(fitz.csRGB, pix)
                pix.save(str(img_path))

            images.append({
                "id": img_id,
                "path": str(img_path),
                "page": page_num,
                "caption": "",  # filled in post-processing if caption block follows
            })

    doc.close()

    # Post-process: attach captions to images by proximity
    _attach_captions(sections, images)

    result = {
        "metadata": metadata,
        "sections": sections,
        "images": images,
    }

    out_json = out_dir.parent / "extracted.json"
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"✅ Extracted {len(sections)} blocks, {len(images)} images → {out_json}")
    return result


def _attach_captions(sections: list, images: list):
    """Simple heuristic: pair each image with the nearest following caption block."""
    captions = [(i, s) for i, s in enumerate(sections) if s["type"] == "caption"]
    for img_idx, img in enumerate(images):
        page = img["page"]
        # Find first caption on the same or next page
        for _, cap in captions:
            if cap["page"] >= page:
                img["caption"] = cap["text"]
                break


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Extract PDF content to JSON + images")
    parser.add_argument("--pdf", required=True, help="Path to input PDF")
    parser.add_argument("--out-dir", default="output/assets", help="Directory for extracted images")
    parser.add_argument("--dpi", type=int, default=120, help="DPI for image extraction")
    args = parser.parse_args()

    if not os.path.isfile(args.pdf):
        print(f"ERROR: PDF not found: {args.pdf}")
        sys.exit(1)

    extract(args.pdf, args.out_dir, args.dpi)


if __name__ == "__main__":
    main()
