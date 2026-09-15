<div align="center">

# 📄 paper-to-learning-path

**Kỹ năng AI Agent chuyển đổi bài báo khoa học (PDF) thành trang HTML dịch thuật đẹp mắt, Lộ trình Tự học đa chương và Hướng dẫn Setup Repository chi tiết.**

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

## 🌟 Skill này làm được gì?

Khi đọc bài báo AI/ML phức tạp (*3D Gaussian Splatting, Diffusion Models, Transformer, NeRF...*), bạn thường gặp 2 rào cản lớn:

1. **Rào cản ngôn ngữ & định dạng** — Công cụ dịch thông thường làm vỡ công thức LaTeX, mất hình ảnh, file PDF khó đọc.
2. **Thiếu kiến thức nền tảng** — Bài báo phức tạp giả định bạn đã biết rất nhiều khái niệm. Không có nền tảng, đọc rất khó hiểu.

**`paper-to-learning-path`** giải quyết cả 2 bằng một hệ sinh thái học tập hoàn chỉnh:

| Output | Mô tả |
|--------|-------|
| 📄 `paper.html` | Bài báo dịch tự chứa — KaTeX math, ảnh nhúng, mục lục sidebar |
| 🗺️ `index.html` | Dashboard trung tâm — stats, quick links, lộ trình học |
| 📚 `learning/` | Website học đa chương — C1: Transformer, C2: Attention, … → Deep-dive |
| 🔧 `setup-guide.html` | Hướng dẫn setup repo — clone, môi trường, dataset, training, inference, FAQ |

---

## 🚀 Bắt đầu nhanh

### 1. Clone repo

```bash
git clone https://github.com/ToanHac/paper-to-learning-path.git
cd paper-to-learning-path
```

### 2. Cài đặt thư viện Python

```bash
pip install pymupdf deep-translator langdetect
```

### 3. Cài đặt cho AI assistant của bạn (xem hướng dẫn bên dưới)

Sau đó chỉ cần yêu cầu AI assistant của bạn:

```
Dịch ./paper.pdf sang tiếng Việt và tạo lộ trình tự học đầy đủ với hướng dẫn setup repo.
```

---

## 🛠️ Hướng dẫn cài đặt cho từng AI Assistant

### ⚡ Google Antigravity

Antigravity tự động phát hiện skill trong `.agents/skills/<name>/SKILL.md` — không cần cấu hình thêm.

**Cách A — Per-project (khuyến nghị):**

```bash
# Từ thư mục gốc dự án của bạn
cp -r /path/to/paper-to-learning-path/.agents/skills/paper-to-learning-path \
      .agents/skills/paper-to-learning-path
```

**Cách B — Global (dùng cho tất cả project):**

```bash
# macOS / Linux / WSL
cp -r .agents/skills/paper-to-learning-path \
      ~/.gemini/antigravity/skills/paper-to-learning-path

# Windows (PowerShell)
Copy-Item -Recurse .agents\skills\paper-to-learning-path `
  "$env:USERPROFILE\.gemini\antigravity\skills\paper-to-learning-path"
```

**Kích hoạt:** Mở Antigravity trong project và gõ:

```
Dịch ./papers/attention.pdf sang tiếng Việt và tạo lộ trình học đầy đủ.
```

Skill tự động kích hoạt khi bạn đề cập đến file PDF hoặc bài báo khoa học. Không cần gọi tên skill.

---

### 🤖 Anthropic Claude Code

Hỗ trợ 2 cách cài đặt:

#### Cách 1 — Claude Plugin (Marketplace)

```bash
/plugin marketplace add ToanHac/paper-to-learning-path
/plugin install paper-to-learning-path@paper-to-learning-path
```

#### Cách 2 — Cài thủ công

```bash
# Sao chép skill vào đường dẫn Claude nhận diện
cp -r .claude/skills/paper-to-learning-path ~/.claude/skills/paper-to-learning-path

# Hoặc cài per-project
cp -r .claude/skills/paper-to-learning-path .claude/skills/paper-to-learning-path
```

Sau đó thêm vào project context của Claude:

```bash
/add-dir .claude/skills/paper-to-learning-path
```

**Các lệnh mẫu:**

```
Dịch ./paper.pdf sang tiếng Việt và tạo lộ trình học.
```

```
Chuyển bài báo này ./resplat.pdf sang tiếng Pháp với hướng dẫn cài đặt đầy đủ.
```

> **Ghi chú:** File `CLAUDE.md` trong thư mục gốc được Claude Code tự đọc như project context — không cần cấu hình thêm nếu bạn clone toàn bộ repo.

---

### 🖱️ Cursor IDE

File `.cursor/rules/paper-to-learning-path.mdc` được Cursor Agent tự nhận diện.

**Cài đặt:**

```bash
# Sao chép rule vào project của bạn
mkdir -p .cursor/rules
cp .cursor/rules/paper-to-learning-path.mdc .cursor/rules/

