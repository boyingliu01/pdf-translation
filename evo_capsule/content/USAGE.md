# Capsule Usage Guide

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/boyingliu01/pdf-translation.git
cd pdf-translation

# Install dependencies
pip install -r requirements.txt
```

### Basic Translation

```python
from pdf_translator import PDFTranslator

# Initialize with config
translator = PDFTranslator(config_path="config/config.zhipu.json")

# Translate
result = translator.translate_pdf(
    input_pdf="my-document.pdf",
    output_dir="./output"
)

print(f"Done! Output: {result.dual_pdf_path}")
```

### Advanced: Multi-Model Fallback

```python
config = {
    "translation_engine": "openai",
    "models": [
        {
            "name": "zhipu",
            "api_key": "your-key-here",
            "base_url": "https://open.bigmodel.cn/api/paas/v4",
            "model": "glm-4-flash"
        },
        {
            "name": "openai",
            "api_key": "your-key-here", 
            "base_url": "https://api.openai.com/v1",
            "model": "gpt-4o-mini"
        }
    ],
    "fallback": {
        "consecutive_failures": 3
    },
    "qps": 4,
    "debug": False
}

translator = PDFTranslator(config_dict=config)
result = translator.translate_pdf("paper.pdf", output_dir="./translated")
```

### Progress Callbacks

```python
def progress_callback(event):
    event_type = event.get("type")
    
    if event_type == "progress_update":
        stage = event.get("stage")
        progress = event.get("overall_progress", 0)
        print(f"[{stage}] {progress:.1f}%")
    
    elif event_type == "error":
        print(f"Error: {event.get('error')}")
    
    elif event_type == "finish":
        print("Translation completed!")

result = translator.translate_pdf(
    "document.pdf",
    progress_callback=progress_callback
)
```

### Specific Pages

```python
# Translate only pages 1-10 and 20-25
result = translator.translate_pdf(
    "document.pdf",
    pages="1-10,20-25"
)
```

## Configuration Reference

See `config/` directory for templates:
- `config.zhipu.json` - ZhipuAI (recommended, free tier)
- `config.openai.json` - OpenAI
- `config.siliconflow.json` - SiliconFlow (DeepSeek)
- `config.volcengine.json` - VolcEngine
- `config.multi-model.json` - Multiple models with fallback

## Troubleshooting

### JSON Parsing Errors

The control character patch automatically handles this. If you still see errors:

```python
# Enable debug mode
config["debug"] = True
translator = PDFTranslator(config_dict=config)
```

### Content Filter Errors

Configure fallback models - the capsule will auto-switch on filter errors.

### Cross-Page Issues

The cross-page patch automatically detects and merges split paragraphs.

## Output Files

- `<name>.zh.dual.pdf` - Bilingual (side-by-side)
- `<name>.zh.mono.pdf` - Translation only
- `<name>.zh.glossary.csv` - Extracted terms (if enabled)

## License

MIT
