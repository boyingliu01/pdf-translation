# AGENTS.md - Test Directory Guidelines

**Generated:** 2026-05-05

## OVERVIEW

Unified pytest test suite for PDF translation tool. 124 tests across 6 modules. All API calls mocked — no real keys required.

## WHERE TO LOOK

| Task | File | Notes |
|------|------|-------|
| Config / model tests | `test_config_creation.py` | pydantic SettingsModel, OpenAISettings |
| Control char cleaning | `test_clean_json_output.py` | 32 parametrised control-char tests |
| Translation core | `test_translate.py` | Async flow, fallback, TranslationResult |
| CLI parsing | `test_cli.py` | argparse, main() success/failure paths |
| Engine templates | `test_engines.py` | All 7 config templates validated |
| Utility functions | `test_utils.py` | _is_incomplete_sentence, create_example_config |
| Shared fixtures | `conftest.py` | mock_config, mock_pdf_path, mock_translator |
| Test runner config | `pytest.ini` | Ignores legacy standalone scripts |
| **Legacy (deprecated)** | `test_final.py` | Standalone script — excluded from pytest |
| **Legacy (deprecated)** | `test_translate_docs.py` | Standalone script — excluded from pytest |
| Performance bench | `performance_test.py` | Timing metrics (not part of pytest suite) |
| Example usage | `example_usage.py` | Code examples (not part of pytest suite) |

## CONVENTIONS

### Framework: pytest

```bash
# Run all tests
python -m pytest test/

# Run with coverage
python -m pytest test/ --cov=pdf_translator --cov=translate_pdf --cov-report=term-missing

# Run single file
python -m pytest test/test_translate.py -v

# Run single test
python -m pytest test/test_translate.py::TestFallbackTranslator::test_fallback_exhausted -v
```

### Fixture Reuse

Shared fixtures in `conftest.py`:
- `mock_config` — minimal valid translator config dict
- `mock_pdf_path` — tmp_path PDF that actually exists (needed for translate_pdf_async)
- `mock_translator` — PDFTranslator instance with mock config
- `mock_translation_result` — MagicMock with all result attributes
- `mock_translate_stream` — async generator yielding progress + finish events

### Mocking Rules

- **API calls**: always mock (monkeypatch / unittest.mock.patch)
- **File system**: use `tmp_path` fixture for real files, `tmp_path` / `monkeypatch` for dirs
- **Async streams**: patch `pdf_translator.do_translate_async_stream` with async generator

### Writing New Tests

```python
def test_something(mock_translator, mock_pdf_path):
    """Use fixtures from conftest.py, assert with plain assert."""
    settings = mock_translator._create_settings(
        input_pdf=str(mock_pdf_path), output_dir="./out"
    )
    assert settings.translation.lang_in == "en"
```

## ANTI-PATTERNS

- **Do NOT** add `sys.path.insert(0, ...)` in test files — handled by `conftest.py`
- **Do NOT** use `print()` for assertions — use `assert` + pytest
- **Do NOT** call real APIs — always mock external services
- **Do NOT** commit tests that require real `config/config.json`

## COMMANDS

```bash
# Full test suite
python -m pytest test/ -v

# Coverage check
python -m pytest test/ --cov=pdf_translator --cov=translate_pdf --cov-report=term-missing

# Static analysis
python -m ruff check pdf_translator.py translate_pdf.py
python -m mypy pdf_translator.py translate_pdf.py --ignore-missing-imports
python -m bandit -r pdf_translator.py translate_pdf.py -f txt
python -m radon cc pdf_translator.py -a
```

## NOTES

- 124 tests, 0 failures, all offline
- Coverage: ~54% (patches for BabelDOC internals and PyMuPDF page numbering not unit-testable)
- Tests run in ~5 seconds
- `pytest.ini` excludes legacy scripts (`test_final.py`, `example_usage.py`, `performance_test.py`, `test_translate_docs.py`)