# Hoặc sao chép file .cursorrules vào thư mục gốc project
cp .cursorrules /path/to/your/project/.cursorrules
```

**Sao chép toàn bộ skill (kèm scripts):**

```bash
cp -r .agents/skills/paper-to-learning-path \
      /path/to/your/project/.agents/skills/paper-to-learning-path
```

**Kích hoạt:** Mở Cursor Composer (`Ctrl+Shift+P` → "Open Composer") và gõ:

```
Dịch ./paper.pdf sang tiếng Việt và tạo lộ trình tự học.
```

Cursor tự động áp dụng rule cho các yêu cầu dịch/chuyển đổi PDF.

---

### 🌊 Windsurf (Cascade)

**Cài đặt:**

```bash
# Sao chép Windsurf rules vào thư mục gốc project
cp .windsurfrules /path/to/your/project/.windsurfrules

# Sao chép skill scripts
cp -r .agents/skills/paper-to-learning-path \
      /path/to/your/project/.agents/skills/paper-to-learning-path
```

**Kích hoạt:** Mở Windsurf Cascade chat và gõ:

```
Dùng skill paper-to-learning-path để dịch ./paper.pdf sang tiếng Việt.
```

---

### 🧩 Cline / Roo Code

**Cài đặt:**

```bash
cp .clinerules /path/to/your/project/.clinerules
cp -r .agents/skills/paper-to-learning-path \
      /path/to/your/project/.agents/skills/paper-to-learning-path
```

**Kích hoạt:** Trong Cline / Roo Code chat:

```
Dịch ./paper.pdf sang tiếng Việt với lộ trình học tự động.
```

---

### ⌨️ Aider

```bash
aider --read .agents/skills/paper-to-learning-path/SKILL.md
```

Sau đó gõ:

```
/ask Dịch ./paper.pdf sang tiếng Việt với lộ trình học.
```

---

### 🖥️ CLI Độc lập (Không cần AI)

Chạy toàn bộ pipeline trực tiếp từ terminal:

```bash
# Interactive mode — hỏi bạn các tùy chọn trước khi chạy
python .agents/skills/paper-to-learning-path/scripts/cli.py --pdf paper.pdf

# Full pipeline (bài báo + lộ trình học + setup guide)
python .agents/skills/paper-to-learning-path/scripts/cli.py \
    --pdf paper.pdf \
    --target vi \
    --learning-path \
    --setup-guide

# Chỉ dịch bài báo, không tạo lộ trình học
python .agents/skills/paper-to-learning-path/scripts/cli.py \
    --pdf paper.pdf --target fr \
    --no-learning-path --no-setup-guide
```

---

## 💬 Câu lệnh mẫu cho AI Assistant

Sau khi cài đặt, chỉ cần mô tả yêu cầu bằng ngôn ngữ tự nhiên:

```
Dịch ./papers/attention.pdf sang tiếng Việt và tạo lộ trình tự học đầy đủ
với hướng dẫn setup repo.
```

```
Chuyển bài báo ./resplat.pdf sang tiếng Pháp. Tôi cần lộ trình học cho
người mới bắt đầu chỉ biết Python cơ bản.
```

```
Dịch ./3dgs.pdf sang tiếng Trung (zh). Chỉ dịch bài báo, không cần lộ trình học.
```

```
Tạo hướng dẫn setup repo cho bài báo ./resplat.pdf — tôi muốn clone, cài môi trường
và chạy demo thử.
```

---

## 🏗️ Kiến trúc Pipeline (12 bước)

```
                       [ Input: PDF File ]
                                │
                                ▼
    [Bước 1]  check_deps.py      ──► Kiểm tra thư viện Python
                                │
                                ▼
    [Bước 2]  extract_pdf.py     ──► Tách Text + Công thức LaTeX + Ảnh PNG
                                │
                                ▼
    [Bước 3]  detect_lang.py     ──► Tự nhận diện ngôn ngữ gốc
                                │
                                ▼
    [Bước 4]  translate_content  ──► Dịch thuật (LaTeX placeholders bảo vệ)
                                │
                 ┌──────────────┴──────────────┐
                 ▼                             ▼
    [Bước 5] render_html.py         [Bước 6] analyze_paper.py
    ──► paper.html (Nature UI)       ──► Phân tích khái niệm & prerequisites
                                                │
                                                ▼
                                    [Bước 7] generate_setup_guide.py
                                     ──► setup-guide.html (nếu yêu cầu)
                                                │
                                                ▼
                                    [Bước 8] generate_learning_path.py
                                     ──► Dashboard index.html + learning/ chapters
                                                │
                                                ▼
                                    [Bước 9-11] AI Agent viết nội dung
                                     ──► Hệ sinh thái học tập hoàn chỉnh!
