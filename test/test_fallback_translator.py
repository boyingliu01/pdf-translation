#!/usr/bin/env python3
"""Tests for FallbackTranslator class."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
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