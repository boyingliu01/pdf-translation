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


def _apply_babeldoc_patch():
    """
    应用 babeldoc 补丁，修复控制字符导致JSON解析失败的问题

    这个补丁修复了 babeldoc 中 _clean_json_output 方法没有清理控制字符的问题。
    控制字符（ASCII 0-31）会导致 JSON 解析失败，触发 fallback 机制，
    从而导致译文中出现 "th"、"ft" 等残留字符。

    参考: https://github.com/your-repo/pdf-translation/issues/X
    """
    try:
        from babeldoc.format.pdf.document_il.midend import il_translator_llm_only

        # 保存原始方法（如果需要回滚）
        original_clean_json_output = il_translator_llm_only.ILTranslatorLLMOnly._clean_json_output

        def patched_clean_json_output(self, llm_output: str) -> str:
            """
            清理JSON输出，移除包装标签和控制字符

            这个补丁版本添加了控制字符清理功能。
            """
            # Clean up JSON output by removing common wrapper tags
            llm_output = llm_output.strip()
            if llm_output.startswith("<json>"):
                llm_output = llm_output[6:]
            if llm_output.endswith("</json>"):
                llm_output = llm_output[:-7]
            if llm_output.startswith("```json"):
                llm_output = llm_output[7:]
            if llm_output.startswith("```"):
                llm_output = llm_output[3:]
            if llm_output.endswith("```"):
                llm_output = llm_output[:-3]

            # 移除控制字符（ASCII 0-31，除了换行符、制表符、回车）
            # 这些控制字符会导致JSON解析失败，触发fallback机制
            llm_output = ''.join(
                char for char in llm_output
                if ord(char) >= 32 or char in '\n\t\r'
            )

            return llm_output.strip()

        # 应用补丁
        il_translator_llm_only.ILTranslatorLLMOnly._clean_json_output = patched_clean_json_output
        logging.getLogger(__name__).info("Successfully applied babeldoc control character patch")

    except ImportError:
        logging.getLogger(__name__).warning(
            "Could not apply babeldoc patch: module not found. "
            "This may cause 'th'/'ft' residual characters in translations."
        )
    except Exception as e:
        logging.getLogger(__name__).warning(
            f"Could not apply babeldoc patch: {e}. "
            "This may cause 'th'/'ft' residual characters in translations."
        )


# 在模块加载时自动应用补丁
_apply_babeldoc_patch()


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


def clean_json_output(self_or_output, llm_output: str = None) -> str:
    """
    清理JSON输出，移除包装标签和控制字符

    可以作为独立函数或实例方法调用：
    - 作为独立函数: clean_json_output(output_string)
    - 作为实例方法: self._clean_json_output(output_string)

    Args:
        self_or_output: 如果作为实例方法调用，这是self；否则是输出字符串
        llm_output: 如果第一个参数是self，则这是输出字符串

    Returns:
        清理后的JSON字符串

    Note:
        控制字符（ASCII 0-31，除了换行符、制表符、回车）会导致JSON解析失败，
        触发fallback机制，从而导致译文中出现"th"、"ft"等残留字符。
    """
    # 处理两种调用方式
    if llm_output is None:
        # 作为独立函数调用: clean_json_output(output_string)
        output = self_or_output
    else:
        # 作为实例方法调用: self._clean_json_output(output_string)
        output = llm_output

    # Clean up JSON output by removing common wrapper tags
    output = output.strip()
    if output.startswith("<json>"):
        output = output[6:]
    if output.endswith("</json>"):
        output = output[:-7]
    if output.startswith("```json"):
        output = output[7:]
    if output.startswith("```"):
        output = output[3:]
    if output.endswith("```"):
        output = output[:-3]

    # 移除控制字符（ASCII 0-31，除了换行符、制表符、回车）
    # 这些控制字符会导致JSON解析失败，触发fallback机制
    output = ''.join(
        char for char in output
        if ord(char) >= 32 or char in '\n\t\r'
    )

    return output.strip()


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
