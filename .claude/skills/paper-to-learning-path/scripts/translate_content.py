#!/usr/bin/env python3
"""
translate_content.py — Translate text sections from source to target language.

Skips math_block sections entirely. Handles inline math by replacing
LaTeX tokens with placeholders before translation and restoring them after.

Usage:
    python translate_content.py \\
        --json extracted.json \\
        --source en \\
        --target vi \\
        --out translated.json \\
        [--chunk-delay 0.5] \\
        [--chunk-size 4000]
"""

import argparse
import json
import re
import sys
import time
from copy import deepcopy

try:
    from deep_translator import GoogleTranslator
    from deep_translator.exceptions import RequestError, TranslationNotFound
except ImportError:
    print("ERROR: deep-translator not installed. Run: pip install deep-translator")
    sys.exit(1)


# ---------------------------------------------------------------------------
# Math placeholder protection
# ---------------------------------------------------------------------------
# Matches: $...$ or \(...\) or \[...\] or $$...$$
_MATH_RE = re.compile(
    r"(\$\$[\s\S]+?\$\$"      # display $$ ... $$
    r"|\$[^$\n]{1,300}\$"     # inline $ ... $
    r"|\\\[[\s\S]+?\\\]"      # display \[ ... \]
    r"|\\\([\s\S]+?\\\))",    # inline \( ... \)
    re.DOTALL,
)

# Citation patterns like [1], [Author, 2020]
_CITE_RE = re.compile(r"\[[^\[\]]{1,60}\]")


def _protect(text: str) -> tuple[str, dict]:
    """Replace math/citation tokens with safe placeholders."""
    placeholders = {}
    counter = [0]

    def replace(m):
        key = f"__MATH_{counter[0]:04d}__"
        placeholders[key] = m.group(0)
        counter[0] += 1
        return key

    protected = _MATH_RE.sub(replace, text)
    protected = _CITE_RE.sub(replace, protected)
    return protected, placeholders


def _restore(text: str, placeholders: dict) -> str:
    """Restore protected placeholders to their original content."""
    for key, value in placeholders.items():
        text = text.replace(key, value)
    return text


# ---------------------------------------------------------------------------
# Terminology consistency
# ---------------------------------------------------------------------------

class TermGlossary:
    """
    Builds a term map on first pass so repeated technical terms are
    translated consistently throughout the document.
    """

    def __init__(self):
        self._map: dict[str, str] = {}

    def register(self, original: str, translated: str):
        # Only register multi-word terms (likely technical)
        if len(original.split()) >= 2:
            self._map[original] = translated

    def apply(self, text: str) -> str:
        for src, tgt in self._map.items():
            text = text.replace(src, tgt)
        return text


# ---------------------------------------------------------------------------
# Chunked translation
# ---------------------------------------------------------------------------

def translate_text(
    text: str,
    source: str,
    target: str,
    chunk_size: int = 4000,
    delay: float = 0.5,
) -> str:
    """Translate text in chunks, preserving math/citations."""
    protected, placeholders = _protect(text)

    # Split into chunks at sentence boundaries
    chunks = _split_chunks(protected, chunk_size)
    translated_chunks = []

    translator = GoogleTranslator(source=source, target=target)

    for chunk in chunks:
        if not chunk.strip():
            translated_chunks.append(chunk)
            continue
        try:
            result = translator.translate(chunk)
            if result is None:
                result = chunk
            translated_chunks.append(result)
            if delay > 0:
                time.sleep(delay)
        except (RequestError, TranslationNotFound, Exception) as e:
            print(f"  ⚠️  Translation error: {e}. Keeping original chunk.")
            translated_chunks.append(chunk)

    merged = " ".join(translated_chunks)
    return _restore(merged, placeholders)


def _split_chunks(text: str, max_size: int) -> list[str]:
    """Split text into chunks no larger than max_size, splitting at sentence ends."""
    if len(text) <= max_size:
        return [text]

    chunks = []
    # Split on sentence boundaries
    sentences = re.split(r"(?<=[.!?])\s+", text)
    current = ""
    for sentence in sentences:
        if len(current) + len(sentence) + 1 > max_size:
            if current:
                chunks.append(current)
            current = sentence
        else:
            current = (current + " " + sentence).strip()
    if current:
        chunks.append(current)
    return chunks


# ---------------------------------------------------------------------------
# Main translation loop
# ---------------------------------------------------------------------------

def translate_document(
    json_path: str,
    source: str,
    target: str,
    out_path: str,
    chunk_size: int = 4000,
    chunk_delay: float = 0.5,
):
    with open(json_path, encoding="utf-8") as f:
        data = json.load(f)

    result = deepcopy(data)
    glossary = TermGlossary()
    sections = result.get("sections", [])

    total = len(sections)
    skipped = 0
    translated = 0

    print(f"📄 Translating {total} blocks  [{source} → {target}]")
    print("-" * 50)

    for i, section in enumerate(sections):
        btype = section.get("type")

        if btype == "math_block":
            # Never translate math
            skipped += 1
            continue

        original = section.get("text", "")
        if not original.strip():
            continue

        try:
            t = translate_text(original, source, target, chunk_size, chunk_delay)
            t = glossary.apply(t)
            glossary.register(original[:80], t[:80])
            section["text_original"] = original
            section["text"] = t
            translated += 1
            if (i + 1) % 10 == 0:
                print(f"  [{i+1}/{total}] ✓ {btype}")
        except Exception as e:
            print(f"  [{i+1}/{total}] ⚠️  Failed: {e}")
            section["text_original"] = original  # keep original on failure

    # Translate image captions
    for img in result.get("images", []):
        cap = img.get("caption", "")
        if cap.strip():
            img["caption_original"] = cap
            img["caption"] = translate_text(cap, source, target, chunk_size, chunk_delay)

    result["translation"] = {"source": source, "target": target}

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print("-" * 50)
    print(f"✅ Done. Translated: {translated}, Skipped (math): {skipped}")
    print(f"📝 Output → {out_path}")


def main():
    parser = argparse.ArgumentParser(description="Translate extracted PDF JSON")
    parser.add_argument("--json", required=True, help="Path to extracted.json")
    parser.add_argument("--source", required=True, help="Source language BCP-47 code")
    parser.add_argument("--target", required=True, help="Target language BCP-47 code")
    parser.add_argument("--out", default="translated.json", help="Output JSON path")
    parser.add_argument("--chunk-size", type=int, default=4000)
    parser.add_argument("--chunk-delay", type=float, default=0.5)
    args = parser.parse_args()

    translate_document(
        args.json,
        args.source,
        args.target,
        args.out,
        args.chunk_size,
        args.chunk_delay,
    )


if __name__ == "__main__":
    main()
