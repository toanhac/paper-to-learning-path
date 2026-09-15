#!/usr/bin/env python3
"""
check_deps.py — Verify that all required Python packages are installed.
Exits with code 0 if all dependencies are present, 1 otherwise.
"""
import importlib
import sys

REQUIRED = {
    "fitz": "pymupdf",
    "deep_translator": "deep-translator",
    "langdetect": "langdetect",
}

OPTIONAL = {
    "openai": "openai (optional — for GPT-4 translation engine)",
    "anthropic": "anthropic (optional — for Claude translation engine)",
    "deepl": "deepl (optional — for DeepL translation engine)",
}

print("─" * 50)
print(" Dependency Check — paper-to-learning-path v2")
print("─" * 50)

missing = []
print("\n[Required]")
for module, package in REQUIRED.items():
    if importlib.util.find_spec(module) is None:
        missing.append(package)
        print(f"  ✗  MISSING  {package}")
    else:
        # Show installed version if available
        try:
            mod = importlib.import_module(module)
            ver = getattr(mod, "__version__", "?")
        except Exception:
            ver = "?"
        print(f"  ✓  OK       {package}  ({ver})")

print("\n[Optional — for premium translation engines]")
for module, package in OPTIONAL.items():
    status = "✓" if importlib.util.find_spec(module) else "·"
    print(f"  {status}  {package}")

print()
if missing:
    print(f"❌  {len(missing)} required package(s) missing.\n")
    print("    Install with:")
    print(f"    pip install {' '.join(missing)}\n")
    sys.exit(1)

print("✅  All required dependencies are installed.\n")
sys.exit(0)
