# Multi-Model Fallback Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Implement automatic fallback between multiple translation models when one fails, with configurable priority order.

**Architecture:** Create a `FallbackTranslator` class that wraps multiple translator instances and handles switching logic. The class tracks consecutive failures and switches to the next model when threshold is reached. Logs notify users when switching occurs.

**Tech Stack:** Python 3.12+, pdf2zh-next, BabelDOC, OpenAI-compatible API

---

## Requirements Summary

| Item | Decision |
|------|----------|
| Trigger condition | All translation failures trigger fallback |
| Configuration | Array of models with priority order |
| Fallback granularity | Smart switching: switch after N consecutive failures |
| Notification | Log output to console |
| Backward compatibility | Support existing single-model config |

---

## File Structure

**Modify:**
- `pdf_translator.py` - Add `FallbackTranslator` class and integration

**Create:**
- `test/test_fallback_translator.py` - Unit tests for fallback logic

**Update:**
- `config/config.example.json` - Add multi-model config example

---

## Task 1: Define Configuration Schema

**Files:**
- Modify: `config/config.example.json`

**Step 1: Add multi-model configuration example**

```json
{
  "translation_engine": "openai",
  "models": [
    {
      "name": "zhipu",
      "api_key": "your-zhipu-api-key",
      "base_url": "https://open.bigmodel.cn/api/paas/v4",
      "model": "glm-4-flash"
    },
    {
      "name": "openai",
      "api_key": "your-openai-api-key",
      "base_url": "https://api.openai.com/v1",
      "model": "gpt-4o-mini"
    }
  ],
  "fallback": {
    "consecutive_failures": 3
  },
  "qps": 4,
  "min_text_length": 5,
  "debug": false
}
```

**Step 2: Commit**

```bash
git add config/config.example.json
git commit -m "docs: add multi-model fallback configuration example"
```

---

## Task 2: Implement FallbackTranslator Class

**Files:**
- Modify: `pdf_translator.py`
- Create: `test/test_fallback_translator.py`

**Step 1: Write the failing test**

Create `test/test_fallback_translator.py`:

```python
#!/usr/bin/env python3
"""Tests for FallbackTranslator class."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
from unittest.mock import Mock, patch, MagicMock
from pdf_translator import FallbackTranslator, FallbackModelConfig


def test_fallback_model_config():
    """Test FallbackModelConfig dataclass."""
    config = FallbackModelConfig(
        name="test",
        api_key="key123",
        base_url="https://api.test.com/v1",
        model="test-model"
    )
    assert config.name == "test"
    assert config.api_key == "key123"
    assert config.base_url == "https://api.test.com/v1"
    assert config.model == "test-model"


def test_fallback_translator_init():
    """Test FallbackTranslator initialization with multiple models."""
    models = [
        FallbackModelConfig("model1", "key1", "url1", "m1"),
        FallbackModelConfig("model2", "key2", "url2", "m2"),
    ]
    translator = FallbackTranslator(models)
    assert translator.current_index == 0
    assert translator.consecutive_failures == 0
    assert len(translator.models) == 2


def test_fallback_translator_switch_on_failures():
    """Test that translator switches after consecutive failures threshold."""
    models = [
        FallbackModelConfig("model1", "key1", "url1", "m1"),
        FallbackModelConfig("model2", "key2", "url2", "m2"),
    ]
    translator = FallbackTranslator(models, consecutive_failures_threshold=3)

    # Simulate 3 failures
    for _ in range(3):
        translator.record_failure()

    assert translator.current_index == 1
    assert translator.consecutive_failures == 0  # Reset after switch


def test_fallback_translator_reset_on_success():
    """Test that consecutive failures reset on success."""
    models = [
        FallbackModelConfig("model1", "key1", "url1", "m1"),
        FallbackModelConfig("model2", "key2", "url2", "m2"),
    ]
    translator = FallbackTranslator(models, consecutive_failures_threshold=3)

    # Simulate 2 failures
    translator.record_failure()
    translator.record_failure()
    assert translator.consecutive_failures == 2

    # Simulate success
    translator.record_success()
    assert translator.consecutive_failures == 0


def test_fallback_translator_no_more_models():
    """Test behavior when all models have failed."""
    models = [
        FallbackModelConfig("model1", "key1", "url1", "m1"),
    ]
    translator = FallbackTranslator(models, consecutive_failures_threshold=1)

    # Should not crash, just stay at 0
    translator.record_failure()
    translator.record_failure()
    translator.record_failure()

    assert translator.current_index == 0
    assert translator.has_more_models() == False


def test_fallback_translator_get_current():
    """Test getting current model config."""
    models = [
        FallbackModelConfig("model1", "key1", "url1", "m1"),
        FallbackModelConfig("model2", "key2", "url2", "m2"),
    ]
    translator = FallbackTranslator(models)

    current = translator.get_current_model()
    assert current.name == "model1"

    translator.record_failure()
    translator.record_failure()
    translator.record_failure()

    current = translator.get_current_model()
    assert current.name == "model2"


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    test_fallback_model_config()
    test_fallback_translator_init()
    test_fallback_translator_switch_on_failures()
    test_fallback_translator_reset_on_success()
    test_fallback_translator_no_more_models()
    test_fallback_translator_get_current()
    print("All tests passed!")
```

