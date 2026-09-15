<div align="center">

# 📄 paper-to-learning-path

**An AI agent skill that transforms research paper PDFs into beautifully translated HTML pages, multi-page prerequisite learning paths, and detailed repository setup guides.**

<p align="center">
  <a href="README.vi.md">🇻🇳 Tiếng Việt</a> |
  <a href="README.md">🇺🇸 English</a>
</p>

<p align="center">
  <a href="https://github.com/ToanHac/paper-to-learning-path/releases"><img src="https://img.shields.io/github/v/release/ToanHac/paper-to-learning-path?style=for-the-badge&color=5a7a55" alt="GitHub Release"></a>
  <img src="https://img.shields.io/badge/Python-3.9%2B-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.9+">
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License MIT"></a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Antigravity-Ready-4285F4?style=flat-square&logo=google&logoColor=white" alt="Antigravity">
  <img src="https://img.shields.io/badge/Claude%20Code-Plugin%20Ready-D97706?style=flat-square&logo=anthropic&logoColor=white" alt="Claude Code">
  <img src="https://img.shields.io/badge/Cursor-Rules%20Ready-000000?style=flat-square" alt="Cursor">
  <img src="https://img.shields.io/badge/Windsurf-Cascade-0284C7?style=flat-square" alt="Windsurf">
  <img src="https://img.shields.io/badge/Cline%20%2F%20Roo%20Code-10B981?style=flat-square" alt="Cline">
</p>

</div>

---

## 🌟 What It Does

When reading cutting-edge AI/ML research papers (e.g. *3D Gaussian Splatting, Diffusion Models, Transformers, NeRF*), researchers and students face two major bottlenecks:

1. **Formatting & Math Loss** — Translation tools break LaTeX formulas, destroy figures, and produce cluttered outputs.
2. **The Prerequisites Gap** — Complex papers assume deep background knowledge. Without it, reading is overwhelming.

**`paper-to-learning-path`** solves both challenges with a complete learning ecosystem:

| Output | Description |
|--------|-------------|
| 📄 `paper.html` | Self-contained translated HTML — KaTeX math, embedded images, sidebar TOC |
| 🗺️ `index.html` | Central dashboard hub — stats, quick links, learning roadmap |
| 📚 `learning/` | Multi-chapter prerequisite site — C1: Transformers, C2: Attention, … → Deep-dive |
| 🔧 `setup-guide.html` | Full repo setup guide — clone, environment, dataset, training, inference, FAQ |

---

## 🚀 Quick Install (Recommended)

### Using npm CLI

```bash
# 1. Install the CLI globally
npm install -g paper-to-learning-path-cli

# 2. Go to your project
cd /path/to/your/project

# 3. Install for your AI assistant
p2lp init --ai antigravity   # Google Antigravity
p2lp init --ai claude        # Claude Code
p2lp init --ai cursor        # Cursor IDE
p2lp init --ai windsurf      # Windsurf
p2lp init --ai cline         # Cline / Roo Code
p2lp init --ai all           # All platforms at once
```

### Python dependencies (required)

```bash
pip install pymupdf langdetect
```

> **💡 Zero API Keys Needed:** When used with an AI Agent (Claude Code, Antigravity, Cursor, Windsurf, Cline), the Agent performs the translation and content generation directly using its own intelligence — no external API keys or subscriptions required!

### Other CLI commands

```bash
p2lp init --ai claude --global   # Install globally (all projects)
p2lp init --ai cursor --dry-run  # Preview without writing files
p2lp update                      # Refresh from installed package version
p2lp uninstall --ai cursor       # Remove for a specific platform
p2lp list                        # List all supported platforms
```

### Manual install (without npm)

```bash
git clone https://github.com/ToanHac/paper-to-learning-path.git
cd paper-to-learning-path
pip install pymupdf langdetect
python scripts/install.py --all
```

---

## 🛠️ Installation by AI Assistant

### ⚡ Google Antigravity

Antigravity auto-discovers skills in `.agents/skills/<name>/SKILL.md`. No extra configuration needed — just copy the folder to your project.

**Option A — Per-project (recommended):**

```bash
# In your project root
cp -r /path/to/paper-to-learning-path/.agents/skills/paper-to-learning-path \
      .agents/skills/paper-to-learning-path
```

**Option B — Global (available in all projects):**

```bash
# macOS / Linux / WSL
cp -r .agents/skills/paper-to-learning-path \
      ~/.gemini/antigravity/skills/paper-to-learning-path

# Windows (PowerShell)
Copy-Item -Recurse .agents\skills\paper-to-learning-path `
  "$env:USERPROFILE\.gemini\antigravity\skills\paper-to-learning-path"
