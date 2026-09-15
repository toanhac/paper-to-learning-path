#!/usr/bin/env python3
"""
generate_setup_guide.py — Extract repo setup instructions from paper content
and produce a self-contained nature-inspired setup-guide.html.

Usage:
    python generate_setup_guide.py \
        --translated output/translated.json \
        --analysis   output/analysis.json \
        --out        output/setup-guide.html \
        [--paper-title "My Paper"] \
        [--authors "Author A, Author B"] \
        [--target-lang vi]
"""

import argparse
import json
import re
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
TEMPLATE_PATH = SKILL_DIR / "resources" / "nature_setup.html"

# ── Heuristic extraction helpers ──────────────────────────────────────────────

def _find_github_url(text: str) -> str:
    """Search full text for any GitHub/GitLab/Bitbucket URL."""
    patterns = [
        r'https?://github\.com/[^\s\)\]"<>]+',
        r'https?://gitlab\.com/[^\s\)\]"<>]+',
        r'https?://bitbucket\.org/[^\s\)\]"<>]+',
    ]
    for p in patterns:
        m = re.search(p, text)
        if m:
            url = m.group().rstrip('.,;')
            return url
    return ""


def _extract_requirements(blocks: list[dict]) -> list[str]:
    """Heuristically detect Python/CUDA requirements from text blocks."""
    found = []
    patterns = [
        r'\b(torch|torchvision|torchaudio|tensorflow|keras|jax)\b',
        r'\b(numpy|scipy|opencv|cv2|PIL|pillow|matplotlib|sklearn|scikit-learn)\b',
        r'\b(transformers|diffusers|accelerate|peft|bitsandbytes)\b',
        r'\b(CUDA|cudatoolkit|cudnn)\s*[\d\.]+',
        r'\b(Python)\s*[\d\.]+',
        r'\brequirements\.txt\b',
        r'\benvironment\.ya?ml\b',
        r'\bpip install\s+([^\s\n]+)',
        r'\bconda install\s+([^\s\n]+)',
    ]
    text = " ".join(b.get("text","") for b in blocks if b.get("type") == "text")
    for p in patterns:
        for m in re.finditer(p, text, re.IGNORECASE):
            val = m.group().strip()
            if val not in found:
                found.append(val)
    return found


def _extract_datasets(blocks: list[dict]) -> list[str]:
    """Heuristically detect dataset names from Experiments section."""
    dataset_kw = [
        r'\b(ImageNet|CIFAR[\-\d]+|COCO|VOC|ScanNet|NYUv2|KITTI|nuScenes|Waymo)\b',
        r'\b(ShapeNet|ModelNet|S3DIS|PointCloud|Tanks and Temples|DTU)\b',
        r'\b(MS-COCO|RefCOCO|VQA|GQA|SQA|VCR)\b',
        r'\b(LAION|CC\d+M|WebImageText|WikiText|Books3|C4)\b',
        r'\b([A-Z][a-z]*(?:[A-Z][a-z]*)*(?:[-\d]+)?)\s+dataset\b',
        r'dataset\s+([A-Z][^\s,\.\(]{2,30})\b',
    ]
    text = " ".join(b.get("text","") for b in blocks if b.get("type") == "text")
    found = []
    for p in dataset_kw:
        for m in re.finditer(p, text):
            val = m.group(0).strip()
            if val not in found and len(val) > 3:
                found.append(val)
    return found[:8]  # Cap at 8


def _build_step_html(num: int, icon: str, id_: str, title: str, content: str) -> str:
    return f"""
<section class="step-section" id="{id_}">
  <div class="step-header">
    <div class="step-badge">{num}</div>
    <span class="step-icon">{icon}</span>
    <h2>{title}</h2>
  </div>
  {content}
</section>
"""


def _code_block(lang: str, code: str, desc: str = "") -> str:
    return f"""<div class="code-block">
  <div class="code-header">
    <span class="code-lang">{lang}</span>
    <button class="copy-btn">Copy</button>
  </div>
  <pre><code>{code}</code></pre>
</div>"""


