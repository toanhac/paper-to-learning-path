#!/usr/bin/env python3
"""
generate_learning_path.py — Generate a multi-page HTML learning path site.

Reads analysis.json (produced by analyze_paper.py) and generates:
  - learning/index.html                  (roadmap landing page — fully rendered)
  - learning/NN-<slug>.html              (one scaffolded chapter per prerequisite)
  - learning/final-deep-dive.html        (scaffolded paper deep-dive)

Scaffolded chapter files contain <!-- AGENT: ... --> placeholder comments that
the AI agent will fill in with educational content.

Usage:
    python generate_learning_path.py \\
        --analysis analysis.json \\
        --paper-html paper.html \\
        --out-dir output/learning \\
        [--index-template ../resources/nature_index.html] \\
        [--chapter-template ../resources/nature_learning.html]
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# HTML helpers
# ---------------------------------------------------------------------------

def _esc(text: str) -> str:
    return (text.replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


# ---------------------------------------------------------------------------
# Index page builder
# ---------------------------------------------------------------------------

def _build_index(analysis: dict, template: str, out_path: str, paper_html_rel: str):
    paper = analysis["paper"]
    prerequisites = analysis["prerequisites"]
    total_chapters = analysis["total_chapters"]
    total_min = analysis["total_reading_min"]
    audience = analysis["target_audience"]

    # Build phase groups
    phases: dict[str, list] = {}
    for p in prerequisites:
        phase = p.get("phase", "Uncategorized")
        phases.setdefault(phase, []).append(p)

    # Build roadmap items HTML
    roadmap_items = []
    for p in prerequisites:
        num = p.get("chapter_num", 0)
        title = _esc(p.get("title", ""))
        desc = _esc(p.get("description", ""))
        phase = _esc(p.get("phase", ""))
        fname = p.get("filename", f"{num:02d}-untitled.html")
        importance = p.get("importance", "important")
        est_min = p.get("estimated_reading_min", 20)
        concepts = p.get("concepts", [])[:4]

        tags_html = "".join(f'<span class="tag">{_esc(c)}</span>' for c in concepts)
        importance_class = {"critical": "dot-critical", "important": "dot-important", "helpful": "dot-helpful"}.get(importance, "")

        roadmap_items.append(f"""
    <div class="roadmap-item">
      <div class="roadmap-dot {importance_class}">{num}</div>
      <a href="{fname}" class="roadmap-card">
        <div class="roadmap-phase">{phase}</div>
        <div class="roadmap-title">{title}</div>
        <div class="roadmap-desc">{desc}</div>
        <div class="roadmap-meta">~{est_min} min read</div>
        <div class="roadmap-tags">{tags_html}</div>
      </a>
    </div>""")

    # Phase labels in stats
    unique_phases = len(set(p.get("phase","") for p in prerequisites))
    total_concepts = sum(len(p.get("concepts",[])) for p in prerequisites)

    roadmap_html = "\n".join(roadmap_items)

    # Prerequisites the user needs BEFORE starting
    base_prereq = analysis.get("prerequisites", [{}])[0]
    base_concepts = base_prereq.get("concepts", [])
    base_concepts_html = "\n".join(f"<li><strong>{_esc(c)}</strong></li>" for c in base_concepts)

    # Glossary sample
    glossary = analysis.get("glossary", {})
    glossary_html = ""
    if glossary:
        sample = list(glossary.items())[:6]
        glossary_html = '<div class="glossary-grid">' + "".join(
            f'<div class="glossary-item"><span class="gterm">{_esc(k)}</span><span class="gdef">{_esc(v[:80])}</span></div>'
            for k, v in sample
        ) + "</div>"

    first_chapter = prerequisites[0]["filename"] if prerequisites else "#"

    html = template
    replacements = {
        "{{TITLE}}": _esc(paper.get("title", "Research Paper")),
        "{{AUTHORS}}": _esc(paper.get("authors", "")),
        "{{FIELD}}": _esc(paper.get("field", "")),
        "{{DIFFICULTY}}": _esc(paper.get("difficulty", "")),
        "{{SOURCE_LANG}}": _esc(paper.get("source_lang", "?")),
        "{{TARGET_LANG}}": _esc(paper.get("target_lang", "?")),
        "{{AUDIENCE}}": _esc(audience),
        "{{TOTAL_CHAPTERS}}": str(total_chapters),
        "{{TOTAL_PHASES}}": str(unique_phases),
        "{{TOTAL_CONCEPTS}}": str(total_concepts),
        "{{TOTAL_MIN}}": str(total_min),
        "{{ROADMAP_ITEMS}}": roadmap_html,
        "{{BASE_CONCEPTS}}": base_concepts_html,
        "{{GLOSSARY}}": glossary_html,
        "{{FIRST_CHAPTER}}": first_chapter,
        "{{PAPER_HTML}}": paper_html_rel,
    }
    for key, val in replacements.items():
        html = html.replace(key, val)

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"  ✓ Index     → {out_path}")


# ---------------------------------------------------------------------------
# Chapter scaffolder
# ---------------------------------------------------------------------------

def _build_chapter(chapter: dict, all_chapters: list[dict],
                   template: str, out_path: str, paper_info: dict, paper_html_rel: str):
    num = chapter.get("chapter_num", 0)
    title = chapter.get("title", "Chapter")
    desc = chapter.get("description", "")
    phase = chapter.get("phase", "")
    concepts = chapter.get("concepts", [])
    est_min = chapter.get("estimated_reading_min", 20)
    is_deep_dive = chapter.get("id") == "paper-deep-dive"

    # Prev / Next
    prev_ch = next((c for c in all_chapters if c.get("chapter_num") == num - 1), None)
    next_ch = next((c for c in all_chapters if c.get("chapter_num") == num + 1), None)

    prev_html = ""
    if prev_ch:
        prev_html = f"""<a href="{prev_ch['filename']}" class="page-nav-btn prev">
        <span class="nav-label">← Previous</span>
        <span class="nav-title">{_esc(prev_ch['title'])}</span>
      </a>"""
    else:
        prev_html = '<a href="index.html" class="page-nav-btn prev"><span class="nav-label">← Back to</span><span class="nav-title">Learning Path</span></a>'

    next_html = ""
    if next_ch:
        next_html = f"""<a href="{next_ch['filename']}" class="page-nav-btn next">
        <span class="nav-label">Next →</span>
        <span class="nav-title">{_esc(next_ch['title'])}</span>
      </a>"""
    else:
        next_html = f'<a href="{paper_html_rel}" class="page-nav-btn next"><span class="nav-label">Read →</span><span class="nav-title">Full Translated Paper</span></a>'

    # Nav links (all chapters for top nav)
    nav_links = '<a href="index.html">Home</a>'
    for ch in all_chapters:
        active = ' class="active"' if ch["chapter_num"] == num else ""
        nav_links += f'\n    <a href="{ch["filename"]}"{active}>{_esc(ch["title"][:20])}</a>'
    nav_links += f'\n    <a href="{paper_html_rel}">Full Paper</a>'

    # Concepts list for the header
    concepts_html = " · ".join(f'<span class="concept-tag">{_esc(c)}</span>' for c in concepts[:5])

    # Scaffolded content blocks
    if is_deep_dive:
        content_html = _scaffold_deep_dive(chapter, paper_info)
    else:
        content_html = _scaffold_prereq_chapter(chapter, num, len(all_chapters))

    html = template
    replacements = {
        "{{TITLE}}": _esc(title),
        "{{DESCRIPTION}}": _esc(desc),
        "{{PHASE}}": _esc(phase),
        "{{CHAPTER_NUM}}": str(num),
        "{{TOTAL_CHAPTERS}}": str(len(all_chapters)),
        "{{EST_MIN}}": str(est_min),
        "{{TARGET_LANG}}": _esc(paper_info.get("target_lang", "en")),
        "{{NAV_LINKS}}": nav_links,
        "{{CONCEPTS}}": concepts_html,
        "{{CONTENT}}": content_html,
        "{{PREV_NAV}}": prev_html,
        "{{NEXT_NAV}}": next_html,
        "{{PAPER_TITLE}}": _esc(paper_info.get("title", "Research Paper")),
    }
    for key, val in replacements.items():
        html = html.replace(key, val)

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"  ✓ Ch.{num:02d}    → {out_path}")


def _scaffold_prereq_chapter(chapter: dict, num: int, total: int) -> str:
    title = chapter.get("title", "")
    concepts = chapter.get("concepts", [])
    desc = chapter.get("description", "")

    concept_blocks = "\n".join(
        f"""
  <h3>{_esc(c.title())}</h3>
  <!-- AGENT: Explain "{_esc(c)}" here. Start with an intuitive analogy, then give the
       formal definition or math. Use <div class="math-block">$$...$$</div> for equations
       and <div class="info-box tip">...</div> for practical tips.
       Target length: 150–300 words per concept. -->
  <p class="placeholder-hint">[ Agent: write content for "{_esc(c)}" here ]</p>
