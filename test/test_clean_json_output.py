"""Test control-character cleaning in JSON output."""

import json

import pytest

from pdf_translator import clean_json_output


class TestCleanJsonOutput:
    """Tests for clean_json_output wrapper-tags and control-char removal."""

    def test_normal_json_unchanged(self):
        """Normal JSON without wrappers or control chars should pass through."""
        text = '[{"id": 0, "output": "hello world"}]'
        assert clean_json_output(text) == text

    def test_strip_json_wrapper_tags(self):
        """<json>...</json> tags should be removed."""
        text = '<json>[{"id": 0, "output": "hello"}]</json>'
        assert clean_json_output(text) == '[{"id": 0, "output": "hello"}]'

    def test_strip_markdown_code_block(self):
        """```json and ``` fences should be removed."""
        text = '```json\n[{"id": 0, "output": "hello"}]\n```'
        assert clean_json_output(text) == '[{"id": 0, "output": "hello"}]'

    def test_strip_plain_code_block(self):
        """Plain ``` fences without language tag should also be removed."""
        text = '```\n[{"id": 0, "output": "hello"}]\n```'
        assert clean_json_output(text) == '[{"id": 0, "output": "hello"}]'

    @pytest.mark.parametrize("code", list(range(32)))
    def test_control_chars_removed_except_whitespace(self, code):
        """All ASCII 0-31 control chars should be removed except \\t \\n \\r."""
        char = chr(code)
        if char in ("\t", "\n", "\r"):
            text = f'[{{"output": "hello{char}world"}}]'
            result = clean_json_output(text)
            assert char in result, f"Whitespace char {code!r} should be preserved"
        else:
            text = f'[{{"output": "hello{char}world"}}]'
            result = clean_json_output(text)
            assert char not in result, f"Control char {code!r} should be removed"

    def test_multiple_control_chars(self):
        """Multiple consecutive control chars should all be removed."""
        text = '[{"output": "hello' + chr(0) + chr(1) + chr(2) + 'world"}]'
        result = clean_json_output(text)
        assert result == '[{"output": "helloworld"}]'

    def test_result_is_valid_json(self):
        """After cleaning, the string should be valid JSON."""
        text = '[{"id": 0, "output": "hello' + chr(0) + 'world"}]'
        cleaned = clean_json_output(text)
        parsed = json.loads(cleaned)
        assert parsed[0]["id"] == 0
        assert parsed[0]["output"] == "helloworld"

    def test_real_world_control_char_scenario(self):
        """Simulate a real-world PDF extraction with mixed control chars."""
        text = '[{"output": "This is' + chr(1) + chr(2) + chr(3) + 'a test"}]'
        cleaned = clean_json_output(text)
        parsed = json.loads(cleaned)
        assert parsed[0]["output"] == "This isa test"


class TestBabelDocImport:
    """Smoke tests for BabelDOC internal module availability."""

    def test_il_translator_llm_only_has_clean_method(self):
        """ILTranslatorLLMOnly should expose _clean_json_output."""
        pytest.importorskip(
            "babeldoc.format.pdf.document_il.midend.il_translator_llm_only",
            reason="babeldoc not installed",
        )
        from babeldoc.format.pdf.document_il.midend.il_translator_llm_only import (
            ILTranslatorLLMOnly,
        )

        assert hasattr(ILTranslatorLLMOnly, "_clean_json_output")

    def test_clean_method_signature(self):
        """_clean_json_output should accept llm_output parameter."""
        pytest.importorskip(
            "babeldoc.format.pdf.document_il.midend.il_translator_llm_only",
            reason="babeldoc not installed",
        )
        from babeldoc.format.pdf.document_il.midend.il_translator_llm_only import (
            ILTranslatorLLMOnly,
        )
        import inspect

        sig = inspect.signature(ILTranslatorLLMOnly._clean_json_output)
        assert "llm_output" in sig.parameters

    def test_monkey_patch_compatible(self):
        """Our clean_json_output should be assignable to ILTranslatorLLMOnly."""
        pytest.importorskip(
            "babeldoc.format.pdf.document_il.midend.il_translator_llm_only",
            reason="babeldoc not installed",
        )
        from babeldoc.format.pdf.document_il.midend.il_translator_llm_only import (
            ILTranslatorLLMOnly,
        )

        original = ILTranslatorLLMOnly._clean_json_output
        try:
            ILTranslatorLLMOnly._clean_json_output = clean_json_output
            # Verify it behaves correctly after patch
            text = '[{"output": "test' + chr(0) + '"}]'
            result = ILTranslatorLLMOnly._clean_json_output(None, text)
            assert chr(0) not in result
        finally:
            ILTranslatorLLMOnly._clean_json_output = original
