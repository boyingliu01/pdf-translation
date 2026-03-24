# AGENTS.md - Agent Guidelines for pdf-translation

## Project Overview

A Python-based PDF translation tool using pdf2zh-next and BabelDOC. Converts PDFs to bilingual versions while preserving formatting (formulas, tables, graphics). Supports multiple translation engines (ZhipuAI, VolcEngine, SiliconFlow, OpenAI) via OpenAI-compatible APIs.

## Build and Test Commands

### Installation
```bash
pip install -r requirements.txt
```

### Running Tests
Tests are standalone Python scripts (not pytest/unittest):
```bash
# Run a single test
python test/test_translate.py
python test/test_engines.py
python test/test_config_creation.py

# Run all tests (if needed)
python test/test_translate.py && python test/test_engines.py && python test/test_config_creation.py
```

### Running Translations
```bash
# Basic translation
python translate_pdf.py -i document.pdf -o output

# With options
python translate_pdf.py -i doc.pdf --lang-in en --lang-out zh --pages "1-5"

# Create config template
python translate_pdf.py --create-config -c config/myconfig.json
```

## Code Style Guidelines

### Environment
- Python 3.13+
- Use `pathlib.Path` for file operations (never string concatenation)

### Import Order
```python
# 1. Standard library
import asyncio
import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any

# 2. Third-party
from pydantic import BaseModel

# 3. Local
from pdf_translator import PDFTranslator
```

### Naming Conventions
- **Classes**: `PascalCase` (e.g., `PDFTranslator`, `TranslationResult`)
- **Functions/Methods**: `snake_case` (e.g., `translate_pdf`, `_create_settings`)
- **Private**: Prefix with `_` (e.g., `_create_settings`)
- **Constants**: `UPPER_SNAKE_CASE`
- **Variables**: `snake_case`

### Type Hints
Required for all function signatures:
```python
def translate_pdf(
    self,
    input_pdf: str,
    output_dir: Optional[str] = None,
    source_lang: str = "en",
) -> TranslationResult:
```

### String Formatting
- Use f-strings for interpolation
- JSON configs: `json.dump(config, f, indent=2, ensure_ascii=False)`

### Logging
```python
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
self.logger = logging.getLogger(__name__)
```

### Error Handling
- Use specific exceptions (`ValueError`, `FileNotFoundError`)
- **Never** use empty catch blocks
- Log with `exc_info=True` for debugging
```python
try:
    # code
except Exception as e:
    self.logger.error(f"Failed: {e}", exc_info=True)
    raise
```

### Docstrings
- Chinese docstrings are acceptable
- Include Args and Returns sections
```python
"""Translate PDF asynchronously.

Args:
    input_pdf: Input PDF path
    output_dir: Output directory (default: current directory)

Returns:
    TranslationResult instance
"""
```

### Async Pattern
```python
async def translate_async(self, ...) -> Result:
    async for event in stream():
        # handle
    return result

def translate(self, ...) -> Result:
    return asyncio.run(self.translate_async(...))
```

### Callbacks
Always check existence before calling:
```python
if progress_callback:
    progress_callback(event)
```

## Project Structure

```
pdf-translation/
├── config/               # JSON configs (config.json, config.zhipu.json, etc.)
├── test/                 # Standalone test scripts
├── docs/                 # Documentation
├── pdf_translator.py     # Core Translation class
├── translate_pdf.py      # CLI entry point
└── requirements.txt
```

## Key Patterns

### Creating Translator
```python
from pdf_translator import PDFTranslator

translator = PDFTranslator(config_path="config/config.json")
# or
translator = PDFTranslator(config_dict={"translation_engine": "openai", ...})
```

### Settings Validation
```python
settings = translator._create_settings(...)
settings.validate_settings()  # Always validate
```

### Config Schema
```json
{
  "translation_engine": "openai",
  "openai_api_key": "your-key",
  "openai_base_url": "https://api.openai.com/v1",
  "openai_model": "gpt-4o-mini",
  "qps": 4,
  "min_text_length": 5,
  "debug": false
}
```

## Important Reminders

1. Never use `try/except: pass` - always handle or re-raise
2. Always validate file paths with `Path.exists()` before operations
3. Always call `settings.validate_settings()` after creating settings
4. Progress callbacks are optional - check existence before calling
5. Tests are standalone scripts; run directly with `python test/<name>.py`
6. Use Chinese docstrings when appropriate for this codebase
7. CLI errors should exit with `sys.exit(1)`
