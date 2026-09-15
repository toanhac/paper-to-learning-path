<div align="center">

# 📄 paper-to-learning-path

**Kỹ năng AI Agent chuyển đổi bài báo khoa học (PDF) thành trang HTML dịch thuật đẹp mắt & tự động tạo Lộ trình Tự học (Learning Path) từ kiến thức nền tảng.**

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

## 🌟 Giới thiệu

Khi đọc một bài báo nghiên cứu phức tạp (ví dụ: *3D Gaussian Splatting, Diffusion Models, Transformer variants*), người đọc thường gặp 2 rào cản lớn:
1. **Rào cản ngôn ngữ & định dạng:** File PDF khó đọc, dịch bằng Google thông thường làm vỡ công thức toán học ($\LaTeX$) và mất hình ảnh.
2. **Thiếu kiến thức nền tảng (Prerequisites):** Không thể hiểu phương pháp mới nếu chưa nắm vững các khái niệm cơ sở của lĩnh vực đó.

**`paper-to-learning-path`** giải quyết triệt để 2 vấn đề trên:
- **Dịch thuật giữ nguyên công thức:** Toàn bộ công thức toán học $\LaTeX$ và trích dẫn được bảo vệ tuyệt đối, kết xuất đẹp mắt với KaTeX.
- **Tự trích xuất ảnh:** Mọi sơ đồ, đồ thị từ file PDF được xuất thành file PNG và nhúng trực tiếp dạng Base64 vào HTML tự chứa (self-contained).
- **Giao diện Cảm hứng Thiên nhiên (Nature-inspired UI):** Tông màu dịu mắt (rêu, cát, đá, hồ nước), thanh tiến trình đọc, mục lục tự động cuộn thông minh.
- **Tự động phân tích & tạo Lộ trình học (Learning Path):** AI phân tích bài báo, xác định các chủ đề nền tảng cần biết, và sinh ra website học tập đa chương (gồm trang Roadmap + từng chương kiến thức + chương Deep Dive bài báo).

---

## 🚀 Cài đặt nhanh (1 Lệnh)

### macOS / Linux / WSL
```bash
curl -fsSL https://raw.githubusercontent.com/ToanHac/paper-to-learning-path/main/install.sh | bash
```

### Windows (PowerShell)
```powershell
irm https://raw.githubusercontent.com/ToanHac/paper-to-learning-path/main/install.ps1 | iex
```

### Hoặc cài đặt thủ công bằng Python:
```bash
git clone https://github.com/ToanHac/paper-to-learning-path.git
cd paper-to-learning-path
pip install pymupdf deep-translator langdetect
python scripts/install.py --all
```

---

## 🛠️ Hướng dẫn tích hợp cho từng Agent Platform

| AI Platform | Cách cài đặt & Kích hoạt |
| :--- | :--- |
| **Google Antigravity** | Đặt thư mục vào `.agents/skills/paper-to-learning-path` hoặc `~/.gemini/antigravity/skills/`. Antigravity sẽ tự động nhận diện skill khi bạn nhắc đến PDF / bài báo. |
| **Anthropic Claude Code** | Cài đặt qua Plugin: sao chép vào `.claude/skills/paper-to-learning-path/` hoặc dùng lệnh `/add-dir .agents/skills/paper-to-learning-path`. |
| **Cursor IDE** | Quy tắc đã được cấu hình sẵn trong `.cursor/rules/paper-to-learning-path.mdc`. Cursor Agent sẽ tự kích hoạt khi bạn mở file PDF. |
| **Windsurf (Cascade)** | Đã tích hợp qua `.windsurfrules`. Chỉ cần yêu cầu Cascade xử lý bài báo trong chat. |
| **Cline / Roo Code** | Đã tích hợp qua `.clinerules`. Gọi lệnh dịch hoặc tạo lộ trình trực tiếp trong khung chat. |
| **Aider** | Chạy: `aider --read .agents/skills/paper-to-learning-path/SKILL.md` |
| **CLI Độc lập (Không cần AI)** | Chạy trực tiếp qua terminal: `python scripts/cli.py --pdf paper.pdf --target vi` |

---

## 💬 Câu lệnh mẫu để yêu cầu AI Agent

Sau khi cài đặt, bạn chỉ cần mở AI Agent lên và gửi câu lệnh:

```text
Dịch bài báo ./papers/2510.08575v3.pdf sang tiếng Việt và tạo lộ trình tự học chi tiết.
```

```text
Convert this research paper ./attention.pdf to Vietnamese with a complete learning path for a beginner.
```

```text
Dịch file ./resplat.pdf sang tiếng Việt (chỉ dịch bài báo, không cần lộ trình học).
```

---

## 🏗️ Kiến trúc Pipeline 8 bước

