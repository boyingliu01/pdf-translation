"""
PDF Translation Tool
基于 PDFMathTranslate-next 和 BabelDOC 的PDF翻译工具
"""

import asyncio
import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any, Union, List

from dataclasses import dataclass

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


# =============================================================================
# Multi-Model Fallback System
# =============================================================================


@dataclass
class FallbackModelConfig:
    """Configuration for a single translation model."""

    name: str
    api_key: str
    base_url: str
    model: str


class FallbackTranslator:
    """Manages fallback between multiple translation models.

    Tracks consecutive failures and switches to next model when threshold
    is reached. Logs all switching events for user visibility.
    """

    def __init__(
        self,
        models: List[FallbackModelConfig],
        consecutive_failures_threshold: int = 3,
    ):
        """Initialize with list of model configs.

        Args:
            models: List of FallbackModelConfig in priority order
            consecutive_failures_threshold: Number of failures before switching
        """
        if not models:
            raise ValueError("At least one model must be provided")

        self.models = models
        self.current_index = 0
        self.consecutive_failures = 0
        self.consecutive_failures_threshold = consecutive_failures_threshold
        self.logger = logging.getLogger(__name__)

    def get_current_model(self) -> FallbackModelConfig:
        """Get the currently active model configuration."""
        return self.models[self.current_index]

    def record_failure(self) -> bool:
        """Record a translation failure.

        Returns:
            True if switched to a new model, False otherwise
        """
        self.consecutive_failures += 1

        if self.consecutive_failures >= self.consecutive_failures_threshold:
            return self._switch_to_next_model()

        return False

    def record_success(self):
        """Record a successful translation, reset failure counter."""
        self.consecutive_failures = 0

    def _switch_to_next_model(self) -> bool:
        """Switch to the next available model.

        Returns:
            True if switched successfully, False if no more models
        """
        if self.current_index >= len(self.models) - 1:
            self.logger.warning(
                f"All {len(self.models)} models have failed. "
                "No more fallback options available."
            )
            return False

        old_model = self.get_current_model()
        self.current_index += 1
        self.consecutive_failures = 0
        new_model = self.get_current_model()

        self.logger.warning(
            f"Model '{old_model.name}/{old_model.model}' failed "
            f"{self.consecutive_failures_threshold} times consecutively. "
            f"Switching to '{new_model.name}/{new_model.model}'"
        )

        return True

    def has_more_models(self) -> bool:
        """Check if there are more models to fall back to."""
        return self.current_index < len(self.models) - 1


# =============================================================================
# BabelDOC Patches
# =============================================================================


def _apply_babeldoc_patch():
    """
    应用 babeldoc 补丁，修复控制字符导致JSON解析失败的问题

    这个补丁修复了 babeldoc 中 _clean_json_output 方法没有清理控制字符的问题。
    控制字符（ASCII 0-31）会导致 JSON 解析失败，触发 fallback 机制，
    从而导致译文中出现 "th"、"ft" 等残留字符。
    """
    try:
        from babeldoc.format.pdf.document_il.midend import il_translator_llm_only

        # 保存原始方法（如果需要回滚）
        original_clean_json_output = (
            il_translator_llm_only.ILTranslatorLLMOnly._clean_json_output
        )

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
            llm_output = "".join(
                char for char in llm_output if ord(char) >= 32 or char in "\n\t\r"
            )

            return llm_output.strip()

        # 应用补丁
        il_translator_llm_only.ILTranslatorLLMOnly._clean_json_output = (
            patched_clean_json_output
        )
        logging.getLogger(__name__).info(
            "Successfully applied babeldoc control character patch"
        )

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


def _is_incomplete_sentence(text: str) -> bool:
    """检查文本是否是不完整的句子（可能被截断的跨页段落）。

    不完整的标志：
    - 以小写字母结尾且最后一个词很短（可能被截断）
    - 以不完整的标点结尾（如逗号、左括号等）
    - 没有任何句子结束符
    """
    if not text or not text.strip():
        return False

    text = text.rstrip()

    # 太短的文本不算完整句子（即使以标点结尾）
    if len(text) < 3:
        return False

    # 检查是否以完整句子结束符结尾
    complete_endings = (".", "!", "?", ":", ";", "—", "-", '"', "'", ")", "]", "»", "›")
    if text.endswith(complete_endings):
        return True

    # 如果文本很短（< 15字符）且不以句子结束符结尾，可能是截断的
    if len(text) < 15:
        return False

    # 检查最后几个词是否可能是单词的一部分
    words = text.split()
    if words:
        last_word = words[-1]
        # 如果最后一个词很短（<=4字符）且是小写，可能是截断
        if len(last_word) <= 4 and last_word.islower():
            return False  # 短词小写不是完整句子

    # 没有句子结束符
    return False


