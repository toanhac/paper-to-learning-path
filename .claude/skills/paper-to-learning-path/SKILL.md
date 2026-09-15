---
name: paper-to-learning-path
description: >-
  Use this skill when the user wants to convert a research paper (PDF) into a
  translated, visually appealing HTML page AND/OR generate a multi-page learning
  path for readers who need to build prerequisite knowledge before understanding
  the paper. The skill extracts text, math, and images from the PDF; translates
  the content preserving all LaTeX math verbatim; renders a self-contained HTML
  paper; analyzes the paper's concepts and difficulty; and generates a complete
  dashboard site with: a central index.html hub, one chapter per prerequisite
  topic, a final paper deep-dive chapter, and optionally a repo setup guide page.
  Activate when the user provides a PDF path and a target language, or asks to
  "translate", "convert", or "explain" a research paper.
---

# paper-to-learning-path Skill

Converts a research-paper PDF into a full learning ecosystem:
1. **`paper.html`** — Translated, self-contained HTML with KaTeX math and embedded images
2. **`index.html`** — Central dashboard hub linking all outputs
3. **`learning/`** — Multi-chapter prerequisite learning path site
4. **`setup-guide.html`** *(optional)* — Full repository setup guide

> **Platform note:** Works on Antigravity, Cursor, Claude Code, Cline, Aider, and any
> agent with Python execution capability. See
> [`references/platform-notes.md`](./references/platform-notes.md).

---

## ⚡ Pre-Flight: Ask the User These Questions First

**Before running any script**, ask the user the following (you can ask all at once):

```
1. Bạn muốn tạo Lộ trình tự học (Learning Path) không?
   → yes = tạo learning/, index.html dashboard | no = chỉ tạo paper.html

2. Bạn muốn tạo trang Hướng dẫn Setup Repository không?
   → yes = tạo setup-guide.html với: clone, environment, dataset, training, inference, FAQ
   → no = bỏ qua bước này

3. Ngôn ngữ dịch đầu ra là gì?
   → Ví dụ: vi (Tiếng Việt), fr (Français), de (Deutsch), es (Español), zh (中文) ...

4. Background của người đọc là gì?
   → Ví dụ: "Sinh viên năm 3 CNTT", "ML engineer quen CNN", "Researcher không biết 3D vision"
   → (Dùng để xác định cấp độ khó của các chương học)
```

Record the answers as: `want_learning_path`, `want_setup_guide`, `target_lang`, `audience`.
Then proceed with the pipeline below, running only the steps relevant to the user's choices.

---

## Prerequisites Check

Ensure the required Python packages are installed:

```bash
pip install pymupdf langdetect
```

Run the check script first:

```bash
python scripts/check_deps.py
```

If anything is missing, ask the user to install it. Do not proceed until all deps pass.

---

## Inputs to Collect

| Parameter | Required | Default | Notes |
|-----------|----------|---------|-------|
| `pdf_path` | ✅ | — | Absolute or relative path to the PDF |
| `target_lang` | ✅ | — | BCP-47 code or name (e.g. `vi`, `fr`, `de`) |
| `source_lang` | ❌ | auto-detect | Skip to auto-detect from content |
| `output_dir` | ❌ | `./output` | Root directory for all generated files |
| `want_learning_path` | ❌ | ask user | Whether to generate the learning path site |
| `want_setup_guide` | ❌ | ask user | Whether to generate the repo setup guide |
| `audience` | ❌ | auto-detect | Reader's background for difficulty calibration |

---

## Step 1 — Validate & Install

```bash
python scripts/check_deps.py
```

If any package is missing, ask the user to install it and stop.

---

## Step 2 — Extract PDF Content

```bash
python scripts/extract_pdf.py \
  --pdf "<pdf_path>" \
  --out-dir "<output_dir>/assets"
```

Produces `<output_dir>/extracted.json` and image files in `<output_dir>/assets/`.

**Math detection rules:**
- Text with > 25% symbol density (`+-*/=^_{}\\$`) is classified `math_block`
- Text matching LaTeX command patterns is classified `math_block`
- **Math blocks are never translated** — they pass through verbatim

---

## Step 3 — Detect Source Language

If `source_lang` was not provided:

```bash
python scripts/detect_lang.py --json "<output_dir>/extracted.json"
```

Note the `LANG_CODE=` line from the output. If confidence < 85%, confirm with the user.

---

## Step 4 — Translate Content (Agent Direct Translation — Zero API Keys Needed)

Because you are an advanced AI agent, **you perform the translation directly using your own intelligence** — no external API keys (Gemini, OpenAI) or third-party translation subscriptions are needed!

1. **Scaffold the translation file:**
   ```bash
   python scripts/translate_content.py \
     --scaffold \
     --json "<output_dir>/extracted.json" \
     --source "<source_lang>" \
     --target "<target_lang>" \
     --out "<output_dir>/translated.json"
   ```
   This copies the structure, records `text_original`, and locks all `math_block` sections so equations remain 100% untouched.

