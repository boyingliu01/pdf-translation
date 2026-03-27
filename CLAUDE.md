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

### Code Quality Checks
```bash
# Run all quality checks
python -m ruff check pdf_translator.py translate_pdf.py
python -m radon cc pdf_translator.py -a
python -m pylint --disable=all --enable=similarities pdf_translator.py
python -m bandit -r pdf_translator.py translate_pdf.py -f txt

# Generate comprehensive test report
python test/performance_test.py
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
python test/test_final.py
python test/test_debug.py
python test/test_fix.py
python test/test_translate_docs.py
```

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

### Available Config Templates

The `config/` directory provides multiple configuration templates:
- `config.example.json` - General configuration example
- `config.openai.json` - OpenAI configuration template
- `config.zhipu.json` - ZhipuAI configuration template (recommended, free tier available)
- `config.siliconflow.json` - SiliconFlow configuration template
- `config.volcengine.json` - VolcEngine configuration template
- `config.test.json` - Test configuration

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

### Code Style

- Python 3.13+
- Import order: stdlib, third-party, local
- Classes: PascalCase, Functions: snake_case, Private methods: _prefix
- Type hints required: use `typing` module
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

## Code Quality Standards

### Complete Static Analysis Toolchain

This project uses a comprehensive static analysis toolchain:

| Tool | Purpose | Command | Priority |
|------|---------|---------|----------|
| **Ruff** | Fast Python linter (replaces flake8/pylint) | `python -m ruff check pdf_translator.py translate_pdf.py` | Primary |
| **Mypy** | Static type checker | `python -m mypy pdf_translator.py translate_pdf.py --ignore-missing-imports` | High |
| **Bandit** | Security vulnerability scanner | `python -m bandit -r pdf_translator.py translate_pdf.py -f txt` | High |
| **Radon** | Cyclomatic complexity analyzer | `python -m radon cc pdf_translator.py -a` | Medium |
| **Lizard** | Alternative complexity analyzer | `python -m lizard pdf_translator.py` | Medium |
| **Pylint** | Code analysis (similarities) | `python -m pylint --disable=all --enable=similarities pdf_translator.py` | Low |
| **Flake8** | Style guide enforcement | `python -m flake8 pdf_translator.py translate_pdf.py --max-line-length=120` | Deprecated (use Ruff) |
| **Isort** | Import sorting | `python -m isort pdf_translator.py translate_pdf.py --check-only` | Medium |

### Quick Quality Check (Recommended)
```bash
# Run the essential checks quickly
python -m ruff check pdf_translator.py translate_pdf.py
python -m mypy pdf_translator.py translate_pdf.py --ignore-missing-imports
python -m bandit -r pdf_translator.py translate_pdf.py -f txt
python -m radon cc pdf_translator.py -a
```

### Full Quality Check (Pre-commit)
```bash
# Generate complete test reports
python -m ruff check pdf_translator.py translate_pdf.py > test/ruff_report.txt
python -m mypy pdf_translator.py translate_pdf.py --ignore-missing-imports > test/mypy_report.txt
python -m bandit -r pdf_translator.py translate_pdf.py -f txt > test/bandit_report.txt
python -m radon cc pdf_translator.py -a > test/radon_report.txt
python -m lizard pdf_translator.py > test/lizard_report.txt
python -m pylint --disable=all --enable=similarities pdf_translator.py > test/pylint_report.txt
python -m flake8 pdf_translator.py translate_pdf.py --max-line-length=120 > test/flake8_report.txt
```

### Linting and Formatting
- **Ruff** (preferred): Fast Python linter, replaces flake8/pylint
  - Line length limit: 120 characters
  - No unused imports or variables
  - No undefined names
- **Mypy**: Type checking for Python
  - All functions should have type hints
  - Use `--ignore-missing-imports` for third-party libraries without stubs
- **Isort**: Import sorting and organization
  - Standard library imports first
  - Third-party imports second
  - Local imports last

### Complexity Standards (Clean Code)
- **Cyclomatic Complexity**: CCN < 10 per function/method
- **Average Complexity**: Target grade A (avg < 4.0)
- **Function Length**: < 50 lines per function
- **Duplicate Code**: < 3% (checked via pylint similarities)
- **File Length**: < 500 lines per file
- Check with: `python -m radon cc pdf_translator.py -a` or `python -m lizard pdf_translator.py`

### Security Scanning
- **Bandit**: Security vulnerability scanner
- Run: `python -m bandit -r pdf_translator.py translate_pdf.py -f txt`
- Target: 0 high/medium severity issues
- Common issues to avoid: hardcoded passwords, SQL injection, shell injection

### ⚠️ Security Red Lines (Never Commit)
**绝对禁止提交到 git 仓库的内容：**
1. ✅ **API Keys / Tokens** - 包括 OpenAI、ZhipuAI、VolcEngine 等所有翻译引擎的密钥
2. ✅ **Passwords** - 任何密码或凭据
3. ✅ **Private Configs** - 包含真实密钥的配置文件 (`config/config.json`)
4. ✅ **Personal Data** - 用户个人数据或敏感信息

**预提交安全检查：**
```bash
# 检查即将提交的内容是否包含敏感信息
git diff --cached | grep -E "(api_key|apikey|password|secret|token)" || echo "✅ No sensitive data found"

# 检查 config.json 是否在 .gitignore 中
grep "config/config.json" .gitignore || echo "⚠️ config/config.json not in .gitignore!"
```

**如果不小心提交了敏感信息：**
1. **立即撤销密钥** - 在服务商后台吊销泄漏的 API Key
2. **清理历史** - 使用 git-filter-repo 从历史中移除敏感信息
3. **强制推送** - `git push --force origin --all`
4. **重新生成密钥** - 生成新的 API Key 并更新本地配置

### Pre-commit Checklist
Before committing code:
1. ✅ Ruff passes with no errors
2. ✅ Mypy passes with no type errors (or only expected missing imports)
3. ✅ Radon shows average complexity grade A or B
4. ✅ No functions with complexity grade D or F
5. ✅ Pylint similarities shows no duplicate code
6. ✅ Bandit shows no security issues
7. ✅ Isort passes (imports are sorted correctly)

### Test Requirements
- Tests are standalone scripts in `test/` directory
- Run all tests before major commits:
  ```bash
  python test/test_translate.py
  python test/test_config_creation.py
  python test/test_engines.py
  ```
