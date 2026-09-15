<div align="center">

# 📄 paper-to-learning-path

**An AI agent skill that transforms academic research PDFs into beautifully translated, nature-inspired HTML pages and automatically generates multi-page prerequisite learning paths.**

<p align="center">
  <a href="README.vi.md">🇻🇳 Tiếng Việt</a> |
  <a href="README.md">🇺🇸 English</a>
</p>

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python: 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue.svg?logo=python&logoColor=white)](https://python.org)
[![Platform: Antigravity](https://img.shields.io/badge/Antigravity-Ready-4285F4?logo=google&logoColor=white)](https://antigravity.dev)
[![Platform: Claude Code](https://img.shields.io/badge/Claude%20Code-Plugin%20%26%20Skill-D97706?logo=anthropic&logoColor=white)](https://claude.ai)
[![Platform: Cursor](https://img.shields.io/badge/Cursor-Rules%20%26%20Agent-000000?logo=cursor&logoColor=white)](https://cursor.sh)
[![Platform: Windsurf](https://img.shields.io/badge/Windsurf-Cascade-0284C7)](https://codeium.com/windsurf)
[![Platform: Cline](https://img.shields.io/badge/Cline-Roo%20Code-10B981)](https://github.com/cline/cline)

</div>

---

## 🌟 Overview

When reading cutting-edge scientific research papers (e.g. *3D Gaussian Splatting, Diffusion Models, State Space Models*), researchers and students encounter two major bottlenecks:
1. **Formatting & Math Loss:** Traditional translation tools break LaTeX math formulas ($\LaTeX$), destroy diagrams, and produce cluttered files.
2. **The Prerequisite Knowledge Gap:** Complex papers assume deep prior knowledge. Without understanding the foundational concepts, reading the paper is overwhelming.

**`paper-to-learning-path`** solves both challenges seamlessly:
- **Zero Math Corruption:** All LaTeX equations and citation markers are protected with placeholder tokens during translation and rendered beautifully via KaTeX.
- **Embedded Visuals:** PDF figures and charts are automatically extracted as high-res PNGs and embedded as Base64 data inside a single self-contained HTML file.
- **Nature-Inspired UI:** Calming earth & foliage color palette, reading progress bar, responsive sidebar TOC, and academic typography.
- **Automatic Prerequisite Learning Path:** The AI analyzes the paper's concepts, determines prerequisite topics, and scaffolds an interactive multi-chapter learning website (roadmap index + prerequisite modules + paper deep dive).

---

## 🚀 One-Line Quick Install

### macOS / Linux / WSL
```bash
curl -fsSL https://raw.githubusercontent.com/ToanHac/paper-to-learning-path/main/install.sh | bash
```

### Windows (PowerShell)
```powershell
irm https://raw.githubusercontent.com/ToanHac/paper-to-learning-path/main/install.ps1 | iex
```

### Python Manual Setup
```bash
git clone https://github.com/ToanHac/paper-to-learning-path.git
cd paper-to-learning-path
pip install pymupdf deep-translator langdetect
python scripts/install.py --all
```

---

## 🛠️ Multi-Platform Installation Guide

| Platform | Setup & Activation |
| :--- | :--- |
| **Google Antigravity** | Clone into workspace `.agents/skills/paper-to-learning-path` or global `~/.gemini/antigravity/skills/`. The agent auto-activates when research PDFs are discussed. |
| **Anthropic Claude Code** | Included via `.claude-plugin/plugin.json` and `.claude/skills/paper-to-learning-path/`. Use `/add-dir .agents/skills/paper-to-learning-path` if adding manually. |
| **Cursor IDE** | Configured via `.cursor/rules/paper-to-learning-path.mdc` and `.cursorrules`. Cursor Agent detects PDF conversion prompts automatically. |
| **Windsurf (Cascade)** | Pre-configured via `.windsurfrules`. Prompt Cascade in chat to process any PDF. |
| **Cline / Roo Code** | Configured via `.clinerules`. Invoke translation or learning path generation in chat. |
| **Aider** | Run: `aider --read .agents/skills/paper-to-learning-path/SKILL.md` |
| **Standalone CLI (No AI chat)** | Run directly in terminal: `python scripts/cli.py --pdf paper.pdf --target vi` |

---

## 💬 Example AI Agent Prompts

Once installed, simply prompt your favorite AI coding assistant:

```text
Translate ./papers/2510.08575v3.pdf to Vietnamese and generate a comprehensive learning path for it.
```

```text
Convert this research paper ./attention.pdf to Vietnamese HTML with a step-by-step learning guide.
```

```text
Translate ./paper.pdf to French (mode: paper-only).
```

---

## 🏗️ 8-Step Pipeline Architecture

```
                       [ Input: PDF File ]
                                │
                                ▼
    [Step 1] check_deps.py       ──► Validate Python dependencies
                                │
                                ▼
    [Step 2] extract_pdf.py      ──► Extract Text + LaTeX Math + PNG Images
                                │
                                ▼
    [Step 3] detect_lang.py      ──► Auto-detect source language
                                │
                                ▼
    [Step 4] translate_content   ──► Translate with LaTeX placeholder protection
                                │
                 ┌──────────────┴──────────────┐
                 ▼                             ▼
    [Step 5] render_html.py         [Step 6] analyze_paper.py
    ──► Self-contained paper.html    ──► Extract concepts & Prerequisites
        (Nature UI, KaTeX math)                │
                                               ▼
                                    [Step 7] generate_learning_path.py
                                     ──► Scaffold Index & Chapter HTML files
                                               │
                                               ▼
                                    [Step 8] AI Agent writes Chapter Content
                                     ──► Full Multi-Page Educational Site!
```

---

## 📂 Project Structure

```
paper-to-learning-path/
├── README.md                                   # English documentation
├── README.vi.md                                # Vietnamese documentation
├── LICENSE                                     # MIT License
├── CHANGELOG.md                                # Version history
├── pyproject.toml                              # Python package configuration
├── install.sh                                  # One-line installer for Linux/macOS
├── install.ps1                                 # One-line installer for Windows
├── .gitignore
│
├── .agents/skills/paper-to-learning-path/      # Primary Skill package
│   ├── SKILL.md                               # Agent instruction manifest (8 steps)
│   ├── scripts/
│   │   ├── check_deps.py                      # Dependency checker
│   │   ├── extract_pdf.py                     # PDF text/math/image extractor
│   │   ├── detect_lang.py                     # Language detection
│   │   ├── translate_content.py               # Math-safe translation engine
│   │   ├── render_html.py                     # Nature HTML renderer
│   │   ├── analyze_paper.py                   # Paper prerequisite analyzer
│   │   ├── generate_learning_path.py          # Learning site scaffolder
│   │   └── cli.py                             # Standalone CLI runner
│   ├── resources/
│   │   ├── nature_paper.html                  # Paper translation template
│   │   ├── nature_index.html                  # Roadmap index template
│   │   └── nature_learning.html               # Learning chapter template
│   └── references/                            # Documentation references
│
├── .claude-plugin/                             # Claude Marketplace integration
│   ├── plugin.json
│   └── marketplace.json
├── .cursor/rules/                              # Cursor IDE rules
│   └── paper-to-learning-path.mdc
├── .clinerules                                 # Cline / Roo Code rules
├── .windsurfrules                              # Windsurf Cascade rules
├── CLAUDE.md                                   # Claude Code instructions
├── examples/resplat/                           # Live example (ReSplat ECCV 2025 demo)
└── docs/how-it-works.md                        # In-depth technical architecture
```

---

## 🎨 Nature-Inspired Visual Philosophy

- **Organic Color System:** Deep moss green (`#5a7a55`), Warm sand (`#ede8df`), Natural stone (`#8a7e6e`), Lake blue (`#4a7a8a`), Warm parchment background (`#f5f0e8`).
- **Academic Typography:** High-readability Serif typography paired with crisp Sans-serif labels and JetBrains Mono for equations and code blocks.
- **Micro-Interactions:** Subtle sunlight shift transitions (220ms), fixed reading progress bar, floating sidebar TOC with intersection observer tracking.
- **Educational Callout Boxes:** Standardized Note, Tip, Warning, and Important info cards.

---

## 🤝 Contributing

Contributions from the community are warmly welcome!
1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

Distributed under the [MIT License](LICENSE). Free for personal, academic, and commercial use.
