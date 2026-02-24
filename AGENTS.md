# AGENTS.md - Agent Guidelines for pdf-translation

## Project Overview

这是一个基于 PDFMathTranslate-next 和 BabelDOC 的专业 PDF 翻译工具，支持将 PDF 文档转换为双语（中英文对照）版本，同时完整保留原始排版格式，包括公式、表格和图形。项目支持多种翻译引擎（智谱AI、火山引擎、硅基流动、OpenAI等），提供命令行接口和 Python API。

## Build and Test Commands

### Installation
```bash
pip install -r requirements.txt
```

### Running Translations
```bash
# 基础翻译
python translate_pdf.py --input path/to/document.pdf --output path/to/output --config config/config.json

# 指定语言
python translate_pdf.py -i document.pdf -o output --config config/config.json --lang-in en --lang-out zh

# 指定页码范围
python translate_pdf.py -i document.pdf -o output --pages "1-5"

# 不生成双语PDF
python translate_pdf.py -i document.pdf --no-dual

# 不生成单语PDF
python translate_pdf.py -i document.pdf --no-mono

# 启用无水印输出
python translate_pdf.py -i document.pdf --watermark no_watermark

# 大文档分批处理
python translate_pdf.py -i document.pdf --max-pages-per-part 20

# 启用兼容性增强
python translate_pdf.py -i document.pdf --enhance-compatibility
```

### Running Tests
测试是独立的 Python 脚本（非 pytest/unittest）：
```bash
# 运行特定测试
python test/test_translate.py
python test/test_config_creation.py
python test/test_engines.py
python test/test_final.py
python test/test_debug.py
python test/test_fix.py
python test/test_translate_docs.py

# 运行使用示例
python test/example_usage.py
```

### Building Windows Executable

项目支持打包为独立的 Windows 可执行程序（.exe），无需安装 Python 环境即可运行。

#### Prerequisites
- Python 3.13+
- 管理员权限（安装依赖时）

#### Quick Build (Windows)

```bash
# 双击运行或命令行执行
build.bat
```

构建脚本会自动：
1. 检查并安装 PyInstaller
2. 安装项目依赖
3. 执行打包流程
4. 复制配置文件模板

#### Build Output

打包完成后，可执行文件位于：
```
dist/pdf-translator.exe
```

配置文件模板位于：
```
dist/config/
```

#### Using the Executable

```bash
# 基础使用
pdf-translator.exe --input document.pdf --output output_dir

# 使用自定义配置
pdf-translator.exe --input document.pdf --config config/config.json

# 查看帮助
pdf-translator.exe --help
```

#### Manual Build

如果不使用自动脚本，可以手动执行：

```bash
# 安装 PyInstaller
pip install pyinstaller>=6.0.0

# 安装依赖
pip install -r requirements.txt

# 打包（使用 spec 文件）
pyinstaller translate_pdf.spec --clean

# 或直接打包
pyinstaller --onefile --name pdf-translator --console translate_pdf.py
```

#### Cleaning Build Files

```bash
# 双击运行或命令行执行
clean.bat
```

清理脚本会删除：
- `build/` 目录
- `dist/` 目录
- `translate_pdf.spec` 文件
- 临时文件

#### Build Configuration

打包配置位于 `translate_pdf.spec`，可以自定义：
- 包含的数据文件（配置模板）
- 隐藏导入模块
- 排除的依赖（减小体积）
- 输出文件名和图标

#### Tips

1. **首次打包可能需要 5-10 分钟**
2. **生成的 .exe 文件较大**（约 50-100MB），这是正常的
3. **杀毒软件可能误报**，添加到白名单即可
4. **配置文件需要单独放置**，建议与 .exe 在同一目录的 config/ 子目录中
5. **分发时包含配置模板**，方便用户自定义

## Code Structure

### Core Classes

#### PDFTranslator
主要翻译器类，位于 `pdf_translator.py`

**初始化参数:**
- `config_path`: 配置文件路径（JSON）
- `config_dict`: 配置字典（优先级高于 config_path）

**主要方法:**
- `_create_settings(...) -> SettingsModel`: 创建翻译配置
- `translate_pdf_async(...) -> TranslationResult`: 异步翻译
- `translate_pdf(...) -> TranslationResult`: 同步翻译包装器

#### TranslationResult
翻译结果类，封装翻译输出信息

**属性:**
- `original_pdf_path`: 原始 PDF 路径
- `mono_pdf_path`: 单语 PDF 路径
- `dual_pdf_path`: 双语 PDF 路径
- `no_watermark_mono_pdf_path`: 无水印单语 PDF 路径
- `no_watermark_dual_pdf_path`: 无水印双语 PDF 路径
- `auto_extracted_glossary_path`: 术语表路径
- `total_seconds`: 总耗时（秒）
- `peak_memory_usage`: 内存峰值（MB）

