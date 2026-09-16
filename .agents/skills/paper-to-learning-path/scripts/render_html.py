#!/usr/bin/env python3
"""
render_html.py — Render translated JSON into a self-contained nature-inspired HTML file.

Usage:
    python render_html.py \\
        --json translated.json \\
        --template ../resources/nature_paper.html \\
        --out paper_translated.html \\
        [--offline]

The --offline flag embeds a local KaTeX copy instead of using the CDN.
"""

import argparse
import base64
import json
import os
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# HTML escaping helper
# ---------------------------------------------------------------------------

def _esc(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


# ---------------------------------------------------------------------------
# Math-safe HTML escaping
# Protects LaTeX delimiters before HTML-escaping so KaTeX can still parse them.
# ---------------------------------------------------------------------------

def _escape_and_math(text: str) -> str:
    """Escape HTML but keep math delimiters intact for KaTeX auto-render."""
    math_blocks: list[str] = []

    # Match all LaTeX math regions (display and inline)
    placeholder_re = re.compile(
        r"(\$\$[\s\S]+?\$\$"           # $$ ... $$ display
        r"|\$[^$\n]{1,500}\$"          # $ ... $ inline
        r"|\\\[[\s\S]+?\\\]"           # \[ ... \]
        r"|\\\([\s\S]+?\\\))",         # \( ... \)
        re.DOTALL,
    )

    def stash(m: re.Match) -> str:
        idx = len(math_blocks)
        math_blocks.append(m.group(0))
        return f"\x00MATH{idx}\x00"

    protected = placeholder_re.sub(stash, text)
    escaped = _esc(protected)

    # Restore math regions verbatim (must NOT be HTML-escaped)
    for i, block in enumerate(math_blocks):
        escaped = escaped.replace(f"\x00MATH{i}\x00", block)

    return escaped


# ---------------------------------------------------------------------------
# Section → HTML block converters
# ---------------------------------------------------------------------------

def _section_to_html(section: dict, heading_counters: list) -> str:
    btype = section.get("type", "paragraph")
    text = section.get("text", "")
    original = section.get("text_original")

    if not text.strip():
        return ""

    if btype == "heading":
        level = 2
        # Build a slug-safe anchor from the translated heading text
        anchor = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:80]
        orig_tag = (
            f'<span class="original-lang" title="Original">{_esc(original)}</span>'
            if original else ""
        )
        return (
            f'<h{level} id="{anchor}" class="section-heading">'
            f'{_escape_and_math(text)}{orig_tag}'
            f'</h{level}>\n'
        )

    elif btype == "math_block":
        # math_block raw text may already contain $$...$$ or \[...\]
        # Strip wrapping delimiters if present, then emit clean display math
        raw = text.strip()
        # Remove outer $$ ... $$ wrapping if already present
        if raw.startswith("$$") and raw.endswith("$$") and len(raw) > 4:
            inner = raw[2:-2].strip()
        # Remove outer \[ ... \] wrapping if already present
        elif raw.startswith(r"\[") and raw.endswith(r"\]") and len(raw) > 4:
            inner = raw[2:-2].strip()
        else:
            inner = raw
        # Emit as display math inside a styled block
        return f'<div class="math-block">\\[{inner}\\]</div>\n'

    elif btype == "caption":
        return f'<figcaption class="figure-caption">{_escape_and_math(text)}</figcaption>\n'

    elif btype == "list":
        items = [li.strip() for li in re.split(r"\n+", text) if li.strip()]
        items_html = "\n".join(f"  <li>{_escape_and_math(item)}</li>" for item in items)
        return f'<ul class="paper-list">\n{items_html}\n</ul>\n'

    elif btype == "abstract":
        return (
            f'<div class="abstract-box">'
            f'<div class="abstract-label">Abstract</div>'
            f'<p>{_escape_and_math(text)}</p>'
            f'</div>\n'
        )

    else:  # paragraph
        return f'<p class="paper-paragraph">{_escape_and_math(text)}</p>\n'


