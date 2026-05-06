"""Pytest configuration and shared fixtures for pdf-translation tests."""

import sys
from pathlib import Path
from unittest.mock import MagicMock, AsyncMock

import pytest

# Add project root to Python path (replaces manual sys.path in each test file)
PROJECT_ROOT = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(PROJECT_ROOT))


@pytest.fixture
def project_root() -> Path:
    """Return the project root directory."""
    return PROJECT_ROOT


@pytest.fixture
def mock_config() -> dict:
    """Return a minimal valid translator config dict."""
    return {
        "translation_engine": "openai",
        "openai_api_key": "sk-test-key",
        "openai_base_url": "https://api.openai.com/v1",
        "openai_model": "gpt-4o-mini",
        "qps": 4,
        "min_text_length": 5,
        "debug": False,
        "custom_system_prompt": None,
    }


@pytest.fixture
def mock_pdf_path(tmp_path: Path) -> Path:
    """Return a dummy PDF file path that actually exists (needed for translate_pdf_async)."""
    path = tmp_path / "test.pdf"
    path.write_bytes(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n2 0 obj\n<< /Type /Pages /Kids [] /Count 0 >>\nendobj\nxref\n0 3\n0000000000 65535 f\n0000000015 00000 n\n0000000066 00000 n\ntrailer\n<< /Size 3 /Root 1 0 R >>\nstartxref\n115\n%%EOF\n")
    return path


@pytest.fixture
def mock_translator(mock_config: dict):
    """Return a PDFTranslator instance with mock config."""
    from pdf_translator import PDFTranslator

    return PDFTranslator(config_dict=mock_config)


@pytest.fixture
def mock_translation_result():
    """Return a mock TranslationResult-like object."""
    result = MagicMock()
    result.original_pdf_path = "test.pdf"
    result.mono_pdf_path = "test.mono.pdf"
    result.dual_pdf_path = "test.dual.pdf"
    result.no_watermark_mono_pdf_path = "test.mono.no-watermark.pdf"
    result.no_watermark_dual_pdf_path = "test.dual.no-watermark.pdf"
    result.auto_extracted_glossary_path = None
    result.total_seconds = 12.34
    result.peak_memory_usage = 256.0
    return result


@pytest.fixture
def mock_translate_stream(mock_translation_result):
    """Return an async generator that yields progress events and a finish event."""

    async def stream(*args, **kwargs):
        yield {"type": "progress_update", "stage": "translate", "stage_progress": 0.5, "overall_progress": 0.5}
        yield {
            "type": "finish",
            "translate_result": mock_translation_result,
        }

    return stream
