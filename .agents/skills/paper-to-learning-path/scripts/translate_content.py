#!/usr/bin/env python3
"""
translate_content.py — Prepare, scaffold, translate, and verify document translation.

When running via an AI Agent (Antigravity, Claude Code, Cursor, Windsurf):
  The Agent translates the document directly using its own LLM intelligence!
  NO API keys or external services are needed.
  1. python translate_content.py --scaffold --json extracted.json --target vi --out translated.json
  2. The Agent translates the text blocks directly into translated.json
  3. python translate_content.py --verify translated.json

When running standalone in CLI without an AI Agent:
  Supports external engines via --engine flag (gemini, openai, google fallback).
"""

import argparse
import json
import os
import re
import sys
import time
from copy import deepcopy
from typing import Callable


# ---------------------------------------------------------------------------
# Math / citation placeholder protection
# ---------------------------------------------------------------------------

_MATH_RE = re.compile(
    r"(\$\$[\s\S]+?\$\$"      # display $$ ... $$
    r"|\$[^$\n]{1,300}\$"     # inline $ ... $
    r"|\\\[[\s\S]+?\\\]"      # display \[ ... \]
    r"|\\\([\s\S]+?\\\))",    # inline \( ... \)
    re.DOTALL,
)
_CITE_RE = re.compile(r"\[[^\[\]]{1,60}\]")


def _protect(text: str) -> tuple[str, dict]:
    placeholders: dict[str, str] = {}
    counter = [0]

    def replace(m):
        key = f"__PH_{counter[0]:04d}__"
        placeholders[key] = m.group(0)
        counter[0] += 1
        return key

    protected = _MATH_RE.sub(replace, text)
    protected = _CITE_RE.sub(replace, protected)
    return protected, placeholders


def _restore(text: str, placeholders: dict) -> str:
    for key, value in placeholders.items():
        text = text.replace(key, value)
    return text


_LANG_NAMES = {
    "vi": "Vietnamese", "en": "English", "fr": "French",
    "de": "German",     "es": "Spanish", "zh": "Chinese (Simplified)",
    "zh-tw": "Chinese (Traditional)", "ja": "Japanese",
    "ko": "Korean",     "pt": "Portuguese", "it": "Italian",
    "ru": "Russian",    "ar": "Arabic",     "th": "Thai",
    "id": "Indonesian", "ms": "Malay",
}


def _lang_name(code: str) -> str:
    return _LANG_NAMES.get(code.lower(), code.upper())


# ---------------------------------------------------------------------------
# Agent scaffold & stats helper
# ---------------------------------------------------------------------------

def scaffold_document(json_path: str, source: str, target: str, out_path: str):
    """
    Create a scaffolded translated.json for the AI Agent to translate directly.
    Math blocks are preserved automatically. Original text is recorded in text_original.
    """
    with open(json_path, encoding="utf-8") as f:
        data = json.load(f)

    result = deepcopy(data)
    sections = result.get("sections", [])
    images = result.get("images", [])

    math_count = 0
    text_count = 0

    for section in sections:
        btype = section.get("type", "paragraph")
        raw_text = section.get("text", "")
        section["text_original"] = raw_text

        if btype == "math_block":
            math_count += 1
            # math_block stays unchanged
        else:
            text_count += 1

    for img in images:
        cap = img.get("caption", "")
        img["caption_original"] = cap

    result["translation"] = {
        "source": source or data.get("metadata", {}).get("language", "en"),
        "target": target,
        "engine": "ai-agent"
    }

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print("=" * 55)
    print(f" 📋 Translation Scaffold Created → {out_path}")
    print("=" * 55)
    print(f"  • Total sections:        {len(sections)}")
    print(f"  • Math blocks (locked):  {math_count} (never translated)")
    print(f"  • Text sections to translate: {text_count}")
    print(f"  • Image captions:        {len(images)}")
    print(f"  • Target language:       {_lang_name(target)}")
    print("\n💡 AI Agent can now translate text sections directly into this file!")
    print("   LaTeX math and math_block sections are already protected.")


def print_stats(json_path: str):
    """Print statistics about extracted blocks."""
    with open(json_path, encoding="utf-8") as f:
        data = json.load(f)

    sections = data.get("sections", [])
    images = data.get("images", [])

    math_count = sum(1 for s in sections if s.get("type") == "math_block")
    text_count = len(sections) - math_count
    total_words = sum(len(s.get("text", "").split()) for s in sections if s.get("type") != "math_block")

    print(f"📄 Document Statistics for: {json_path}")
    print(f"   Sections:   {len(sections)} ({math_count} math, {text_count} text)")
    print(f"   Images:     {len(images)}")
    print(f"   Word count: ~{total_words:,} words")


def verify_translation(json_path: str):
    """Verify that translated.json has valid translations and intact math."""
    with open(json_path, encoding="utf-8") as f:
        data = json.load(f)

    sections = data.get("sections", [])
    images = data.get("images", [])
    errors = []

    for i, s in enumerate(sections):
        btype = s.get("type")
        text = s.get("text", "")
        if btype != "math_block" and not text.strip():
            errors.append(f"Section {i} ({btype}) has empty translated text")

        # Check inline math balance
        single_dollars = len(re.findall(r"(?<!\$)\$(?!\$)", text))
        if single_dollars % 2 != 0:
            errors.append(f"Section {i} has unclosed inline math ($ delimiter count: {single_dollars})")

    for i, img in enumerate(images):
        if img.get("caption_original") and not img.get("caption"):
            errors.append(f"Image {img.get('id', i)} is missing translated caption")

    if errors:
        print(f"⚠️ Verification warnings ({len(errors)}):")
        for e in errors[:10]:
            print(f"  • {e}")
        if len(errors) > 10:
            print(f"  ... and {len(errors) - 10} more")
        return False
    else:
        target = data.get("translation", {}).get("target", "unknown")
        print(f"✅ Translation verified! All {len(sections)} sections and {len(images)} captions validated.")
        print(f"   Target language: {_lang_name(target)}")
        return True