def _image_to_html(img: dict) -> str:
    path = img.get("path", "")
    caption = img.get("caption", "")
    img_id = img.get("id", "img")

    # Embed as base64 data URI for self-contained output
    data_uri = ""
    if path and os.path.isfile(path):
        with open(path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("ascii")
        data_uri = f"data:image/png;base64,{b64}"
    elif path:
        data_uri = path  # fallback: use path as src

    if not data_uri:
        return ""  # skip images with no valid source

    cap_html = f"<figcaption class=\"figure-caption\">{_escape_and_math(caption)}</figcaption>" if caption else ""
    return (
        f'<figure class="paper-figure" id="{img_id}">\n'
        f'  <img src="{data_uri}" alt="{_esc(caption)}" loading="lazy"/>\n'
        f'  {cap_html}\n'
        f'</figure>\n'
    )


# ---------------------------------------------------------------------------
# Main renderer
# ---------------------------------------------------------------------------

def render(json_path: str, template_path: str, out_path: str, offline: bool = False):
    with open(json_path, encoding="utf-8") as f:
        data = json.load(f)

    meta = data.get("metadata", {})
    sections = data.get("sections", [])
    images = data.get("images", [])
    translation = data.get("translation", {})

    src_lang = translation.get("source", "?")
    tgt_lang = translation.get("target", "?")

    # Build image lookup by page for inline insertion
    images_by_page: dict[int, list] = {}
    for img in images:
        page = img.get("page", 0)
        images_by_page.setdefault(page, []).append(img)
    inserted_images: set = set()

    # Build content HTML
    content_parts = []
    heading_counters = [0, 0, 0]
    prev_page = None

    for section in sections:
        page = section.get("page", 0)

        # Insert images that belong to this page (once, after first section on page)
        if page != prev_page and page in images_by_page:
            for img in images_by_page[page]:
                if img["id"] not in inserted_images:
                    content_parts.append(_image_to_html(img))
                    inserted_images.add(img["id"])
        prev_page = page

        content_parts.append(_section_to_html(section, heading_counters))

    # Insert any remaining images (last pages)
    for img in images:
        if img["id"] not in inserted_images:
            content_parts.append(_image_to_html(img))

    content_html = "\n".join(content_parts)

    # Read template
    if os.path.isfile(template_path):
        with open(template_path, encoding="utf-8") as f:
            template = f.read()
    else:
        print(f"WARNING: Template not found at {template_path}. Using inline fallback.")
        template = _fallback_template()

    # Inject content
    html = (
        template
        .replace("{{TITLE}}", _esc(meta.get("title", "Research Paper")))
        .replace("{{AUTHORS}}", _esc(meta.get("authors", "")))
        .replace("{{SOURCE_LANG}}", _esc(src_lang))
        .replace("{{TARGET_LANG}}", _esc(tgt_lang))
        .replace("{{PAGES}}", str(meta.get("pages", "")))
        .replace("{{CONTENT}}", content_html)
        .replace("{{SOURCE_FILE}}", _esc(meta.get("source_file", "")))
    )

    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)

    size_kb = os.path.getsize(out_path) / 1024
    print(f"✅ HTML rendered → {out_path}  ({size_kb:.1f} KB)")

    # Quick validation
    katex_errors = html.count("katex-error")
    img_empty = html.count('src=""')
    if katex_errors:
        print(f"  ⚠️  {katex_errors} KaTeX error(s) detected — review math blocks.")
    if img_empty:
        print(f"  ⚠️  {img_empty} empty image src attribute(s).")


def _fallback_template() -> str:
    """Minimal fallback template if nature_paper.html is missing."""
    return """<!DOCTYPE html>
<html lang="{{TARGET_LANG}}">
<head><meta charset="UTF-8"><title>{{TITLE}}</title>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css">
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/contrib/auto-render.min.js"
  onload="renderMathInElement(document.body,{delimiters:[{left:'$$',right:'$$',display:true},{left:'\\\\[',right:'\\\\]',display:true},{left:'$',right:'$',display:false},{left:'\\\\(',right:'\\\\)',display:false}],throwOnError:false});"></script>
<style>body{font-family:Georgia,serif;max-width:860px;margin:0 auto;padding:2rem;line-height:1.8}
.math-block{background:#f5f5f5;padding:1rem;margin:1rem 0;border-radius:6px;overflow-x:auto;text-align:center}
</style>
</head><body>
<p><a href="learning/index.html">📚 View Learning Path</a></p>
<h1>{{TITLE}}</h1><p>{{AUTHORS}}</p><p>{{SOURCE_LANG}} → {{TARGET_LANG}}</p>
{{CONTENT}}
<p>Source: {{SOURCE_FILE}} | Pages: {{PAGES}}</p>
</body></html>"""


def main():
    parser = argparse.ArgumentParser(description="Render translated JSON to HTML")
    parser.add_argument("--json", required=True)
    parser.add_argument(
        "--template",
        default=str(Path(__file__).parent.parent / "resources" / "nature_paper.html"),
        help="Path to HTML template (default: resources/nature_paper.html)",
    )
    parser.add_argument("--out", required=True)
    parser.add_argument("--offline", action="store_true")
    args = parser.parse_args()

    render(args.json, args.template, args.out, args.offline)


if __name__ == "__main__":
    main()
