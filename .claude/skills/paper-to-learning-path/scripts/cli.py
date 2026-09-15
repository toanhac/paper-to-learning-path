#!/usr/bin/env python3
"""
cli.py — Command-line interface for the paper-to-learning-path pipeline.

Supports interactive mode (asks user which features to enable) and
full non-interactive mode via flags.

Usage:
    python scripts/cli.py --pdf paper.pdf --target vi
    python scripts/cli.py --pdf paper.pdf --target vi --learning-path --setup-guide
    python scripts/cli.py --pdf paper.pdf --target fr --no-learning-path --no-setup-guide
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
SKILL_SCRIPTS = ROOT_DIR / ".agents" / "skills" / "paper-to-learning-path" / "scripts"
SKILL_RESOURCES = ROOT_DIR / ".agents" / "skills" / "paper-to-learning-path" / "resources"


def run_cmd(cmd: list, desc: str):
    print(f"\n▶ {desc}...")
    result = subprocess.run(cmd)
    if result.returncode != 0:
        print(f"❌ Failed: {desc}")
        sys.exit(result.returncode)


def ask_yes_no(question: str, default: bool = True) -> bool:
    suffix = " [Y/n]" if default else " [y/N]"
    while True:
        answer = input(question + suffix + ": ").strip().lower()
        if answer in ("", "y", "yes"):
            return True if (answer != "" or default) else False
        if answer in ("n", "no"):
            return False
        print("  Please answer y or n.")


def interactive_questions(args) -> dict:
    """Ask pre-flight questions and merge with CLI flags. Returns settings dict."""
    print("\n" + "═" * 58)
    print("  📄 paper-to-learning-path — Pre-flight Setup")
    print("═" * 58)

    # Target language
    target_lang = args.target
    if not target_lang:
        target_lang = input("\n🌐 Ngôn ngữ dịch (ví dụ: vi, fr, de, es, zh) [vi]: ").strip() or "vi"

    # Learning path
    if args.learning_path is None:
        want_lp = ask_yes_no("\n📚 Tạo Lộ trình tự học (Learning Path + Dashboard)?", default=True)
    else:
        want_lp = args.learning_path

    # Setup guide
    if args.setup_guide is None:
        want_sg = ask_yes_no("🔧 Tạo trang Hướng dẫn Setup Repository?", default=True)
    else:
        want_sg = args.setup_guide

    # Translation engine
    engine = getattr(args, "engine", "") or ""
    api_key = getattr(args, "api_key", "") or ""
    model   = getattr(args, "model",   "") or ""

    if not engine:
        import os
        print("\n🤖 Chọn phương thức dịch:")
        print("   1) agent    — AI Agent dịch trực tiếp (Mặc định — KHÔNG cần API key)")
        print("   2) gemini   — Tự động qua Google Gemini API")
        print("   3) openai   — Tự động qua OpenAI API")
        print("   4) google   — Google Translate (dự phòng legacy)")
        choice = input("   Nhập 1/2/3/4 [1]: ").strip()
        engine_map = {"1": "agent", "2": "gemini", "3": "openai", "4": "google",
                      "agent": "agent", "gemini": "gemini", "openai": "openai", "google": "google"}
        engine = engine_map.get(choice, "agent")

    if engine in ("gemini", "openai") and not api_key:
        import os
        env_key = "GEMINI_API_KEY" if engine == "gemini" else "OPENAI_API_KEY"
        api_key = os.environ.get(env_key, "")
        if not api_key:
            api_key = input(f"\n🔑 {engine.capitalize()} API Key (hoặc nhấn Enter để dùng Agent trực tiếp): ").strip()
            if not api_key:
                engine = "agent"

    # Audience
    audience = getattr(args, "audience", "") or ""
    if not audience and want_lp:
        audience = input("\n🎓 Background của người đọc (để xác định cấp độ chương học)\n   Ví dụ: 'Sinh viên CNTT', 'ML engineer quen CNN'\n   Nhấn Enter để bỏ qua: ").strip()
        if not audience:
            audience = "Reader with basic machine learning knowledge"

    print()
    print(f"  ✓ PDF:            {args.pdf}")
    print(f"  ✓ Target lang:    {target_lang}")
    print(f"  ✓ Engine:         {engine}")
    print(f"  ✓ Learning path:  {'Yes' if want_lp else 'No'}")
    print(f"  ✓ Setup guide:    {'Yes' if want_sg else 'No'}")
    if audience:
        print(f"  ✓ Audience:       {audience}")
    print("═" * 58 + "\n")

    return {
        "target_lang": target_lang,
        "want_lp": want_lp,
        "want_sg": want_sg,
        "audience": audience or "",
        "engine": engine,
        "api_key": api_key,
        "model": model,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Convert research paper PDF to translated HTML, learning path, and setup guide"
    )
    parser.add_argument("--pdf", required=True, help="Path to input PDF file")
    parser.add_argument("--target", default="", help="Target language code (e.g. vi, fr, de, es)")
    parser.add_argument("--source", default="", help="Source language code (default: auto-detect)")
    parser.add_argument("--out-dir", default="output", help="Output directory (default: ./output)")
    parser.add_argument("--audience", default="", help="Reader background for difficulty calibration")

    # Feature flags — None means "ask interactively"
    lp_group = parser.add_mutually_exclusive_group()
    lp_group.add_argument("--learning-path", dest="learning_path", action="store_true",
                          default=None, help="Generate learning path + dashboard")
    lp_group.add_argument("--no-learning-path", dest="learning_path", action="store_false",
                          help="Skip learning path generation")

    sg_group = parser.add_mutually_exclusive_group()
    sg_group.add_argument("--setup-guide", dest="setup_guide", action="store_true",
                          default=None, help="Generate repo setup guide page")
    sg_group.add_argument("--no-setup-guide", dest="setup_guide", action="store_false",
                          help="Skip setup guide generation")

    parser.add_argument("--non-interactive", action="store_true",
                        help="Skip all interactive questions; use flag defaults")

    # Translation engine flags
    parser.add_argument("--engine", default="agent", choices=["agent", "gemini", "openai", "google"],
                        help="Translation engine: agent (default, zero API key), gemini, openai, google")
    parser.add_argument("--api-key", default="",
                        help="API key for Gemini or OpenAI (optional)")
    parser.add_argument("--model", default="",
                        help="Model override (e.g. gemini-1.5-pro, gpt-4o)")

    args = parser.parse_args()

    # Gather settings interactively or from flags
    if args.non_interactive or (args.target and args.learning_path is not None and args.setup_guide is not None):
        settings = {
            "target_lang": args.target or "vi",
            "want_lp": args.learning_path if args.learning_path is not None else True,
            "want_sg": args.setup_guide if args.setup_guide is not None else False,
            "audience": args.audience,
            "engine":  args.engine or "agent",
            "api_key": args.api_key or os.environ.get("GEMINI_API_KEY", "") or os.environ.get("OPENAI_API_KEY", ""),
            "model":   args.model or "",
        }
    else:
        settings = interactive_questions(args)

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    assets_dir = out_dir / "assets"
    extracted_json = out_dir / "extracted.json"
    translated_json = out_dir / "translated.json"
    analysis_json = out_dir / "analysis.json"
    paper_html = out_dir / "paper.html"
    setup_guide_html = out_dir / "setup-guide.html"
    learning_dir = out_dir / "learning"

    target_lang = settings["target_lang"]
    want_lp = settings["want_lp"]
    want_sg = settings["want_sg"]
    audience = settings["audience"]
    engine  = settings.get("engine", "agent")
    api_key = settings.get("api_key", "")
    model   = settings.get("model", "")

    print("=" * 58)
    print(f" 🏃 Running pipeline → {out_dir}/")
    print("=" * 58)

    # Step 1 — Check deps
    run_cmd([sys.executable, str(SKILL_SCRIPTS / "check_deps.py")], "Checking dependencies")

    # Step 2 — Extract PDF
    run_cmd([sys.executable, str(SKILL_SCRIPTS / "extract_pdf.py"),
             "--pdf", args.pdf, "--out-dir", str(assets_dir)],
            "Extracting text, math, and images from PDF")

    # Step 3 — Detect language
    source_lang = args.source
    if not source_lang:
        print("\n▶ Detecting source language...")
        res = subprocess.run([sys.executable, str(SKILL_SCRIPTS / "detect_lang.py"),
                              "--json", str(extracted_json)],
                             capture_output=True, text=True)
        for line in res.stdout.splitlines():
            if line.startswith("LANG_CODE="):
                source_lang = line.split("=")[-1].strip()
                print(f"  Detected: {source_lang}")
                break
        if not source_lang:
            source_lang = "en"

    # Step 4 — Translate
    if engine == "agent":
        if not translated_json.exists():
            run_cmd([sys.executable, str(SKILL_SCRIPTS / "translate_content.py"),
                     "--scaffold",
                     "--json", str(extracted_json),
                     "--source", source_lang, "--target", target_lang,
                     "--out", str(translated_json)],
                    "Creating translation scaffold for AI Agent (No API key needed)")
        else:
            print("\n▶ Found existing translated.json → using it.")
    else:
        translate_cmd = [sys.executable, str(SKILL_SCRIPTS / "translate_content.py"),
                         "--json", str(extracted_json),
                         "--source", source_lang, "--target", target_lang,
                         "--out", str(translated_json),
                         "--engine", engine]
        if api_key:
            translate_cmd += ["--api-key", api_key]
        if model:
            translate_cmd += ["--model", model]
        run_cmd(translate_cmd, f"Translating with {engine} ({source_lang} → {target_lang})")

    # Step 5 — Render paper HTML
    run_cmd([sys.executable, str(SKILL_SCRIPTS / "render_html.py"),
             "--json", str(translated_json),
             "--template", str(SKILL_RESOURCES / "nature_paper.html"),
             "--out", str(paper_html)],
            "Rendering paper HTML")

    # Steps 6+ — Learning path & setup guide
    if want_lp or want_sg:

        # Step 6 — Analyze
        analyze_cmd = [sys.executable, str(SKILL_SCRIPTS / "analyze_paper.py"),
                       "--json", str(translated_json),
                       "--out", str(analysis_json)]
        if audience:
            analyze_cmd += ["--audience", audience]
        run_cmd(analyze_cmd, "Analyzing paper concepts and prerequisites")

    if want_sg:
        # Step 7 — Setup guide
        run_cmd([sys.executable, str(SKILL_SCRIPTS / "generate_setup_guide.py"),
                 "--translated", str(translated_json),
                 "--analysis", str(analysis_json),
                 "--out", str(setup_guide_html),
                 "--target-lang", target_lang],
                "Generating repo setup guide")
        print(f"   ⚠️  Remember to fill <!-- AGENT: ... --> placeholders in setup-guide.html!")

    if want_lp:
        # Step 8 — Learning path + dashboard
        lp_cmd = [sys.executable, str(SKILL_SCRIPTS / "generate_learning_path.py"),
                  "--analysis", str(analysis_json),
                  "--paper-html", str(paper_html),
                  "--out-dir", str(learning_dir),
                  "--dashboard"]
        if want_sg:
            lp_cmd += ["--setup-guide", str(setup_guide_html)]
        run_cmd(lp_cmd, "Generating learning path and dashboard")

    # Summary
    print("\n" + "=" * 58)
    print("🎉 Pipeline completed!")
    print(f"\nOutput files in: {out_dir}/")
    if want_lp:
        print(f"  🗺️  Dashboard:   {out_dir}/index.html   ← Open this!")
    print(f"  📄  Paper HTML:  {out_dir}/paper.html")
    if want_sg:
        print(f"  🔧  Setup Guide: {out_dir}/setup-guide.html")
    if want_lp:
        print(f"  📚  Chapters:    {out_dir}/learning/")
    if want_lp or want_sg:
        print("\n📝 Next: Fill in <!-- AGENT: ... --> placeholders in chapter/setup files.")
    print("=" * 58 + "\n")


if __name__ == "__main__":
    main()