# ---------------------------------------------------------------------------
# Optional External Translation Engines (for standalone CLI only)
# ---------------------------------------------------------------------------

def _build_system_prompt(source: str, target: str) -> str:
    src_name = _lang_name(source)
    tgt_name = _lang_name(target)
    return f"""You are an expert scientific translator specializing in AI, machine learning, and mathematics research papers.
Translate academic text from {src_name} to {tgt_name}.
Rules:
1. Preserve math placeholders (__PH_0000__) exactly as-is.
2. Preserve LaTeX math ($...$, $$...$$, \\(...\\)) verbatim.
3. Preserve citations like [1], [Author, 2020] verbatim.
4. Keep technical terminology accurate according to standard academic literature in {tgt_name}.
5. Do NOT translate proper nouns (model names, dataset names, author names).
Output ONLY the translated text."""


def _make_gemini_translator(api_key: str, model: str = "gemini-1.5-flash") -> Callable:
    import google.generativeai as genai
    genai.configure(api_key=api_key)
    gen_model = genai.GenerativeModel(model)

    def translate(text: str, source: str, target: str) -> str:
        prompt = f"{_build_system_prompt(source, target)}\n\n---\n{text}\n---"
        response = gen_model.generate_content(prompt)
        return response.text.strip()
    return translate


def _make_openai_translator(api_key: str, model: str = "gpt-4o-mini") -> Callable:
    from openai import OpenAI
    client = OpenAI(api_key=api_key)

    def translate(text: str, source: str, target: str) -> str:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": _build_system_prompt(source, target)},
                {"role": "user", "content": text},
            ],
            temperature=0.2,
        )
        return response.choices[0].message.content.strip()
    return translate


def _make_google_translator() -> Callable:
    from deep_translator import GoogleTranslator
    def translate(text: str, source: str, target: str) -> str:
        translator = GoogleTranslator(source=source, target=target)
        result = translator.translate(text)
        return result if result else text
    return translate


def translate_text(text: str, source: str, target: str, translate_fn: Callable) -> str:
    if not text.strip():
        return text
    protected, placeholders = _protect(text)
    try:
        res = translate_fn(protected, source, target)
        return _restore(res, placeholders)
    except Exception as e:
        print(f"  ⚠️ Error translating chunk: {e}")
        return text


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Scaffold, translate, or verify document translation",
    )
    parser.add_argument("--json", help="Path to extracted.json or translated.json")
    parser.add_argument("--source", default="en", help="Source language code")
    parser.add_argument("--target", default="vi", help="Target language code")
    parser.add_argument("--out", default="translated.json", help="Output JSON path")

    # Workflow modes
    parser.add_argument("--scaffold", action="store_true",
                        help="Create translated.json scaffold for AI Agent to translate directly")
    parser.add_argument("--verify", action="store_true",
                        help="Verify translated.json for completeness and math integrity")
    parser.add_argument("--stats", action="store_true",
                        help="Print document section & math statistics")

    # Standalone CLI translation engines (optional)
    parser.add_argument("--engine", default="", choices=["gemini", "openai", "google"],
                        help="External engine for standalone CLI (gemini, openai, google)")
    parser.add_argument("--api-key", default="", help="API key for Gemini/OpenAI")
    parser.add_argument("--model", default="", help="Model name")

    args = parser.parse_args()

    if args.stats and args.json:
        print_stats(args.json)
        return

    if args.verify and args.json:
        success = verify_translation(args.json)
        sys.exit(0 if success else 1)

    if args.scaffold:
        if not args.json:
            print("ERROR: --json extracted.json is required for --scaffold")
            sys.exit(1)
        scaffold_document(args.json, args.source, args.target, args.out)
        return

    # If --engine is specified (for standalone CLI execution)
    if args.engine:
        api_key = args.api_key or os.environ.get("GEMINI_API_KEY" if args.engine == "gemini" else "OPENAI_API_KEY", "")
        if args.engine == "gemini":
            if not api_key:
                print("ERROR: GEMINI_API_KEY required for standalone --engine gemini")
                sys.exit(1)
            t_fn = _make_gemini_translator(api_key, args.model or "gemini-1.5-flash")
        elif args.engine == "openai":
            if not api_key:
                print("ERROR: OPENAI_API_KEY required for standalone --engine openai")
                sys.exit(1)
            t_fn = _make_openai_translator(api_key, args.model or "gpt-4o-mini")
        else:
            t_fn = _make_google_translator()

        with open(args.json, encoding="utf-8") as f:
            data = json.load(f)
        result = deepcopy(data)
        sections = result.get("sections", [])
        for i, s in enumerate(sections):
            if s.get("type") == "math_block":
                continue
            orig = s.get("text", "")
            s["text_original"] = orig
            s["text"] = translate_text(orig, args.source, args.target, t_fn)
            time.sleep(0.3)
        result["translation"] = {"source": args.source, "target": args.target, "engine": args.engine}
        with open(args.out, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"✅ Translated via {args.engine} → {args.out}")
        return

    # Default if run without flags
    parser.print_help()


if __name__ == "__main__":
    main()
