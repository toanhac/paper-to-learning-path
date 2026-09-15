#!/usr/bin/env python3
"""
analyze_paper.py — Analyze a translated paper JSON to produce a structured
prerequisite map and chapter outline for learning path generation.

This script uses HEURISTIC analysis (no external LLM API required).
It outputs analysis.json which the AI AGENT reads to write chapter content.

Usage:
    python analyze_paper.py \\
        --json translated.json \\
        --audience "ML engineer familiar with CNNs and Transformers" \\
        --out analysis.json \\
        [--lang vi]
"""

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path


# ---------------------------------------------------------------------------
# Domain keyword → prerequisite topic mapping
# Extend this dictionary for new research fields.
# ---------------------------------------------------------------------------
DOMAIN_MAP = {
    # Computer Vision / 3D
    "gaussian": {
        "id": "gaussian-splatting",
        "title": "3D Gaussian Splatting",
        "importance": "critical",
        "phase": "Phase 2 — Core",
        "description": "Scene representation using 3D Gaussian primitives, splatting/rasterization, and spherical harmonics",
        "concepts": ["Gaussian primitive", "splatting", "rasterization", "spherical harmonics", "alpha compositing"],
        "estimated_reading_min": 35,
    },
    "nerf": {
        "id": "neural-rendering",
        "title": "Neural Rendering & NeRF",
        "importance": "important",
        "phase": "Phase 1 — Foundations",
        "description": "Volume rendering, neural radiance fields, and implicit scene representations",
        "concepts": ["volume rendering", "ray marching", "radiance field", "implicit representation"],
        "estimated_reading_min": 30,
    },
    "camera": {
        "id": "3d-vision-fundamentals",
        "title": "3D Computer Vision Fundamentals",
        "importance": "critical",
        "phase": "Phase 1 — Foundations",
        "description": "Camera models, projection, 3D coordinate systems, and multi-view geometry",
        "concepts": ["pinhole camera", "projection matrix", "intrinsics", "extrinsics", "epipolar geometry"],
        "estimated_reading_min": 25,
    },
    "depth": {
        "id": "depth-estimation",
        "title": "Depth Estimation & Multi-View Stereo",
        "importance": "important",
        "phase": "Phase 2 — Core",
        "description": "Monocular depth estimation, cost volumes, and multi-view stereo",
        "concepts": ["monocular depth", "cost volume", "stereo matching", "MVS", "ViT/DPT"],
        "estimated_reading_min": 25,
    },
    "recurrent": {
        "id": "recurrent-optimization",
        "title": "Recurrent Networks & Learning to Optimize",
        "importance": "important",
        "phase": "Phase 3 — Advanced",
        "description": "GRU update modules, iterative refinement, and learning to optimize paradigm",
        "concepts": ["GRU", "ConvGRU", "iterative refinement", "RAFT", "weight sharing", "deep equilibrium"],
        "estimated_reading_min": 30,
    },
    "transformer": {
        "id": "transformers-attention",
        "title": "Transformers & Attention Mechanisms",
        "importance": "important",
        "phase": "Phase 1 — Foundations",
        "description": "Self-attention, multi-head attention, Vision Transformers (ViT)",
        "concepts": ["self-attention", "multi-head attention", "ViT", "positional encoding", "cross-attention"],
        "estimated_reading_min": 25,
    },
    "diffusion": {
        "id": "diffusion-models",
        "title": "Diffusion Models",
        "importance": "important",
        "phase": "Phase 2 — Core",
        "description": "Denoising diffusion probabilistic models, score matching, DDPM/DDIM",
        "concepts": ["forward process", "reverse process", "score matching", "DDPM", "DDIM", "classifier-free guidance"],
        "estimated_reading_min": 35,
    },
    "reinforcement": {
        "id": "reinforcement-learning",
        "title": "Reinforcement Learning Basics",
        "importance": "important",
        "phase": "Phase 2 — Core",
        "description": "MDP, policy gradient, value functions, Q-learning",
        "concepts": ["MDP", "policy", "reward", "Q-function", "policy gradient", "PPO"],
        "estimated_reading_min": 30,
    },
    "point cloud": {
        "id": "point-cloud-processing",
        "title": "Point Cloud Processing",
        "importance": "helpful",
        "phase": "Phase 1 — Foundations",
        "description": "3D point cloud representation, PointNet, voxel-based methods",
        "concepts": ["point cloud", "PointNet", "voxelization", "k-NN", "FPS"],
        "estimated_reading_min": 20,
    },
    "flow": {
        "id": "optical-flow",
        "title": "Optical Flow & Motion Estimation",
        "importance": "helpful",
        "phase": "Phase 1 — Foundations",
        "description": "Classical and deep optical flow methods, RAFT",
        "concepts": ["optical flow", "warping", "correlation volume", "RAFT", "FlowNet"],
        "estimated_reading_min": 20,
    },
}

