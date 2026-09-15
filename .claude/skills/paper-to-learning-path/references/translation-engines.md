# Translation Engine Options

## Default: Google Translate (via deep-translator, free, no API key)

The default engine is `GoogleTranslator` from `deep-translator`. It:
- Requires **no API key**
- Supports **130+ languages**
- Has a **5000 character per request** limit (the script chunks automatically)
- Rate-limits after ~100 rapid requests (use `--chunk-delay 1.0` for large papers)

---

## Supported Language Codes

Use BCP-47 codes as the `--source` and `--target` arguments.
Common examples:

| Language | Code |
|----------|------|
| English | `en` |
| Vietnamese | `vi` |
| Chinese (Simplified) | `zh-CN` |
| Chinese (Traditional) | `zh-TW` |
| French | `fr` |
| German | `de` |
| Japanese | `ja` |
| Korean | `ko` |
| Spanish | `es` |
| Portuguese | `pt` |
| Russian | `ru` |
| Arabic | `ar` |
| Italian | `it` |

Full list: https://cloud.google.com/translate/docs/languages

---

## Translation Quality Tips

### 1. Academic / Technical Papers
- Use DeepL or GPT-4o for higher accuracy with specialized vocabulary
- Enable the terminology glossary (built-in to translate_content.py)

### 2. Math-heavy Papers
- The placeholder system (`__MATH_0001__`) protects all LaTeX expressions
- If inline math gets corrupted, increase the regex conservatism in translate_content.py

### 3. CJK Languages (Chinese, Japanese, Korean)
- No special config needed; Google Translate handles CJK well
- For Traditional vs. Simplified Chinese, use `zh-TW` vs. `zh-CN` explicitly

### 4. Right-to-Left Languages (Arabic, Hebrew)
- The HTML template uses `lang` attribute for correct text direction
- Add `dir="rtl"` to the `<html>` tag in the template for RTL languages:
  Replace `<html lang="{{TARGET_LANG}}">` with `<html lang="{{TARGET_LANG}}" dir="rtl">`

### 5. Rate Limiting
- Default delay between chunks: 0.5s
- For large papers (> 30 pages): use `--chunk-delay 1.5`
- If you get 429 errors: use `--chunk-delay 3.0` or switch to DeepL/OpenAI

---

## Using a Custom LLM for Translation

For highest fidelity with domain-specific terminology:

```python
# In translate_content.py, replace the translate_text() function body:

import anthropic
client = anthropic.Anthropic()  # Uses ANTHROPIC_API_KEY env var

SYSTEM_PROMPT = """You are an expert academic translator specializing in scientific papers.
Rules:
1. Preserve all LaTeX math expressions (anything between $, $$, \\[, \\() verbatim.
2. Preserve citation references like [1], [Author, 2020] verbatim.
3. Maintain consistent terminology throughout the document.
4. Use formal, academic register appropriate for research papers.
5. Return ONLY the translated text, no explanations."""

def translate_text(text, source, target, **kwargs):
    protected, placeholders = _protect(text)
    msg = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        messages=[{
            "role": "user",
            "content": f"Translate from {source} to {target}:\n\n{protected}"
        }]
    )
    result = msg.content[0].text
    return _restore(result, placeholders)
```