**Step 2: Run test to verify it fails**

```bash
cd /e/2-booboo/pdf-translation && python test/test_fallback_translator.py
```

Expected: FAIL with ImportError or AttributeError

**Step 3: Implement FallbackTranslator class**

Add to `pdf_translator.py` after imports:

```python
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class FallbackModelConfig:
    """Configuration for a single translation model."""
    name: str
    api_key: str
    base_url: str
    model: str


class FallbackTranslator:
    """Manages fallback between multiple translation models.

    Tracks consecutive failures and switches to next model when threshold
    is reached. Logs all switching events for user visibility.
    """

    def __init__(
        self,
        models: List[FallbackModelConfig],
        consecutive_failures_threshold: int = 3,
    ):
        """Initialize with list of model configs.

        Args:
            models: List of FallbackModelConfig in priority order
            consecutive_failures_threshold: Number of failures before switching
        """
        if not models:
            raise ValueError("At least one model must be provided")

        self.models = models
        self.current_index = 0
        self.consecutive_failures = 0
        self.consecutive_failures_threshold = consecutive_failures_threshold
        self.logger = logging.getLogger(__name__)

    def get_current_model(self) -> FallbackModelConfig:
        """Get the currently active model configuration."""
        return self.models[self.current_index]

    def record_failure(self) -> bool:
        """Record a translation failure.

        Returns:
            True if switched to a new model, False otherwise
        """
        self.consecutive_failures += 1

        if self.consecutive_failures >= self.consecutive_failures_threshold:
            return self._switch_to_next_model()

        return False

    def record_success(self):
        """Record a successful translation, reset failure counter."""
        self.consecutive_failures = 0

    def _switch_to_next_model(self) -> bool:
        """Switch to the next available model.

        Returns:
            True if switched successfully, False if no more models
        """
        if self.current_index >= len(self.models) - 1:
            self.logger.warning(
                f"All {len(self.models)} models have failed. "
                "No more fallback options available."
            )
            return False

        old_model = self.get_current_model()
        self.current_index += 1
        self.consecutive_failures = 0
        new_model = self.get_current_model()

        self.logger.warning(
            f"Model '{old_model.name}/{old_model.model}' failed "
            f"{self.consecutive_failures_threshold} times consecutively. "
            f"Switching to '{new_model.name}/{new_model.model}'"
        )

        return True

    def has_more_models(self) -> bool:
        """Check if there are more models to fall back to."""
        return self.current_index < len(self.models) - 1
```

**Step 4: Run test to verify it passes**

```bash
cd /e/2-booboo/pdf-translation && python test/test_fallback_translator.py
```

Expected: "All tests passed!"

**Step 5: Commit**

```bash
git add pdf_translator.py test/test_fallback_translator.py
git commit -m "feat: add FallbackTranslator class with core switching logic"
```

---

## Task 3: Integrate with PDFTranslator

**Files:**
- Modify: `pdf_translator.py`

**Step 1: Add configuration parsing helper**

Add to `pdf_translator.py`:

