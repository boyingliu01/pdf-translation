"""Test translation engine configuration templates."""

import json
from pathlib import Path

import pytest

from pdf_translator import PDFTranslator


PROJECT_ROOT = Path(__file__).parent.parent.resolve()
CONFIG_DIR = PROJECT_ROOT / "config"

# Config templates that should be loadable (no real API keys required)
CONFIG_TEMPLATES = [
    ("config.example.json", "Example"),
    ("config.openai.json", "OpenAI"),
    ("config.zhipu.json", "ZhipuAI"),
    ("config.volcengine.json", "VolcEngine"),
    ("config.siliconflow.json", "SiliconFlow"),
    ("config.test.json", "Test"),
    ("config.multi-model.json", "Multi-model"),
]


class TestEngineConfigTemplates:
    """Validate that every config template can initialise a translator."""

    @pytest.fixture(scope="class")
    def config_data(self):
        """Load all template configs once."""
        data = {}
        for filename, _ in CONFIG_TEMPLATES:
            path = CONFIG_DIR / filename
            if path.exists():
                with open(path, encoding="utf-8") as f:
                    data[filename] = json.load(f)
            else:
                data[filename] = None
        return data

    @pytest.mark.parametrize("filename, name", CONFIG_TEMPLATES)
    def test_config_loads(self, config_data, filename, name):
        """Each template should be valid JSON and loadable."""
        assert config_data[filename] is not None, f"{filename} not found"
        assert "translation_engine" in config_data[filename]

    @pytest.mark.parametrize("filename, name", CONFIG_TEMPLATES)
    def test_translator_init(self, config_data, filename, name):
        """PDFTranslator should initialise from each template."""
        config = config_data[filename]
        if config is None:
            pytest.skip(f"{filename} not found")

        # Override API key with a dummy so validation doesn't complain
        if "openai_api_key" in config:
            config["openai_api_key"] = "sk-test-dummy"
        if "models" in config:
            for m in config["models"]:
                m["api_key"] = "sk-test-dummy"

        translator = PDFTranslator(config_dict=config)
        assert translator.config is not None

    @pytest.mark.parametrize("filename, name", CONFIG_TEMPLATES)
    def test_create_settings(self, config_data, filename, name, tmp_path):
        """_create_settings should work for each engine template."""
        config = config_data[filename]
        if config is None:
            pytest.skip(f"{filename} not found")

        if "openai_api_key" in config:
            config["openai_api_key"] = "sk-test-dummy"
        if "models" in config:
            for m in config["models"]:
                m["api_key"] = "sk-test-dummy"

        translator = PDFTranslator(config_dict=config)
        pdf_path = tmp_path / "test.pdf"
        pdf_path.write_bytes(b"%PDF-1.4\n")  # minimal valid PDF header

        settings = translator._create_settings(
            input_pdf=str(pdf_path),
            output_dir="./output",
            source_lang="en",
            target_lang="zh",
        )
        assert settings.translation.lang_in == "en"
        assert settings.translate_engine_settings is not None

    @pytest.mark.parametrize("filename, name", CONFIG_TEMPLATES)
    def test_settings_validation(self, config_data, filename, name, tmp_path):
        """Settings should pass validation when input_files is bypassed."""
        config = config_data[filename]
        if config is None:
            pytest.skip(f"{filename} not found")

        if "openai_api_key" in config:
            config["openai_api_key"] = "sk-test-dummy"
        if "models" in config:
            for m in config["models"]:
                m["api_key"] = "sk-test-dummy"

        translator = PDFTranslator(config_dict=config)
        pdf_path = tmp_path / "test.pdf"
        pdf_path.write_bytes(b"%PDF-1.4\n")

        settings = translator._create_settings(
            input_pdf=str(pdf_path),
            output_dir="./output",
        )
        # Temporarily clear input_files to skip file-existence check
        original = settings.basic.input_files
        settings.basic.input_files = set()
        try:
            settings.validate_settings()
        finally:
            settings.basic.input_files = original


class TestMultiModelFallbackConfig:
    """Specific tests for the multi-model fallback template."""

    @pytest.fixture
    def multi_config(self):
        path = CONFIG_DIR / "config.multi-model.json"
        if not path.exists():
            pytest.skip("config.multi-model.json not found")
        with open(path, encoding="utf-8") as f:
            return json.load(f)

    def test_has_models_array(self, multi_config):
        """Multi-model config must contain a 'models' list."""
        assert "models" in multi_config
        assert isinstance(multi_config["models"], list)
        assert len(multi_config["models"]) >= 2

    def test_fallback_threshold(self, multi_config):
        """Fallback threshold should be a positive integer."""
        fb = multi_config.get("fallback", {})
        assert "consecutive_failures" in fb
        assert fb["consecutive_failures"] > 0

    def test_models_have_required_fields(self, multi_config):
        """Each model entry must have api_key, base_url, model."""
        for m in multi_config["models"]:
            assert "api_key" in m
            assert "base_url" in m
            assert "model" in m

    def test_fallback_translator_created(self, multi_config):
        """PDFTranslator should detect multi-model config and create FallbackTranslator."""
        # Sanitise keys
        for m in multi_config["models"]:
            m["api_key"] = "sk-test-dummy"
        translator = PDFTranslator(config_dict=multi_config)
        assert translator.fallback_translator is not None
        assert len(translator.fallback_translator.models) == len(multi_config["models"])
