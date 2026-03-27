# BabelDOC Control Character Fix Capsule

## Problem

BabelDOC/pdf2zh-next fails to translate PDFs when control characters (ASCII 0-31) are present in extracted text. This causes:

1. **JSON parsing failures** - Control characters break LLM response parsing
2. **Fallback loop triggers** - Failed parsing triggers model fallback unnecessarily  
3. **Residual characters** - 'Th', 'ft' and other fragments appear in output

## Root Cause

PDF text extraction includes control characters that:
- Originate from PDF formatting codes
- Survive through the translation pipeline
- Break JSON parser when included in LLM responses

## Solution

This capsule provides three critical patches:

### 1. Control Character Cleaning

```python
def clean_control_chars(text: str) -> str:
    """Remove control characters (ASCII 0-31, preserve \\n\\t\\r)"""
    if not isinstance(text, str):
        return text
    return "".join(char for char in text if ord(char) >= 32 or char in "\n\t\r")
```

Patches `ILTranslatorLLMOnly._clean_json_output` to clean both input and output.

### 2. Multi-Model Fallback

```python
def patch_fallback_on_content_filter(self, text, **kwargs):
    """Switch models on content filter errors"""
    try:
        return original_translate(self, text, **kwargs)
    except BadRequestError as e:
        if "content_filter" in str(e):
            return fallback_translate(self, text, **kwargs)
        raise
```

### 3. Cross-Page Paragraph Merging

```python
def _is_incomplete_sentence(text: str) -> bool:
    """Detect paragraphs split across pages"""
    if not text or not text.strip():
        return False
    stripped = text.rstrip()
    if not stripped:
        return False
    last_char = stripped[-1]
    if last_char in '.!?!"':
        return False
    return True
```

## Usage

```python
from pdf_translator import PDFTranslator

# The patches are auto-applied on import
translator = PDFTranslator(config_path="config.json")

# Multi-model fallback configuration
config = {
    "models": [
        {"name": "primary", "api_key": "...", "model": "glm-4-flash"},
        {"name": "fallback", "api_key": "...", "model": "gpt-4o-mini"}
    ],
    "fallback": {"consecutive_failures": 3}
}

# Translate with progress callback
def progress(event):
    if event.get("type") == "progress_update":
        print(f"[{event.get('stage')}] {event.get('overall_progress', 0):.1f}%")

result = translator.translate_pdf(
    input_pdf="document.pdf",
    output_dir="./output",
    progress_callback=progress
)
```

## Files Included

- `pdf_translator.py` - Core library with all patches
- `translate_pdf.py` - CLI entry point
- `config/` - Configuration templates
- `test/` - Test scripts

## Comparison

| Feature | BabelDOC | pdf2zh-next-mcp | This Capsule |
|---------|----------|-----------------|--------------|
| Control char fix | ❌ | ❌ | ✅ |
| Multi-model fallback | ❌ | ❌ | ✅ |
| Cross-page merge | ❌ | ❌ | ✅ |
| Progress callbacks | ❌ | ❌ | ✅ |
| Requires service | ❌ | ✅ | ❌ |

## License

MIT
