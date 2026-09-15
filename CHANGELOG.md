# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [2.1.0] — 2026-09-15

### Added
- **Central Dashboard `index.html`** — Hub page linking all outputs (paper, chapters, setup guide) with stats grid, quick-action cards, and learning roadmap
  - New template: `resources/nature_dashboard.html`
  - New function: `_build_dashboard()` in `generate_learning_path.py`
- **Repo Setup Guide page** (`setup-guide.html`) — Full 7-step guide: Clone → Environment → Dependencies → Dataset → Training → Inference → FAQ & Troubleshooting
  - New script: `scripts/generate_setup_guide.py` with heuristic GitHub URL, requirements, and dataset detection
  - New template: `resources/nature_setup.html` with copy-to-clipboard code blocks, collapsible FAQ, and reading progress bar
- **Interactive CLI pre-flight questions** — Agent asks user which features to enable before running
  - New flags: `--learning-path` / `--no-learning-path`, `--setup-guide` / `--no-setup-guide`, `--non-interactive`
- **SKILL.md** updated with Pre-Flight Q&A section, Steps 9–12, updated output structure

### Changed
- `generate_learning_path.py` — New `--dashboard` and `--setup-guide` flags; chapters now in `learning/` subdirectory relative to dashboard
- `resources/nature_paper.html` — Nav now links to both Dashboard and Learning Path
- `resources/nature_learning.html` — Chapter nav home button now links back to `../index.html` (dashboard)
- Output structure: `index.html` (dashboard) + `paper.html` + `setup-guide.html` + `learning/` (chapters)

---

## [2.0.0] — 2026-08-28

### Added
- **Learning path generation** — AI-driven multi-page prerequisite learning site
  - `scripts/analyze_paper.py` — extracts key concepts, identifies prerequisites, estimates difficulty
  - `scripts/generate_learning_path.py` — produces a full multi-page HTML learning site
  - `resources/nature_index.html` — roadmap landing page template
  - `resources/nature_learning.html` — chapter/module page template with prev/next nav
- **Upgraded paper template** (`resources/nature_paper.html`)
  - Fixed top navigation bar with chapter links
  - Reading progress bar
  - Info boxes (note / tip / warning / important)
  - Improved mobile responsive layout
  - Dark mode support via `prefers-color-scheme`
- **Professional project structure** suitable for GitHub publishing
  - `README.md` with badges, quick start, feature table
  - `LICENSE` (MIT)
  - `pyproject.toml` for optional pip install
  - `examples/resplat/` — live demo generated from arxiv paper `2510.08575v3.pdf`
  - `docs/how-it-works.md` — architecture overview
- **Platform notes** updated to cover Cline and Aider configuration

### Changed
- Skill renamed from `pdf-to-html-translator` → `paper-to-learning-path`
- Project reorganized from `.agents/skills/pdf-to-html-translator/` to root-level GitHub layout
- `check_deps.py` now validates all v2 dependencies

### Fixed
- Math placeholder restoration edge case with nested `$` delimiters
- Image extraction fallback for non-standard PDF image formats

---

## [1.0.0] — 2026-08-27

### Added
- Initial release: PDF extraction, language detection, translation, HTML rendering
- Nature-inspired HTML template with KaTeX math support
- Base64 image embedding for self-contained output
- Platform-agnostic skill structure for Antigravity, Cursor, Claude Code
