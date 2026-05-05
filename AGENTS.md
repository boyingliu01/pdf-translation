# AGENTS.md - Agent Guidelines for pdf-translation

**Generated:** 2026-05-05
**Commit:** 8505f80
**Branch:** master

## OVERVIEW

Python PDF translation tool (pdf2zh-next/BabelDOC) → bilingual PDFs. OpenAI-compatible API abstraction (ZhipuAI/OpenAI/SiliconFlow/VolcEngine).

## STRUCTURE

```
pdf-translation/
├── pdf_translator.py     # Core TranslationResult + PDFTranslator class (1128 lines)
├── translate_pdf.py      # CLI entry (argparse, 192 lines)
├── config/               # JSON config templates (12 files)
├── test/                 # Standalone test scripts (18 files)
├── docs/                 # Project documentation
├── evo_capsule/          # Custom capsule packaging for distribution
└── requirements.txt      # Dependencies
```

**Architecture**: Flat structure (no `src/`), intentional for CLI tool simplicity.

## WHERE TO LOOK

| Task | Location | Notes |
|------|----------|-------|
| Translation logic | `pdf_translator.py` | PDFTranslator class, async streaming |
| CLI interface | `translate_pdf.py` | argparse, 14 CLI options |
| Add translation engine | `config/*.json` templates | OpenAI-compatible abstraction |
| Multi-model fallback | `pdf_translator.py` → `FallbackTranslator` | Automatic switch on content filter |
| Test new feature | `test/test_*.py` | Standalone scripts, `python test/<name>.py` |
| Config validation | `pdf_translator.py` → `_create_settings()` | pydantic SettingsModel |
| Progress callback | `pdf_translator.py` → `translate_pdf_async()` | Event streaming |

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
- Python 3.12+
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

## Available Config Templates

The `config/` directory provides 12 JSON configuration templates:

**Single-model configs:**
- `config.example.json` - General configuration example with full options
- `config.zhipu.json` - ZhipuAI/GLM-4-Flash (recommended, free tier available)
- `config.openai.json` - OpenAI native
- `config.siliconflow.json` - SiliconFlow/DeepSeek
- `config.volcengine.json` - VolcEngine/Doubao (PRO subscription)
- `config.bailian-only.json` - Alibaba Bailian single-provider
- `config.foreign-only.json` - Foreign language source optimization
- `config.test.json` - Test configuration (placeholder API key)

**Multi-model / special:**
- `config.multi-model.json` - Multi-model fallback chain configuration
- `config.json.example` - Minimal example (mirrors active config.json)
- `test_config.json` - Test-specific config

## Multi-Model Fallback

`pdf_translator.py` supports automatic model fallback on content filter errors or consecutive failures:

```json
{
  "models": [
    {
      "name": "primary",
      "api_key": "key1",
      "base_url": "https://open.bigmodel.cn/api/paas/v4",
      "model": "glm-4-flash"
    },
    {
      "name": "backup",
      "api_key": "key2",
      "base_url": "https://api.openai.com/v1",
      "model": "gpt-4o-mini"
    }
  ],
  "fallback": {
    "consecutive_failures": 3
  }
}
```

**Fallback triggers:**
- `BadRequestError` (content filter) → immediate switch + retry
- `consecutive_failures` threshold reached → switch to next model
- Patches applied at 3 levels: OpenAITranslator, ILTranslator, ILTranslatorLLMOnly

**To use single-model mode:** omit the `"models"` array and use backward-compatible top-level fields (`openai_api_key`, etc.)

## Translation Engine Abstraction

The tool uses an OpenAI-compatible API interface. Multiple providers are supported via `openai_base_url` configuration:
- **ZhipuAI (GLM-4-Flash)** - Free, recommended (`https://open.bigmodel.cn/api/paas/v4`)
- **OpenAI** - Native (`https://api.openai.com/v1`)
- **SiliconFlow (DeepSeek)** - Free tokens (`https://api.siliconflow.cn/v1`)
- **VolcEngine (Doubao)** - PRO subscription (`https://ark.cn-beijing.volces.com/api/v3`)

## Important Reminders

1. Never use `try/except: pass` - always handle or re-raise
2. Always validate file paths with `Path.exists()` before operations
3. Always call `settings.validate_settings()` after creating settings
4. Progress callbacks are optional - check existence before calling
5. Tests are standalone scripts; run directly with `python test/<name>.py`
6. Use Chinese docstrings when appropriate for this codebase
7. CLI errors should exit with `sys.exit(1)`
8. Large documents benefit from `--max-pages-per-part` option
9. Increasing `qps` in config improves translation speed
10. Recommended model: ZhipuAI's glm-4-flash (free and high quality)

## Code Quality Standards

### Complete Static Analysis Toolchain

| Tool | Purpose | Command | Priority |
|------|---------|---------|----------|
| **Ruff** | Fast Python linter | `python -m ruff check pdf_translator.py translate_pdf.py` | Primary |
| **Mypy** | Static type checker | `python -m mypy pdf_translator.py translate_pdf.py --ignore-missing-imports` | High |
| **Bandit** | Security vulnerability scanner | `python -m bandit -r pdf_translator.py translate_pdf.py -f txt` | High |
| **Radon** | Cyclomatic complexity analyzer | `python -m radon cc pdf_translator.py -a` | Medium |
| **Lizard** | Alternative complexity analyzer | `python -m lizard pdf_translator.py` | Medium |

### Quick Quality Check
```bash
python -m ruff check pdf_translator.py translate_pdf.py
python -m mypy pdf_translator.py translate_pdf.py --ignore-missing-imports
python -m bandit -r pdf_translator.py translate_pdf.py -f txt
python -m radon cc pdf_translator.py -a
```

### Complexity Standards (Clean Code)
- **Cyclomatic Complexity**: CCN < 10 per function/method
- **Average Complexity**: Target grade A (avg < 4.0)
- **Function Length**: < 50 lines per function
- **Duplicate Code**: < 3% (checked via pylint similarities)
- **File Length**: < 500 lines per file

### Security Red Lines (Never Commit)
**绝对禁止提交到 git 仓库的内容：**
1. ✅ **API Keys / Tokens** - 包括所有翻译引擎的密钥
2. ✅ **Passwords** - 任何密码或凭据
3. ✅ **Private Configs** - 包含真实密钥的配置文件 (`config/config.json`)
4. ✅ **Personal Data** - 用户个人数据或敏感信息

**预提交安全检查：**
```bash
git diff --cached | grep -E "(api_key|apikey|password|secret|token)" || echo "✅ No sensitive data found"
grep "config/config.json" .gitignore || echo "⚠️ config/config.json not in .gitignore!"
```

**泄漏响应步骤：**
1. **立即撤销密钥** - 在服务商后台吊销泄漏的 API Key
2. **清理历史** - 使用 `git-filter-repo` 从历史中移除
3. **强制推送** - `git push --force origin --all`
4. **重新生成密钥** - 生成新的 API Key

### Pre-commit Checklist
Before committing code:
1. ✅ Ruff passes with no errors
2. ✅ Bandit shows no security issues
3. ✅ Radon shows average complexity grade A or B
4. ✅ No sensitive data in staged changes
5. ✅ config/config.json is in .gitignore
