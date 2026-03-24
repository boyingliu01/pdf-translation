#!/usr/bin/env python3
"""
简化诊断脚本：追踪跨页段落处理
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging

# 设置日志输出到文件
log_file = r"E:\2-booboo\Palantir\output\diagnostic-log.txt"
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',
    handlers=[
        logging.FileHandler(log_file, mode='w', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

# 在导入 babeldoc 之前应用 patches
from pdf_translator import _apply_babeldoc_patch, patch_babeldoc_cross_page

# 额外的诊断 hook
def add_diagnostics():
    """添加诊断代码来追踪段落处理"""
    from babeldoc.format.pdf.document_il.midend import il_translator_llm_only

    original_process_cross_page = il_translator_llm_only.ILTranslatorLLMOnly.process_cross_page_paragraph
    original_process_page = il_translator_llm_only.ILTranslatorLLMOnly.process_page
    original_filter = il_translator_llm_only.ILTranslatorLLMOnly._filter_paragraphs

    def diagnostic_filter_paragraphs(self, page, translated_ids=None, require_body_text=False):
        result = original_filter(self, page, translated_ids, require_body_text)

        page_num = getattr(page, 'page_number', '?')
        body_count = len([p for p in result if self._is_body_text_paragraph(p)])

        print(f"[FILTER] Page {page_num}: require_body_text={require_body_text}, "
              f"result={len(result)}, body_text_count={body_count}")

        return result

    def diagnostic_process_cross_page(self, docs, executor, pbar=None, tracker=None, executor2=None, translated_ids=None):
        print("\n" + "="*60)
        print("CROSS-PAGE PROCESSING START")
        print("="*60)

        if translated_ids is None:
            translated_ids = set()

        # 调用原始方法
        original_process_cross_page(self, docs, executor, pbar, tracker, executor2, translated_ids)

        print(f"\nAfter cross-page: translated_ids = {len(translated_ids)}")
        print("="*60)
        print("CROSS-PAGE PROCESSING END")
        print("="*60)

    def diagnostic_process_page(self, page, executor, pbar=None, tracker=None, executor2=None, translated_ids=None):
        page_num = getattr(page, 'page_number', '?')

        print(f"\n" + "-"*60)
        print(f"PAGE {page_num} PROCESSING")
        print("-"*60)

        if translated_ids is None:
            translated_ids = set()

        all_paragraphs = [p for p in page.pdf_paragraph if p.debug_id is not None and p.unicode is not None]
        skipped = [p for p in all_paragraphs if id(p) in translated_ids]
        to_process = [p for p in all_paragraphs if id(p) not in translated_ids]

        print(f"Total paragraphs: {len(all_paragraphs)}")
        print(f"Skipped (already in translated_ids): {len(skipped)}")
        print(f"To process: {len(to_process)}")

        # 打印跳过的段落详情
        for p in skipped:
            text_preview = p.unicode[:50] + "..." if len(p.unicode) > 50 else p.unicode
            print(f"  SKIP: id={p.debug_id}, layout={p.layout_label}, text='{text_preview}'")

        original_process_page(self, page, executor, pbar, tracker, executor2, translated_ids)

    il_translator_llm_only.ILTranslatorLLMOnly._filter_paragraphs = diagnostic_filter_paragraphs
    il_translator_llm_only.ILTranslatorLLMOnly.process_cross_page_paragraph = diagnostic_process_cross_page
    il_translator_llm_only.ILTranslatorLLMOnly.process_page = diagnostic_process_page

    print("Diagnostics hooks installed!")

add_diagnostics()

# 现在运行翻译测试
from pdf_translator import PDFTranslator

translator = PDFTranslator(config_path="config/config.json")

# 只翻译问题页
result = translator.translate_pdf(
    input_pdf=r"E:\2-booboo\Palantir\The Philosopher in the Valley Alex Karp, Palantir, and the Rise of the Surveillance State.pdf",
    output_dir=r"E:\2-booboo\Palantir\output\diagnostic-test",
    pages="4-6,9-10,12-13",
    no_mono=True
)

print("\n" + "="*60)
print("DIAGNOSTIC COMPLETE")
print("="*60)
print(f"Dual PDF: {result.dual_pdf_path}")
print(f"Log file: {log_file}")