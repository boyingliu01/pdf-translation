#!/usr/bin/env python3
"""
诊断脚本：追踪第13页段落处理
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging

# 设置详细日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)

# 应用 patches
from pdf_translator import _apply_babeldoc_patch, patch_babeldoc_cross_page

# 添加诊断 hook
def add_page13_diagnostics():
    """添加诊断代码来追踪第13页段落处理"""
    from babeldoc.format.pdf.document_il.midend import il_translator_llm_only

    original_process_page = il_translator_llm_only.ILTranslatorLLMOnly.process_page
    original_translate_paragraph = il_translator_llm_only.ILTranslatorLLMOnly.translate_paragraph

    def diagnostic_process_page(self, page, executor, pbar=None, tracker=None, executor2=None, translated_ids=None):
        page_num = getattr(page, 'page_number', '?')

        if page_num == 13:  # 只追踪第13页
            print(f"\n{'='*60}")
            print(f"PAGE 13 PROCESSING")
            print(f"{'='*60}")

            if translated_ids is None:
                translated_ids = set()

            all_paragraphs = [p for p in page.pdf_paragraph if p.debug_id is not None and p.unicode is not None]

            print(f"Total paragraphs on page 13: {len(all_paragraphs)}")

            for idx, p in enumerate(all_paragraphs):
                text_preview = p.unicode[:80] + "..." if len(p.unicode) > 80 else p.unicode
                is_translated = id(p) in translated_ids
                is_body = self._is_body_text_paragraph(p)
                print(f"\n  Para {idx}: id={p.debug_id}, layout={p.layout_label}")
                print(f"    body_text={is_body}, translated={is_translated}")
                print(f"    text: '{text_preview}'")

        return original_process_page(self, page, executor, pbar, tracker, executor2, translated_ids)

    def diagnostic_translate_paragraph(self, batch_paragraph, *args, **kwargs):
        """追踪实际翻译的段落"""
        paragraphs = batch_paragraph.paragraphs
        for p in paragraphs:
            page_num = getattr(p, 'page_number', '?')
            if page_num == 13 or (hasattr(batch_paragraph, 'pages') and any(getattr(pg, 'page_number', 0) == 13 for pg in batch_paragraph.pages)):
                text_preview = p.unicode[:60] + "..." if p.unicode and len(p.unicode) > 60 else p.unicode
                print(f"\n  [TRANSLATE] Page {page_num}: id={p.debug_id}, text='{text_preview}'")

        return original_translate_paragraph(self, batch_paragraph, *args, **kwargs)

    il_translator_llm_only.ILTranslatorLLMOnly.process_page = diagnostic_process_page
    il_translator_llm_only.ILTranslatorLLMOnly.translate_paragraph = diagnostic_translate_paragraph

    print("Page 13 diagnostic hooks installed!")

add_page13_diagnostics()

# 运行翻译
from pdf_translator import PDFTranslator

translator = PDFTranslator(config_path="config/config.json")

# 只翻译第12-14页来诊断
result = translator.translate_pdf(
    input_pdf=r"E:\2-booboo\Palantir\The Philosopher in the Valley Alex Karp, Palantir, and the Rise of the Surveillance State.pdf",
    output_dir=r"E:\2-booboo\Palantir\output\page13-diagnostic",
    pages="12-14",
    no_mono=True
)

print("\n" + "="*60)
print("DIAGNOSTIC COMPLETE")
print("="*60)
print(f"Dual PDF: {result.dual_pdf_path}")