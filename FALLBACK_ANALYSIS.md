# Fallback 机制失效根因分析报告

## 问题现象

在进行全文翻译时，以下7个页面的敏感段落未被翻译：
- Page 13, 24, 28, 170, 171, 172, 176

这些段落包含敏感词（俄乌战争、Project Maven、Hamas袭击等），智谱AI (glm-4-flash) 返回内容过滤错误，但 fallback 机制未切换到备用模型。

## 代码架构分析

当前实现了3层 fallback 补丁：

1. **OpenAITranslator.do_llm_translate** (第580-647行)
   - 拦截 OpenAI 翻译器的底层调用
   - 捕获 BadRequestError 并切换模型

2. **ILTranslator.translate_paragraph** (第649-749行)  
   - 在 BabelDOC 的 ILTranslator 层拦截
   - 捕获 BadRequestError 和 contentFilter 错误

3. **ILTranslatorLLMOnly.translate_paragraph** (第751-828行)
   - 在 ILTranslatorLLMOnly 层拦截（实际使用的类）
   - 捕获包含 "contentFilter"、"1301"、"BadRequestError" 的错误

## 根因分析

### 核心问题：错误处理层级冲突

**实际错误处理流程：**

```
BabelDOC 翻译流程：
1. ILTranslatorLLMOnly.translate_paragraph() 
   ↓ 调用
2. OpenAITranslator.translate_paragraph()
   ↓ 调用
3. OpenAITranslator.do_llm_translate()
```

**问题：**

1. **错误在 BabelDOC 内部被捕获并处理**
   - BabelDOC 的 `translate_paragraph` 方法在内部 try-except 块中捕获了异常
   - 错误被记录后继续处理下一个段落，没有向上抛出
   - 这导致我们的 fallback 补丁**无法拦截到错误**

2. **模型切换后设置未正确传播**
   - `_update_translator_settings` 方法更新的是 BabelDOC 内部的 translator 实例
   - 但实际翻译使用的是子线程/进程中的 translator 实例
   - 新实例没有继承切换后的模型设置

3. **连续失败计数器未正确重置**
   - 当一个段落被过滤后，后续段落继续失败
   - 但连续失败计数未达到阈值（设为1）时就重置了
   - 原因：不同段落之间的成功记录混淆了计数

### 具体代码问题

```python
# 问题1：错误类型不匹配
# 智谱AI返回的错误可能不是标准的 BadRequestError
# 而是包装在 BabelDOC 的 TranslationError 中

# 问题2：ILTranslatorLLMOnly 补丁未正确应用
# 从日志可以看到翻译使用的是 ILTranslatorLLMOnly
# 但我们的补丁可能没有正确覆盖所有调用路径

# 问题3：模型切换后 client 未更新
# _update_translator_settings 更新了 settings
# 但 translator 实例可能使用了缓存的 client
```

## 修复建议

### 方案1：在 BabelDOC 层拦截（推荐）

修改 `translate_paragraph` 方法，在错误处理块中插入 fallback 逻辑：

```python
# 在 BabelDOC 的 translate_paragraph 方法中
def translate_paragraph(...):
    try:
        # 原有翻译逻辑
        return result
    except Exception as e:
        # 检查是否是内容过滤错误
        if is_content_filter_error(e):
            # 尝试 fallback
            for model in fallback_models:
                try:
                    switch_to_model(model)
                    result = retry_translate()
                    return result
                except:
                    continue
        # 如果所有模型都失败，抛出错误
        raise
```

### 方案2：预处理敏感内容

在翻译前检测敏感词，直接使用备用模型：

```python
def translate_with_fallback(paragraph):
    if contains_sensitive_words(paragraph):
        return translate_with_backup_model(paragraph)
    return translate_with_primary_model(paragraph)
```

### 方案3：使用更健壮的模型作为主力

将阿里云百炼 (qwen3.5-plus) 设为主力模型：
- 百炼模型对敏感内容容忍度更高
- 减少 fallback 触发需求

## 当前解决方案的局限性

当前代码的 fallback 补丁**理论上应该工作**，但实际未生效的原因是：

1. **BabelDOC 的错误处理机制复杂**
   - 多层 try-except 包装
   - 子线程/进程隔离
   - 异步执行流程

2. **补丁应用时机问题**
   - 补丁在模块加载时应用
   - 但 BabelDOC 可能在运行时动态创建 translator 实例
   - 新实例没有继承补丁

3. **日志显示 fallback 未触发**
   - 从回归测试日志看，没有 "Switched to fallback model" 的日志
   - 说明错误没有被我们的补丁捕获

## 结论

fallback 机制未生效的根本原因是：**BabelDOC 内部的错误处理机制在更低层级捕获了内容过滤错误，导致我们的补丁无法拦截到异常。**

### 为什么单独翻译这些页面可以成功？

使用阿里云百炼模型单独翻译时：
1. 使用不同的配置（bailian-only.json）
2. 百炼模型对敏感内容容忍度更高
3. 不需要 fallback 机制

### 修复建议

1. **短期**：使用百炼模型作为主力模型（已验证可行）
2. **中期**：在翻译前预处理敏感内容段落，直接路由到备用模型
3. **长期**：深入研究 BabelDOC 源码，在正确的位置插入 fallback 逻辑

---
**分析完成时间**: 2026-03-26
**分析人**: Claude Code