```python
def parse_fallback_config(config: Dict[str, Any]) -> Optional[FallbackTranslator]:
    """Parse fallback configuration from config dict.

    Args:
        config: Configuration dictionary

    Returns:
        FallbackTranslator if multi-model config, None otherwise
    """
    models_config = config.get("models")

    if not models_config:
        # Single model mode - use backward compatible config
        return None

    if not isinstance(models_config, list) or len(models_config) == 0:
        raise ValueError("'models' must be a non-empty list")

    models = []
    for m in models_config:
        if not all(k in m for k in ["api_key", "base_url", "model"]):
            raise ValueError(
                "Each model must have 'api_key', 'base_url', and 'model' fields"
            )
        models.append(FallbackModelConfig(
            name=m.get("name", m["model"]),
            api_key=m["api_key"],
            base_url=m["base_url"],
            model=m["model"],
        ))

    fallback_config = config.get("fallback", {})
    threshold = fallback_config.get("consecutive_failures", 3)

    return FallbackTranslator(models, threshold)
```

**Step 2: Modify PDFTranslator.__init__**

Update `PDFTranslator.__init__` to parse fallback config:

```python
def __init__(
    self,
    config_path: Optional[str] = None,
    config_dict: Optional[Dict[str, Any]] = None,
):
    """
    初始化翻译器

    Args:
        config_path: 配置文件路径（JSON格式）
        config_dict: 配置字典（优先级高于config_path）
    """
    if config_dict:
        self.config = config_dict
    elif config_path:
        with open(config_path, "r", encoding="utf-8") as f:
            self.config = json.load(f)
    else:
        raise ValueError("必须提供 config_path 或 config_dict")

    # 设置日志
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    self.logger = logging.getLogger(__name__)

    # Parse fallback configuration
    self.fallback_translator = parse_fallback_config(self.config)
```

**Step 3: Add patch application method**

Add method to apply translation fallback patch:

```python
def _apply_fallback_patch(self):
    """Apply patch to intercept translation failures and trigger fallback."""
    if not self.fallback_translator:
        return  # No fallback configured

    try:
        from babeldoc.format.pdf.document_il.midend import il_translator
        from openai import BadRequestError

        original_translate_paragraph = il_translator.ILTranslator.translate_paragraph

        def patched_translate_paragraph(self_il, *args, **kwargs):
            """Patched translate_paragraph with fallback support."""
            max_attempts = len(self.fallback_translator.models)

            for attempt in range(max_attempts):
                try:
                    result = original_translate_paragraph(self_il, *args, **kwargs)
                    self.fallback_translator.record_success()
                    return result
                except BadRequestError as e:
                    self.logger.warning(
                        f"Translation failed with BadRequestError: {e}"
                    )
                    if not self.fallback_translator.record_failure():
                        raise  # No more models to try
                    # Update translator settings for new model
                    self._update_translator_settings(self_il)
                except Exception as e:
                    self.logger.warning(f"Translation failed: {e}")
                    if not self.fallback_translator.record_failure():
                        raise
                    self._update_translator_settings(self_il)

            raise RuntimeError("All translation models failed")

        il_translator.ILTranslator.translate_paragraph = patched_translate_paragraph
        self.logger.info("Fallback translation patch applied successfully")

    except ImportError as e:
        self.logger.warning(f"Could not apply fallback patch: {e}")
    except Exception as e:
        self.logger.warning(f"Could not apply fallback patch: {e}")

def _update_translator_settings(self, il_translator_instance):
    """Update translator instance with current fallback model settings."""
    if not self.fallback_translator:
        return

    model_config = self.fallback_translator.get_current_model()

    # Update the translate engine settings
    settings = il_translator_instance.translation_config.translate_engine_settings
    settings.openai_api_key = model_config.api_key
    settings.openai_base_url = model_config.base_url
    settings.openai_model = model_config.model

    # Recreate the client if needed
    if hasattr(il_translator_instance.translate_engine, 'client'):
        import openai
        il_translator_instance.translate_engine.client = openai.OpenAI(
            base_url=model_config.base_url,
            api_key=model_config.api_key,
        )
```

**Step 4: Call patch in translate_pdf_async**

Add patch call at the beginning of `translate_pdf_async`:

```python
async def translate_pdf_async(
    self,
    input_pdf: str,
    output_dir: Optional[str] = None,
    source_lang: str = "en",
    target_lang: str = "zh",
    progress_callback=None,
    **kwargs,
) -> TranslationResult:
    """..."""
    # Apply fallback patch if configured
    self._apply_fallback_patch()

    input_path = Path(input_pdf)
    # ... rest of the method
```