### pdf2zh_next Settings Components

- **BasicSettings**: 基本设置（输入文件、调试模式）
- **TranslationSettings**: 翻译设置（语言、输出目录、QPS、最小文本长度）
- **PDFSettings**: PDF 设置（输出类型、水印、页码范围）
- **OpenAISettings**: OpenAI 兼容引擎设置（API 密钥、基础 URL、模型）
- **SettingsModel**: 完整设置模型，包含所有子设置

## Code Style Guidelines

### Environment Requirements
- Python 3.13+
- Windows 10/11, macOS, Linux
- pip for package management
- Active internet connection for translation APIs

### Python Version
- Python 3.13+

### Import Order
1. Standard library imports (asyncio, json, logging, sys, os)
2. Third-party imports
3. Local imports

Example:
```python
import asyncio
import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any, Union

from pdf_translator import PDFTranslator
from pdf2zh_next.config.model import SettingsModel
```

### Naming Conventions
- **Classes**: PascalCase (e.g., `PDFTranslator`, `TranslationResult`)
- **Functions/Methods**: snake_case (e.g., `translate_pdf`, `_create_settings`)
- **Private methods**: Prefix with underscore (e.g., `_create_settings`)
- **Constants**: UPPER_SNAKE_CASE (not heavily used, but preferred)
- **Variables**: snake_case

### Type Hints
- Use typing module for type hints
- Required for function signatures
    ```python
    from typing import Optional, Dict, Any, Union

    def translate_pdf(
        self,
        input_pdf: str,
        output_dir: Optional[str] = None,
        source_lang: str = "en",
        target_lang: str = "zh",
        **kwargs,
    ) -> TranslationResult:
    ```

### File Paths
- Always use `pathlib.Path` for file operations
    ```python
    from pathlib import Path

    input_path = Path(input_pdf)
    if not input_path.exists():
        raise FileNotFoundError(f"PDF file not found: {input_pdf}")
    ```

### String Formatting
- Use f-strings for string interpolation
- Use `json.dump()` with `indent=2` and `ensure_ascii=False` for JSON configs
    ```python
    json.dump(config, f, indent=2, ensure_ascii=False)
    ```

### Logging
- Use Python's `logging` module
- Setup with standard format including timestamp
- Log levels: INFO for normal operations, ERROR for failures
    ```python
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    self.logger = logging.getLogger(__name__)
    ```

### Docstrings
- Use triple quotes for docstrings
- Chinese docstrings are acceptable in this codebase
- Include Args and Returns sections for methods
    ```python
    """
    Translate PDF file asynchronously

    Args:
        input_pdf: Input PDF path
        output_dir: Output directory (default: current directory)
        source_lang: Source language code (default: en)
        target_lang: Target language code (default: zh)

    Returns:
        TranslationResult instance
    """
    ```

### Error Handling
- Use specific exceptions (ValueError, FileNotFoundError) when possible
- Never use empty catch blocks
- Log errors with `exc_info=True` for debugging
    ```python
    try:
        # code
    except Exception as e:
        self.logger.error(f"Translation failed: {e}", exc_info=True)
        raise
    ```

### Configuration Management
- 所有配置文件均为 JSON 格式，存放在 `config/` 目录
- 配置文件结构遵循 pdf2zh_next 的 SettingsModel
- 使用 `settings.validate_settings()` 验证配置
- 支持的翻译引擎：openai（通过 openai_base_url 配置不同服务商）
- 关键配置字段：
  - `translation_engine`: "openai"
  - `openai_api_key`: API 密钥
  - `openai_base_url`: API 端点 URL
  - `openai_model`: 模型名称（如 "gpt-4o-mini", "glm-4-flash"）
  - `qps`: 并发请求数（默认: 4）
  - `min_text_length`: 最小翻译文本长度（默认: 5）
  - `debug`: 调试模式标志
  - `custom_system_prompt`: 自定义系统提示词（可选）

### Available Config Templates
`config/` 目录提供多个配置模板：
- `config.example.json` - 通用配置示例
- `config.openai.json` - OpenAI 配置模板
- `config.zhipu.json` - 智谱AI配置模板（推荐，完全免费）
- `config.siliconflow.json` - 硅基流动配置模板
- `config.volcengine.json` - 火山引擎配置模板
- `config.test.json` - 测试配置

使用配置模板：
```bash
# 复制模板作为当前配置
cp config/config.zhipu.json config/config.json
# 编辑 config/config.json 填入 API 密钥
```