```

**Activation:** Just open Antigravity in your project and say:

```
Translate ./papers/attention.pdf to Vietnamese with a full learning path.
```

The skill activates automatically when you mention PDF files or research papers.

---

### 🤖 Anthropic Claude Code

Two installation methods are supported:

#### Method 1 — Claude Plugin (Marketplace)

```bash
/plugin marketplace add ToanHac/paper-to-learning-path
/plugin install paper-to-learning-path@paper-to-learning-path
```

#### Method 2 — Manual Skill Installation

```bash
# Copy skill to Claude's skill discovery path
cp -r .claude/skills/paper-to-learning-path ~/.claude/skills/paper-to-learning-path

# Or add to your project (per-project)
cp -r .claude/skills/paper-to-learning-path .claude/skills/paper-to-learning-path
```

Then add to your Claude project context:

```bash
/add-dir .claude/skills/paper-to-learning-path
```

**Activation prompt examples:**

```
Translate ./paper.pdf to Vietnamese and generate a learning path.
```

```
Convert this research paper ./resplat.pdf to French with a complete prerequisite guide.
```

> **Tip:** The `CLAUDE.md` file at the project root is automatically read by Claude Code as project context — no extra steps needed if you clone the full repo.

---

### 🖱️ Cursor IDE

The `.cursor/rules/paper-to-learning-path.mdc` file is auto-detected by Cursor Agent.

**Installation:**

```bash
# Copy rule to your project
mkdir -p .cursor/rules
cp .cursor/rules/paper-to-learning-path.mdc .cursor/rules/
```

Or copy the entire `.cursorrules` file to your project root:

```bash
cp .cursorrules /path/to/your/project/.cursorrules
```

**Full skill (with scripts):**

```bash
cp -r .agents/skills/paper-to-learning-path \
      /path/to/your/project/.agents/skills/paper-to-learning-path
```

**Activation:** Open Cursor Agent (`Ctrl+Shift+P` → "Open Composer") and type:

```
Translate ./paper.pdf to Vietnamese and generate a learning path.
```

Cursor automatically applies the rule for PDF-to-HTML translation requests.

---

### 🌊 Windsurf (Cascade)

**Installation:**

```bash
# Copy Windsurf rules to your project root
cp .windsurfrules /path/to/your/project/.windsurfrules

# Copy skill scripts
cp -r .agents/skills/paper-to-learning-path \
      /path/to/your/project/.agents/skills/paper-to-learning-path
```

**Activation:** Open Windsurf Cascade chat and type:

```
Translate ./paper.pdf to Vietnamese using the paper-to-learning-path skill.
```

---

### 🧩 Cline / Roo Code

**Installation:**

```bash
cp .clinerules /path/to/your/project/.clinerules
cp -r .agents/skills/paper-to-learning-path \
      /path/to/your/project/.agents/skills/paper-to-learning-path
```

**Activation:** In Cline / Roo Code chat:

```
Use paper-to-learning-path to translate ./paper.pdf to Vietnamese.
```

---

### ⌨️ Aider

```bash
aider --read .agents/skills/paper-to-learning-path/SKILL.md
```

Then prompt:

```
/ask Translate ./paper.pdf to Vietnamese with a learning path.
```

---

### 🖥️ Standalone CLI (No AI Required)

Run the full pipeline directly from your terminal:

```bash
# Interactive mode — asks which features and AI engine to use
python .agents/skills/paper-to-learning-path/scripts/cli.py --pdf paper.pdf

# Full pipeline with Gemini AI translation (free API key from Google AI Studio)
python .agents/skills/paper-to-learning-path/scripts/cli.py \
    --pdf paper.pdf \
    --target vi \
    --engine gemini \
    --api-key "$GEMINI_API_KEY" \
    --learning-path \
    --setup-guide

# Paper translation only
python .agents/skills/paper-to-learning-path/scripts/cli.py \
    --pdf paper.pdf --target fr \
    --engine gemini \
    --no-learning-path --no-setup-guide
