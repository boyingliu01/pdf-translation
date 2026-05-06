"""Test PDF translation flow with mocked async stream."""

from unittest.mock import patch

import pytest

from pdf_translator import PDFTranslator, TranslationResult


class TestPDFTranslatorCreation:
    """Smoke tests for translator initialization and settings."""

    def test_init_from_dict(self, mock_config):
        """Translator should initialise from a config dict."""
        translator = PDFTranslator(config_dict=mock_config)
        assert translator.config["translation_engine"] == "openai"

    def test_init_from_missing_path_raises(self):
        """Translator should raise when config path does not exist."""
        with pytest.raises(FileNotFoundError):
            PDFTranslator(config_path="nonexistent.json")

    def test_init_without_args_raises(self):
        """Translator should raise when neither path nor dict is given."""
        with pytest.raises(ValueError):
            PDFTranslator()


class TestCreateSettings:
    """Tests for _create_settings method."""

    def test_basic_settings(self, mock_translator, mock_pdf_path):
        """_create_settings should produce settings with correct langs."""
        settings = mock_translator._create_settings(
            input_pdf=str(mock_pdf_path),
            output_dir="./output",
            source_lang="en",
            target_lang="zh",
        )
        assert settings.translation.lang_in == "en"
        assert settings.translation.lang_out == "zh"

    def test_pages_option(self, mock_translator, mock_pdf_path):
        """pages kwarg should be reflected in PDFSettings."""
        settings = mock_translator._create_settings(
            input_pdf=str(mock_pdf_path),
            output_dir="./output",
            pages="1-5",
        )
        assert settings.pdf.pages == "1-5"

    def test_no_dual_no_mono(self, mock_translator, mock_pdf_path):
        """no_dual / no_mono flags should be stored in PDFSettings."""
        settings = mock_translator._create_settings(
            input_pdf=str(mock_pdf_path),
            output_dir="./output",
            no_dual=True,
            no_mono=True,
        )
        assert settings.pdf.no_dual is True
        assert settings.pdf.no_mono is True


class TestTranslationResult:
    """Tests for TranslationResult dataclass-like wrapper."""

    def test_from_object(self, mock_translation_result):
        """TranslationResult should accept a mocked object with attributes."""
        tr = TranslationResult(mock_translation_result)
        assert tr.dual_pdf_path == "test.dual.pdf"
        assert tr.total_seconds == 12.34

    def test_from_dict(self):
        """TranslationResult should accept a plain dict."""
        data = {
            "original_pdf_path": "a.pdf",
            "mono_pdf_path": "a.mono.pdf",
            "dual_pdf_path": "a.dual.pdf",
            "no_watermark_mono_pdf_path": None,
            "no_watermark_dual_pdf_path": None,
            "auto_extracted_glossary_path": None,
            "total_seconds": 5.0,
            "peak_memory_usage": 128.0,
        }
        tr = TranslationResult(data)
        assert tr.original_pdf_path == "a.pdf"
        assert tr.total_seconds == 5.0

    def test_str_output(self, mock_translation_result):
        """String representation should contain key paths."""
        tr = TranslationResult(mock_translation_result)
        text = str(tr)
        assert "Original PDF" in text
        assert "test.dual.pdf" in text


class TestTranslatePdfAsync:
    """Tests for the async translation flow using mocked stream."""

    @pytest.mark.asyncio
    async def test_translate_emits_progress(self, mock_translator, mock_pdf_path, mock_translate_stream):
        """translate_pdf_async should yield progress events and return result."""
        with patch("pdf_translator.do_translate_async_stream", mock_translate_stream):
            result = await mock_translator.translate_pdf_async(
                input_pdf=str(mock_pdf_path),
                output_dir="./output",
            )
        assert result is not None
        assert result.dual_pdf_path == "test.dual.pdf"

    @pytest.mark.asyncio
    async def test_translate_with_callback(self, mock_translator, mock_pdf_path, mock_translate_stream):
        """Progress callback should receive progress_update events."""
        callbacks = []

        def cb(event):
            callbacks.append(event)

        with patch("pdf_translator.do_translate_async_stream", mock_translate_stream):
            await mock_translator.translate_pdf_async(
                input_pdf=str(mock_pdf_path),
                output_dir="./output",
                progress_callback=cb,
            )

        assert len(callbacks) >= 1
        assert callbacks[0]["type"] == "progress_update"

    @pytest.mark.asyncio
    async def test_translate_missing_pdf_raises(self, mock_translator):
        """Translating a non-existent PDF should raise FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            await mock_translator.translate_pdf_async(input_pdf="/nonexistent/file.pdf")


class TestFallbackTranslator:
    """Tests for multi-model fallback logic."""

    @pytest.fixture
    def fallback_config(self):
        return {
            "models": [
                {
                    "name": "primary",
                    "api_key": "key1",
                    "base_url": "https://api.openai.com/v1",
                    "model": "gpt-4o-mini",
                },
                {
                    "name": "backup",
                    "api_key": "key2",
                    "base_url": "https://api.openai.com/v1",
                    "model": "gpt-4o",
                },
            ],
            "fallback": {"consecutive_failures": 2},
        }

    def test_parse_fallback_creates_translator(self, fallback_config):
        """parse_fallback_config should build FallbackTranslator from dict."""
        from pdf_translator import parse_fallback_config

        ft = parse_fallback_config(fallback_config)
        assert ft is not None
        assert len(ft.models) == 2
        assert ft.get_current_model().name == "primary"

    def test_fallback_records_failure_and_switches(self, fallback_config):
        """After threshold failures, fallback should switch to next model."""
        from pdf_translator import parse_fallback_config

        ft = parse_fallback_config(fallback_config)
        assert ft.record_failure() is False  # 1 failure, threshold=2
        assert ft.record_failure() is True   # 2 failures, switch
        assert ft.get_current_model().name == "backup"

    def test_fallback_exhausted(self, fallback_config):
        """When all models fail, record_failure should return False."""
        from pdf_translator import parse_fallback_config

        ft = parse_fallback_config(fallback_config)
        ft.record_failure()  # 1
        ft.record_failure()  # 2 → switch to backup
        ft.record_failure()  # 1 on backup
        ft.record_failure()  # 2 on backup → exhausted
        assert ft.record_failure() is False
        assert ft.has_more_models() is False

    def test_single_model_returns_none(self, mock_config):
        """Config without 'models' array should return None (no fallback)."""
        from pdf_translator import parse_fallback_config

        assert parse_fallback_config(mock_config) is None

    def test_empty_models_raises(self):
        """Empty models list should raise ValueError."""
        from pdf_translator import FallbackTranslator

        with pytest.raises(ValueError, match="At least one model"):
            FallbackTranslator([])
