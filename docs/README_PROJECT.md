# PDF 翻译工具 - 完整使用说明

## 目录

- [项目简介](#项目简介)
- [业界同类方案对比](#业界同类方案对比)
- [项目实现原理](#项目实现原理)
- [安装配置](#安装配置)
- [快速开始](#快速开始)
- [详细使用指南](#详细使用指南)
- [翻译引擎配置](#翻译引擎配置)
- [性能优化](#性能优化)
- [常见问题](#常见问题)
- [附录](#附录)

---

## 项目简介

这是一个基于 GitHub 开源项目的专业 PDF 翻译工具，能够将 PDF 文档翻译成双语对照版本，同时完整保留原始排版格式，包括数学公式、表格、图形等复杂元素。

### 核心特性

| 特性 | 说明 |
|------|------|
| **双语对照翻译** | 原文和译文并排显示，便于对照学习 |
| **保持原始排版** | 完整保留公式、表格、图形、字体等格式 |
| **自动术语提取** | 自动生成专业术语词汇表，便于术语管理 |
| **多引擎支持** | 支持智谱AI、火山引擎、硅基流动、OpenAI 等 |
| **高性能** | 支持高并发翻译，可处理数百页的大型文档 |
| **完全本地运行** | 除了 API 调用，所有处理在本地完成 |

### 适用场景

- 📚 技术文档翻译（如用户手册、技术规范）
- 🎓 学术论文翻译（保持公式和引用格式）
- 💼 商业文档翻译（合同、报告等）
- 📖 电子书翻译（小说、散文等）
- 🔬 科研文献翻译（含复杂数学公式）

---

## 业界同类方案对比

### 1. 浏览器翻译插件（沉浸式翻译）

| 方案 | 优点 | 缺点 |
|------|------|------|
| **沉浸式翻译** | 方便快捷、支持任何网页 | 需要 PDF 在线打开、需要网络、排版可能错乱 |
| **Google 翻译** | 免费、支持语言多 | 排版破坏严重、公式丢失 |
| **DeepL** | 翻译质量高 | 需要上传文件、隐私风险、大小限制 |

### 2. 专业 PDF 翻译软件

| 软件 | 价格 | 优点 | 缺点 |
|------|------|------|------|
| **ABBYY FineReader** | 收费 | OCR 强、翻译准确 | 贵、排版保留一般 |
| **Adobe Acrobat Pro** | 收费 | 原生 PDF 支持 | 价格昂贵、翻译引擎一般 |
| **Foxit PhantomPDF** | 收费 | 性价比高 | 格式保留不完美 |
| **Trados** | 收费 | 专业术语管理 | 学习成本高、昂贵 |

### 3. 在线翻译服务

| 服务 | 价格 | 优点 | 缺点 |
|------|------|------|------|
| **Google 文档翻译** | 免费 | 免费、方便 | 需上传文件、隐私风险 |
| **DeepL 翻译** | 免费版有限 | 质量高 | 文件大小限制、排版问题 |
| **有道翻译** | 免费 | 中文优化好 | 公式翻译差 |
| **百度翻译** | 免费 | 免费额度大 | 技术文档质量一般 |

### 4. 开源项目

| 项目 | 语言 | 优点 | 缺点 |
|------|------|------|------|
| **PDFMathTranslate** | Python | 保留公式、开源 | 需要配置、命令行 |
| **BabelDOC** | Python | 排版保留好 | 文档较少 |
| **TransPDF** | 在线 | 简单 | 收费、不免费 |
| **Omnivore** | Web | 多格式 | 翻译质量一般 |

### 本项目优势对比

| 特性 | 本项目 | 沉浸式翻译 | Adobe Acrobat | Google 翻译 |
|------|--------|-------------|--------------|-------------|
| **排版保留** | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ | ⭐ |
| **公式保留** | ⭐⭐⭐⭐⭐ | ⭐ | ⭐⭐⭐ | ⭐ |
| **双语对照** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ | ⭐ |
| **完全免费** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐ | ⭐⭐⭐⭐⭐ |
| **本地处理** | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐ |
| **批量处理** | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ | ⭐ |
| **术语提取** | ⭐⭐⭐⭐⭐ | ⭐ | ⭐⭐ | ⭐ |

---

## 项目实现原理

### 技术架构

本项目基于两个成熟的 GitHub 开源项目：

```
┌─────────────────────────────────────────────────────────────┐
│                    PDF 翻译工具                         │
├─────────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────────────┐    ┌──────────────┐    ┌─────────┐ │
│  │  命令行工具  │───>│ 核心翻译引擎 │───>│ API调用 │ │
│  │ translate_  │    │ pdf_translator│    │ (火山/ │ │
│  │ pdf.py      │    │              │    │ 智谱/ │ │
│  └─────────────┘    └──────────────┘    │ OpenAI) │ │
│                                          └─────────┘ │
│                                                 ▼     │
│  ┌──────────────────────────────────────────────────┐    │
│  │         pdf2zh-next (核心翻译库)             │    │
│  │  - PDF 解析                                 │    │
│  │  - 段落提取                                 │    │
│  │  - 公式识别                                 │    │
│  └──────────────────────────────────────────────────┘    │
│                        ▼                            │
│  ┌──────────────────────────────────────────────────┐    │
│  │         BabelDOC (PDF 处理库)              │    │
│  │  - 布局分析                                 │    │
│  │  - PDF 生成                                 │    │
│  │  - 排版保持                                 │    │
│  └──────────────────────────────────────────────────┘    │
│                        ▼                            │
│              ┌─────────────────┐                       │
│              │  输出 PDF 文件  │                       │
│              │ - 双语对照版    │                       │
│              │ - 单语版        │                       │
│              │ - 术语表        │                       │
│              └─────────────────┘                       │
└─────────────────────────────────────────────────────────────┘
```

### 核心依赖

| 依赖 | 版本 | 用途 |
|------|------|------|
| **pdf2zh-next** | >=0.1.0 | 核心翻译引擎 |
| **PyMuPDF** | >=1.23.0 | PDF 解析和处理 |
| **pydantic** | >=2.0.0 | 配置验证 |
| **configargparse** | >=1.5.0 | 命令行参数解析 |
| **rich** | >=13.0.0 | 终端美化输出 |
| **tqdm** | >=4.65.0 | 进度条显示 |
| **asyncio** | (stdlib) | 异步并发处理 |

### 翻译流程

```
1. PDF 解析
   └─> 提取文本、图片、公式、表格
   └─> 识别文档布局结构
   └─> 提取字体和样式信息

2. 内容分段
   └─> 按段落分割文本
   └─> 识别公式区域
   └─> 标记表格和图片

3. 术语提取
   └─> 自动识别专业术语
   └─> 生成术语词汇表
   └─> 术语一致性检查

4. 翻译处理
   └─> 并发调用翻译 API
   └─> 保留格式标记
   └─> 术语替换

5. PDF 重建
   └─> 重新布局内容
   └─> 双语对照排版
   └─> 嵌入字体和图片
   └─> 生成最终 PDF
```

---

## 安装配置

### 系统要求

- **操作系统**: Windows / macOS / Linux
- **Python 版本**: 3.8+（推荐 3.13+）
- **内存**: 最低 4GB（处理大文档需要 8GB+）
- **网络**: 需要连接互联网（调用翻译 API）

### 安装步骤

#### 1. 克隆或下载项目

```bash
# 如果有 git
git clone <repository-url>
cd pdf-translation

# 或直接下载解压
```

#### 2. 安装 Python 依赖

```bash
pip install -r requirements.txt
```

如果遇到权限问题，使用：

```bash
pip install -r requirements.txt --user
```

#### 3. 验证安装

```bash
python translate_pdf.py --help
```

如果看到帮助信息，说明安装成功。

---

## 快速开始

### 第一步：选择翻译引擎

#### 方案 A：智谱 AI（推荐，完全免费）

1. 注册账号：https://open.bigmodel.cn（免费，5 分钟完成）
2. 登录控制台
3. 点击"API密钥" -> "创建新密钥"
4. 复制 API 密钥

#### 方案 B：火山引擎豆包（已订阅 PRO）

1. 登录控制台：https://console.volcengine.com/ark
2. 查看推理接入点（Endpoint）
3. 复制 API 密钥和模型 ID

#### 方案 C：硅基流动 DeepSeek

1. 注册账号：https://siliconflow.cn
2. 创建 API 密钥
3. 选择 DeepSeek-V3 模型

### 第二步：配置 API 密钥

#### 使用智谱 AI

```bash
cp config/config.zhipu.json config/config.json
```

编辑 `config/config.json`：

```json
{
  "translation_engine": "openai",
  "openai_api_key": "你的智谱AI密钥",
  "openai_base_url": "https://open.bigmodel.cn/api/paas/v4",
  "openai_model": "glm-4-flash",
  "qps": 4,
  "min_text_length": 5,
  "debug": false
}
```

#### 使用火山引擎

```bash
cp config/config.volcengine.json config/config.json
```

编辑 `config/config.json`：

```json
{
  "translation_engine": "openai",
  "openai_api_key": "你的火山引擎密钥",
  "openai_base_url": "https://ark.cn-beijing.volces.com/api/coding/v3",
  "openai_model": "doubao-seed-code",
  "qps": 16,
  "min_text_length": 5,
  "debug": false
}
```

### 第三步：翻译 PDF

#### 基本翻译

```bash
python translate_pdf.py \
    --input "你的文件.pdf" \
    --output "./output"
```

#### 指定语言

```bash
python translate_pdf.py \
    --input "你的文件.pdf" \
    --output "./output" \
    --lang-in en \
    --lang-out zh
```

### 第四步：查看结果

翻译完成后，输出目录会生成：

- `<文件名>.zh.dual.pdf` - **双语对照版 PDF**（推荐）
- `<文件名>.zh.glossary.csv` - 术语表

---

## 详细使用指南

### 命令行参数说明

#### 必需参数

| 参数 | 简写 | 说明 | 示例 |
|------|------|------|------|
| `--input` | `-i` | 输入 PDF 文件路径 | `--input doc.pdf` |

#### 可选参数

| 参数 | 简写 | 默认值 | 说明 |
|------|------|--------|------|
| `--output` | `-o` | PDF 所在目录 | 输出目录路径 |
| `--config` | `-c` | `config/config.json` | 配置文件路径 |
| `--lang-in` | `-li` | `en` | 源语言代码 |
| `--lang-out` | `-lo` | `zh` | 目标语言代码 |
| `--no-dual` | - | `False` | 不生成双语版 PDF |
| `--no-mono` | - | `False` | 不生成单语版 PDF |
| `--watermark` | - | `watermarked` | 水印模式：`watermarked`/`no_watermark`/`both` |
| `--pages` | - | 全部页 | 翻译特定页码，如 `1,2,1-,-3,3-5` |
| `--max-pages-per-part` | - | 无限制 | 分批处理时每批最大页数（最小 50） |
| `--enhance-compatibility` | - | `False` | 启用兼容性增强选项 |
| `--create-config` | - | `False` | 创建示例配置文件 |

### 配置文件参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `translation_engine` | `openai` | 翻译引擎类型 |
| `openai_api_key` | - | API 密钥（必需） |
| `openai_base_url` | `https://api.openai.com/v1` | API 基础 URL |
| `openai_model` | `gpt-4o-mini` | 模型名称 |
| `qps` | `4` | 每秒并发请求数 |
| `min_text_length` | `5` | 最小文本长度（低于此值不翻译） |
| `debug` | `false` | 调试模式 |
| `custom_system_prompt` | `null` | 自定义系统提示词 |
| `enable_term_extraction` | `false` | 启用术语提取 |
| `page_markdown` | `false` | 生成页面 Markdown |

### 常用命令示例

#### 只翻译特定页面

```bash
python translate_pdf.py \
    --input "document.pdf" \
    --output "./output" \
    --pages "1-5,10,15-20"
```

#### 只生成双语版，不生成单语版

```bash
python translate_pdf.py \
    --input "document.pdf" \
    --output "./output" \
    --no-mono
```

#### 生成无水印版本

```bash
python translate_pdf.py \
    --input "document.pdf" \
    --output "./output" \
    --watermark no_watermark
```

#### 同时生成带水印和无水印版本

```bash
python translate_pdf.py \
    --input "document.pdf" \
    --output "./output" \
    --watermark both
```

#### 处理大文档（分批处理）

```bash
python translate_pdf.py \
    --input "large_document.pdf" \
    --output "./output" \
    --max-pages-per-part 50
```

#### 启用术语提取

先编辑配置文件：

```json
{
  "enable_term_extraction": true
}
```

然后运行翻译。

---

## 翻译引擎配置

### 智谱 AI（推荐，完全免费）

**特点**：
- ✅ 完全免费，无需付费
- ✅ 翻译质量优秀，专为中英文优化
- ✅ 响应速度快
- ✅ 支持长文档（128K 上下文）

**配置**：

```json
{
  "translation_engine": "openai",
  "openai_api_key": "你的密钥",
  "openai_base_url": "https://open.bigmodel.cn/api/paas/v4",
  "openai_model": "glm-4-flash",
  "qps": 8
}
```

**模型选择**：
- `glm-4-flash` - 速度快，推荐用于翻译
- `glm-4-air` - 平衡质量和速度
- `glm-4-plus` - 质量最高，速度较慢

### 火山引擎豆包（已订阅 PRO）

**特点**：
- ✅ 你已订阅 PRO 套餐，直接使用
- ✅ 翻译质量优秀
- ✅ 性价比高
- ✅ 中文优化

**配置**：

```json
{
  "translation_engine": "openai",
  "openai_api_key": "你的密钥",
  "openai_base_url": "https://ark.cn-beijing.volces.com/api/coding/v3",
  "openai_model": "doubao-seed-code",
  "qps": 16
}
```

**获取配置**：
1. 登录火山引擎控制台
2. 进入"大模型推理" -> "推理接入点"
3. 创建或查看已有 Endpoint
4. 复制 API Key 和 Endpoint ID

### 硅基流动 DeepSeek

**特点**：
- ✅ 新用户有免费 Token 额度
- ✅ DeepSeek-V3 质量优秀
- ✅ 价格便宜

**配置**：

```json
{
  "translation_engine": "openai",
  "openai_api_key": "你的密钥",
  "openai_base_url": "https://api.siliconflow.cn/v1",
  "openai_model": "deepseek-ai/DeepSeek-V3",
  "qps": 8
}
```

### OpenAI

**特点**：
- ✅ 质量最高
- ✅ 服务稳定
- ⚠️ 需要付费

**配置**：

```json
{
  "translation_engine": "openai",
  "openai_api_key": "sk-...",
  "openai_base_url": "https://api.openai.com/v1",
  "openai_model": "gpt-4o-mini",
  "qps": 8
}
```

**模型选择**：
- `gpt-4o-mini` - 速度快，价格便宜，推荐
- `gpt-4o` - 质量最高，价格较高
- `gpt-4-turbo` - 性价比高

---

## 性能优化

### 提高翻译速度

#### 1. 增加 QPS（并发数）

编辑 `config.json`：

```json
{
  "qps": 16  // 从 4 增加到 16
}
```

**注意**：QPS 过高可能触发 API 限流，建议根据实际效果调整。

#### 2. 使用更快的模型

| 模型 | 速度 | 质量 | 推荐度 |
|------|------|------|--------|
| glm-4-flash | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| gpt-4o-mini | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| doubao-seed-code | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

#### 3. 减少输出文件

只生成双语版，不生成单语版：

```bash
python translate_pdf.py \
    --input "document.pdf" \
    --output "./output" \
    --no-mono
```

#### 4. 分批处理大文档

```bash
python translate_pdf.py \
    --input "large_document.pdf" \
    --output "./output" \
    --max-pages-per-part 50
```

**性能对比示例**（730 页文档）：

| 配置 | 耗时 | 提升 |
|------|------|------|
| 智谱AI, QPS=4, 不分批 | ~8-12 小时 | 基准 |
| 智谱AI, QPS=16, 分批50页 | ~2-3 小时 | 3-4x |
| 火山引擎, QPS=16, 分批50页 | **~1.5 小时** | **5-6x** |

### 内存优化

翻译大文档时内存使用较高，可以：

1. **减少 `max-pages-per-part`**：从 50 降到 30
2. **关闭术语提取**：设置 `enable_term_extraction: false`
3. **增加系统内存**：推荐 8GB+ 可用内存

### 网络优化

1. 使用稳定的网络连接
2. 如果在海外，建议使用国内 API（智谱、火山）
3. 开启 API 调用缓存（自动）

---

## 常见问题

### 安装问题

#### Q1: `pip install` 失败

**解决方案**：

```bash
# 升级 pip
python -m pip install --upgrade pip

# 使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

#### Q2: 提示找不到 `pdf2zh_next` 模块

**解决方案**：

```bash
pip install -r requirements.txt --upgrade
```

### 配置问题

#### Q3: API 密钥无效

**检查步骤**：
1. API 密钥是否复制正确
2. 账号是否已激活
3. API 配额是否充足
4. 网络是否能访问 API

#### Q4: 翻译引擎不支持

**当前支持的引擎**：
- `openai`（所有 OpenAI 兼容的 API）

**配置错误示例**：

```json
{
  "translation_engine": "other"  // 错误
}
```

**正确配置**：

```json
{
  "translation_engine": "openai"  // 正确，所有引擎都用这个
}
```

### 翻译问题

#### Q5: 翻译速度慢

**解决方案**：
1. 增加 `qps` 值（如从 4 增加到 16）
2. 使用更快的模型（如 `glm-4-flash`）
3. 使用 `--max-pages-per-part` 分批处理
4. 检查网络连接

#### Q6: 翻译质量不理想

**解决方案**：
1. 尝试不同的模型
2. 使用自定义系统提示词：

```json
{
  "custom_system_prompt": "你是一名专业的技术文档翻译员，请准确翻译以下内容，保持专业术语的一致性。"
}
```

3. 启用术语提取并检查术语表

#### Q7: 排版错乱

**可能原因**：
1. PDF 是扫描版（不支持）
2. 特殊字体未嵌入
3. 表格结构过于复杂

**解决方案**：
- 使用可编辑的 PDF（非扫描版）
- 启用 `--enhance-compatibility` 选项

#### Q8: 公式显示错误

**原因**：某些数学公式可能无法完美保留

**解决方案**：
- 检查原文公式是否正确
- 使用支持数学公式的模型
- 手动调整生成 PDF 中的公式

### 大文档处理

#### Q9: 内存不足

**解决方案**：
```bash
python translate_pdf.py \
    --input "large_document.pdf" \
    --output "./output" \
    --max-pages-per-part 30  # 减少每批页数
```

#### Q10: 翻译中断怎么办

**当前版本**：如果中断，需要重新翻译

**建议**：
- 使用稳定的网络
- 分批处理（`--max-pages-per-part`）
- 确保电源供应稳定

---

## 附录

### 支持的语言

基于翻译引擎的不同，支持的语言对也不同：

**智谱 AI**：中、英、日、韩、法、德、俄等 26 种语言

**火山引擎**：中、英、日等主流语言

**DeepSeek**：支持中英文翻译优化

**OpenAI**：支持 50+ 种语言

### 语言代码参考

| 语言 | 代码 |
|------|------|
| 中文（简体） | `zh` / `zh-CN` |
| 英文 | `en` / `en-US` |
| 日文 | `ja` |
| 韩文 | `ko` |
| 法文 | `fr` |
| 德文 | `de` |
| 俄文 | `ru` |
| 西班牙文 | `es` |

### 输出文件说明

| 文件 | 说明 | 推荐用途 |
|------|------|----------|
| `<文件名>.zh.dual.pdf` | 双语对照 PDF | 学习、对照、技术文档 |
| `<文件名>.zh.mono.pdf` | 单语 PDF | 纯阅读 |
| `<文件名>.zh.dual.no-watermark.pdf` | 无水印双语 PDF | 正式使用 |
| `<文件名>.zh.mono.no-watermark.pdf` | 无水印单语 PDF | 正式使用 |
| `<文件名>.glossary.csv` | 术语表 | 术语管理、质量检查 |

### 参考资源

**GitHub 开源项目**：
- [PDFMathTranslate-next](https://github.com/Byaidu/PDFMathTranslate) - 核心翻译库
- [BabelDOC](https://github.com/Renyz/PDFMathTranslate) - PDF 处理库

**API 文档**：
- [智谱 AI](https://open.bigmodel.cn/dev/api) - 开放平台文档
- [火山引擎](https://www.volcengine.com/docs/82379) - 大模型推理文档
- [OpenAI](https://platform.openai.com/docs) - 官方文档

**工具**：
- [CLAUDE.md](../CLAUDE.md) - 项目指南（面向开发者）
- [requirements.txt](../requirements.txt) - 依赖列表

### 贡献

如果你遇到问题或有改进建议：

1. 查看现有文档
2. 检查常见问题
3. 提交 Issue 或 Pull Request

### 许可证

本项目基于以下开源项目开发，遵循相应的开源许可证：
- [PDFMathTranslate-next](https://github.com/Byaidu/PDFMathTranslate)
- [BabelDOC](https://github.com/Renyz/PDFMathTranslate)

---

## 总结

本 PDF 翻译工具是一个功能强大、易于使用的开源工具，具有以下优势：

✅ **完全免费** - 使用智谱 AI 等 API，成本低廉
✅ **排版完美** - 保留公式、表格、图形
✅ **双语对照** - 便于学习和对照
✅ **高性能** - 支持高并发和分批处理
✅ **易于配置** - 简单的配置文件和命令行界面

**立即开始翻译你的 PDF 文档吧！** 🚀