# General ML prerequisites always included
BASE_PREREQUISITES = {
    "id": "deep-learning-basics",
    "title": "Deep Learning Fundamentals",
    "importance": "critical",
    "phase": "Phase 0 — Prerequisites",
    "description": "Backpropagation, loss functions, optimizers, training loop, CNNs",
    "concepts": ["backpropagation", "gradient descent", "Adam", "CNN", "encoder-decoder", "batch norm"],
    "estimated_reading_min": 20,
}


# ---------------------------------------------------------------------------
# Text analysis helpers
# ---------------------------------------------------------------------------

def _collect_text(data: dict) -> str:
    """Collect all translatable text from the document."""
    parts = []
    for s in data.get("sections", []):
        if s.get("type") not in ("math_block",):
            parts.append(s.get("text", ""))
    return " ".join(parts).lower()


def _extract_glossary_terms(data: dict) -> dict[str, str]:
    """Extract any glossary terms stored in translation metadata."""
    # Paragraphs with parenthetical definitions: "Term (definition)"
    glossary = {}
    abbr_re = re.compile(r"\b([A-Z][A-Za-z]+(?:\s[A-Z][A-Za-z]+)*)\s*\(([^)]{5,80})\)")
    for s in data.get("sections", []):
        text = s.get("text_original", s.get("text", ""))
        for m in abbr_re.finditer(text):
            term, defn = m.group(1), m.group(2)
            if len(term.split()) <= 4:
                glossary[term] = defn
    return glossary


def _detect_field(text: str) -> str:
    """Rough field detection from keyword frequency."""
    field_keywords = {
        "Computer Vision / 3D Rendering": ["gaussian", "nerf", "rendering", "splat", "point cloud", "camera", "3d"],
        "Natural Language Processing": ["token", "language model", "bert", "gpt", "llm", "text", "embedding"],
        "Reinforcement Learning": ["reward", "policy", "agent", "environment", "q-value", "mdp"],
        "Generative Modeling": ["diffusion", "vae", "gan", "score", "latent", "generative"],
        "Medical Imaging": ["segmentation", "mri", "ct scan", "clinical", "radiology"],
        "Robotics": ["robot", "manipulation", "grasping", "locomotion", "sim-to-real"],
    }
    counts = {field: sum(text.count(kw) for kw in kws) for field, kws in field_keywords.items()}
    return max(counts, key=counts.get)


def _detect_difficulty(text: str, section_count: int) -> str:
    """Estimate paper difficulty from vocabulary density."""
    advanced_terms = ["ablation", "convergence", "latent space", "posterior", "covariance",
                      "eigenvalue", "manifold", "variational", "stochastic", "KL divergence",
                      "rasterization", "spherical harmonics", "epipolar", "quaternion"]
    score = sum(1 for term in advanced_terms if term in text)
    if score >= 6 or section_count > 8:
        return "advanced"
    elif score >= 3:
        return "intermediate"
    return "beginner"


def _select_prerequisites(text: str) -> list[dict]:
    """Select relevant prerequisite topics based on keyword presence."""
    prereqs = []
    seen_ids = set()

    # Always include deep learning basics for ML papers
    prereqs.append(BASE_PREREQUISITES)
    seen_ids.add(BASE_PREREQUISITES["id"])

    # Score each domain entry
    scored = []
    for keyword, info in DOMAIN_MAP.items():
        if keyword in text and info["id"] not in seen_ids:
            count = text.count(keyword)
            scored.append((count, info))
            seen_ids.add(info["id"])

    # Sort by frequency, then importance
    importance_order = {"critical": 3, "important": 2, "helpful": 1}
    scored.sort(key=lambda x: (x[0], importance_order.get(x[1]["importance"], 0)), reverse=True)

    # Take top 6 (to keep learning path manageable)
    for _, info in scored[:6]:
        prereqs.append(info)

    # Sort by phase order
    phase_order = {"Phase 0 — Prerequisites": 0, "Phase 1 — Foundations": 1,
                   "Phase 2 — Core": 2, "Phase 3 — Advanced": 3, "Phase 4 — Paper": 4}
    prereqs.sort(key=lambda x: phase_order.get(x.get("phase", ""), 5))

    return prereqs


def _extract_paper_sections(data: dict) -> list[dict]:
    """Extract paper section headings and their content summaries."""
    sections = []
    current_heading = None
    current_text = []

    for s in data.get("sections", []):
        if s.get("type") == "heading":
            if current_heading and current_text:
                sections.append({
                    "heading": current_heading,
                    "summary": " ".join(current_text)[:300] + "...",
                    "key_concepts": [],
                })
            current_heading = s.get("text", "")
            current_text = []
        elif s.get("type") == "paragraph" and current_heading:
            current_text.append(s.get("text", "")[:200])

    if current_heading and current_text:
        sections.append({
            "heading": current_heading,
            "summary": " ".join(current_text)[:300] + "...",
            "key_concepts": [],
        })

    return sections