### Async/Await Patterns
- Use `asyncio` for async operations
- Prefer `async for` with streaming generators
- Provide sync wrapper that uses `asyncio.run()`
    ```python
    async def translate_pdf_async(self, ...) -> TranslationResult:
        async for event in do_translate_async_stream(settings, input_path):
            # handle events
        return result

    def translate_pdf(self, ...) -> TranslationResult:
        return asyncio.run(self.translate_pdf_async(...))
    ```

### Callbacks
- Use optional callback functions for progress reporting
- Callback receives event dict with type-specific fields
- Always check if callback exists before calling
    ```python
    if progress_callback:
        progress_callback(event)
    ```

### Command Line Interface
- 使用 `argparse` 进行命令行参数解析
- 提供短选项和长选项（--input 和 -i）
- 使用 `action="store_true"` 标志参数
- 错误时使用 `sys.exit(1)` 退出

### CLI Options
- `--input, -i`: 输入 PDF 文件路径（必需）
- `--output, -o`: 输出目录（默认: PDF 文件所在目录）
- `--config, -c`: 配置文件路径（默认: config/config.json）
- `--lang-in, -li`: 源语言代码（默认: en）
- `--lang-out, -lo`: 目标语言代码（默认: zh）
- `--no-dual`: 不生成双语 PDF
- `--no-mono`: 不生成单语 PDF
- `--watermark`: 水印模式（watermarked/no_watermark/both，默认: watermarked）
- `--pages`: 指定翻译页码（如: 1,2,1-,-3,3-5）
- `--max-pages-per-part`: 每个分部的最大页数（用于大文档）
- `--enhance-compatibility`: 启用兼容性增强选项
- `--create-config`: 创建示例配置文件

## Project Structure

```
pdf-translation/
├── config/                      # JSON 配置文件目录
│   ├── config.json              # 当前使用的配置（智谱AI）
│   ├── config.example.json      # 通用配置示例
│   ├── config.openai.json       # OpenAI 配置模板
│   ├── config.siliconflow.json  # 硅基流动配置模板
│   ├── config.volcengine.json   # 火山引擎配置模板
│   ├── config.zhipu.json        # 智谱AI 配置模板
│   ├── config.test.json         # 测试配置
│   └── test_config.json         # 测试配置
├── docs/                        # 文档目录
│   ├── README.md                # 主要文档
│   ├── ENGINES_GUIDE.md         # 翻译引擎指南
│   ├── FIX.md                   # 问题修复记录
│   ├── INTEGRATION.md           # 集成指南
│   ├── PROJECT_SUMMARY.md       # 项目总结
│   ├── QUICKSTART.md            # 快速开始
│   ├── TEST_SUMMARY.md          # 测试总结
│   ├── TRANSLATE_TEST.md        # 翻译测试记录
│   ├── TRANSLATION_ENGINES.md   # 翻译引擎说明
│   ├── USAGE.md                 # 使用说明
│   └── USAGE_GUIDE.md           # 详细使用指南
├── test/                        # 测试脚本目录
│   ├── example_usage.py         # 使用示例
│   ├── test_config_creation.py  # 配置创建测试
│   ├── test_debug.py            # 调试测试
│   ├── test_engines.py          # 引擎测试
│   ├── test_final.py            # 最终测试
│   ├── test_fix.py              # 修复测试
│   ├── test_translate.py        # 翻译测试
│   └── test_translate_docs.py   # 文档翻译测试
├── examples/                    # 示例 PDF 文件
│   ├── 00 Color Front Matter SA (V.4.5.1)-A4.pdf
│   └── 01 - Body.pdf
├── AGENTS.md                    # Agent 指南（本文件）
├── CLAUDE.md                    # Claude AI 配置
├── README.md                    # 项目说明
├── pdf_translator.py            # 核心翻译类
├── translate_pdf.py             # 命令行工具
└── requirements.txt             # Python 依赖
```

## Key Dependencies

- **pdf2zh-next**: 核心翻译库 (>=0.1.0)
- **PyMuPDF**: PDF 处理 (>=1.23.0)
- **pydantic**: 数据验证 (>=2.0.0)
- **configargparse**: 命令行参数解析 (>=1.5.0)
- **rich**: 终端输出格式化 (>=13.0.0)
- **tqdm**: 进度条 (>=4.65.0)
- **asyncio**: 异步支持（Python 标准库）

## Translation Engines Support

### Supported Engines
项目通过 OpenAI 兼容接口支持多种翻译引擎：

1. **智谱AI**（推荐）- 完全免费，翻译质量优秀
   - 模型: glm-4-flash, glm-4
   - 注册: https://open.bigmodel.cn/
   - 配置: 使用 config/config.zhipu.json

2. **火山引擎** - 需要订阅，速度快
   - 模型: doubao-pro-4k, doubao-pro-32k
   - 配置: 使用 config/config.volcengine.json

