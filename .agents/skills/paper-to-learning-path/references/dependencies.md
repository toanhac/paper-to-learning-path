# Dependency Alternatives

## Core Dependencies

### PDF Parsing

| Library | Install | Notes |
|---------|---------|-------|
| **PyMuPDF** (`fitz`) ✅ | `pip install pymupdf` | **Recommended.** Fast, accurate text/image extraction, handles most PDF types |
| pdfplumber | `pip install pdfplumber` | Better table extraction; slower on large PDFs |
| pdfminer.six | `pip install pdfminer.six` | Pure Python; no binary deps but limited image support |
| pypdf | `pip install pypdf` | Lightweight; limited layout-aware extraction |

### Language Detection

| Library | Install | Notes |
|---------|---------|-------|
| **langdetect** ✅ | `pip install langdetect` | **Recommended.** Port of Google's language-detect |
| langid | `pip install langid` | Faster; less accurate on short texts |
| fasttext (lid.176.bin) | `pip install fasttext` | Most accurate; requires downloading a 917MB model |
| lingua-py | `pip install lingua-language-detector` | Very accurate; pure Python |

### Translation

| Library | Install | API Key? | Notes |
|---------|---------|----------|-------|
| **deep-translator** (GoogleTranslator) ✅ | `pip install deep-translator` | ❌ No key needed | **Recommended.** Free, easy, 5000 char/request limit |
| deep-translator (DeepLTranslator) | same package | ✅ DeepL API key | Higher quality; 500K chars/month free tier |
| deep-translator (MicrosoftTranslator) | same package | ✅ Azure key | Good quality; pay-as-you-go |
| openai (GPT-4o) | `pip install openai` | ✅ OpenAI key | Best quality for technical/academic text; pass `--engine openai` to translate script |
| anthropic (Claude) | `pip install anthropic` | ✅ Anthropic key | Excellent for preserving academic tone and terminology |

---

## Switching Translation Engine (translate_content.py)

To use a different engine, modify the `translate_text()` function in
[`../scripts/translate_content.py`](../scripts/translate_content.py):

```python
# DeepL example
from deep_translator import DeepLTranslator
translator = DeepLTranslator(api_key="YOUR_KEY", source=source, target=target)

# OpenAI example
from openai import OpenAI
client = OpenAI()
def translate_with_openai(text, source, target):
    resp = client.chat.completions.create(
        model="gpt-4o",
        messages=[{
            "role": "system",
            "content": f"Translate from {source} to {target}. Preserve LaTeX math verbatim. Keep technical terms consistent."
        }, {
            "role": "user", "content": text
        }]
    )
    return resp.choices[0].message.content
```

---

## Minimal Install (no image extraction needed)

```bash
pip install pdfminer.six deep-translator langdetect
```

Use `--extract-images false` flag with extract_pdf.py.

---

## Full Install (recommended)

```bash
pip install pymupdf deep-translator langdetect
```