2. **Translate the text sections:**
   Inspect and update `<output_dir>/translated.json`:
   - For every text section (`title`, `heading`, `paragraph`, `abstract`): translate `text` into `<target_lang>` with high academic quality.
   - **Math blocks (`type == "math_block"`):** NEVER translate — keep verbatim.
   - **Inline LaTeX math (`$...$`, `\(...\)`, `$$...$$`):** Keep strictly verbatim.
   - **Citations (`[1]`, `[Author, 2020]`):** Keep strictly verbatim.
   - **Domain nomenclature:** Keep standard model names (*NeRF*, *3DGS*, *Transformer*, *AdamW*) and dataset names (*ImageNet*, *COCO*, *ScanNet*) intact.
   - **Image captions:** Translate the `caption` field in `images`.

3. **Verify translation integrity:**
   ```bash
   python scripts/translate_content.py --verify "<output_dir>/translated.json"
   ```

---

## Step 5 — Render Paper HTML

```bash
python scripts/render_html.py \
  --json "<output_dir>/translated.json" \
  --template resources/nature_paper.html \
  --out "<output_dir>/paper.html"
```

The output `paper.html` is a fully self-contained file with:
- KaTeX-rendered math (loaded from CDN)
- Base64-embedded images
- Sticky TOC sidebar
- Reading progress bar
- Language badge (`source → target`)

**Verify:** Open in a browser. Search for `katex-error` — if found, review the math in `translated.json`.

---

## Step 6 — Analyze Paper (Learning Path Mode)

> Skip this step if `mode` is `paper-only`.

```bash
python scripts/analyze_paper.py \
  --json "<output_dir>/translated.json" \
  --audience "<audience_description>" \
  --out "<output_dir>/analysis.json"
```

This script:
1. Extracts the paper's key concepts and terminology from the glossary
2. Identifies all technical terms referenced in the paper
3. Generates a structured prompt for the agent to determine prerequisites
4. Outputs `analysis.json` with prerequisite chapters and chapter outlines

**After running the script, read `analysis.json` and:**
- Review `prerequisites` — the list of knowledge areas the reader needs
- Review `paper_sections` — the outline of the paper itself
- Review `agent_prompt` — the instruction for generating chapter content
- Adjust if needed based on the user's stated audience/background

---

## Step 7 — Generate Learning Path Scaffolding

> Skip this step if `mode` is `paper-only`.

```bash
python scripts/generate_learning_path.py \
  --analysis "<output_dir>/analysis.json" \
  --paper-html "<output_dir>/paper.html" \
  --out-dir "<output_dir>/learning"
```

This generates:
- `learning/index.html` — the roadmap landing page (fully rendered)
- `learning/NN-<slug>.html` — one scaffolded chapter per prerequisite
- `learning/final-deep-dive.html` — scaffolded paper deep-dive chapter

Scaffolded chapters contain `<!-- AGENT: ... -->` placeholder comments where
**you (the agent) must fill in the educational content** in the next step.

---

## Step 8 — Write Chapter Content (Agent Task)

This is the most important step. Read `<output_dir>/analysis.json` carefully, then:

For **each chapter file** in `<output_dir>/learning/`:
1. Open the file and locate all `<!-- AGENT: ... -->` comment blocks
2. Each comment describes what content to write in that section
3. Replace the comment with well-written educational content in `<target_lang>`
4. Use the following HTML components available in the template:

```html
<!-- Info boxes -->
<div class="info-box note"><div class="box-label">📝 Note</div>Your text here.</div>
<div class="info-box tip"><div class="box-label">💡 Tip</div>Your text here.</div>
<div class="info-box warning"><div class="box-label">⚠️ Warning</div>Your text here.</div>
<div class="info-box important"><div class="box-label">🔑 Important</div>Your text here.</div>

<!-- Math blocks -->
<div class="math-block">$$your LaTeX here$$</div>

<!-- Figures with ASCII diagrams -->
<div class="figure">
  <div class="diagram"><pre class="ascii-diagram">Your ASCII art here</pre></div>
  <p class="caption">Figure N.M: Caption text</p>
</div>

<!-- Code blocks -->
<pre><code class="language-python">your code here</code></pre>
```

**Content guidelines:**
- Write for the audience described in `analysis.json`
- Each chapter should be self-contained: briefly recap what was in the previous chapter
- Explain concepts intuitively before introducing formal math
- Use concrete, visual analogies before abstract definitions
- Each concept should appear in a logical order: motivation → intuition → formulation → example
- End each chapter with a "What's Next" paragraph linking to the next chapter

**Final chapter (deep-dive):**
- Walk through each section of the paper in order
- Reference the prerequisite chapters for concepts ("As we saw in Chapter 2...")
- Include the key math from the paper (copied from `analysis.json`)
- Add a "Key Takeaways" section at the end

---

## Step 9 — Generate Setup Guide *(only if `want_setup_guide = yes`)*

```bash
python scripts/generate_setup_guide.py \
    --translated <output_dir>/translated.json \
    --analysis   <output_dir>/analysis.json \
    --out        <output_dir>/setup-guide.html \
    --target-lang <target_lang>
```