"""
        for c in concepts
    )

    return f"""
  <div class="info-box note">
    <div class="box-label">📝 Note</div>
    <!-- AGENT: Write a 1–2 sentence overview of this chapter and why it matters
         for understanding the paper. -->
    <p class="placeholder-hint">[ Agent: write chapter overview note here ]</p>
  </div>

  <h2>Why You Need to Know This</h2>
  <!-- AGENT: Explain in 2–3 paragraphs WHY this prerequisite topic is necessary
       for understanding the paper. Connect it concretely to the paper's methods. -->
  <p class="placeholder-hint">[ Agent: explain motivation and relevance to paper ]</p>

  {concept_blocks}

  <h2>Key Takeaways</h2>
  <!-- AGENT: Write 4–6 bullet points summarizing the most important things
       the reader should remember from this chapter before moving on. -->
  <ul class="placeholder-hint">
    <li>[ Agent: key takeaway 1 ]</li>
    <li>[ Agent: key takeaway 2 ]</li>
    <li>[ Agent: key takeaway 3 ]</li>
  </ul>

  <h2>What's Next</h2>
  <!-- AGENT: Write 1 paragraph explaining what the reader will learn in the
       next chapter, and how this chapter's knowledge will be used there. -->
  <p class="placeholder-hint">[ Agent: write "what's next" transition paragraph ]</p>