def _info(type_: str, label: str, text: str) -> str:
    return f"""<div class="info-box {type_}"><div class="box-label">{label}</div><p>{text}</p></div>"""


# ── Section generators ─────────────────────────────────────────────────────────

def gen_clone_section(github_url: str, paper_title: str) -> str:
    if github_url:
        clone_cmd = f"git clone {github_url}\ncd {github_url.rstrip('/').split('/')[-1]}"
        note = f"Repository chính thức của bài báo <em>{paper_title}</em>."
    else:
        clone_cmd = "# Chưa tìm thấy URL repo chính thức trong bài báo.\n# Hãy tìm link trên trang author, arXiv, hoặc paper website và thay vào đây:\ngit clone https://github.com/AUTHOR/REPO_NAME"
        note = "⚠️ Agent không tìm thấy link GitHub trong nội dung bài báo. Hãy tự bổ sung URL chính xác."

    content = f"""
<p>{note}</p>
{_code_block("bash", clone_cmd)}
{_info("note", "💡 Tip", "Dùng <code class='inline-code'>git clone --recursive</code> nếu repo có submodule.")}
"""
    return content


def gen_environment_section(requirements: list[str]) -> str:
    req_text = ""
    if requirements:
        req_text = "<p>Các thư viện/framework được phát hiện trong bài báo:</p><ul>" + \
                   "".join(f"<li><code class='inline-code'>{r}</code></li>" for r in requirements[:10]) + \
                   "</ul>"

    content = f"""
<p>Tạo môi trường ảo Python để tránh xung đột phụ thuộc.</p>
{_info("warning", "⚠️ GPU Requirement", "Hầu hết các bài báo Deep Learning yêu cầu GPU với CUDA. Kiểm tra phần Experiments trong bài báo để biết cấu hình tối thiểu.")}
{_code_block("bash", "# Tạo conda environment (khuyến nghị)\nconda create -n paper_env python=3.10 -y\nconda activate paper_env\n\n# Hoặc dùng venv\npython -m venv .venv\nsource .venv/bin/activate  # Linux/macOS\n# .venv\\Scripts\\activate   # Windows")}
{req_text}
"""
    return content


def gen_dependencies_section(github_url: str) -> str:
    content = f"""
<p>Cài đặt các thư viện cần thiết từ file requirements.</p>
{_code_block("bash", "# Cài từ requirements.txt\npip install -r requirements.txt\n\n# Hoặc từ setup.py / pyproject.toml\npip install -e .\n\n# Hoặc từ environment.yml (conda)\nconda env update -f environment.yml")}
{_info("tip", "💡 Tip", "Nếu gặp lỗi về CUDA version, cài đặt PyTorch phù hợp từ <a href='https://pytorch.org/get-started/locally/' target='_blank'>pytorch.org/get-started/locally</a> trước.")}
{_info("note", "📝 Note", "Một số repo yêu cầu build thêm CUDA extensions. Xem README của repo để biết thêm chi tiết.")}
<!-- AGENT: Add specific dependency installation commands found in the paper/repo here -->
"""
    return content


def gen_dataset_section(datasets: list[str]) -> str:
    if datasets:
        ds_list = "<ul>" + "".join(f"<li>{d}</li>" for d in datasets) + "</ul>"
        ds_note = f"<p>Các dataset được phát hiện trong bài báo:</p>{ds_list}"
    else:
        ds_note = "<p>Xem phần <strong>Experiments</strong> trong bài báo để biết tên dataset cụ thể.</p>"

    content = f"""
{ds_note}
{_info("important", "📦 Quan trọng", "Một số dataset yêu cầu đăng ký tài khoản hoặc chấp nhận điều khoản sử dụng trước khi tải xuống.")}
{_code_block("bash", "# Ví dụ: Tải dataset (thay bằng lệnh cụ thể của repo)\n# Kiểm tra scripts/download_*.sh hoặc README của repo\nmkdir -p data/\n\n# Nếu repo có script tải dataset:\nbash scripts/download_data.sh\n\n# Hoặc dùng wget/gdown:\n# wget -O data/dataset.tar.gz <DATASET_URL>\n# gdown <GOOGLE_DRIVE_ID> -O data/")}
{_code_block("bash", "# Cấu trúc thư mục data thường gặp:\n# data/\n#   ├── train/\n#   ├── val/\n#   └── test/")}
<!-- AGENT: Fill in actual dataset download commands specific to this paper -->
"""
    return content


