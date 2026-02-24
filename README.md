# PDF Translation Tool

A professional PDF translation tool based on [PDFMathTranslate-next](https://github.com/Byaidu/PDFMathTranslate) and [BabelDOC](https://github.com/Byaidu/BabelDOC) that converts PDF documents to bilingual (dual-language) versions while preserving original formatting including formulas, tables, and graphics.

## Features

- **Format Preservation**: Maintains original layout, formulas, tables, and graphics
- **Bilingual Output**: Generates both dual-language (bilingual) and single-language (translation only) PDFs
- **Multiple Translation Engines**: Supports various translation providers including ZhipuAI, VolcEngine, SiliconFlow, and OpenAI
- **Term Extraction**: Automatically extracts and generates glossary files
- **Batch Processing**: Supports batch translation of multiple PDF files
- **Customizable**: Supports custom system prompts and translation parameters
- **Page Range Selection**: Translate specific pages or ranges
- **High Performance**: Configurable QPS (queries per second) for faster translation

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/boyingliu01/pdf-translation.git
cd pdf-translation

# Install dependencies
pip install -r requirements.txt
```

### Configuration

Copy and edit a configuration template based on your preferred translation provider:

```bash
# Using ZhipuAI (recommended, free tier available)
cp config/config.zhipu.json config/config.json
# Edit config/config.json and replace "your-zhipuai-api-key-here" with your actual API key

# Using VolcEngine
cp config/config.volcengine.json config/config.json
# Edit config/config.json and replace "your-volcengine-api-key-here" with your actual API key

# Using SiliconFlow
cp config/config.siliconflow.json config/config.json
# Edit config/config.json and replace "your-siliconflow-api-key-here" with your actual API key

# Using OpenAI
cp config/config.openai.json config/config.json
# Edit config/config.json and replace "your-api-key-here" with your actual API key
```

**API Key Registration:**
- **ZhipuAI**: [https://open.bigmodel.cn/](https://open.bigmodel.cn/) - Free tier available, recommended
- **VolcEngine**: [https://console.volcengine.com/ark](https://console.volcengine.com/ark) - Requires subscription
- **SiliconFlow**: [https://siliconflow.cn/](https://siliconflow.cn/) - Various models available
- **OpenAI**: [https://platform.openai.com/](https://platform.openai.com/) - Pay-as-you-go

### Translation

```bash
# Basic translation
python translate_pdf.py -i path/to/document.pdf -o path/to/output

# With language specification
python translate_pdf.py -i document.pdf -o output --lang-in en --lang-out zh

# Specific pages only
python translate_pdf.py -i document.pdf -o output --pages "1-5"

# Without dual-language output
python translate_pdf.py -i document.pdf -o output --no-dual
```

## Usage

### Command Line Arguments

| Argument | Short | Description | Default |
|----------|-------|-------------|---------|
| `--input` | `-i` | Input PDF file path (required) | - |
| `--output` | `-o` | Output directory | PDF parent directory |
| `--config` | `-c` | Configuration file path | `config/config.json` |
| `--lang-in` | `-li` | Source language code | `en` |
| `--lang-out` | `-lo` | Target language code | `zh` |
| `--no-dual` | - | Skip dual-language PDF output | `false` |
| `--no-mono` | - | Skip single-language PDF output | `false` |
| `--watermark` | - | Watermark mode: `watermarked`/`no_watermark`/`both` | `watermarked` |
| `--pages` | - | Page range: `1,2,1-,-3,3-5` | All pages |
| `--max-pages-per-part` | - | Max pages per batch for large documents | - |
| `--enhance-compatibility` | - | Enable compatibility enhancements | `false` |
| `--create-config` | - | Create example config file | - |

### Configuration Options

| Option | Description | Default |
|--------|-------------|---------|
| `translation_engine` | Translation engine type | `openai` |
| `openai_api_key` | API key for the translation service | - |
| `openai_base_url` | API base URL | - |
| `openai_model` | Model name | `glm-4-flash` (ZhipuAI) |
| `qps` | Queries per second (higher = faster) | `4` |
| `min_text_length` | Minimum text length for translation | `5` |
| `debug` | Enable debug mode | `false` |
| `custom_system_prompt` | Custom system prompt | `null` |
| `enable_term_extraction` | Enable term extraction/glossary | `false` |
| `page_markdown` | Enable page markdown | `false` |

## Translation Engines

### ZhipuAI (Recommended)

Uses the GLM-4-Flash model from ZhipuAI. Offers a generous free tier with high translation quality.

**Registration:** [https://open.bigmodel.cn/](https://open.bigmodel.cn/)

### VolcEngine

Uses Doubao models from VolcEngine. Requires a subscription plan.

**Registration:** [https://console.volcengine.com/ark](https://console.volcengine.com/ark)

### SiliconFlow

Supports various models including DeepSeek.

**Registration:** [https://siliconflow.cn/](https://siliconflow.cn/)

### OpenAI

Uses native OpenAI models like GPT-4o-mini.

**Registration:** [https://platform.openai.com/](https://platform.openai.com/)

## Output Files

Translation generates the following files:

- `<filename>.zh-CN.dual.pdf` - Bilingual PDF (recommended)
- `<filename>.zh-CN.mono.pdf` - Single-language PDF (translation only)
- `<filename>.zh-CN.dual.no-watermark.pdf` - Unwatermarked dual (if watermark mode is set to `both` or `no_watermark`)
- `<filename>.zh-CN.mono.no-watermark.pdf` - Unwatermarked mono (if watermark mode is set to `both` or `no_watermark`)
- `<filename>.zh-CN.glossary.csv` - Glossary file (if term extraction enabled)

## Performance Tips

1. **Increase QPS**: Set a higher `qps` value in the configuration file for faster translation
2. **Use faster models**: Models like `glm-4-flash` or `doubao-pro-4k` offer good speed-quality balance
3. **Batch processing**: Use `--max-pages-per-part` for very large documents
4. **Page range selection**: Translate specific pages first to test quality before full translation

## Documentation

For more detailed information, see the [docs/](./docs/) directory:

- [QUICKSTART.md](./docs/QUICKSTART.md) - Quick start guide
- [USAGE_GUIDE.md](./docs/USAGE_GUIDE.md) - Detailed usage guide
- [ENGINES_GUIDE.md](./docs/ENGINES_GUIDE.md) - Translation engine configuration guide

## FAQ

### Q: The translation speed is slow. What can I do?

A: Increase the `qps` value in your configuration file, use a faster model (like `glm-4-flash`), or use the `--max-pages-per-part` option for batch processing.

### Q: How can I improve translation quality?

A: Use a higher-quality model (like `gpt-4o`), add a custom system prompt, or enable term extraction to provide context.

### Q: Which languages are supported?

A: The tool supports translation between all major language pairs, including Chinese-English, English-Japanese, English-French, and more.

### Q: Can I use my own translation API?

A: Yes, as long as your API is OpenAI-compatible, you can configure it by setting the appropriate `openai_base_url` and `openai_model` in the configuration file.

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

This project is built upon:

- [PDFMathTranslate-next](https://github.com/Byaidu/PDFMathTranslate) - Core translation library
- [BabelDOC](https://github.com/Byaidu/BabelDOC) - PDF parsing and layout analysis

## Contact

For questions or support, please open an issue on GitHub.