"""


def _scaffold_deep_dive(chapter: dict, paper_info: dict) -> str:
    paper_title = paper_info.get("title", "the paper")
    paper_sections = paper_info.get("paper_sections", [])

    section_blocks = ""
    for s in paper_sections:
        heading = s.get("heading", "Section")
        summary = s.get("summary", "")[:200]
        section_blocks += f"""
  <h2>{_esc(heading)}</h2>
  <!-- AGENT: Explain this section of the paper in detail.
       Summary hint: {_esc(summary)}
       - What problem does this section address?
       - What is the key idea / method / result?
       - Include relevant math from the paper using <div class="math-block">$$...$$</div>
       - Reference prerequisite chapters where relevant ("As covered in Chapter N...")
       Target: 200–400 words per section. -->
  <p class="placeholder-hint">[ Agent: write explanation for "{_esc(heading)}" section ]</p>
"""

    return f"""
  <div class="info-box important">
    <div class="box-label">🔑 Important</div>
    <!-- AGENT: Write a 2–3 sentence introduction to the paper deep-dive chapter.
         Congratulate the reader on reaching this point and tell them what this
         final chapter covers. -->
    <p class="placeholder-hint">[ Agent: write deep-dive chapter introduction ]</p>
  </div>

  <h2>Paper Overview</h2>
  <!-- AGENT: Write a 1-paragraph executive summary of the full paper — what
       problem it solves, what method it proposes, and what the key results are. -->
  <p class="placeholder-hint">[ Agent: write 1-paragraph paper overview ]</p>

  {section_blocks}

  <h2>Key Contributions</h2>
  <!-- AGENT: List the paper's 3–5 key contributions as a bulleted list with brief
       explanations. These should be the things the paper claims as novel. -->
  <ul class="placeholder-hint">
    <li>[ Agent: contribution 1 ]</li>
    <li>[ Agent: contribution 2 ]</li>
  </ul>

  <h2>Results & Comparison</h2>
  <!-- AGENT: Describe the paper's experimental results. What benchmarks were used?
       How did the method compare to baselines? What were the most impressive numbers?
       Use a <table> if helpful. -->
  <p class="placeholder-hint">[ Agent: describe experimental results ]</p>

  <h2>Limitations & Future Work</h2>
  <!-- AGENT: Describe any limitations of the method and what future work the authors
       suggest or what the community could explore next. -->
  <p class="placeholder-hint">[ Agent: describe limitations and future directions ]</p>

  <div class="info-box tip">
    <div class="box-label">💡 Congratulations</div>
    <!-- AGENT: Write a congratulatory closing message. Encourage the reader to
         now read the original paper and mention what skills they have built. -->
    <p class="placeholder-hint">[ Agent: write closing congratulations ]</p>
  </div>
