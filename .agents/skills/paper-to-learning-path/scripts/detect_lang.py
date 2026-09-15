#!/usr/bin/env python3
"""
detect_lang.py — Auto-detect the source language of the PDF content.

Usage:
    python detect_lang.py --json extracted.json

Output:
    Prints detected BCP-47 language code and confidence to stdout.
    Exits with code 0 on success, 1 on failure.
"""

import argparse
import json
import sys

try:
    from langdetect import detect, detect_langs, LangDetectException
except ImportError:
    print("ERROR: langdetect not installed. Run: pip install langdetect")
    sys.exit(1)


def detect_language(json_path: str, min_confidence: float = 0.85) -> tuple[str, float]:
    with open(json_path, encoding="utf-8") as f:
        data = json.load(f)

    # Collect paragraph/heading text (skip math blocks — they are language-neutral)
    texts = [
        s["text"]
        for s in data.get("sections", [])
        if s.get("type") in ("paragraph", "heading", "caption")
    ]

    if not texts:
        print("ERROR: No translatable text blocks found in extracted.json")
        sys.exit(1)

    # Use a large representative sample
    sample = " ".join(texts[:60])[:8000]

    try:
        results = detect_langs(sample)
    except LangDetectException as e:
        print(f"ERROR: Language detection failed: {e}")
        sys.exit(1)

    if not results:
        print("ERROR: No language detected.")
        sys.exit(1)

    top = results[0]
    lang_code = top.lang
    confidence = round(top.prob, 4)

    print(f"Detected language : {lang_code}")
    print(f"Confidence        : {confidence:.1%}")

    if confidence < min_confidence:
        print(
            f"\n⚠️  Confidence ({confidence:.1%}) is below {min_confidence:.0%}. "
            "Please confirm the source language manually."
        )

    # Also print as parseable line for agent consumption
    print(f"\nLANG_CODE={lang_code}")
    print(f"CONFIDENCE={confidence}")

    return lang_code, confidence


def main():
    parser = argparse.ArgumentParser(description="Detect source language of extracted PDF JSON")
    parser.add_argument("--json", required=True, help="Path to extracted.json")
    parser.add_argument("--min-confidence", type=float, default=0.85)
    args = parser.parse_args()

    detect_language(args.json, args.min_confidence)


if __name__ == "__main__":
    main()
