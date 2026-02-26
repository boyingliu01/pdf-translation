"""
PDF Translation Tool
基于 PDFMathTranslate-next 和 BabelDOC 的PDF翻译工具
"""

import asyncio
import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any, Union

# 导入 pdf2zh_next 的相关模块
try:
    from pdf2zh_next.config.model import (
        SettingsModel,
        BasicSettings,
        TranslationSettings,
        PDFSettings,
        WatermarkOutputMode,
    )
    from pdf2zh_next.config.translate_engine_model import OpenAISettings
    from pdf2zh_next.high_level import do_translate_async_stream
except ImportError:
    print("请先安装依赖: pip install -r requirements.txt")
    raise


class TranslationResult:
    """翻译结果"""

    def __init__(self, result_data: Union[Dict[str, Any], Any]):
        # 如果传入的是TranslateResult对象（BabelDOC的结果），直接读取其属性
        # 如果传入的是字典，则从字典中提取数据
        if hasattr(result_data, "original_pdf_path"):
            # TranslateResult对象
            self.original_pdf_path = result_data.original_pdf_path
            self.mono_pdf_path = result_data.mono_pdf_path
            self.dual_pdf_path = result_data.dual_pdf_path
            self.no_watermark_mono_pdf_path = result_data.no_watermark_mono_pdf_path
            self.no_watermark_dual_pdf_path = result_data.no_watermark_dual_pdf_path
            self.auto_extracted_glossary_path = result_data.auto_extracted_glossary_path
            self.total_seconds = result_data.total_seconds
            self.peak_memory_usage = result_data.peak_memory_usage
        elif isinstance(result_data, dict):
            # 字典格式
            self.original_pdf_path = result_data.get("original_pdf_path")
            self.mono_pdf_path = result_data.get("mono_pdf_path")
            self.dual_pdf_path = result_data.get("dual_pdf_path")
            self.no_watermark_mono_pdf_path = result_data.get("no_watermark_mono_pdf_path")
            self.no_watermark_dual_pdf_path = result_data.get("no_watermark_dual_pdf_path")
            self.auto_extracted_glossary_path = result_data.get("auto_extracted_glossary_path")
            self.total_seconds = result_data.get("total_seconds", 0.0)
            self.peak_memory_usage = result_data.get("peak_memory_usage", 0.0)
        else:
            # 未知格式，初始化为默认值
            self.original_pdf_path = None
            self.mono_pdf_path = None
            self.dual_pdf_path = None
            self.no_watermark_mono_pdf_path = None
            self.no_watermark_dual_pdf_path = None
            self.auto_extracted_glossary_path = None
            self.total_seconds = 0.0
            self.peak_memory_usage = 0.0

    def __str__(self):
        return f"""TranslationResult:
  Original PDF: {self.original_pdf_path}
  Mono PDF: {self.mono_pdf_path}
  Dual PDF: {self.dual_pdf_path}
  Time: {self.total_seconds:.2f}s
  Memory: {self.peak_memory_usage:.2f}"""


