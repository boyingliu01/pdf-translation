"""Test configuration creation (no file validation required)."""

import pytest

from pdf2zh_next.config.model import BasicSettings, PDFSettings, SettingsModel, TranslationSettings
from pdf2zh_next.config.translate_engine_model import OpenAISettings


class TestOpenAISettings:
    """Tests for OpenAISettings model creation."""

    def test_create_openai_settings(self):
        """OpenAISettings should accept api_key, base_url, and model."""
        engine = OpenAISettings(
            openai_api_key="sk-test",
            openai_base_url="https://api.openai.com/v1",
            openai_model="gpt-4o-mini",
        )
        assert engine.translate_engine_type == "OpenAI"
        assert engine.openai_model == "gpt-4o-mini"
        assert engine.openai_base_url == "https://api.openai.com/v1"
        assert engine.openai_api_key == "sk-test"


class TestSettingsModel:
    """Tests for SettingsModel creation and validation."""

    @pytest.fixture
    def valid_settings(self):
        """Build a minimal valid SettingsModel."""
        engine = OpenAISettings(
            openai_api_key="sk-test",
            openai_base_url="https://api.openai.com/v1",
            openai_model="gpt-4o-mini",
        )
        basic = BasicSettings(input_files={"test.pdf"}, debug=False)
        translation = TranslationSettings(lang_in="en", lang_out="zh", output="./output", qps=4)
        pdf = PDFSettings()
        return SettingsModel(
            basic=basic,
            translation=translation,
            pdf=pdf,
            translate_engine_settings=engine,
        )

    def test_create_settings_model(self, valid_settings):
        """SettingsModel should assemble all sub-models correctly."""
        assert valid_settings.basic.input_files == {"test.pdf"}
        assert valid_settings.translation.lang_in == "en"
        assert valid_settings.translation.lang_out == "zh"
        assert valid_settings.pdf is not None
        assert valid_settings.translate_engine_settings.openai_model == "gpt-4o-mini"

    def test_validate_settings_without_file_check(self, valid_settings):
        """validate_settings should pass when input_files is empty."""
        original = valid_settings.basic.input_files
        valid_settings.basic.input_files = set()
        try:
            valid_settings.validate_settings()
        finally:
            valid_settings.basic.input_files = original


class TestPDFTranslatorConfig:
    """Tests for PDFTranslator configuration handling."""

    def test_translator_from_dict(self, mock_config):
        """PDFTranslator should initialize from a config dict."""
        from pdf_translator import PDFTranslator

        translator = PDFTranslator(config_dict=mock_config)
        assert translator.config == mock_config
        assert translator.fallback_translator is None

    def test_create_settings(self, mock_translator, mock_pdf_path):
        """_create_settings should produce a valid SettingsModel."""
        settings = mock_translator._create_settings(
            input_pdf=str(mock_pdf_path),
            output_dir="./output",
            source_lang="en",
            target_lang="zh",
        )
        assert settings.basic.input_files == {str(mock_pdf_path)}
        assert settings.translation.lang_in == "en"
        assert settings.translation.lang_out == "zh"
        assert settings.translate_engine_settings.openai_model == "gpt-4o-mini"
