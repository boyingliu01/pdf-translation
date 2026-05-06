"""Test utility functions and edge cases in pdf_translator.py."""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from pdf_translator import (
    TranslationResult,
    _is_incomplete_sentence,
    clean_json_output,
    create_example_config,
)


class TestIsIncompleteSentence:
    """Tests for the _is_incomplete_sentence helper."""

    def test_empty_returns_false(self):
        assert _is_incomplete_sentence("") is False
        assert _is_incomplete_sentence(None) is False
        assert _is_incomplete_sentence("   ") is False

    def test_too_short_returns_false(self):
        assert _is_incomplete_sentence("ab") is False

    def test_ends_with_period_is_complete(self):
        assert _is_incomplete_sentence("Hello world.") is True

    def test_ends_with_exclamation_is_complete(self):
        assert _is_incomplete_sentence("Hello!") is True

    def test_ends_with_question_is_complete(self):
        assert _is_incomplete_sentence("Hello?") is True

    def test_ends_with_colon_is_complete(self):
        assert _is_incomplete_sentence("Note:") is True

    def test_ends_with_quote_is_complete(self):
        assert _is_incomplete_sentence('She said "hello"') is True

    def test_ends_with_paren_is_complete(self):
        assert _is_incomplete_sentence("(hello)") is True

    def test_short_no_ending_is_incomplete(self):
        assert _is_incomplete_sentence("short") is False

    def test_long_no_ending_with_short_word(self):
        assert _is_incomplete_sentence("this is a test") is False

    def test_long_with_sentence_ending(self):
        assert _is_incomplete_sentence("this is a complete sentence.") is True

    def test_ends_with_dash_is_complete(self):
        assert _is_incomplete_sentence("hello—") is True


class TestCleanJsonOutputEdgeCases:
    """Additional edge-case tests for clean_json_output."""

    def test_standalone_function_call(self):
        """Calling as standalone function (not method) should work."""
        text = '<json>[{"id": 1}]</json>'
        result = clean_json_output(text)
        assert result == '[{"id": 1}]'

    def test_method_call_with_self(self):
        """Calling with dummy self argument should work."""
        text = '```json\n[{"id": 2}]\n```'
        result = clean_json_output(MagicMock(), text)
        assert result == '[{"id": 2}]'

    def test_only_whitespace(self):
        assert clean_json_output("   ") == ""

    def test_nested_wrappers(self):
        """Multiple overlapping wrappers should all be removed."""
        text = '<json>```json\n[{"id": 3}]\n```</json>'
        result = clean_json_output(text)
        assert result == '[{"id": 3}]'


class TestCreateExampleConfig:
    """Tests for the create_example_config helper."""

    def test_creates_valid_json(self, tmp_path):
        path = tmp_path / "example.json"
        create_example_config(str(path))
        assert path.exists()
        config = json.loads(path.read_text(encoding="utf-8"))
        assert config["translation_engine"] == "openai"
        assert config["openai_api_key"] == "your-api-key-here"
        assert config["qps"] == 4

    def test_default_path(self, tmp_path, monkeypatch):
        """Default path should be config/config.json relative to cwd."""
        monkeypatch.chdir(tmp_path)
        (tmp_path / "config").mkdir()
        create_example_config()
        assert (tmp_path / "config" / "config.json").exists()


class TestTranslationResultEdgeCases:
    """Edge cases for TranslationResult."""

    def test_from_unknown_type(self):
        """Passing an unknown type should initialise with defaults."""
        tr = TranslationResult(12345)
        assert tr.original_pdf_path is None
        assert tr.total_seconds == 0.0

    def test_str_with_none_paths(self):
        tr = TranslationResult({})
        text = str(tr)
        assert "Original PDF" in text
        assert "None" in text
