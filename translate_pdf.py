#!/usr/bin/env python3
"""
PDF Translation CLI
命令行工具，用于翻译PDF文件
"""

import argparse
import sys
from pathlib import Path

from pdf_translator import PDFTranslator, create_example_config


def main():
    parser = argparse.ArgumentParser(
        description="PDF翻译工具 - 基于PDFMathTranslate-next和BabelDOC"
    )

    # 必需参数
    parser.add_argument(
        "--input",
        "-i",
        required=False,
        help="输入PDF文件路径",
    )
    parser.add_argument(
        "--output",
        "-o",
        help="输出目录（默认: PDF文件所在目录）",
    )
    parser.add_argument(
        "--config",
        "-c",
        default="config/config.json",
        help="配置文件路径（默认: config/config.json）",
    )

    # 语言选项
    parser.add_argument(
        "--lang-in",
        "-li",
        default="en",
        help="源语言代码（默认: en）",
    )
    parser.add_argument(
        "--lang-out",
        "-lo",
        default="zh",
        help="目标语言代码（默认: zh）",
    )

    # PDF处理选项
    parser.add_argument(
        "--no-dual",
        action="store_true",
        help="不输出双语PDF",
    )
    parser.add_argument(
        "--no-mono",
        action="store_true",
        help="不输出单语PDF",
    )
    parser.add_argument(
        "--watermark",
        choices=["watermarked", "no_watermark", "both"],
        default="watermarked",
        help="水印模式（默认: watermarked）",
    )
    parser.add_argument(
        "--pages",
        help="指定翻译的页码（例如: 1,2,1-,-3,3-5）",
    )
    parser.add_argument(
        "--max-pages-per-part",
        type=int,
        help="每个分部的最大页数（用于大文档）",
    )
    parser.add_argument(
        "--enhance-compatibility",
        action="store_true",
        help="启用所有兼容性增强选项",
    )

    # 工具命令
    parser.add_argument(
        "--create-config",
        action="store_true",
        help="创建示例配置文件",
    )

    args = parser.parse_args()

    # 创建示例配置文件
    if args.create_config:
        create_example_config(args.config)
        return

    # 检查输入文件
    if not args.input:
        print("错误: 缺少必需参数 --input/-i", file=sys.stderr)
        print("使用 --help 查看帮助信息", file=sys.stderr)
        sys.exit(1)

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"错误: 文件不存在: {args.input}", file=sys.stderr)
        sys.exit(1)

    # 检查配置文件
    config_path = Path(args.config)
    if not config_path.exists():
        print(
            f"错误: 配置文件不存在: {args.config}",
            file=sys.stderr,
        )
        print(f"提示: 使用 --create-config 创建示例配置文件", file=sys.stderr)
        sys.exit(1)

    print("=" * 60)
    print("PDF翻译工具")
    print("=" * 60)
    print(f"输入文件: {args.input}")
    print(f"配置文件: {args.config}")
    print(f"源语言: {args.lang_in}")
    print(f"目标语言: {args.lang_out}")
    if args.output:
        print(f"输出目录: {args.output}")
    else:
        print(f"输出目录: {input_path.parent}")
    print("=" * 60)
    print()

    # 创建翻译器
    translator = PDFTranslator(config_path=args.config)

    # 定义进度回调
    def progress_callback(event):
        if event is None:
            return
        stage = event.get("stage", "")
        overall = event.get("overall_progress", 0)
        print(f"\r[进度] {overall:.1f}% - {stage}", end="", flush=True)

    # 执行翻译
    try:
        result = translator.translate_pdf(
            input_pdf=args.input,
            output_dir=args.output,
            source_lang=args.lang_in,
            target_lang=args.lang_out,
            progress_callback=progress_callback,
            no_dual=args.no_dual,
            no_mono=args.no_mono,
            watermark_output_mode=args.watermark,
            pages=args.pages,
            max_pages_per_part=args.max_pages_per_part,
            enhance_compatibility=args.enhance_compatibility,
        )

        print()  # 换行
        print()
        print("=" * 60)
        print("翻译完成!")
        print("=" * 60)

        if result.dual_pdf_path:
            print(f"双语版PDF: {result.dual_pdf_path}")
        if result.mono_pdf_path:
            print(f"单语版PDF: {result.mono_pdf_path}")
        if result.no_watermark_dual_pdf_path:
            print(f"无水印双语PDF: {result.no_watermark_dual_pdf_path}")
        if result.no_watermark_mono_pdf_path:
            print(f"无水印单语PDF: {result.no_watermark_mono_pdf_path}")
        if result.auto_extracted_glossary_path:
            print(f"术语表: {result.auto_extracted_glossary_path}")

        print(f"耗时: {result.total_seconds:.2f}秒")
        print(f"内存峰值: {result.peak_memory_usage:.2f}")
        print("=" * 60)

    except Exception as e:
        print()
        print()
        print("=" * 60, file=sys.stderr)
        print("翻译失败!", file=sys.stderr)
        print("=" * 60, file=sys.stderr)
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
