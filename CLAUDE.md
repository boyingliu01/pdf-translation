# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python-based PDF translation tool that converts PDF documents to bilingual (dual-language) versions while preserving original formatting including formulas, tables, and graphics. Built on top of:
- **pdf2zh-next** (formerly PDFMathTranslate-next) - Core translation library
- **BabelDOC** - PDF parsing and layout analysis

## Common Commands

### Installation
```bash
pip install -r requirements.txt
```

### Running Translations
```bash
# Basic translation
python translate_pdf.py --input path/to/document.pdf --output path/to/output

# With language specification
python translate_pdf.py -i document.pdf -o output --lang-in en --lang-out zh

# Specific pages only
python translate_pdf.py -i document.pdf -o output --pages "1-5"

# Create example config
python translate_pdf.py --create-config --config config/myconfig.json
```

### Running Tests
Tests are standalone Python scripts (not pytest/unittest):
```bash
python test/test_translate.py
python test/test_config_creation.py
python test/test_engines.py
python test/example_usage.py
```

### Building Windows Executable

The project supports packaging as a standalone Windows executable (.exe).

```bash
# Quick build (Windows)
build.bat

# Manual build
pip install pyinstaller>=6.0.0
pyinstaller translate_pdf.spec --clean

# Clean build files
clean.bat
```

Output: `dist/pdf-translator.exe` with `dist/config/` templates

## Architecture

### Core Components

**pdf_translator.py** - Main translation library
- `TranslationResult` - Data class holding translation output paths and metrics
- `PDFTranslator` - Core translation class with async/sync methods
- `create_example_config()` - Helper to generate config templates

**translate_pdf.py** - CLI interface using argparse

### Configuration System

All configs are JSON files in `config/` directory, validated by pydantic models from pdf2zh_next:

- `SettingsModel` - Root settings model
- `BasicSettings` - Input files and debug mode
- `TranslationSettings` - Languages, QPS, output directory, custom prompts
- `PDFSettings` - PDF output options (dual/mono, watermark, page ranges)
- `OpenAISettings` - API configuration

**Important:** Always call `settings.validate_settings()` after creating settings.

### Translation Engine Abstraction

The tool uses an OpenAI-compatible API interface. Multiple providers are supported via `openai_base_url` configuration:
- **ZhipuAI (GLM-4-Flash)** - Free, recommended (`https://open.bigmodel.cn/api/paas/v4`)
- **OpenAI** - Native (`https://api.openai.com/v1`)
- **SiliconFlow (DeepSeek)** - Free tokens (`https://api.siliconflow.cn/v1`)
- **VolcEngine (Doubao)** - PRO subscription (`https://ark.cn-beijing.volces.com/api/v3`)

Only the "openai" engine type is implemented; other providers are different URLs for the same interface.

### Async/Await Pattern

Core translation is asynchronous using `asyncio`:
- `translate_pdf_async()` - Main async method yielding streaming events
- `translate_pdf()` - Sync wrapper using `asyncio.run()`
- Uses `do_translate_async_stream()` from pdf2zh_next

### Progress Callback System

Optional callback receives event dict with type-specific fields:
- `progress_update` - Contains `stage`, `stage_progress`, `overall_progress`
- `error` - Contains `error`, `error_type`
- `finish` - Contains `translate_result` (TranslationResult)

**Always check if callback exists before calling:**
```python
if progress_callback:
    progress_callback(event)
```

### Code Style (from AGENTS.md)

- Python 3.13+
- Import order: stdlib, third-party, local
- Classes: PascalCase, Functions: snake_case, Private methods: _prefix
- Type hints required for all function signatures
- Use `pathlib.Path` for file operations
- f-strings for string formatting
- Logging with timestamp format
- Chinese docstrings acceptable
- Exit with `sys.exit(1)` on CLI errors

### Config File Schema

```json
{
  "translation_engine": "openai",
  "openai_api_key": "your-api-key-here",
  "openai_base_url": "https://api.openai.com/v1",
  "openai_model": "gpt-4o-mini",
  "qps": 4,
  "min_text_length": 5,
  "debug": false,
  "custom_system_prompt": null,
  "enable_term_extraction": false,
  "page_markdown": false
}
```

### Key CLI Arguments

- `--input/-i` - Input PDF path
- `--output/-o` - Output directory (default: PDF parent directory)
- `--config/-c` - Config file (default: config/config.json)
- `--lang-in/-li` - Source language (default: en)
- `--lang-out/-lo` - Target language (default: zh)
- `--no-dual` - Skip dual-language PDF output
- `--no-mono` - Skip single-language PDF output
- `--watermark` - Watermark mode: watermarked/no_watermark/both
- `--pages` - Page range: "1,2,1-,-3,3-5"
- `--max-pages-per-part` - Max pages per batch for large documents
- `--enhance-compatibility` - Enable compatibility enhancements
- `--create-config` - Generate example config file

### Output Files

Translation generates:
- `<filename>.zh-CN.dual.pdf` - Bilingual PDF (recommended)
- `<filename>.zh-CN.mono.pdf` - Single-language PDF (translation only)
- `<filename>.zh-CN.dual.no-watermark.pdf` - Unwatermarked dual (if enabled)
- `<filename>.zh-CN.mono.no-watermark.pdf` - Unwatermarked mono (if enabled)
- Glossary file (if term extraction enabled)

## Common Patterns

### Creating Translator Instance
```python
from pdf_translator import PDFTranslator

# From config file
translator = PDFTranslator(config_path="config/config.json")

# From config dict
config = {"translation_engine": "openai", ...}
translator = PDFTranslator(config_dict=config)
```

### Progress Callback Pattern
```python
def progress_callback(event):
    event_type = event.get("type")
    if event_type == "progress_update":
        stage = event.get("stage")
        progress = event.get("overall_progress", 0)
        print(f"[{stage}] {progress:.1f}%")

result = translator.translate_pdf(..., progress_callback=progress_callback)
```

### Settings Validation
Always validate settings before use:
```python
settings = translator._create_settings(...)
settings.validate_settings()
```

## Important Reminders

1. Always call `settings.validate_settings()` after creating settings
2. Progress callbacks are optional - check existence before calling
3. Use `pathlib.Path` for all file operations
4. Tests are standalone scripts, not pytest/unittest framework
5. CLI errors should exit with `sys.exit(1)`
6. Chinese docstrings are acceptable in this codebase
7. Only the "openai" translation engine type is implemented
8. Large documents benefit from `--max-pages-per-part` option
9. Increasing `qps` in config improves translation speed
10. Recommended model: ZhipuAI's glm-4-flash (free and high quality)