def patch_babeldoc_cross_page():
    """Apply BabelDOC cross-page paragraph handling patch.

    This patch fixes cross-page paragraph translation by:
    1. Detecting incomplete paragraphs at page boundaries
    2. Merging them with the next page's first paragraph
    3. Submitting them for translation as a batch

    The original BabelDOC only handles 'body text' paragraphs.
    This patch extends detection to all translatable paragraphs.
    """
    _logger = logging.getLogger(__name__)

    try:
        from babeldoc.format.pdf.document_il.midend import il_translator_llm_only
        from babeldoc.format.pdf.document_il.midend.il_translator_llm_only import (
            BatchParagraph,
        )
        from babeldoc.format.pdf.document_il.midend.il_translator import (
            DocumentTranslateTracker,
        )

        # Save original method for reference (not used, but kept for potential rollback)
        original_method = (
            il_translator_llm_only.ILTranslatorLLMOnly.process_cross_page_paragraph
        )

        def patched_process_cross_page_paragraph(
            self,
            docs,
            executor,
            pbar=None,
            tracker=None,
            executor2=None,
            translated_ids=None,
        ):
            """Process cross-page paragraphs with enhanced detection.

            Key differences from original:
            1. Uses all translatable paragraphs, not just body text
            2. Checks paragraph completeness before merging
            3. Handles cases where original method misses cross-page paragraphs
            """
            self.translation_config.raise_if_cancelled()

            if tracker is None:
                tracker = DocumentTranslateTracker()

            if translated_ids is None:
                translated_ids = set()

            # Process all adjacent page pairs
            for i in range(len(docs.page) - 1):
                page_curr = docs.page[i]
                page_next = docs.page[i + 1]

                # Get all translatable paragraphs (not just body text)
                curr_paragraphs = self._filter_paragraphs(
                    page_curr, translated_ids, require_body_text=False
                )
                next_paragraphs = self._filter_paragraphs(
                    page_next, translated_ids, require_body_text=False
                )

                if not curr_paragraphs or not next_paragraphs:
                    continue

                last_curr = curr_paragraphs[-1]
                first_next = next_paragraphs[0]

                # Skip if already translated
                if id(last_curr) in translated_ids or id(first_next) in translated_ids:
                    continue

                # Check if the last paragraph is incomplete (possibly truncated)
                is_incomplete = (
                    _is_incomplete_sentence(last_curr.unicode)
                    if last_curr.unicode
                    else False
                )

                if not is_incomplete:
                    continue

                _logger.info(
                    f"Cross-page: merging incomplete paragraph ending with '"
                    f"{last_curr.unicode[-30:] if last_curr.unicode else ''}'"
                )

                # Build font maps
                curr_font_map, curr_xobj_font_map = self._build_font_maps(page_curr)
                next_font_map, next_xobj_font_map = self._build_font_maps(page_next)
                merged_font_map = {**curr_font_map, **next_font_map}
                merged_xobj_font_map = {**curr_xobj_font_map, **next_xobj_font_map}

                # Calculate token count
                total_token_count = self.calc_token_count(
                    last_curr.unicode
                ) + self.calc_token_count(first_next.unicode)

                # Create and submit batch
                cross_page_paragraphs = [last_curr, first_next]
                cross_page_pages = [page_curr, page_next]
                batch_paragraph = BatchParagraph(
                    cross_page_paragraphs, cross_page_pages, tracker.new_cross_page()
                )

                self.mid += 1
                executor.submit(
                    self.translate_paragraph,
                    batch_paragraph,
                    pbar,
                    merged_font_map,
                    merged_xobj_font_map,
                    self.translation_config.shared_context_cross_split_part.first_paragraph,
                    self.translation_config.shared_context_cross_split_part.recent_title_paragraph,
                    executor2,
                    priority=1048576 - total_token_count,
                    paragraph_token_count=total_token_count,
                    mp_id=self.mid,
                )

                # Mark as translated
                translated_ids.add(id(last_curr))
                translated_ids.add(id(first_next))

        # Apply patch
        il_translator_llm_only.ILTranslatorLLMOnly.process_cross_page_paragraph = (
            patched_process_cross_page_paragraph
        )
        _logger.info("BabelDOC cross-page patch applied successfully")

    except Exception as e:
        _logger.warning(f"BabelDOC cross-page patch failed: {e}")


