# CLAUDE.md — Claude Code Project Instructions

This project provides the `paper-to-learning-path` skill, which turns academic research PDFs into beautifully formatted, translated HTML pages and comprehensive prerequisite learning paths.

## Key Workflow
Follow `.claude/skills/paper-to-learning-path/SKILL.md` when processing papers:
1. `check_deps.py`: Verify PyMuPDF, deep-translator, langdetect.
2. `extract_pdf.py`: Extract text blocks, mathematical formulas, and embedded images.
3. `detect_lang.py`: Auto-detect source language.
4. `translate_content.py`: Translate prose while protecting LaTeX tokens with placeholders.
5. `render_html.py`: Generate single self-contained paper HTML with KaTeX & base64 images.
6. `analyze_paper.py`: Map paper concepts to prerequisite domains.
7. `generate_learning_path.py`: Generate scaffolding for roadmap index & chapter pages.
8. Fill in `<!-- AGENT: ... -->` placeholders with educational content, intuition, and formulas.

## Architecture & Code Standards
- Python 3.9+ pure standard library + pymupdf + deep-translator + langdetect
- Nature-inspired design tokens (`--moss`, `--stone`, `--lake`, `--bg: #f5f0e8`)
- Fully self-contained outputs (openable directly in browser with no backend)