```
                       [ Input: PDF File ]
                                │
                                ▼
    [Bước 1] check_deps.py       ──► Kiểm tra thư viện Python
                                │
                                ▼
    [Bước 2] extract_pdf.py      ──► Tách Text + Công thức LaTeX + Ảnh PNG
                                │
                                ▼
    [Bước 3] detect_lang.py      ──► Tự nhận diện ngôn ngữ gốc
                                │
                                ▼
    [Bước 4] translate_content   ──► Dịch (Bảo vệ tuyệt đối LaTeX & Citations)
                                │
                 ┌──────────────┴──────────────┐
                 ▼                             ▼
    [Bước 5] render_html.py         [Bước 6] analyze_paper.py
    ──► Tạo paper.html               ──► Phân tích chủ đề & Prerequisites
        (HTML tự chứa, KaTeX)                  │
                                               ▼
                                    [Bước 7] generate_learning_path.py
                                     ──► Sinh khung trang Index & Các chương
                                               │
                                               ▼
                                    [Bước 8] AI Agent viết nội dung các chương
                                     ──► Hoàn thiện website tự học đa chương!
```

---

## 📂 Cấu trúc thư mục dự án

```
paper-to-learning-path/
├── README.md                                   # Hướng dẫn Tiếng Anh
├── README.vi.md                                # Hướng dẫn Tiếng Việt
├── LICENSE                                     # Giấy phép MIT
├── CHANGELOG.md                                # Lịch sử cập nhật
├── pyproject.toml                              # Cấu hình gói Python
├── install.sh                                  # Script cài đặt cho Linux/macOS
├── install.ps1                                 # Script cài đặt cho Windows
├── .gitignore
│
├── .agents/skills/paper-to-learning-path/      # Thư mục Skill chính
│   ├── SKILL.md                               # Hướng dẫn chi tiết cho Agent (8 bước)
│   ├── scripts/
│   │   ├── check_deps.py                      # Kiểm tra package
│   │   ├── extract_pdf.py                     # Trích xuất PDF
│   │   ├── detect_lang.py                     # Tự động nhận diện ngôn ngữ
│   │   ├── translate_content.py               # Dịch thuật & bảo vệ công thức
│   │   ├── render_html.py                     # Tạo HTML bài báo
│   │   ├── analyze_paper.py                   # Phân tích điều kiện tiên quyết
│   │   └── generate_learning_path.py          # Tạo cấu trúc lộ trình học
│   ├── resources/
│   │   ├── nature_paper.html                  # Template bài báo dịch
│   │   ├── nature_index.html                  # Template Roadmap trang chủ
│   │   └── nature_learning.html               # Template từng chương học
│   └── references/                            # Tài liệu mở rộng
│
├── .claude-plugin/                             # Tích hợp Claude Marketplace
│   ├── plugin.json
│   └── marketplace.json
├── .cursor/rules/                              # Quy tắc cho Cursor IDE
│   └── paper-to-learning-path.mdc
├── .clinerules                                 # Quy tắc cho Cline
├── .windsurfrules                              # Quy tắc cho Windsurf
├── CLAUDE.md                                   # Hướng dẫn cho Claude Code
├── examples/resplat/                           # Bản demo thực tế (ReSplat ECCV 2025)
└── docs/how-it-works.md                        # Kiến trúc chi tiết
```

---

## 🎨 Ngôn ngữ thiết kế Nature-Inspired

Giao diện áp dụng triết lý thiết kế gần gũi với thiên nhiên:
- **Bảng màu:** Xanh rêu (`#5a7a55`), Vàng cát (`#ede8df`), Đá ấm (`#8a7e6e`), Xanh mặt hồ (`#4a7a8a`), Giấy da cổ (`#f5f0e8`).
- **Typography:** Serif cổ điển kết hợp Sans-serif hiện đại cho các khối nội dung học thuật.
- **Tương tác:** Hiệu ứng chuyển động ánh sáng mượt mà (220ms), thanh tiến trình đọc bám theo màn hình, mục lục bên hông bám sát vị trí đọc.
- **Hộp thông tin chuyên dụng:** Ghi chú (Note), Mẹo (Tip), Cảnh báo (Warning), Quan trọng (Important).

---

## 🤝 Đóng góp phát triển

Mọi đóng góp từ cộng đồng đều được hoan nghênh!
1. Fork repository này
2. Tạo branch mới (`git checkout -b feature/tinh-nang-moi`)
3. Commit thay đổi (`git commit -m 'feat: Thêm tính năng mới'`)
4. Push lên branch (`git push origin feature/tinh-nang-moi`)
5. Tạo Pull Request

---

## 📄 Bản quyền

Dự án phát hành dưới giấy phép [MIT License](LICENSE).
Tự do sử dụng, chỉnh sửa và chia sẻ cho mục đích cá nhân và thương mại.
