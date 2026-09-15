#!/usr/bin/env bash
# ==============================================================================
#  paper-to-learning-path — One-Line Bash Installer (macOS & Linux)
# ==============================================================================
set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}╔══════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  📄  paper-to-learning-path — Skill Installer (Bash)            ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: python3 is not installed. Please install Python 3.9+ first.${NC}"
    exit 1
fi

echo -e "${BLUE}==>${NC} Installing required Python packages..."
python3 -m pip install --quiet --upgrade pymupdf deep-translator langdetect

# Find script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
SKILL_SRC="$SCRIPT_DIR/.agents/skills/paper-to-learning-path"

# Global install paths
ANTIGRAVITY_SKILLS="$HOME/.gemini/antigravity/skills/paper-to-learning-path"
CLAUDE_SKILLS="$HOME/.claude/skills/paper-to-learning-path"
CURSOR_RULES="$HOME/.cursor/rules/paper-to-learning-path.mdc"

echo ""
echo -e "${BLUE}==>${NC} Installing skill to AI Agent directories..."

# 1. Antigravity Global
if [ -d "$HOME/.gemini" ]; then
    mkdir -p "$(dirname "$ANTIGRAVITY_SKILLS")"
    rm -rf "$ANTIGRAVITY_SKILLS"
    cp -r "$SKILL_SRC" "$ANTIGRAVITY_SKILLS"
    echo -e "  ${GREEN}✓${NC} Antigravity skill installed: $ANTIGRAVITY_SKILLS"
fi

# 2. Claude Code Global
mkdir -p "$(dirname "$CLAUDE_SKILLS")"
rm -rf "$CLAUDE_SKILLS"
cp -r "$SKILL_SRC" "$CLAUDE_SKILLS"
echo -e "  ${GREEN}✓${NC} Claude Code skill installed: $CLAUDE_SKILLS"

# 3. Cursor Global
if [ -f "$SCRIPT_DIR/.cursor/rules/paper-to-learning-path.mdc" ]; then
    mkdir -p "$(dirname "$CURSOR_RULES")"
    cp "$SCRIPT_DIR/.cursor/rules/paper-to-learning-path.mdc" "$CURSOR_RULES"
    echo -e "  ${GREEN}✓${NC} Cursor rule installed: $CURSOR_RULES"
fi

echo ""
echo -e "${GREEN}🎉 Installation complete!${NC}"
echo "You can now prompt your AI agent (Antigravity, Claude Code, Cursor, Cline):"
echo -e "  ${YELLOW}\"Convert paper.pdf to Vietnamese with a complete learning path\"${NC}"
echo ""
