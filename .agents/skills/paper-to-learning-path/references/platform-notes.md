# Platform-Specific Notes

This skill (`paper-to-learning-path`) is **platform-agnostic**. The Python scripts
in `scripts/` run on any platform that can execute Python 3.9+.

---

## Antigravity (AGY)

- Auto-discovered from `.agents/skills/paper-to-learning-path/` at the project root.
- Activate by mentioning "convert PDF", "translate paper", "learning path", or "explain paper" in your prompt.
- The agent reads `SKILL.md` automatically and orchestrates all 8 steps.

**Example prompts:**
```
Convert the paper at ./papers/attention.pdf to Vietnamese, full mode.
```
```
Generate a learning path for this paper: ./resplat.pdf, target language: French
```

---

## Cursor (AI IDE)

- Cursor's Composer or Agent mode supports terminal command execution.
- Ensure your venv/conda environment with dependencies is active in the Cursor terminal.
- Create a rule file at `.cursor/rules/paper-to-learning-path.mdc`:

```markdown
---
description: Convert research PDFs to translated HTML with a learning path
---

When the user asks to convert, translate, or explain a research paper PDF,
follow the 8-step workflow in:
.agents/skills/paper-to-learning-path/SKILL.md
```

---

## Claude Code (Anthropic)

- Use `/add-dir .agents/skills/paper-to-learning-path` to inject the skill into context.
- Claude Code can run all Python scripts via its bash tool.
- The `computer_use` mode can open generated HTML files in a browser for verification.

**Tip:** Add the skill path to your project's `CLAUDE.md` file for persistent context.

---

## Cline (VS Code Extension)

- Reference `SKILL.md` in the Cline system prompt configuration.
- Cline supports direct script execution — all scripts work as-is.
- Add to `.clinerules` at project root:
  ```
  When asked to convert or translate a research paper, use the skill at:
  .agents/skills/paper-to-learning-path/SKILL.md
  ```

---

## Aider

```bash
# Add skill to Aider's context at startup:
aider --read .agents/skills/paper-to-learning-path/SKILL.md

# Or add during a session:
/add .agents/skills/paper-to-learning-path/SKILL.md
```

---

## GitHub Copilot (VS Code / JetBrains)

- Add to `.github/copilot-instructions.md`:
  ```markdown
  When the user asks to convert or translate a research paper PDF, follow the workflow in:
  .agents/skills/paper-to-learning-path/SKILL.md
  ```
- Copilot does not run scripts directly; it will generate the shell commands for the user to run.

---

## Any Agent with Python Tool Access

Requirements:
1. Python 3.9+
2. `pip install pymupdf deep-translator langdetect`
3. Ability to read/write files and run shell commands

The skill will work on any such agent with zero modification.

---

## Offline / Air-gapped Environments

If CDN access (KaTeX, Google Fonts) is unavailable:

```bash
# Download KaTeX locally
npm install katex
# or
pip install katex-server  # Python wrapper
```

Update all three templates to load assets from local paths instead of CDN URLs.
Use `--offline` flag with `render_html.py` for future offline support integration.
