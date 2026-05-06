# Examples

This directory contains sample files for testing the PDF translation tool.

## Files

- `sample.pdf` — A minimal 1-page PDF with English text, used for quick translation tests.

## Quick Start

```bash
# Install the tool
pip install -e .

# Configure a translation engine
cp config/config.zhipu.json config/config.json
# Edit config/config.json and add your API key

# Translate the sample
pdf-translate -i examples/sample.pdf -o examples/output --config config/config.json
```

## Output

Translated files are written to `examples/output/` (gitignored).

```
examples/output/
├── sample.zh-CN.dual.pdf      # Bilingual (original + translation)
├── sample.zh-CN.mono.pdf      # Translation only
└── sample.zh-CN.glossary.csv  # Auto-extracted terms (if enabled)
```

## Creating Your Own Sample

```python
import fitz  # PyMuPDF

doc = fitz.open()
page = doc.new_page()
page.insert_text((72, 72), "Your text here", fontsize=12)
doc.save("examples/my_sample.pdf")
doc.close()
```
