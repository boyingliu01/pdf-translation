# BabelDoc Issue: 多模型 Fallback 支持

## 标题

feat(translator): add multi-model fallback support for content filter errors

## 正文

## Feature Request

### Problem Statement

When translating PDF documents containing sensitive content (e.g., geopolitical conflicts, military topics), some LLM providers (like ZhipuAI) return content filter errors. Currently, BabelDoc throws a `ContentFilterError` and skips translating these paragraphs, leaving them untranslated in the output.

### Use Case

In our PDF translation project, we encountered this issue with pages discussing:
- Russia-Ukraine conflict
- Project Maven (Pentagon AI program)
- Hamas attack events

These paragraphs were left in English while the rest of the document was translated to Chinese.

### Proposed Solution

Add native multi-model fallback support in BabelDoc's translator:

1. **Configuration**: Allow users to specify multiple translation models with priority
2. **Automatic Fallback**: When the primary model fails due to content filtering, automatically try backup models
3. **Error Classification**: Distinguish between content filter errors (retryable) and other errors

### Example Configuration

```toml
[babeldoc.translation]
primary_model = "zhipu"

[[babeldoc.translation.fallback_models]]
name = "bailian"
model = "qwen3.5-plus"
base_url = "https://api.bailian.com/v1"
api_key = "${BAILIAN_API_KEY}"

[[babeldoc.translation.fallback_models]]
name = "codebuddy"
model = "gpt-5.4"
base_url = "https://www.codebuddy.ai/v2"
api_key = "${CODEBUDDY_API_KEY}"
```

### Implementation Sketch

```python
class BaseTranslator:
    def __init__(self, ..., fallback_translators: List[BaseTranslator] = None):
        self.fallback_translators = fallback_translators or []
    
    def translate_with_fallback(self, text, ...):
        try:
            return self.translate(text, ...)
        except ContentFilterError:
            for fallback in self.fallback_translators:
                try:
                    return fallback.translate(text, ...)
                except Exception:
                    continue
            raise TranslationError("All models failed")
```

### Benefits

1. **Higher Translation Success Rate**: Automatically handle content filter errors
2. **Better User Experience**: No manual intervention needed
3. **Flexibility**: Users can choose different providers for fallback (domestic + international)

### Backward Compatibility

This feature should be fully backward compatible. Users who don't configure fallback models will see no change in behavior.

### Willingness to Contribute

I am willing to implement this feature and submit a PR if the maintainers agree with the approach.

---

**Related**: This issue was encountered in our project where we had to implement a workaround by patching BabelDoc's translator externally. Native support would be much cleaner.