```

---

## 💬 Example Prompts

Once installed in any AI assistant, just describe what you want:

```
Translate ./papers/attention.pdf to Vietnamese and generate a complete learning path
with a repo setup guide.
```

```
Convert this research paper ./resplat.pdf to French. I need the learning path
for a beginner with basic Python knowledge.
```

```
Translate ./3dgs.pdf to Chinese (zh). Paper-only mode, no learning path needed.
```

```
Generate a setup guide for the repo in ./resplat.pdf — I want to clone it, set up
the environment, and run the demo.
```

---

## 🏗️ Pipeline Architecture (12 Steps)

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
    [Step 4] translate_content   ──► AI Translate (Gemini/OpenAI; LaTeX protected)
                                │
                 ┌──────────────┴──────────────┐
                 ▼                             ▼
    [Step 5] render_html.py         [Step 6] analyze_paper.py
    ──► paper.html (Nature UI)       ──► Extract concepts + prerequisites
                                                │
                                                ▼
                                    [Step 7] generate_setup_guide.py
                                     ──► setup-guide.html (optional)
                                                │
                                                ▼
                                    [Step 8] generate_learning_path.py
                                     ──► learning/ chapters + index.html dashboard
                                                │
                                                ▼
                                    [Steps 9-11] AI Agent writes content
                                     ──► Full educational ecosystem!
```

---

## 📂 Project Structure

```
paper-to-learning-path/
├── README.md                                   # English documentation (this file)
├── README.vi.md                                # Vietnamese documentation
├── LICENSE                                     # MIT License
├── CHANGELOG.md                                # Version history
├── CLAUDE.md                                   # Claude Code project context
├── .cursorrules                                # Cursor fallback rules
├── .clinerules                                 # Cline / Roo Code rules
├── .windsurfrules                              # Windsurf Cascade rules
├── install.sh                                  # One-line installer (macOS/Linux)
├── install.ps1                                 # One-line installer (Windows)
│
├── .agents/skills/paper-to-learning-path/      ← Primary Skill Package
│   ├── SKILL.md                               # Agent instruction manifest (12 steps)
│   ├── scripts/
│   │   ├── check_deps.py                      # Dependency checker
│   │   ├── extract_pdf.py                     # PDF text/math/image extractor
│   │   ├── detect_lang.py                     # Language auto-detection
│   │   ├── translate_content.py               # Math-safe translation engine
│   │   ├── render_html.py                     # Nature-inspired HTML renderer
│   │   ├── analyze_paper.py                   # Paper concept & prereq analyzer
│   │   ├── generate_learning_path.py          # Multi-chapter site scaffolder + dashboard
│   │   ├── generate_setup_guide.py            # Repo setup guide generator
│   │   └── cli.py                             # Interactive CLI pipeline runner
│   ├── resources/
│   │   ├── nature_paper.html                  # Paper translation template
│   │   ├── nature_dashboard.html              # Central dashboard template
│   │   ├── nature_index.html                  # Roadmap index template
│   │   ├── nature_learning.html               # Learning chapter template
│   │   └── nature_setup.html                  # Setup guide template
│   └── references/
│       ├── platform-notes.md
│       ├── dependencies.md
│       ├── translation-engines.md
│       └── template-design.md
│
├── .claude/skills/paper-to-learning-path/      ← Claude Code mirror
├── .claude-plugin/                              ← Claude Plugin manifest
│   ├── plugin.json
│   └── marketplace.json
├── .cursor/rules/paper-to-learning-path.mdc    ← Cursor auto-activate rule
├── docs/how-it-works.md                        ← Technical architecture
└── examples/resplat/                           ← Live demo (ReSplat ECCV 2025)
```

---

## 🎨 Nature-Inspired Design System

All generated HTML pages share a consistent visual language:

| Token | Value | Usage |
|-------|-------|-------|
| `--moss` | `#5a7a55` | Primary accent (buttons, links) |
| `--bg` | `#f5f0e8` | Warm parchment background |
| `--surface` | `#faf7f2` | Card surfaces |
| `--lake` | `#4a7a8a` | Alternative accent |
| `--amber` | `#8a6e3a` | Setup guide accent |
| `--stone` | `#8a7e6e` | Secondary text |

- **Typography:** `Source Serif 4` for body, `Inter` for UI, `JetBrains Mono` for code
- **Transitions:** Subtle sunlight-shift effects (220ms ease)
- **Math:** KaTeX auto-render on all pages
- **Info boxes:** Note 📝 · Tip 💡 · Warning ⚠️ · Important 🔑

---

## 🤝 Contributing

Contributions from the community are warmly welcome!

1. Fork the repository
2. Create your feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'feat: Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

---

## 📦 Publishing to npm

> For maintainers only. Run these from the `cli/` directory.

```bash
# 1. Log in to npm (only needed once per machine)
npm adduser
# or if already have account:
npm login

# 2. Bundle skill files into the package
npm run sync-assets

# 3. Dry run to verify contents
npm publish --dry-run

# 4. Publish
npm publish
```

After publishing, users can install with:

```bash
npm install -g paper-to-learning-path-cli
p2lp init --ai antigravity
```

---

## 📄 License

Distributed under the [MIT License](LICENSE). Free for personal, academic, and commercial use.