Then **fill in the `<!-- AGENT: ... -->` placeholders** inside `setup-guide.html`:
- Replace placeholder commands in each step with the **actual commands** from the paper's GitHub repo / README
- If you can access the paper's GitHub repo URL, fetch the README and use real commands
- If no URL is available, keep the generic placeholders but note them clearly

> **Agent responsibility:** The setup guide is pre-structured (7 steps: Clone → Environment → Dependencies → Dataset → Training → Inference → FAQ). Your job is to replace the generic examples with paper-specific commands extracted from the paper's experimental setup section.

---

## Step 10 — Generate Central Dashboard *(only if `want_learning_path = yes`)*

After generating learning path chapters AND (optionally) setup-guide.html, generate the central `index.html` dashboard:

```bash
python scripts/generate_learning_path.py \
    --analysis  <output_dir>/analysis.json \
    --paper-html <output_dir>/paper.html \
    --out-dir   <output_dir>/learning \
    --dashboard \
    --setup-guide <output_dir>/setup-guide.html   # omit this flag if no setup guide
```

This creates **`<output_dir>/index.html`** — the central hub that:
- Shows a stats grid (chapters, phases, concepts, reading time)
- Has 3 quick-action cards: Start Learning, Read Paper, Setup Repo
- Lists the full learning roadmap
- Features a prominent setup guide card (if generated)
- Links to all chapters from the roadmap timeline

---

## Step 11 — Fill Chapter Content *(only if `want_learning_path = yes`)*

Open each file in `<output_dir>/learning/` and replace `<!-- AGENT: ... -->` comment blocks with real educational content.

```html
<!-- Info boxes -->
<div class="info-box note"><div class="box-label">📝 Note</div>Your text here.</div>
<div class="info-box tip"><div class="box-label">💡 Tip</div>Your text here.</div>
<div class="info-box warning"><div class="box-label">⚠️ Warning</div>Your text here.</div>
<div class="info-box important"><div class="box-label">🔑 Important</div>Your text here.</div>

<!-- Math blocks -->
<div class="math-block">$$your LaTeX here$$</div>

<!-- Figures with ASCII diagrams -->
<div class="figure">
  <div class="diagram"><pre class="ascii-diagram">Your ASCII art here</pre></div>
  <p class="caption">Figure N.M: Caption text</p>
</div>

<!-- Code blocks -->
<pre><code class="language-python">your code here</code></pre>
```

**Content guidelines:**
- Write for the audience described in `analysis.json`
- Each chapter should be self-contained: briefly recap what was in the previous chapter
- Explain concepts intuitively before introducing formal math
- Use concrete, visual analogies before abstract definitions
- Each concept should appear in a logical order: motivation → intuition → formulation → example
- End each chapter with a "What's Next" paragraph linking to the next chapter

**Final chapter (deep-dive):**
- Walk through each section of the paper in order
- Reference the prerequisite chapters for concepts ("As we saw in Chapter 2...")
- Include the key math from the paper (copied from `analysis.json`)
- Add a "Key Takeaways" section at the end

---

## Step 12 — Verify Output

1. Open `<output_dir>/index.html` in a browser → check the dashboard renders correctly
2. Click all 3 quick-action cards → paper.html, first chapter, setup-guide.html all open
3. Open `<output_dir>/learning/index.html` → click each chapter in the roadmap
4. Confirm prev/next navigation in chapters is correct
5. Search for `<!-- AGENT:` in all output files — none should remain unfilled
6. Open `<output_dir>/paper.html` — verify math renders, images appear
7. If setup guide was generated: open `setup-guide.html`, check code blocks are readable
8. Report the final output directory to the user with a summary

---

## Output Structure

```
<output_dir>/
├── index.html                    ← 🆕 Central dashboard hub
├── paper.html                    ← Self-contained translated paper
├── setup-guide.html              ← 🆕 Repo setup guide (if requested)
├── extracted.json
├── translated.json
├── analysis.json
├── assets/
│   └── img_001.png, ...
└── learning/
    ├── index.html                ← Learning path roadmap (inside learning/)
    ├── 01-<topic>.html           ← Prerequisite chapter 1
    ├── ...
    └── final-deep-dive.html      ← Paper deep-dive chapter
```

---

## Error Handling

| Error | Resolution |
|-------|-----------|
| `ModuleNotFoundError` | `pip install pymupdf deep-translator langdetect` |
| Translation rate limit | Add `--chunk-delay 2.0` to translate script |
| Garbled math rendering | Math delimiters were translated — check `--math-delimiters` |
| Missing images in HTML | Re-run extract with `--dpi 150` |
| `katex-error` in output | Fix raw LaTeX in `translated.json` math_block sections |
| Agent fills wrong language | Re-read `analysis.json` `target_lang` field before writing |
| Dashboard links broken | Ensure chapters are in `learning/` subfolder relative to `index.html` |
| Setup guide has placeholders | Fill `<!-- AGENT: ... -->` blocks with paper-specific commands |

---

## References

- [Platform-specific notes](./references/platform-notes.md)
- [Dependency alternatives](./references/dependencies.md)
- [Translation engine options](./references/translation-engines.md)
- [HTML template design guide](./references/template-design.md)
- [Architecture overview](../../../docs/how-it-works.md)