"""


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def generate(analysis_path: str, paper_html: str,
             out_dir: str, index_template_path: str, chapter_template_path: str,
             dashboard: bool = False, dashboard_template_path: str = "",
             setup_guide_path: str = ""):
    with open(analysis_path, encoding="utf-8") as f:
        analysis = json.load(f)

    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Resolve relative paper HTML path from out_dir
    if paper_html:
        paper_html_rel = os.path.relpath(paper_html, out_dir).replace("\\", "/")
    else:
        paper_html_rel = "../paper.html"

    # Load templates
    def load_template(path: str, fallback: str) -> str:
        if path and Path(path).is_file():
            with open(path, encoding="utf-8") as f:
                return f.read()
        print(f"  ⚠️  Template not found: {path} — using minimal fallback")
        return fallback

    index_template = load_template(index_template_path, _FALLBACK_INDEX)
    chapter_template = load_template(chapter_template_path, _FALLBACK_CHAPTER)

    chapters = analysis.get("prerequisites", [])
    paper_info = {**analysis.get("paper", {}),
                  "paper_sections": analysis.get("paper_sections", [])}

    print(f"\n🌿 Generating learning path → {out_dir}/")

    # Generate learning/ chapters index (roadmap page inside learning/)
    _build_index(analysis, index_template, str(out_dir / "index.html"), paper_html_rel)

    # Generate chapters
    for ch in chapters:
        fname = ch.get("filename", f"{ch.get('chapter_num',0):02d}-untitled.html")
        ch_path = out_dir / fname
        _build_chapter(ch, chapters, chapter_template, str(ch_path), paper_info, paper_html_rel)

    # Generate central dashboard (output/index.html) if requested
    if dashboard:
        dashboard_tpl = load_template(dashboard_template_path, _FALLBACK_INDEX)
        dashboard_out = out_dir.parent / "index.html"
        paper_html_from_dash = os.path.relpath(paper_html, out_dir.parent).replace("\\", "/") if paper_html else "paper.html"
        has_setup = bool(setup_guide_path and Path(setup_guide_path).exists())
        setup_guide_rel = os.path.relpath(setup_guide_path, out_dir.parent).replace("\\", "/") if has_setup else "setup-guide.html"
        _build_dashboard(analysis, dashboard_tpl, str(dashboard_out),
                         paper_html_from_dash, has_setup or bool(setup_guide_path), setup_guide_rel)
        print(f"\n✅ Dashboard generated: {dashboard_out}")

    print(f"\n✅ Learning path generated: {len(chapters)} chapters in {out_dir}/")
    print(f"   Open: {out_dir}/index.html\n")
    print("📝 Next step: Fill in all <!-- AGENT: ... --> placeholders in each chapter file.")





# ---------------------------------------------------------------------------
# Dashboard page builder (generates output/index.html as central hub)
# ---------------------------------------------------------------------------

def _build_dashboard(analysis: dict, template: str, out_path: str,
                     paper_html_rel: str, has_setup_guide: bool, setup_guide_rel: str):
    """Build a rich central dashboard index.html from the dashboard template."""
    paper = analysis["paper"]
    prerequisites = analysis["prerequisites"]
    total_chapters = analysis["total_chapters"]
    total_min = analysis["total_reading_min"]

    # Stats
    unique_phases = len(set(p.get("phase", "") for p in prerequisites))
    total_concepts = sum(len(p.get("concepts", [])) for p in prerequisites)

    # Roadmap items
    roadmap_items = []
    for p in prerequisites:
        num = p.get("chapter_num", 0)
        title = _esc(p.get("title", ""))
        desc = _esc(p.get("description", ""))
        phase = _esc(p.get("phase", ""))
        # chapters live in learning/ subdir relative to dashboard
        fname = "learning/" + p.get("filename", f"{num:02d}-untitled.html")
        importance = p.get("importance", "important")
        est_min = p.get("estimated_reading_min", 20)
        concepts = p.get("concepts", [])[:4]
        tags_html = "".join(f'<span class="tag">{_esc(c)}</span>' for c in concepts)
        dot_class = {"critical": "dot-critical", "important": "dot-important",
                     "helpful": "dot-helpful"}.get(importance, "")
        is_deepdive = p.get("id") == "paper-deep-dive"
        card_class = " deepdive" if is_deepdive else ""
        roadmap_items.append(f"""
    <div class="roadmap-item">
      <div class="roadmap-dot {dot_class if not is_deepdive else 'dot-deepdive'}">{num}</div>
      <a href="{fname}" class="roadmap-card{card_class}">
        <div class="roadmap-phase">{phase}</div>
        <div class="roadmap-title">{title}</div>
        <div class="roadmap-desc">{desc}</div>
        <div class="roadmap-meta">~{est_min} min read</div>
        <div class="roadmap-tags">{tags_html}</div>
      </a>
    </div>""")

    # Base prereqs
    base_prereq = prerequisites[0] if prerequisites else {}
    base_concepts = base_prereq.get("concepts", [])
    base_concepts_html = "\n".join(
        f"<li><strong>{_esc(c)}</strong></li>" for c in base_concepts)

    # Glossary
    glossary = analysis.get("glossary", {})
    glossary_html = ""
    glossary_section = ""
    if glossary:
        sample = list(glossary.items())[:8]
        glossary_html = '<div class="glossary-grid">' + "".join(
            f'<div class="glossary-item"><span class="gterm">{_esc(k)}</span>'
            f'<span class="gdef">{_esc(v[:90])}</span></div>'
            for k, v in sample
        ) + "</div>"
        glossary_section = f'<div class="section-title">📖 Thuật ngữ chính</div>{glossary_html}'

    first_chapter = "learning/" + prerequisites[0]["filename"] if prerequisites else "#"

    # Setup guide placeholders
    if has_setup_guide:
        setup_nav_chip = f'<a href="{setup_guide_rel}" class="nav-chip">🔧 Setup Guide</a>'
        setup_action_card = f"""<a href="{setup_guide_rel}" class="action-card">
        <div class="action-icon">🔧</div>
        <div class="action-title">Setup Repo</div>
        <div class="action-desc">Cài đặt · Dataset · Training</div>
      </a>"""
        setup_guide_card = f"""<a href="{setup_guide_rel}" class="setup-card">
      <div class="setup-card-icon">🔧</div>
      <div class="setup-card-text">
        <div class="setup-card-title">Hướng dẫn Setup Repository</div>
        <div class="setup-card-desc">Clone repo · Cài môi trường · Tải dataset · Chạy training · Inference · FAQ & Troubleshooting</div>
      </div>
      <div class="setup-card-arrow">→</div>
    </a>"""
        setup_footer_link = f' · <a href="{setup_guide_rel}">Setup Guide</a>'
    else:
        setup_nav_chip = ""
        setup_action_card = """<div class="action-card" style="opacity:.5;cursor:default;">
        <div class="action-icon">🔧</div>
        <div class="action-title">Setup Guide</div>
        <div class="action-desc">Chưa được tạo</div>
      </div>"""
        setup_guide_card = ""
        setup_footer_link = ""

    html = template
    replacements = {
        "{{TITLE}}": _esc(paper.get("title", "Research Paper")),
        "{{AUTHORS}}": _esc(paper.get("authors", "")),
        "{{FIELD}}": _esc(paper.get("field", "")),
        "{{DIFFICULTY}}": _esc(paper.get("difficulty", "")),
        "{{SOURCE_LANG}}": _esc(paper.get("source_lang", "?")),
        "{{TARGET_LANG}}": _esc(paper.get("target_lang", "?")),
        "{{TOTAL_CHAPTERS}}": str(total_chapters),
        "{{TOTAL_PHASES}}": str(unique_phases),
        "{{TOTAL_CONCEPTS}}": str(total_concepts),
        "{{TOTAL_MIN}}": str(total_min),
        "{{ROADMAP_ITEMS}}": "\n".join(roadmap_items),
        "{{BASE_CONCEPTS}}": base_concepts_html,
        "{{GLOSSARY_SECTION}}": glossary_section,
        "{{FIRST_CHAPTER}}": first_chapter,
        "{{PAPER_HTML}}": paper_html_rel,
        "{{SETUP_NAV_CHIP}}": setup_nav_chip,
        "{{SETUP_ACTION_CARD}}": setup_action_card,
        "{{SETUP_GUIDE_CARD}}": setup_guide_card,
        "{{SETUP_FOOTER_LINK}}": setup_footer_link,
    }
    for key, val in replacements.items():
        html = html.replace(key, val)

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"  ✓ Dashboard → {out_path}")


# ---------------------------------------------------------------------------
# Minimal fallback templates (used if resource files not found)
# ---------------------------------------------------------------------------

_FALLBACK_INDEX = """<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>Learning Path: {{TITLE}}</title></head>
<body><h1>Learning Path: {{TITLE}}</h1><p>{{TOTAL_CHAPTERS}} chapters</p>
{{ROADMAP_ITEMS}}</body></html>"""

_FALLBACK_CHAPTER = """<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>{{TITLE}}</title>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css">
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/contrib/auto-render.min.js"
  onload="renderMathInElement(document.body,{delimiters:[{left:'$$',right:'$$',display:true},{left:'$',right:'$',display:false}]});"></script>
