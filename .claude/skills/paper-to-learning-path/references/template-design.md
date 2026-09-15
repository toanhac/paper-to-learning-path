# HTML Template Design Guide

## Design System Overview

The skill uses **three nature-inspired HTML templates**, all sharing the same CSS design token system. They follow a warm, organic visual philosophy grounded in earth materials: wood, stone, foliage, and water.

---

## Templates

| Template | File | Purpose |
|----------|------|---------|
| Paper translation | `nature_paper.html` | Full translated paper with TOC sidebar and nav |
| Learning path index | `nature_index.html` | Roadmap landing page with chapter timeline |
| Chapter module | `nature_learning.html` | Per-chapter educational content with prev/next nav |

---

## Shared Color Palette

| Token | Value | Usage |
|-------|-------|-------|
| `--bg` | `#f5f0e8` | Page background (warm parchment) |
| `--surface` | `#faf7f2` | Cards, sidebar (light parchment) |
| `--surface-2` | `#ede8df` | Secondary surfaces (sand) |
| `--border` | `#d4c9b5` | Borders, dividers (stone edge) |
| `--moss` | `#5a7a55` | Primary accent (deep moss) |
| `--moss-light` | `#7a9e74` | Hover states (mid moss) |
| `--moss-pale` | `#d6e8d0` | Tinted backgrounds (pale mint) |
| `--stone` | `#8a7e6e` | Secondary text (warm stone) |
| `--lake` | `#4a7a8a` | Alternative accent (lake blue) |
| `--lake-pale` | `#d0e3e8` | Note box backgrounds |
| `--amber` | `#8a6e3a` | Warning accent (amber wood) |
| `--text` | `#2d2820` | Body text (deep earth) |
| `--heading` | `#3a4e35` | Headings (dark forest) |
| `--math-bg` | `#edf2ed` | Math block backgrounds |
| `--code-bg` | `#e8e3da` | Code block backgrounds |

---

## Template Placeholders

All three templates share these `{{PLACEHOLDER}}` tokens (replaced by `render_html.py` or `generate_learning_path.py`):

| Placeholder | Used In | Content |
|-------------|---------|---------|
| `{{TITLE}}` | all | Paper/chapter title |
| `{{AUTHORS}}` | paper | Author string |
| `{{SOURCE_LANG}}` | paper, index | Source language code |
| `{{TARGET_LANG}}` | all | Target language code |
| `{{PAGES}}` | paper | Total PDF page count |
| `{{SOURCE_FILE}}` | paper | Original PDF filename |
| `{{TOC}}` | paper (legacy) | TOC (now auto-built by JS) |
| `{{CONTENT}}` | paper | Full body HTML |
| `{{ROADMAP_ITEMS}}` | index | Rendered roadmap HTML |
| `{{TOTAL_CHAPTERS}}` | index, chapter | Chapter count |
| `{{TOTAL_PHASES}}` | index | Unique phase count |
| `{{TOTAL_CONCEPTS}}` | index | Total concept count |
| `{{TOTAL_MIN}}` | index | Total reading time (minutes) |
| `{{FIRST_CHAPTER}}` | index | URL of first chapter |
| `{{PAPER_HTML}}` | index, chapter | Relative URL to paper.html |
| `{{BASE_CONCEPTS}}` | index | HTML `<li>` list of base prereqs |
| `{{GLOSSARY}}` | index | Rendered glossary HTML |
| `{{CHAPTER_NUM}}` | chapter | Current chapter number |
| `{{PHASE}}` | chapter | Phase label (e.g. "Phase 1 — Foundations") |
| `{{DESCRIPTION}}` | chapter | One-sentence chapter description |
| `{{CONCEPTS}}` | chapter | Concept tags HTML |
| `{{EST_MIN}}` | chapter | Estimated reading minutes |
| `{{NAV_LINKS}}` | chapter | Top nav `<a>` links HTML |
| `{{PREV_NAV}}` | chapter | Previous chapter button HTML |
| `{{NEXT_NAV}}` | chapter | Next chapter button HTML |
| `{{PAPER_TITLE}}` | chapter | Paper title (for deep-dive footer) |
| `{{AUDIENCE}}` | index | Target audience description |
| `{{FIELD}}` | index | Research field |
| `{{DIFFICULTY}}` | index | beginner / intermediate / advanced |

---

## Info Box Components (all templates)

Available in all chapter and paper templates:

```html
<div class="info-box note">
  <div class="box-label">📝 Note</div>
  Background context or helpful explanation.
</div>

<div class="info-box tip">
  <div class="box-label">💡 Tip</div>
  Best practice or efficiency suggestion.
</div>

<div class="info-box warning">
  <div class="box-label">⚠️ Warning</div>
  Common misconception or potential confusion.
</div>

<div class="info-box important">
  <div class="box-label">🔑 Important</div>
  Critical concept or must-know information.
</div>
```

---

## Figure & Diagram Components

```html
<!-- Image figure -->
<figure class="paper-figure" id="fig-1">
  <img src="data:image/png;base64,..." alt="Description"/>
  <figcaption class="figure-caption">Figure 1: Caption text</figcaption>
</figure>

<!-- ASCII diagram (learning chapters) -->
<div class="figure">
  <div class="diagram">
    <pre class="ascii-diagram">
    Your ASCII art here
    </pre>
  </div>
  <p class="caption">Figure N.M: Caption</p>
</div>
```

---

## Interaction Timings (per design spec)

All transitions use `var(--t)` = **220ms ease** — within the 180–260ms "sunlight shift" range.

Hover effects:
- **TOC links**: color + background tint + left border highlight
- **Roadmap cards**: border color + shadow + `translateY(-1px)`
- **Figures**: shadow deepens + `translateY(-1px)`
- **Buttons**: background brightens, shadow increases

---

## Print Styles

`@media print` in all three templates:
- Hides nav bar, progress bar, sidebar TOC, scroll button
- Removes decorative backgrounds
- `break-inside: avoid` on figures and math blocks
- Sets `background: white`

---

## Dark Mode Note

The current design uses a light warm-parchment palette by default. To add dark mode support, add a `prefers-color-scheme: dark` media query overriding the `:root` tokens. The ReSplat reference project (`examples/resplat/`) uses a dark obsidian theme (`#09090b` background) as an alternative aesthetic reference.
