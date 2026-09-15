# Translation Methods & Architecture

`paper-to-learning-path` is designed primarily as an **AI Agent Skill**. This means the AI assistant you are conversing with (Claude, Gemini, Cursor Agent, Windsurf Cascade, etc.) performs the translation directly!

---

## 1. Native AI Agent Translation (Default — Zero API Keys Required)

When running inside any AI Agent environment:
- **No external API keys required** (no Gemini, OpenAI, or DeepL accounts needed).
- **No third-party subscription costs**.
- The Agent reads `<output_dir>/extracted.json`, understands the scientific context, and directly translates each text block into `<output_dir>/translated.json`.
- All `math_block` sections and inline LaTeX expressions (`$...$`, `$$...$$`, `\(...\)`, `\[...\]`) are locked and preserved automatically by `scripts/translate_content.py --scaffold`.
- Citations (`[1]`, `[Author, 2024]`), model names (*NeRF*, *3DGS*, *Transformer*), and datasets are kept intact.

### Workflow for Agents
```bash
# 1. Scaffold translation file (locks math blocks, sets up structure)
python scripts/translate_content.py --scaffold --json extracted.json --target vi --out translated.json

# 2. The AI Agent translates text sections directly into translated.json

# 3. Verify integrity (delimiters, non-empty blocks, captions)
python scripts/translate_content.py --verify translated.json
```

---

## 2. Standalone CLI Translation (Optional — For Non-Agent Terminal Use)

If you are running the pipeline purely from a terminal shell without an AI assistant, you can optionally pass an external translation engine flag:

| Engine Flag | Engine | Requirements | Notes |
|---|---|---|---|
| `--engine gemini` | Google Gemini API | `pip install google-generativeai`<br>`GEMINI_API_KEY` | Free API tier available at Google AI Studio |
| `--engine openai` | OpenAI GPT-4o-mini | `pip install openai`<br>`OPENAI_API_KEY` | Paid OpenAI account |
| `--engine google` | Google Translate | `pip install deep-translator` | Zero-config fallback (lower academic accuracy) |

Example:
```bash
python scripts/translate_content.py \
    --json extracted.json \
    --source en --target vi \
    --out translated.json \
    --engine gemini \
    --api-key "$GEMINI_API_KEY"
```

---

## Summary of Rules for All Translations

1. **LaTeX Math Integrity:** Math expressions are never translated.
2. **Citations:** Brackets like `[1]` or `[Vaswani et al., 2017]` remain verbatim.
3. **Model & Dataset Nomenclature:** Established names (*ResNet, Transformer, ScanNet*) are kept in standard English notation.
4. **Academic Register:** Professional, published-paper style in the target language.