**Step 5: Commit**

```bash
git add pdf_translator.py
git commit -m "feat: integrate FallbackTranslator with PDFTranslator"
```

---

## Task 4: Add Integration Test

**Files:**
- Create: `test/test_fallback_integration.py`

**Step 1: Write integration test**

```python
#!/usr/bin/env python3
"""Integration test for multi-model fallback."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
from pdf_translator import PDFTranslator, FallbackModelConfig, FallbackTranslator

logging.basicConfig(level=logging.INFO)


def test_config_parsing_multi_model():
    """Test parsing multi-model configuration."""
    config = {
        "models": [
            {
                "name": "model1",
                "api_key": "key1",
                "base_url": "url1",
                "model": "m1"
            },
            {
                "name": "model2",
                "api_key": "key2",
                "base_url": "url2",
                "model": "m2"
            }
        ],
        "fallback": {
            "consecutive_failures": 2
        }
    }

    translator = PDFTranslator(config_dict=config)
    assert translator.fallback_translator is not None
    assert len(translator.fallback_translator.models) == 2
    assert translator.fallback_translator.consecutive_failures_threshold == 2


def test_config_parsing_single_model_backward_compat():
    """Test backward compatibility with single-model config."""
    config = {
        "translation_engine": "openai",
        "openai_api_key": "test-key",
        "openai_base_url": "https://api.test.com/v1",
        "openai_model": "test-model"
    }

    translator = PDFTranslator(config_dict=config)
    # Should NOT have fallback translator in single-model mode
    assert translator.fallback_translator is None


def test_config_validation_missing_fields():
    """Test that missing required fields raise error."""
    config = {
        "models": [
            {
                "name": "incomplete"
                # Missing api_key, base_url, model
            }
        ]
    }

    try:
        translator = PDFTranslator(config_dict=config)
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "must have" in str(e)


if __name__ == "__main__":
    test_config_parsing_multi_model()
    test_config_parsing_single_model_backward_compat()
    test_config_validation_missing_fields()
    print("All integration tests passed!")
```

**Step 2: Run test**

```bash
cd /e/2-booboo/pdf-translation && python test/test_fallback_integration.py
```

Expected: "All integration tests passed!"

**Step 3: Commit**

```bash
git add test/test_fallback_integration.py
git commit -m "test: add integration tests for multi-model fallback config"
```

---

## Task 5: Update CLAUDE.md Documentation

**Files:**
- Modify: `CLAUDE.md`

**Step 1: Add multi-model fallback section**

Add after the config schema section:

```markdown
### Multi-Model Fallback Configuration

For documents with sensitive content that may trigger API content filters,
you can configure multiple translation models with automatic fallback:

```json
{
  "models": [
    {
      "name": "zhipu",
      "api_key": "your-zhipu-key",
      "base_url": "https://open.bigmodel.cn/api/paas/v4",
      "model": "glm-4-flash"
    },
    {
      "name": "openai",
      "api_key": "your-openai-key",
      "base_url": "https://api.openai.com/v1",
      "model": "gpt-4o-mini"
    }
  ],
  "fallback": {
    "consecutive_failures": 3
  }
}
```

**Fallback Behavior:**
- Models are tried in order of configuration
- After N consecutive failures, switches to next model
- Logs warning when switching occurs
- Continues until all models exhausted

**Backward Compatibility:**
- Single-model configuration still supported
- Just use `openai_api_key`, `openai_base_url`, `openai_model` directly
```

**Step 2: Commit**

```bash
git add CLAUDE.md
git commit -m "docs: add multi-model fallback configuration documentation"
```

---

## Verification

### Success Criteria
1. All unit tests pass
2. All integration tests pass
3. Backward compatible with single-model config
4. Logs show model switching when failures occur

### Test Commands
```bash
# Unit tests
python test/test_fallback_translator.py

# Integration tests
python test/test_fallback_integration.py

# Full translation test with multi-model config
python translate_pdf.py -i test.pdf -o output --config config/config.example.json
```

---

## Rollback Plan

If the fallback mechanism causes issues:

1. Use single-model configuration (backward compatible)
2. Or set `models: null` in config to disable fallback

```json
{
  "models": null,
  "openai_api_key": "your-key",
  "openai_base_url": "...",
  "openai_model": "..."
}
```