def _build_agent_prompt(paper_title: str, field: str, difficulty: str,
                         prerequisites: list[dict], sections: list[dict],
                         target_lang: str, audience: str) -> str:
    prereq_list = "\n".join(
        f"  - Chapter: '{p['title']}' (importance: {p['importance']})\n"
        f"    Concepts: {', '.join(p['concepts'][:4])}"
        for p in prerequisites
    )
    section_list = "\n".join(
        f"  - {s['heading']}: {s['summary'][:150]}"
        for s in sections[:8]
    )

    return f"""You are writing educational content for a learning path about this research paper:

PAPER: {paper_title}
FIELD: {field}
DIFFICULTY: {difficulty}
TARGET AUDIENCE: {audience}
OUTPUT LANGUAGE: {target_lang}

The learning path has these chapters (in order):
{prereq_list}

The paper covers these sections:
{section_list}

FOR EACH CHAPTER HTML FILE:
1. Read the <!-- AGENT: ... --> comments in the file carefully
2. Replace EACH comment block with well-written educational content in {target_lang}
3. Use the HTML components defined in the template (info-box, math-block, figure, etc.)
4. Write for the stated audience: {audience}
5. Each concept: motivation first → intuition → formal definition → example
6. Reference previous chapters when building on prior knowledge
7. End with a "What's Next" paragraph

FOR THE FINAL DEEP-DIVE CHAPTER:
- Walk through the paper section by section in the same order as listed above
- Explain the key ideas of each section clearly
- Include the core math from the paper with explanation
- Add a "Key Takeaways" summary at the end

QUALITY STANDARDS:
- Educational prose, not bullet dumps
- Concrete analogies before abstract math
- All technical terms from the glossary should be used consistently
- All math must be valid KaTeX LaTeX inside $...$ or $$...$$
"""


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def analyze(json_path: str, out_path: str, audience: str, target_lang: str):
    with open(json_path, encoding="utf-8") as f:
        data = json.load(f)

    meta = data.get("metadata", {})
    translation = data.get("translation", {})
    title = meta.get("title", "Research Paper")
    tgt = translation.get("target", target_lang)

    full_text = _collect_text(data)
    glossary = _extract_glossary_terms(data)
    field = _detect_field(full_text)
    section_count = sum(1 for s in data.get("sections", []) if s.get("type") == "heading")
    difficulty = _detect_difficulty(full_text, section_count)
    prerequisites = _select_prerequisites(full_text)
    paper_sections = _extract_paper_sections(data)
    agent_prompt = _build_agent_prompt(title, field, difficulty, prerequisites,
                                       paper_sections, tgt, audience)

    # Number prerequisites 01, 02 …
    for i, p in enumerate(prerequisites, start=1):
        p["chapter_num"] = i
        p["filename"] = f"{i:02d}-{p['id']}.html"

    # Add final paper deep-dive chapter
    prerequisites.append({
        "chapter_num": len(prerequisites) + 1,
        "id": "paper-deep-dive",
        "filename": f"{len(prerequisites)+1:02d}-paper-deep-dive.html",
        "title": f"Paper Deep Dive: {title}",
        "importance": "critical",
        "phase": "Phase 4 — Paper",
        "description": f"Full walkthrough of '{title}' — architecture, methods, results, and key insights",
        "concepts": [s["heading"] for s in paper_sections[:6]],
        "estimated_reading_min": 45,
    })

    result = {
        "paper": {
            "title": title,
            "authors": meta.get("authors", ""),
            "field": field,
            "difficulty": difficulty,
            "pages": meta.get("pages", 0),
            "source_lang": translation.get("source", "?"),
            "target_lang": tgt,
        },
        "target_audience": audience,
        "prerequisites": prerequisites,
        "glossary": glossary,
        "paper_sections": paper_sections,
        "agent_prompt": agent_prompt,
        "total_chapters": len(prerequisites),
        "total_reading_min": sum(p.get("estimated_reading_min", 20) for p in prerequisites),
    }

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"✅ Analysis complete → {out_path}")
    print(f"   Field:       {field}")
    print(f"   Difficulty:  {difficulty}")
    print(f"   Chapters:    {len(prerequisites)}")
    print(f"   Glossary:    {len(glossary)} terms")
    print(f"   Est. reading: ~{result['total_reading_min']} min total")


def main():
    parser = argparse.ArgumentParser(description="Analyze paper JSON to produce learning path structure")
    parser.add_argument("--json", required=True, help="Path to translated.json")
    parser.add_argument("--out", default="analysis.json", help="Output path for analysis.json")
    parser.add_argument("--audience", default="Reader familiar with deep learning basics",
                        help="Target audience description")
    parser.add_argument("--lang", default="", help="Target language (overrides translated.json)")
    args = parser.parse_args()

    if not Path(args.json).is_file():
        print(f"ERROR: File not found: {args.json}")
        sys.exit(1)

    analyze(args.json, args.out, args.audience, args.lang)


if __name__ == "__main__":
    main()