# 在模块加载时尝试应用补丁
_apply_babeldoc_patch()
patch_babeldoc_cross_page()


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
            self.no_watermark_mono_pdf_path = result_data.get(
                "no_watermark_mono_pdf_path"
            )
            self.no_watermark_dual_pdf_path = result_data.get(
                "no_watermark_dual_pdf_path"
            )
            self.auto_extracted_glossary_path = result_data.get(
                "auto_extracted_glossary_path"
            )
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


def parse_fallback_config(config: Dict[str, Any]) -> Optional[FallbackTranslator]:
    """Parse fallback configuration from config dict.

    Args:
        config: Configuration dictionary

    Returns:
        FallbackTranslator if multi-model config, None otherwise
    """
    models_config = config.get("models")

    if not models_config:
        # Single model mode - use backward compatible config
        return None

    if not isinstance(models_config, list) or len(models_config) == 0:
        raise ValueError("'models' must be a non-empty list")

    models = []
    for m in models_config:
        if not all(k in m for k in ["api_key", "base_url", "model"]):
            raise ValueError(
                "Each model must have 'api_key', 'base_url', and 'model' fields"
            )
        models.append(
            FallbackModelConfig(
                name=m.get("name", m["model"]),
                api_key=m["api_key"],
                base_url=m["base_url"],
                model=m["model"],
            )
        )

    fallback_config = config.get("fallback", {})
    threshold = fallback_config.get("consecutive_failures", 3)

    return FallbackTranslator(models, threshold)


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

        # Parse fallback configuration
        self.fallback_translator = parse_fallback_config(self.config)
        if self.fallback_translator:
            self.logger.info(
                f"Multi-model fallback configured with {len(self.fallback_translator.models)} models"
            )

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
            watermark_output_mode=kwargs.get("watermark_output_mode", "watermarked"),
            max_pages_per_part=kwargs.get("max_pages_per_part"),
            pages=kwargs.get("pages"),
            enhance_compatibility=kwargs.get("enhance_compatibility", False),
        )

        # 翻译引擎设置
        if self.config.get("translation_engine") == "openai":
            # 优先使用多模型配置的第一个模型
            if self.fallback_translator:
                first_model = self.fallback_translator.get_current_model()
                translate_engine_settings = OpenAISettings(
                    openai_api_key=first_model.api_key,
                    openai_base_url=first_model.base_url,
                    openai_model=first_model.model,
                )
            else:
                # 单模型配置（向后兼容）
                translate_engine_settings = OpenAISettings(
                    openai_api_key=self.config.get("openai_api_key"),
                    openai_base_url=self.config.get(
                        "openai_base_url", "https://api.openai.com/v1"
                    ),
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

    def _apply_fallback_patch(self):
        """Apply patch to intercept translation failures and trigger fallback."""
        if not self.fallback_translator:
            return  # No fallback configured

        try:
            from pdf2zh_next.translator.translator_impl.openai import OpenAITranslator
            from openai import BadRequestError
            import openai

            original_do_llm_translate = OpenAITranslator.do_llm_translate
            fallback_manager = self.fallback_translator  # Capture for closure
            logger = self.logger  # Capture for closure

            def patched_do_llm_translate(self_translator, text, rate_limit_params=None):
                """Patched do_llm_translate with fallback support.

                On BadRequestError (content filter), immediately switch to next model and retry.
                """
                current_model_index = fallback_manager.current_index
                max_attempts = len(fallback_manager.models)

                for attempt in range(max_attempts):
                    try:
                        result = original_do_llm_translate(
                            self_translator, text, rate_limit_params
                        )
                        fallback_manager.record_success()
                        return result
                    except BadRequestError as e:
                        current_model = fallback_manager.get_current_model()
                        logger.warning(
                            f"Model '{current_model.name}/{current_model.model}' rejected content (BadRequestError): {str(e)[:100]}"
                        )

                        # Try to switch to next model
                        if fallback_manager.has_more_models():
                            fallback_manager._switch_to_next_model()
                            new_model = fallback_manager.get_current_model()
                            logger.info(
                                f"Switched to fallback model '{new_model.name}/{new_model.model}'"
                            )
                            # Update translator for next attempt
                            self._update_openai_translator(self_translator)
                        else:
                            # No more models to try
                            logger.error("All fallback models exhausted")
                            raise
                    except Exception as e:
                        logger.warning(f"Translation failed: {e}")
                        if fallback_manager.has_more_models():
                            fallback_manager._switch_to_next_model()
                            self._update_openai_translator(self_translator)
                        else:
                            raise

                raise RuntimeError("All translation models failed")

            OpenAITranslator.do_llm_translate = patched_do_llm_translate
            self.logger.info("Fallback translation patch applied successfully")

        except ImportError as e:
            self.logger.warning(f"Could not apply fallback patch: {e}")
        except Exception as e:
            self.logger.warning(f"Could not apply fallback patch: {e}")

        # Also apply patch at BabelDOC level for content filter errors
        self._apply_babeldoc_fallback_patch()

    def _apply_babeldoc_fallback_patch(self):
        """Apply patch at BabelDOC level to handle content filter errors."""
        if not self.fallback_translator:
            return

        try:
            from babeldoc.format.pdf.document_il.midend import il_translator
            from openai import BadRequestError

            original_translate_paragraph = (
                il_translator.ILTranslator.translate_paragraph
            )
            fallback_manager = self.fallback_translator
            logger = self.logger
            self_ref = self  # Reference to PDFTranslator instance

            def patched_translate_paragraph(
                self_il,
                paragraph,
                pbar=None,
                font_map=None,
                xobj_font_map=None,
                first_paragraph=None,
                recent_title_paragraph=None,
                executor=None,
                tracker=None,
            ):
                """Patched translate_paragraph with fallback support."""
                max_attempts = len(fallback_manager.models)

                for attempt in range(max_attempts):
                    try:
                        result = original_translate_paragraph(
                            self_il,
                            paragraph,
                            pbar,
                            font_map,
                            xobj_font_map,
                            first_paragraph,
                            recent_title_paragraph,
                            executor,
                            tracker,
                        )
                        fallback_manager.record_success()
                        return result
                    except BadRequestError as e:
                        current_model = fallback_manager.get_current_model()
                        logger.warning(
                            f"[BabelDOC] Model '{current_model.name}/{current_model.model}' "
                            f"rejected content (BadRequestError): {str(e)[:80]}"
                        )

                        # Try to switch to next model
                        if fallback_manager.has_more_models():
                            fallback_manager._switch_to_next_model()
                            new_model = fallback_manager.get_current_model()
                            logger.info(
                                f"[BabelDOC] Switched to fallback model "
                                f"'{new_model.name}/{new_model.model}'"
                            )
                            # Update the translator engine
                            self_ref._update_translator_settings(self_il)
                        else:
                            logger.error("[BabelDOC] All fallback models exhausted")
                            raise
                    except Exception as e:
                        if "contentFilter" in str(e) or "1301" in str(e):
                            # Content filter error (possibly wrapped in another exception)
                            current_model = fallback_manager.get_current_model()
                            logger.warning(
                                f"[BabelDOC] Content filter detected with model "
                                f"'{current_model.name}/{current_model.model}'"
                            )

                            if fallback_manager.has_more_models():
                                fallback_manager._switch_to_next_model()
                                new_model = fallback_manager.get_current_model()
                                logger.info(
                                    f"[BabelDOC] Switched to fallback model "
                                    f"'{new_model.name}/{new_model.model}'"
                                )
                                self_ref._update_translator_settings(self_il)
                            else:
                                logger.error("[BabelDOC] All fallback models exhausted")
                                raise
                        else:
                            # Other errors, re-raise
                            raise

                raise RuntimeError("All translation models failed")

            il_translator.ILTranslator.translate_paragraph = patched_translate_paragraph
            self.logger.info("BabelDOC fallback patch applied successfully")

        except ImportError as e:
            self.logger.warning(f"Could not apply BabelDOC fallback patch: {e}")
        except Exception as e:
            self.logger.warning(f"Could not apply BabelDOC fallback patch: {e}")

    def _update_openai_translator(self, translator_instance):
        """Update OpenAI translator instance with current fallback model settings."""
        if not self.fallback_translator:
            return

        model_config = self.fallback_translator.get_current_model()

        # Update settings
        translator_instance.model = model_config.model
        translator_instance.add_cache_impact_parameters("model", model_config.model)

        # Recreate the client
        import openai

        translator_instance.client = openai.OpenAI(
            base_url=model_config.base_url,
            api_key=model_config.api_key,
        )

    def _update_translator_settings(self, il_translator_instance):
        """Update translator instance with current fallback model settings."""
        if not self.fallback_translator:
            return

        model_config = self.fallback_translator.get_current_model()

        # Update the translate engine settings
        settings = il_translator_instance.translation_config.translate_engine_settings
        settings.openai_api_key = model_config.api_key
        settings.openai_base_url = model_config.base_url
        settings.openai_model = model_config.model

        # Recreate the client if needed
        if hasattr(il_translator_instance.translate_engine, "client"):
            import openai

            il_translator_instance.translate_engine.client = openai.OpenAI(
                base_url=model_config.base_url,
                api_key=model_config.api_key,
            )

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
        # Apply fallback patch if configured
        self._apply_fallback_patch()

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
    output = "".join(char for char in output if ord(char) >= 32 or char in "\n\t\r")

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