def gen_training_section() -> str:
    content = f"""
<p>Huấn luyện mô hình từ đầu hoặc fine-tune từ pretrained checkpoint.</p>
{_info("warning", "⚠️ Training Time", "Training các mô hình trong bài báo nghiên cứu thường mất nhiều giờ đến nhiều ngày tùy vào phần cứng. Kiểm tra bảng kết quả trong paper để biết chi tiết.")}
{_code_block("bash", "# Training cơ bản (thay bằng lệnh cụ thể của repo)\npython train.py --config configs/default.yaml\n\n# Training đa GPU (nếu hỗ trợ)\ntorchrun --nproc_per_node=4 train.py --config configs/multi_gpu.yaml\n\n# Training với config tùy chỉnh\npython train.py \\\n    --config configs/default.yaml \\\n    --output_dir ./outputs/experiment_1 \\\n    --epochs 100 \\\n    --batch_size 32")}
{_info("tip", "💡 Quick Test", "Chạy với <code class='inline-code'>--epochs 1 --batch_size 4</code> để kiểm tra pipeline hoạt động trước khi train đầy đủ.")}
<!-- AGENT: Add actual training commands from the paper's repo README or experimental setup section -->
"""
    return content


def gen_inference_section() -> str:
    content = f"""
<p>Chạy inference/demo với pretrained model hoặc model vừa train.</p>
{_code_block("bash", "# Tải pretrained weights (nếu có)\n# Kiểm tra README của repo để lấy link download\n# Hoặc dùng script tải model:\nbash scripts/download_pretrained.sh\n\n# Hoặc từ Hugging Face Hub:\n# from huggingface_hub import hf_hub_download\n# hf_hub_download(repo_id='AUTHOR/MODEL_NAME', filename='model.pth')")}
{_code_block("bash", "# Chạy inference (thay bằng lệnh cụ thể)\npython demo.py --checkpoint outputs/best_model.pth \\\n               --input data/test_samples/ \\\n               --output results/\n\n# Hoặc evaluation:\npython eval.py --checkpoint outputs/best_model.pth \\\n               --dataset data/test/")}
{_code_block("bash", "# Visualize kết quả\npython visualize.py --results results/ --show")}
{_info("note", "📝 Note", "Kết quả inference thường được lưu vào thư mục <code class='inline-code'>results/</code> hoặc <code class='inline-code'>outputs/</code>. Xem README của repo để biết thêm chi tiết.")}
<!-- AGENT: Add actual inference/demo commands from the paper's repo -->
"""
    return content


