#!/usr/bin/env python3
"""
cli.py — Command-line interface for paper-to-learning-path pipeline.

Allows running the full pipeline directly from the terminal.

Usage:
    python scripts/cli.py --pdf paper.pdf --target vi
    python scripts/cli.py --pdf paper.pdf --target vi --mode paper-only
    python scripts/cli.py --pdf paper.pdf --target fr --audience "Robotics PhD student"
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = ROOT_DIR / ".agents" / "skills" / "paper-to-learning-path" / "scripts"
RESOURCES_DIR = ROOT_DIR / ".agents" / "skills" / "paper-to-learning-path" / "resources"


def run_cmd(cmd: list[str], desc: str):
    print(f"\n▶ {desc}...")
    result = subprocess.run(cmd)
    if result.returncode != 0:
        print(f"❌ Failed: {desc}")
        sys.exit(result.returncode)


def main():
    parser = argparse.ArgumentParser(
        description="Convert research paper PDF to translated HTML and generate prerequisite learning path"
    )
    parser.add_argument("--pdf", required=True, help="Path to input PDF file")
    parser.add_argument("--target", required=True, help="Target language code (e.g. vi, fr, de, es, zh)")
    parser.add_argument("--source", default="", help="Source language code (default: auto-detect)")
    parser.add_argument("--out-dir", default="output", help="Output directory (default: ./output)")
    parser.add_argument("--mode", choices=["full", "paper-only"], default="full",
                        help="'full' = paper + learning path, 'paper-only' = translation only")
    parser.add_argument("--audience", default="Reader familiar with basic machine learning",
                        help="Target audience background description")
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    assets_dir = out_dir / "assets"
    extracted_json = out_dir / "extracted.json"
    translated_json = out_dir / "translated.json"
    analysis_json = out_dir / "analysis.json"
    paper_html = out_dir / "paper.html"
    learning_dir = out_dir / "learning"

    print("=" * 60)
    print(" 📄 paper-to-learning-path Pipeline")
    print(f" PDF:    {args.pdf}")
    print(f" Target: {args.target}")
    print(f" Mode:   {args.mode}")
    print(f" Output: {out_dir}/")
    print("=" * 60)

    # 1. Check dependencies
    run_cmd([sys.executable, str(SCRIPTS_DIR / "check_deps.py")], "Checking dependencies")

    # 2. Extract PDF
    run_cmd([sys.executable, str(SCRIPTS_DIR / "extract_pdf.py"), "--pdf", args.pdf, "--out-dir", str(assets_dir)],
            "Extracting text, formulas, and images from PDF")

    # 3. Detect language if not specified
    source_lang = args.source
    if not source_lang:
        print("\n▶ Detecting source language...")
        res = subprocess.run([sys.executable, str(SCRIPTS_DIR / "detect_lang.py"), "--json", str(extracted_json)],
                             capture_output=True, text=True)
        for line in res.stdout.splitlines():
            if line.startswith("LANG_CODE="):
                source_lang = line.split("=")[-1].strip()
                print(f"  Detected source language: {source_lang}")
                break
        if not source_lang:
            source_lang = "en"
            print("  Defaulting source language to 'en'")

    # 4. Translate content
    run_cmd([sys.executable, str(SCRIPTS_DIR / "translate_content.py"),
             "--json", str(extracted_json),
             "--source", source_lang,
             "--target", args.target,
             "--out", str(translated_json)],
            f"Translating content ({source_lang} → {args.target})")

    # 5. Render paper HTML
    run_cmd([sys.executable, str(SCRIPTS_DIR / "render_html.py"),
             "--json", str(translated_json),
             "--template", str(RESOURCES_DIR / "nature_paper.html"),
             "--out", str(paper_html)],
            "Rendering nature-inspired paper HTML")

    # 6 & 7. Learning path if full mode
    if args.mode == "full":
        run_cmd([sys.executable, str(SCRIPTS_DIR / "analyze_paper.py"),
                 "--json", str(translated_json),
                 "--audience", args.audience,
                 "--out", str(analysis_json)],
                "Analyzing paper & determining prerequisite curriculum")

        run_cmd([sys.executable, str(SCRIPTS_DIR / "generate_learning_path.py"),
                 "--analysis", str(analysis_json),
                 "--paper-html", str(paper_html),
                 "--out-dir", str(learning_dir)],
                "Generating learning path scaffolding")

    print("\n" + "=" * 60)
    print("🎉 Pipeline completed successfully!")
    print(f"📄 Translated Paper:  {paper_html}")
    if args.mode == "full":
        print(f"📚 Learning Path:     {learning_dir / 'index.html'}")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
