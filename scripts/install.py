#!/usr/bin/env python3
"""
install.py — Multi-platform installer for paper-to-learning-path skill.

Installs dependencies and installs the skill into your preferred AI agent environment:
- Antigravity (Google DeepMind)
- Claude Code / Claude Desktop (Anthropic)
- Cursor IDE
- Windsurf (Codeium)
- Cline / Roo Code (VS Code)
- Universal Workspace (current folder)

Usage:
    python scripts/install.py                        # Interactive menu
    python scripts/install.py --all                  # Install to all detected agents
    python scripts/install.py --platform antigravity # Specific platform
    python scripts/install.py --global               # Install to user home directory
"""

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

SKILL_NAME = "paper-to-learning-path"
ROOT_DIR = Path(__file__).resolve().parent.parent
SKILL_SOURCE = ROOT_DIR / ".agents" / "skills" / SKILL_NAME
HOME = Path.home()

# Destination paths
DESTINATIONS = {
    "antigravity_global": HOME / ".gemini" / "antigravity" / "skills" / SKILL_NAME,
    "antigravity_local": ROOT_DIR / ".agents" / "skills" / SKILL_NAME,
    "claude_global": HOME / ".claude" / "skills" / SKILL_NAME,
    "claude_local": ROOT_DIR / ".claude" / "skills" / SKILL_NAME,
    "cursor_global": HOME / ".cursor" / "rules" / f"{SKILL_NAME}.mdc",
    "cursor_local": ROOT_DIR / ".cursor" / "rules" / f"{SKILL_NAME}.mdc",
}

DEPENDENCIES = ["pymupdf", "deep-translator", "langdetect"]


def print_banner():
    print("""
\033[32m╔══════════════════════════════════════════════════════════════════╗
║  📄  paper-to-learning-path — Multi-Agent Skill Installer        ║
╚══════════════════════════════════════════════════════════════════╝\033[0m
""")


def install_python_deps():
    print("📦 Installing Python dependencies...")
    cmd = [sys.executable, "-m", "pip", "install", *DEPENDENCIES]
    try:
        subprocess.check_call(cmd)
        print("  \033[32m✓\033[0m Dependencies installed successfully.\n")
        return True
    except subprocess.CalledProcessError as e:
        print(f"  \033[31m✗\033[0m Failed to install dependencies: {e}")
        return False


def copy_skill(dest: Path, is_file: bool = False, file_source: Path = None):
    try:
        if is_file:
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(file_source, dest)
            print(f"  \033[32m✓\033[0m Copied rule to: {dest}")
        else:
            dest.parent.mkdir(parents=True, exist_ok=True)
            if dest.exists():
                shutil.rmtree(dest)
            shutil.copytree(SKILL_SOURCE, dest)
            print(f"  \033[32m✓\033[0m Installed skill to: {dest}")
        return True
    except Exception as e:
        print(f"  \033[31m✗\033[0m Failed to install to {dest}: {e}")
        return False


def install_for_platform(platform: str, is_global: bool = False):
    print(f"⚙️  Setting up for {platform.upper()} ({'global' if is_global else 'workspace'})...")
    cursor_rule_src = ROOT_DIR / ".cursor" / "rules" / f"{SKILL_NAME}.mdc"

    if platform in ("antigravity", "all"):
        dest = DESTINATIONS["antigravity_global"] if is_global else DESTINATIONS["antigravity_local"]
        copy_skill(dest)

    if platform in ("claude", "all"):
        dest = DESTINATIONS["claude_global"] if is_global else DESTINATIONS["claude_local"]
        copy_skill(dest)

    if platform in ("cursor", "all"):
        dest = DESTINATIONS["cursor_global"] if is_global else DESTINATIONS["cursor_local"]
        if cursor_rule_src.exists():
            copy_skill(dest, is_file=True, file_source=cursor_rule_src)

    if platform in ("windsurf", "cline", "all") and not is_global:
        print("  \033[32m✓\033[0m Local .windsurfrules and .clinerules are already configured.")


def interactive_menu():
    print("Select an installation option:")
    print("  1) Install for all AI Agents (Global - user home directory)")
    print("  2) Install for Antigravity (Google DeepMind)")
    print("  3) Install for Claude Code / Claude Desktop")
    print("  4) Install for Cursor IDE")
    print("  5) Setup current workspace only (Local)")
    print("  6) Install Python dependencies only")
    print("  0) Exit")

    choice = input("\nEnter choice [1-6] (default: 1): ").strip() or "1"

    if choice == "1":
        install_python_deps()
        install_for_platform("all", is_global=True)
    elif choice == "2":
        install_python_deps()
        install_for_platform("antigravity", is_global=True)
    elif choice == "3":
        install_python_deps()
        install_for_platform("claude", is_global=True)
    elif choice == "4":
        install_python_deps()
        install_for_platform("cursor", is_global=True)
    elif choice == "5":
        install_python_deps()
        install_for_platform("all", is_global=False)
    elif choice == "6":
        install_python_deps()
    else:
        print("Exiting.")
        sys.exit(0)

    print("\n\033[32m🎉 Setup completed!\033[0m You can now use the skill in your AI agent.\n")


def main():
    parser = argparse.ArgumentParser(description="Install paper-to-learning-path skill")
    parser.add_argument("--all", action="store_true", help="Install to all supported platforms")
    parser.add_argument("--platform", choices=["antigravity", "claude", "cursor", "windsurf", "cline", "all"],
                        help="Specific platform to install for")
    parser.add_argument("--global", dest="is_global", action="store_true", help="Install globally in user home")
    parser.add_argument("--skip-deps", action="store_true", help="Skip pip dependency installation")
    args = parser.parse_args()

    print_banner()

    if not args.all and not args.platform:
        interactive_menu()
        return

    if not args.skip_deps:
        install_python_deps()

    platform = args.platform or "all"
    install_for_platform(platform, is_global=args.is_global)
    print("\n\033[32m🎉 Installation completed successfully!\033[0m\n")


if __name__ == "__main__":
    main()