```

---

## 📂 Cấu trúc thư mục

```
paper-to-learning-path/
├── README.md                                   # Hướng dẫn Tiếng Anh
├── README.vi.md                                # Hướng dẫn Tiếng Việt (file này)
├── LICENSE                                     # Giấy phép MIT
├── CHANGELOG.md                                # Lịch sử cập nhật
├── CLAUDE.md                                   # Context cho Claude Code
├── .cursorrules                                # Quy tắc fallback cho Cursor
├── .clinerules                                 # Quy tắc cho Cline / Roo Code
├── .windsurfrules                              # Quy tắc cho Windsurf
├── install.sh                                  # Script cài đặt Linux/macOS
├── install.ps1                                 # Script cài đặt Windows
│
├── .agents/skills/paper-to-learning-path/      ← Thư mục Skill chính
│   ├── SKILL.md                               # Hướng dẫn cho Agent (12 bước)
│   ├── scripts/
│   │   ├── check_deps.py                      # Kiểm tra package
│   │   ├── extract_pdf.py                     # Trích xuất PDF
│   │   ├── detect_lang.py                     # Tự động nhận diện ngôn ngữ
│   │   ├── translate_content.py               # Dịch thuật & bảo vệ công thức
│   │   ├── render_html.py                     # Tạo HTML bài báo
│   │   ├── analyze_paper.py                   # Phân tích prerequisites
│   │   ├── generate_learning_path.py          # Tạo lộ trình học + dashboard
│   │   ├── generate_setup_guide.py            # Tạo hướng dẫn setup repo
│   │   └── cli.py                             # CLI pipeline runner
│   ├── resources/
│   │   ├── nature_paper.html                  # Template bài báo dịch
│   │   ├── nature_dashboard.html              # Template dashboard trung tâm
│   │   ├── nature_index.html                  # Template roadmap
│   │   ├── nature_learning.html               # Template từng chương học
│   │   └── nature_setup.html                  # Template setup guide
│   └── references/
│       ├── platform-notes.md
│       ├── dependencies.md
│       ├── translation-engines.md
│       └── template-design.md
│
├── .claude/skills/paper-to-learning-path/      ← Mirror cho Claude Code
├── .claude-plugin/                              ← Plugin manifest Claude
│   ├── plugin.json
│   └── marketplace.json
├── .cursor/rules/paper-to-learning-path.mdc    ← Rule tự kích hoạt Cursor
├── docs/how-it-works.md                        ← Kiến trúc kỹ thuật chi tiết
└── examples/resplat/                           ← Demo thực tế (ReSplat ECCV 2025)
```

---

## 🎨 Ngôn ngữ thiết kế Nature-Inspired

Tất cả các trang HTML được tạo ra đều dùng chung một hệ thống thiết kế nhất quán:

| Token | Giá trị | Dùng cho |
|-------|---------|---------|
| `--moss` | `#5a7a55` | Accent chính (nút, link) |
| `--bg` | `#f5f0e8` | Nền giấy da ấm áp |
| `--surface` | `#faf7f2` | Bề mặt thẻ card |
| `--lake` | `#4a7a8a` | Accent phụ |
| `--amber` | `#8a6e3a` | Accent trang setup guide |
| `--stone` | `#8a7e6e` | Chữ thứ cấp |

- **Typography:** `Source Serif 4` cho nội dung, `Inter` cho UI, `JetBrains Mono` cho code & công thức
- **Transitions:** Hiệu ứng ánh sáng thiên nhiên dịu nhẹ (220ms ease)
- **Math:** KaTeX auto-render trên tất cả các trang
- **Info boxes:** Ghi chú 📝 · Mẹo 💡 · Cảnh báo ⚠️ · Quan trọng 🔑

---

## 🤝 Đóng góp phát triển

Mọi đóng góp từ cộng đồng đều được hoan nghênh!

1. Fork repository
2. Tạo branch: `git checkout -b feature/tinh-nang-moi`
3. Commit: `git commit -m 'feat: Thêm tính năng mới'`
4. Push: `git push origin feature/tinh-nang-moi`
5. Tạo Pull Request

---

## 📄 Bản quyền

Phát hành dưới [Giấy phép MIT](LICENSE). Tự do sử dụng cho mục đích cá nhân, học thuật và thương mại.
