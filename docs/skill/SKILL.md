# PDF Translation Skill

## Description

A Python-based PDF translation tool that converts PDF documents to bilingual versions while preserving formatting. Unlike existing MCP servers that require running a separate service, this skill provides a direct Python library interface for AI agents to translate PDFs programmatically.

**Key Differentiators vs pdf2zh-next-mcp:**

1. **No Service Required** - Direct Python API, no need to run a separate MCP server process
2. **Multi-Model Fallback** - Automatically switches to backup models on content filter errors
3. **Cross-Page Paragraph Merging** - Intelligently merges paragraphs split across pages
4. **Control Character Handling** - Fixes JSON parsing errors caused by control characters in PDF text
5. **Progress Callbacks** - Real-time progress reporting for long translations
6. **Flexible Configuration** - JSON config or dict-based configuration

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```python
from pdf_translator import PDFTranslator

# Initialize with config file
translator = PDFTranslator(config_path="config/config.json")

# Or initialize with dict
config = {
    "translation_engine": "openai",
    "openai_api_key": "your-key",
    "openai_base_url": "https://open.bigmodel.cn/api/paas/v4",
    "openai_model": "glm-4-flash",
    "qps": 4,
    "min_text_length": 5,
    "debug": False
}
translator = PDFTranslator(config_dict=config)

# Define progress callback
def progress_callback(event):
    if event.get("type") == "progress_update":
        print(f"[{event.get('stage')}] {event.get('overall_progress', 0):.1f}%")

# Translate PDF
result = translator.translate_pdf(
    input_pdf="document.pdf",
    output_dir="./output",
    source_lang="en",
    target_lang="zh",
    progress_callback=progress_callback
)

print(f"Translated: {result.dual_pdf_path}")
```

## Supported Translation Engines

- **ZhipuAI (GLM-4-Flash)** - Free, recommended
- **OpenAI** - GPT-4o-mini, GPT-4o, etc.
- **SiliconFlow** - DeepSeek models
- **VolcEngine** - Doubao models

All via OpenAI-compatible API interface.

## Configuration File

```json
{
  "translation_engine": "openai",
  "openai_api_key": "your-api-key",
  "openai_base_url": "https://open.bigmodel.cn/api/paas/v4",
  "openai_model": "glm-4-flash",
  "qps": 4,
  "min_text_length": 5,
  "debug": false,
  "custom_system_prompt": null,
  "enable_term_extraction": false,
  "page_markdown": false
}
```

## Advanced Features

### Multi-Model Fallback

Configure fallback models for content filter errors:

```json
{
  "models": [
    {"name": "zhipu", "api_key": "...", "base_url": "...", "model": "glm-4-flash"},
    {"name": "openai", "api_key": "...", "base_url": "...", "model": "gpt-4o-mini"}
  ],
  "fallback": {"consecutive_failures": 3}
}
```

### Page Range Selection

```python
result = translator.translate_pdf(
    input_pdf="document.pdf",
    output_dir="./output",
    pages="1-10,15,20-25"  # Specific pages only
)
```

## Output Files

- `<filename>.zh.dual.pdf` - Bilingual PDF (side-by-side)
- `<filename>.zh.mono.pdf` - Single-language PDF
- `<filename>.zh.glossary.csv` - Extracted terms (if enabled)

## Project Structure

```
pdf-translation/
├── pdf_translator.py      # Core library
├── translate_pdf.py       # CLI entry point
├── config/                # Config templates
├── test/                  # Test scripts
└── docs/                  # Documentation
```

## License

MIT
