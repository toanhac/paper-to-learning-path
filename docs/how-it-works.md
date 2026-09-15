# How It Works — Architecture Guide

## Overview

`paper-to-learning-path` is an 8-step pipeline. Each step is an independent Python
script that can be run standalone or orchestrated by an AI agent.

```
PDF File
   │
   ▼
[Step 1] check_deps.py         → validates environment
   │
   ▼
[Step 2] extract_pdf.py        → extracted.json + assets/img_NNN.png
   │
   ▼
[Step 3] detect_lang.py        → source language code + confidence
   │
   ▼
[Step 4] translate_content.py  → translated.json
   │                              (math/citations protected with placeholders)
   ├──────────────────────────────────────────────────────┐
   ▼                                                      ▼
[Step 5] render_html.py        → paper.html          [Step 6] analyze_paper.py
         (self-contained,             │                       → analysis.json
          nature-inspired,            │                         (prerequisites,
          KaTeX math,                 │                          difficulty,
          base64 images)              │                          glossary,
                                      │                          chapter outline)
                                      │                              │
                                      │                              ▼
                                      │                    [Step 7] generate_learning_path.py
                                      │                             → learning/index.html
                                      │                             → learning/01-*.html
                                      │                             → learning/0N-deep-dive.html
                                      │                             (scaffolding only)
                                      │
                                      │                    [Step 8] Agent fills chapter content
                                      │                             (uses its own knowledge +
                                      │                              analysis.json as context)
                                      ▼
                               FINAL OUTPUT:
                               paper.html            ← translated paper
                               learning/             ← learning path site
```

---

## Script Responsibilities

### `extract_pdf.py`

Uses **PyMuPDF** (`fitz`) to:
- Parse text blocks in reading order (`get_text("blocks", sort=True)`)
- Classify each block: `heading`, `paragraph`, `math_block`, `caption`, `list`
- Math heuristics: symbol density ratio + regex patterns for LaTeX commands
- Extract embedded images as PNG files
- Attach captions to images by page proximity

Output: `extracted.json` (schema in SKILL.md) + `assets/img_NNN.png`

### `detect_lang.py`

Uses **langdetect** on a sample of paragraph/heading text (skips math blocks, which are language-neutral). Reports confidence; warns if < 85%.

### `translate_content.py`

Uses **deep-translator** (Google Translate by default) with:
- **Placeholder protection**: replaces `$…$`, `\[…\]`, `[citation]` with `__MATH_0001__` tokens before translation; restores after
- **Chunked translation**: splits text at sentence boundaries to stay under the 4500-char API limit
- **Terminology glossary**: registers multi-word technical terms from the first 80 chars of each block and applies consistent translations throughout
- **Never translates** `math_block` type sections

### `analyze_paper.py`

Reads `translated.json` and produces `analysis.json` via two strategies:
1. **Heuristic pass**: extracts terms from the glossary, identifies cited works, counts unique concepts
2. **Agent prompt generation**: outputs a structured prompt for the agent to fill in the prerequisites and chapter outline using its own knowledge

This is the key to **Option A** (agent-driven): the script does the mechanical work; the agent provides the educational intelligence.

### `generate_learning_path.py`

Reads `analysis.json` and produces the multi-page learning site:
- `learning/index.html` — roadmap landing with stats grid, prerequisite box, roadmap timeline
- `learning/01-<topic>.html` through `learning/0N-<topic>.html` — one chapter per prerequisite (scaffolded)
- `learning/final-deep-dive.html` — paper walkthrough chapter (scaffolded)

Scaffolded chapters contain:
- Correct HTML structure, nav, metadata
- Section headings from `analysis.json`
- `<!-- AGENT: write content here -->` comment blocks where the agent fills in educational prose
- Placeholder info boxes, math blocks, and diagrams that the agent replaces

### `render_html.py`

Template engine that replaces `{{PLACEHOLDER}}` tokens in any of the three templates with content from JSON data. Handles:
- HTML escaping with math protection
- Base64 image embedding
- KaTeX delimiter normalization
- Table of contents generation

---

## Template System

Three nature-inspired HTML templates, all sharing the same CSS design tokens:

| Template | Purpose | Key Elements |
|----------|---------|--------------|
| `nature_paper.html` | Full translated paper | Reading progress bar, sticky TOC sidebar, info boxes |
| `nature_index.html` | Learning path roadmap | Stats grid, roadmap timeline, prerequisite box, phase labels |
| `nature_learning.html` | Per-chapter module | Top nav with chapter links, chapter progress badge, info boxes, prev/next footer nav |

### Design tokens (shared across all templates)

```css
--color-moss:        #5a7a55   /* primary accent */
--color-stone:       #8a7e6e   /* secondary text */
--color-lake:        #4a7a8a   /* alternative accent */
--color-bg:          #f5f0e8   /* warm parchment background */
--color-surface:     #faf7f2   /* card surfaces */
--transition:        220ms ease
```

---

## Learning Path Generation — Option A (Agent-Driven)

The agent-driven approach works as follows:

1. `analyze_paper.py` produces `analysis.json` with prerequisite topics and chapter outlines
2. `generate_learning_path.py` generates scaffolded HTML with `<!-- AGENT: ... -->` placeholders
3. **The agent reads these files** and fills in the educational content for each chapter using its own knowledge, guided by:
   - The paper's glossary (for consistent terminology)
   - The target audience description in `analysis.json`
   - The chapter outline (section titles, key concepts, suggested depth)
4. The agent saves the filled-in HTML back to the chapter files

This approach is **platform-agnostic**: any LLM-backed agent (Antigravity, Claude Code, Cursor, Cline) can fill in the content without needing a separate API key.

---

## JSON Schema Reference

### `extracted.json`
```jsonc
{
  "metadata": { "title": "...", "authors": "...", "pages": 12 },
  "sections": [
    { "type": "heading|paragraph|math_block|caption|list", "text": "...", "page": 3, "bbox": [...] }
  ],
  "images": [
    { "id": "img_001", "path": "assets/img_001.png", "page": 4, "caption": "..." }
  ]
}
```

### `translated.json`
Same as `extracted.json` plus:
```jsonc
{
  "translation": { "source": "en", "target": "vi" },
  "sections": [
    { "...", "text": "<translated>", "text_original": "<original>" }
  ]
}
```

### `analysis.json`
```jsonc
{
  "paper": { "title": "...", "field": "Computer Vision", "difficulty": "advanced" },
  "target_audience": "Readers familiar with deep learning basics",
  "prerequisites": [
    {
      "id": "01-topic-slug",
      "title": "Topic Name",
      "importance": "critical|important|helpful",
      "phase": "Phase 1 — Foundations",
      "description": "One sentence description",
      "concepts": ["concept A", "concept B"],
      "estimated_reading_min": 20
    }
  ],
  "glossary": { "term": "definition", ... },
  "paper_sections": [
    { "heading": "Introduction", "summary": "...", "key_concepts": [...] }
  ],
  "agent_prompt": "Full structured prompt for agent to fill chapter content"
}
```