class PDFTranslator:
    """PDF翻译器"""

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

    def _create_settings(
        self,
        input_pdf: str,
        output_dir: Optional[str],
        source_lang: str = "en",
        target_lang: str = "zh",
        **kwargs,
    ) -> SettingsModel:
        """
        创建翻译配置

        Args:
            input_pdf: 输入PDF路径
            output_dir: 输出目录
            source_lang: 源语言代码
            target_lang: 目标语言代码
            **kwargs: 其他配置选项

        Returns:
            SettingsModel 实例
        """
        # 基本设置
        basic = BasicSettings(
            input_files={input_pdf},
            debug=self.config.get("debug", False),
        )

        # 翻译设置
        translation = TranslationSettings(
            lang_in=source_lang,
            lang_out=target_lang,
            output=output_dir,
            qps=self.config.get("qps", 4),
            min_text_length=self.config.get("min_text_length", 5),
            custom_system_prompt=self.config.get("custom_system_prompt"),
        )

        # PDF设置
        pdf = PDFSettings(
            no_dual=kwargs.get("no_dual", False),
            no_mono=kwargs.get("no_mono", False),
            watermark_output_mode=kwargs.get(
                "watermark_output_mode", "watermarked"
            ),
            max_pages_per_part=kwargs.get("max_pages_per_part"),
            pages=kwargs.get("pages"),
            enhance_compatibility=kwargs.get("enhance_compatibility", False),
        )

        # 翻译引擎设置
        if self.config.get("translation_engine") == "openai":
            translate_engine_settings = OpenAISettings(
                openai_api_key=self.config.get("openai_api_key"),
                openai_base_url=self.config.get("openai_base_url", "https://api.openai.com/v1"),
                openai_model=self.config.get("openai_model", "gpt-4o-mini"),
            )
        else:
            raise ValueError(
                f"不支持的翻译引擎: {self.config.get('translation_engine')}"
            )

        # 创建完整的设置
        settings = SettingsModel(
            basic=basic,
            translation=translation,
            pdf=pdf,
            translate_engine_settings=translate_engine_settings,
        )

        return settings

    async def translate_pdf_async(
        self,
        input_pdf: str,
        output_dir: Optional[str] = None,
        source_lang: str = "en",
        target_lang: str = "zh",
        progress_callback=None,
        **kwargs,
    ) -> TranslationResult:
        """
        异步翻译PDF文件

        Args:
            input_pdf: 输入PDF路径
            output_dir: 输出目录（默认: 当前目录）
            source_lang: 源语言代码（默认: en）
            target_lang: 目标语言代码（默认: zh）
            progress_callback: 进度回调函数
            **kwargs: 其他配置选项

        Returns:
            TranslationResult 实例
        """
        input_path = Path(input_pdf)
        if not input_path.exists():
            raise FileNotFoundError(f"PDF文件不存在: {input_pdf}")

        # 如果未指定输出目录，使用PDF所在目录
        if output_dir is None:
            output_dir = str(input_path.parent)

        # 创建设置
        settings = self._create_settings(
            input_pdf=str(input_path.absolute()),
            output_dir=output_dir,
            source_lang=source_lang,
            target_lang=target_lang,
            **kwargs,
        )

        # 验证设置
        settings.validate_settings()

        self.logger.info(f"开始翻译: {input_pdf}")
        self.logger.info(f"输出目录: {output_dir}")
        self.logger.info(f"源语言: {source_lang}, 目标语言: {target_lang}")

        result = None

        try:
            # 执行翻译
            async for event in do_translate_async_stream(settings, input_path):
                if event is None:
                    continue

                event_type = event.get("type")

                if event_type == "progress_update":
                    stage = event.get("stage")
                    stage_progress = event.get("stage_progress", 0)
                    overall_progress = event.get("overall_progress", 0)

                    self.logger.info(
                        f"[{stage}] 进度: {stage_progress:.1f}% | 总进度: {overall_progress:.1f}%"
                    )

                    if progress_callback:
                        progress_callback(event)

                elif event_type == "error":
                    error_msg = event.get("error")
                    error_type = event.get("error_type")
                    self.logger.error(f"错误 [{error_type}]: {error_msg}")

                elif event_type == "finish":
                    result = TranslationResult(event["translate_result"])
                    self.logger.info("翻译完成!")
                    self.logger.info(str(result))

            return result

        except Exception as e:
            self.logger.error(f"翻译失败: {e}", exc_info=True)
            raise

    def translate_pdf(
        self,
        input_pdf: str,
        output_dir: Optional[str] = None,
        source_lang: str = "en",
        target_lang: str = "zh",
        progress_callback=None,
        **kwargs,
    ) -> TranslationResult:
        """
        同步翻译PDF文件（包装异步方法）

        Args:
            input_pdf: 输入PDF路径
            output_dir: 输出目录（默认: 当前目录）
            source_lang: 源语言代码（默认: en）
            target_lang: 目标语言代码（默认: zh）
            progress_callback: 进度回调函数
            **kwargs: 其他配置选项

        Returns:
            TranslationResult 实例
        """
        return asyncio.run(
            self.translate_pdf_async(
                input_pdf=input_pdf,
                output_dir=output_dir,
                source_lang=source_lang,
                target_lang=target_lang,
                progress_callback=progress_callback,
                **kwargs,
            )
        )


def create_example_config(output_path: str = "config/config.json"):
    """创建示例配置文件"""
    config = {
        "translation_engine": "openai",
        "openai_api_key": "your-api-key-here",
        "openai_base_url": "https://api.openai.com/v1",
        "openai_model": "gpt-4o-mini",
        "qps": 4,
        "min_text_length": 5,
        "debug": False,
        "custom_system_prompt": None,
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

    print(f"示例配置文件已创建: {output_path}")
    print("请编辑此文件并填入你的API密钥。")


if __name__ == "__main__":
    # 创建示例配置
    create_example_config()
