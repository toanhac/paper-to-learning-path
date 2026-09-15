#!/usr/bin/env python3
"""
check_deps.py — Verify that all required Python packages are installed.
Exits with code 0 if all core dependencies are present, 1 otherwise.
"""
import importlib
import sys

# Core dependencies required for PDF extraction and processing
REQUIRED = {
    "fitz":       "pymupdf",
    "langdetect": "langdetect",
}

# Optional packages only needed if using standalone CLI without an AI agent
OPTIONAL_CLI = {
    "google.generativeai": ("google-generativeai", "Gemini (standalone CLI only)"),
    "openai":              ("openai",               "OpenAI (standalone CLI only)"),
    "deep_translator":     ("deep-translator",      "Google Translate (legacy fallback)"),
}

print("─" * 55)
print(" Dependency Check — paper-to-learning-path")
print("─" * 55)

missing_required = []
print("\n[Required — Core Pipeline]")
for module, package in REQUIRED.items():
    if importlib.util.find_spec(module) is None:
        missing_required.append(package)
        print(f"  ✗  MISSING  {package}")
    else:
        try:
            mod = importlib.import_module(module)
            ver = getattr(mod, "__version__", "?")
        except Exception:
            ver = "?"
        print(f"  ✓  OK       {package}  ({ver})")

print("\n[Optional — Standalone CLI without Agent]")
for module, (package, label) in OPTIONAL_CLI.items():
    status = "✓" if importlib.util.find_spec(module.split(".")[0]) is not None else "·"
    print(f"  {status}  {package:22s}  — {label}")

print()

if missing_required:
    print(f"❌  {len(missing_required)} required package(s) missing.\n")
    print("    Install with:")
    print("    pip install " + " ".join(missing_required))
    print()
    sys.exit(1)

print("✅  Core dependencies ready.")
print("💡  When running via an AI Agent (Claude, Antigravity, Cursor, Windsurf),")
print("    translation is performed directly by the agent — NO API keys required!\n")
sys.exit(0)