</head><body><h1>Ch.{{CHAPTER_NUM}}: {{TITLE}}</h1>{{CONTENT}}
<div>{{PREV_NAV}} {{NEXT_NAV}}</div></body></html>"""


def main():
    parser = argparse.ArgumentParser(description="Generate learning path HTML site from analysis JSON")
    parser.add_argument("--analysis", required=True, help="Path to analysis.json")
    parser.add_argument("--paper-html", default="", help="Path to paper.html (for linking)")
    parser.add_argument("--out-dir", default="output/learning", help="Output directory for chapters")
    parser.add_argument("--dashboard", action="store_true", default=False,
                        help="Also generate a central dashboard index.html one level above out-dir")
    parser.add_argument("--setup-guide", default="",
                        help="Path to setup-guide.html (if already generated) to link from dashboard")
    parser.add_argument("--index-template",
                        default=str(Path(__file__).parent.parent / "resources" / "nature_index.html"))
    parser.add_argument("--dashboard-template",
                        default=str(Path(__file__).parent.parent / "resources" / "nature_dashboard.html"))
    parser.add_argument("--chapter-template",
                        default=str(Path(__file__).parent.parent / "resources" / "nature_learning.html"))
    args = parser.parse_args()

    if not Path(args.analysis).is_file():
        print(f"ERROR: File not found: {args.analysis}")
        sys.exit(1)

    generate(
        analysis_path=args.analysis,
        paper_html=args.paper_html,
        out_dir=args.out_dir,
        index_template_path=args.index_template,
        chapter_template_path=args.chapter_template,
        dashboard=args.dashboard,
        dashboard_template_path=args.dashboard_template,
        setup_guide_path=args.setup_guide,
    )


if __name__ == "__main__":
    main()

