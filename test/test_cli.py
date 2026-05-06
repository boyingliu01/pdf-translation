"""Test CLI argument parsing and main flow in translate_pdf.py."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

import translate_pdf


class TestCLIArguments:
    """Tests for argparse CLI argument parsing."""

    def test_missing_input_exits(self, capsys, monkeypatch):
        """Running without --input should print error and exit with code 1."""
        monkeypatch.setattr("sys.argv", ["translate_pdf.py"])
        with pytest.raises(SystemExit) as exc_info:
            translate_pdf.main()
        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert "缺少必需参数" in captured.err or "required" in captured.err

    def test_create_config_flag(self, tmp_path, monkeypatch):
        """--create-config should write a config file and exit cleanly."""
        config_path = tmp_path / "myconfig.json"
        monkeypatch.setattr("sys.argv", [
            "translate_pdf.py",
            "--create-config",
            "--config", str(config_path),
        ])
        translate_pdf.main()
        assert config_path.exists()
        content = config_path.read_text(encoding="utf-8")
        assert "translation_engine" in content

    def test_input_file_not_found(self, capsys, monkeypatch):
        """Non-existent input file should exit with code 1."""
        monkeypatch.setattr("sys.argv", [
            "translate_pdf.py",
            "--input", "/nonexistent/file.pdf",
        ])
        with pytest.raises(SystemExit) as exc_info:
            translate_pdf.main()
        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert "不存在" in captured.err or "not exist" in captured.err

    def test_config_file_not_found(self, capsys, monkeypatch, mock_pdf_path):
        """Missing config file should exit with code 1."""
        monkeypatch.setattr("sys.argv", [
            "translate_pdf.py",
            "--input", str(mock_pdf_path),
            "--config", "/nonexistent/config.json",
        ])
        with pytest.raises(SystemExit) as exc_info:
            translate_pdf.main()
        assert exc_info.value.code == 1


class TestCLIOptionsParsing:
    """Test that argparse correctly parses each CLI option."""

    @pytest.fixture
    def parser(self):
        """Return the argparse parser for inspection."""
        import argparse
        # Replicate the parser creation from translate_pdf.py
        p = argparse.ArgumentParser()
        p.add_argument("--input", "-i", required=False)
        p.add_argument("--output", "-o")
        p.add_argument("--config", "-c", default="config/config.json")
        p.add_argument("--lang-in", "-li", default="en")
        p.add_argument("--lang-out", "-lo", default="zh")
        p.add_argument("--no-dual", action="store_true")
        p.add_argument("--no-mono", action="store_true")
        p.add_argument("--watermark", choices=["watermarked", "no_watermark", "both"], default="watermarked")
        p.add_argument("--pages")
        p.add_argument("--max-pages-per-part", type=int)
        p.add_argument("--enhance-compatibility", action="store_true")
        p.add_argument("--create-config", action="store_true")
        return p

    def test_defaults(self, parser):
        """Default values should match expected defaults."""
        args = parser.parse_args(["--input", "test.pdf"])
        assert args.config == "config/config.json"
        assert args.lang_in == "en"
        assert args.lang_out == "zh"
        assert args.no_dual is False
        assert args.no_mono is False
        assert args.watermark == "watermarked"
        assert args.pages is None
        assert args.max_pages_per_part is None
        assert args.enhance_compatibility is False

    def test_all_flags(self, parser):
        """All flags should be parsed correctly."""
        args = parser.parse_args([
            "-i", "doc.pdf",
            "-o", "output/",
            "-c", "config/zhipu.json",
            "-li", "ja",
            "-lo", "en",
            "--no-dual",
            "--no-mono",
            "--watermark", "both",
            "--pages", "1-5,10",
            "--max-pages-per-part", "50",
            "--enhance-compatibility",
        ])
        assert args.input == "doc.pdf"
        assert args.output == "output/"
        assert args.config == "config/zhipu.json"
        assert args.lang_in == "ja"
        assert args.lang_out == "en"
        assert args.no_dual is True
        assert args.no_mono is True
        assert args.watermark == "both"
        assert args.pages == "1-5,10"
        assert args.max_pages_per_part == 50
        assert args.enhance_compatibility is True


class TestMainTranslationFlow:
    """Integration-ish tests for the main() translation flow with mocked translator."""

    def test_successful_translation_output(self, mock_pdf_path, monkeypatch, capsys):
        """Successful translation should print result paths."""
        monkeypatch.setattr("sys.argv", [
            "translate_pdf.py",
            "--input", str(mock_pdf_path),
            "--config", "config/config.test.json",
        ])

        mock_result = MagicMock()
        mock_result.dual_pdf_path = str(mock_pdf_path.with_suffix(".dual.pdf"))
        mock_result.mono_pdf_path = None
        mock_result.no_watermark_dual_pdf_path = None
        mock_result.no_watermark_mono_pdf_path = None
        mock_result.auto_extracted_glossary_path = None
        mock_result.total_seconds = 10.5
        mock_result.peak_memory_usage = 128.0

        with patch("translate_pdf.PDFTranslator") as MockTranslator:
            instance = MockTranslator.return_value
            instance.translate_pdf.return_value = mock_result
            translate_pdf.main()

        captured = capsys.readouterr()
        assert "翻译完成" in captured.out or "complete" in captured.out.lower()

    def test_translation_failure_output(self, mock_pdf_path, monkeypatch, capsys):
        """Translation failure should print error and exit with code 1."""
        monkeypatch.setattr("sys.argv", [
            "translate_pdf.py",
            "--input", str(mock_pdf_path),
            "--config", "config/config.test.json",
        ])

        with patch("translate_pdf.PDFTranslator") as MockTranslator:
            instance = MockTranslator.return_value
            instance.translate_pdf.side_effect = RuntimeError("Mock translation failure")
            with pytest.raises(SystemExit) as exc_info:
                translate_pdf.main()
            assert exc_info.value.code == 1

        captured = capsys.readouterr()
        assert "翻译失败" in captured.err or "failed" in captured.err.lower()