def gen_faq_section() -> str:
    faqs = [
        ("CUDA out of memory — phải làm gì?",
         "Giảm batch_size xuống (ví dụ: <code class='inline-code'>--batch_size 8</code>). Nếu vẫn lỗi, thử gradient checkpointing hoặc mixed precision (<code class='inline-code'>--fp16</code>). Xem thêm phần <em>Implementation Details</em> trong bài báo."),
        ("ModuleNotFoundError / ImportError",
         "Chạy lại <code class='inline-code'>pip install -r requirements.txt</code>. Kiểm tra Python version (thường cần 3.8+). Đảm bảo đang ở đúng môi trường ảo."),
        ("Kết quả không match với bảng trong paper",
         "Kiểm tra: (1) đúng pretrained checkpoint chưa, (2) preprocessing data đúng chưa, (3) evaluation metric đúng chưa. Nhiều repo có README note về reproducibility gap."),
        ("RuntimeError: Expected all tensors to be on the same device",
         "Đảm bảo model và data đều được chuyển sang cùng device: thêm <code class='inline-code'>.to(device)</code> cho tất cả tensors."),
        ("Chạy demo mà không có GPU",
         "Thêm flag <code class='inline-code'>--device cpu</code> hoặc chỉnh config <code class='inline-code'>device: 'cpu'</code>. Inference sẽ chậm hơn nhưng vẫn chạy được với model nhỏ."),
        ("Tìm hyperparameters tốt nhất",
         "Xem bảng ablation study trong bài báo (thường ở Section 4 hoặc Appendix). Các giá trị tốt nhất thường được highlight trong bảng."),
    ]

    faq_html = ""
    for q, a in faqs:
        faq_html += f"""<details>
  <summary>{q}</summary>
  <div><p>{a}</p></div>
</details>
"""

    content = f"""
<p>Các câu hỏi thường gặp khi setup và chạy code từ bài báo nghiên cứu.</p>
{faq_html}
<!-- AGENT: Add paper-specific FAQ items based on the paper's known limitations and common issues -->
"""
    return content


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Generate setup guide HTML for a research paper")
    parser.add_argument("--translated", required=True, help="Path to translated.json")
    parser.add_argument("--analysis",   default="",   help="Path to analysis.json (optional)")
    parser.add_argument("--out",        required=True, help="Output HTML path (e.g. output/setup-guide.html)")
    parser.add_argument("--paper-title", default="",  help="Override paper title")
    parser.add_argument("--authors",    default="",   help="Override authors string")
    parser.add_argument("--target-lang", default="vi", help="Target language code")
    parser.add_argument("--first-chapter", default="learning/index.html", help="URL to first chapter or learning index")
    args = parser.parse_args()

    # Load translated.json
    translated_path = Path(args.translated)
    if not translated_path.exists():
        print(f"❌ translated.json not found: {translated_path}", file=sys.stderr)
        sys.exit(1)
    with open(translated_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    blocks = data.get("blocks", [])
    meta = data.get("meta", {})
    paper_title = args.paper_title or meta.get("title", "Research Paper")
    authors = args.authors or meta.get("authors", "")

    # Load analysis.json (optional)
    analysis = {}
    if args.analysis and Path(args.analysis).exists():
        with open(args.analysis, "r", encoding="utf-8") as f:
            analysis = json.load(f)

    # Extract heuristic data
    full_text = " ".join(b.get("text", "") for b in blocks if b.get("type") == "text")
    github_url = _find_github_url(full_text)
    requirements = _extract_requirements(blocks)
    datasets = _extract_datasets(blocks)

    # Build content sections
    sections_html = (
        _build_step_html(1, "📥", "clone",        "Clone Repository",           gen_clone_section(github_url, paper_title)) +
        _build_step_html(2, "🐍", "environment",  "Cài đặt môi trường Python",  gen_environment_section(requirements)) +
        _build_step_html(3, "📦", "dependencies", "Cài đặt Dependencies",       gen_dependencies_section(github_url)) +
        _build_step_html(4, "🗄️", "dataset",      "Tải Dataset",                gen_dataset_section(datasets)) +
        _build_step_html(5, "🏋️", "training",     "Training",                   gen_training_section()) +
        _build_step_html(6, "🚀", "inference",    "Inference / Demo",           gen_inference_section()) +
        _build_step_html(7, "❓", "faq",          "FAQ & Troubleshooting",      gen_faq_section())
    )

    # Load and render template
    if not TEMPLATE_PATH.exists():
        print(f"❌ Template not found: {TEMPLATE_PATH}", file=sys.stderr)
        sys.exit(1)
    template = TEMPLATE_PATH.read_text(encoding="utf-8")

    first_chapter = args.first_chapter

    html = (template
        .replace("{{PAPER_TITLE}}", paper_title)
        .replace("{{AUTHORS}}", authors)
        .replace("{{TARGET_LANG}}", args.target_lang)
        .replace("{{FIRST_CHAPTER}}", first_chapter)
        .replace("{{SETUP_CONTENT}}", sections_html)
    )

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html, encoding="utf-8")

    print(f"✅ Setup guide generated: {out_path}")
    if github_url:
        print(f"   GitHub URL found: {github_url}")
    else:
        print("   ⚠️  No GitHub URL found — fill in the placeholder manually")
    if datasets:
        print(f"   Datasets detected: {', '.join(datasets[:4])}")


if __name__ == "__main__":
    main()
