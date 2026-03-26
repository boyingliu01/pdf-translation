# BabelDoc 多模型 Fallback 支持 PR 提案

## 问题描述

当前 BabelDoc 的翻译器在遇到内容过滤错误（如智谱AI的敏感词过滤）时，会直接抛出 `ContentFilterError` 异常，导致该段落未被翻译。用户需要手动处理这些未翻译的段落。

## 提议的解决方案

在 `BaseTranslator` 类中增加多模型 fallback 机制，当主模型因内容过滤等原因失败时，自动切换到备用模型重试。

## 实现方案

### 1. 配置扩展

在配置文件中支持多模型配置：

```toml
[babeldoc.translation]
# 主模型
primary_model = "zhipu"

# 备用模型列表（按优先级排序）
[[babeldoc.translation.fallback_models]]
name = "bailian"
api_key = "xxx"
base_url = "https://api.bailian.com/v1"
model = "qwen3.5-plus"

[[babeldoc.translation.fallback_models]]
name = "codebuddy"
api_key = "xxx"
base_url = "https://www.codebuddy.ai/v2"
model = "gpt-5.4"
```

### 2. 核心代码修改

#### 2.1 修改 `BaseTranslator` 类

在 `translator.py` 中添加 fallback 支持：

```python
class BaseTranslator(ABC):
    def __init__(self, lang_in, lang_out, ignore_cache, fallback_translators=None):
        # ... 现有代码 ...
        self.fallback_translators = fallback_translators or []
        self.current_fallback_index = 0
    
    def translate_with_fallback(self, text, ignore_cache=False, rate_limit_params=None):
        """
        带 fallback 的翻译方法
        """
        # 尝试主模型
        try:
            return self.translate(text, ignore_cache, rate_limit_params)
        except ContentFilterError as e:
            logger.warning(f"Primary model content filter: {e}")
            
        # 尝试备用模型
        for idx, fallback in enumerate(self.fallback_translators):
            try:
                logger.info(f"Trying fallback model {idx+1}/{len(self.fallback_translators)}")
                return fallback.translate(text, ignore_cache, rate_limit_params)
            except Exception as e:
                logger.warning(f"Fallback model {idx+1} failed: {e}")
                continue
        
        # 所有模型都失败
        raise TranslationError("All translation models failed")
```

#### 2.2 修改 `OpenAITranslator` 类

在 `do_llm_translate` 方法中更好地处理内容过滤错误：

```python
def do_llm_translate(self, text, rate_limit_params: dict = None):
    try:
        # ... 现有代码 ...
    except openai.BadRequestError as e:
        # 检测内容过滤错误
        if "contentFilter" in str(e) or "1301" in str(e) or "敏感" in str(e):
            raise ContentFilterError(str(e))
        raise
```

#### 2.3 修改调用点

在 `il_translator_llm_only.py` 中使用 `translate_with_fallback`：

```python
# 在 translate_paragraph 方法中
translation = translator.translate_with_fallback(
    text, 
    rate_limit_params={...}
)
```

### 3. 命令行参数

添加新的命令行选项：

```bash
babeldoc \
  --openai --openai-model "glm-4-flash" --openai-api-key "KEY1" \
  --fallback-model "qwen3.5-plus" --fallback-api-key "KEY2" \
  --fallback-base-url "https://api.bailian.com/v1" \
  --files example.pdf
```

## 代码实现

我将提交一个 PR，包含以下文件修改：

1. `babeldoc/translator/translator.py` - 添加 fallback 支持
2. `babeldoc/translation_config.py` - 添加配置解析
3. `babeldoc/main.py` - 添加命令行参数
4. `babeldoc/format/pdf/document_il/midend/il_translator_llm_only.py` - 修改调用点

## 测试计划

- 单元测试：验证 fallback 机制在各种错误场景下的行为
- 集成测试：使用包含敏感内容的 PDF 进行端到端测试
- 回归测试：确保不影响正常翻译流程

## 向后兼容性

- 新功能完全向后兼容
- 不使用 fallback 时行为与之前完全一致
- 仅在显式配置 fallback 模型时启用

## 贡献指南遵循

- [x] 使用英文注释和文档
- [x] 遵循 PEP8 命名规范
- [x] 使用类型注解
- [x] 添加适当的日志记录
- [x] 使用 Conventional Commits

---

这个 PR 将使 BabelDoc 更加健壮，能够自动处理内容过滤场景，提高翻译成功率。