3. **硅基流动** - 支持多种模型
   - 模型: Qwen/Qwen2.5-7B-Instruct, deepseek-ai/DeepSeek-V3
   - 配置: 使用 config/config.siliconflow.json

4. **OpenAI** - 原生支持
   - 模型: gpt-4o-mini, gpt-4o
   - 配置: 使用 config/config.openai.json

### Engine Configuration Pattern
所有引擎使用相同的配置结构：
```json
{
  "translation_engine": "openai",
  "openai_api_key": "your-api-key-here",
  "openai_base_url": "https://api.example.com/v1",
  "openai_model": "model-name",
  "qps": 4,
  "min_text_length": 5,
  "debug": false,
  "custom_system_prompt": null
}
```

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

## Testing Notes

- 测试是独立的 Python 脚本，非 pytest/unittest 框架
- 使用直接导入和 sys.path.append（如需要）
- 测试文件使用 shebang: `#!/usr/bin/env python3`
- 使用 print 语句输出测试结果
- 无测试发现机制 - 直接运行脚本

### Test Files
- `test_translate.py` - 翻译功能测试
- `test_config_creation.py` - 配置创建测试
- `test_engines.py` - 翻译引擎测试
- `test_final.py` - 最终集成测试
- `test_debug.py` - 调试测试
- `test_fix.py` - 修复验证测试
- `test_translate_docs.py` - 文档翻译测试
- `example_usage.py` - 使用示例

### Running Tests
```bash
# 运行单个测试
python test/test_translate.py

# 使用 Python 解释器运行
python test/test_engines.py

# 查看使用示例
python test/example_usage.py
```

## Output Files

翻译完成后会生成以下文件：

### PDF 输出
- `*.dual.pdf` - 双语对照 PDF（原文+译文）
- `*.mono.pdf` - 单语翻译 PDF（仅译文）
- `*.no_watermark.dual.pdf` - 无水印双语 PDF（当 watermark_output_mode 为 both 或 no_watermark）
- `*.no_watermark.mono.pdf` - 无水印单语 PDF（当 watermark_output_mode 为 both 或 no_watermark）

### 术语表
- `*.glossary.csv` - 自动提取的术语表（CSV 格式）

### TranslationResult 属性
```python
result.original_pdf_path              # 原始 PDF 路径
result.mono_pdf_path                  # 单语 PDF 路径
result.dual_pdf_path                  # 双语 PDF 路径
result.no_watermark_mono_pdf_path     # 无水印单语 PDF 路径
result.no_watermark_dual_pdf_path     # 无水印双语 PDF 路径
result.auto_extracted_glossary_path   # 术语表路径
result.total_seconds                  # 总耗时（秒）
result.peak_memory_usage              # 内存峰值（MB）
```

## Common Issues & Troubleshooting

### Q: 翻译速度慢怎么办？
**A:**
- 增加配置文件中的 `qps` 值（如设置为 8 或 16）
- 使用更快的模型（如 glm-4-flash）
- 对大文档使用 `--max-pages-per-part` 分批处理
- 检查网络连接和 API 响应速度

### Q: 如何提高翻译质量？
**A:**
- 使用更好的模型（如 gpt-4o, glm-4）
- 添加自定义系统提示词 (`custom_system_prompt`)
- 使用术语表进行术语一致性控制
- 增加 `min_text_length` 避免碎片化翻译

### Q: 支持哪些语言？
**A:**
- 支持所有主流语言对
- 常见: 中英(en↔zh)、英日(en↔ja)、英法(en↔fr)、英德(en↔de)等

### Q: 配置文件找不到怎么办？
**A:**
```bash
# 创建示例配置
python translate_pdf.py --create-config
# 或从模板复制
cp config/config.zhipu.json config/config.json
```

### Q: API 密钥配置错误
**A:**
- 检查 `config/config.json` 中的 `openai_api_key` 字段
- 确保 `openai_base_url` 与选择的服务商匹配
- 验证 API 密钥是否有效且有足够额度

## Important Reminders

1. 永远不要使用 try/except pass 抑制错误
2. 处理前始终验证文件路径是否存在
3. 使用 pathlib.Path 而非字符串拼接处理路径
4. 遵循异步模式进行翻译操作
5. 为所有函数签名使用类型提示
6. 使用前检查可选参数是否存在
7. 进度回调是可选的 - 调用前始终检查
8. 配置文件必须通过 SettingsModel.validate_settings() 验证
9. 使用中文文档字符串在本代码库中是可接受的
10. 大文档建议使用 `--max-pages-per-part` 分批处理
11. 提高翻译速度可以增加配置中的 `qps` 值
12. 推荐使用智谱AI的 glm-4-flash 模型（免费且质量优秀）
