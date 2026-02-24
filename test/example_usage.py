"""
PDF Translation Tool 使用示例
"""

from pdf_translator import PDFTranslator
from pathlib import Path


def example_basic_translation():
    """基本翻译示例"""
    print("示例1: 基本翻译")
    print("-" * 60)

    # 初始化翻译器
    translator = PDFTranslator(config_path="config.json")

    # 翻译PDF文件
    result = translator.translate_pdf(
        input_pdf="document.pdf",
        output_dir="./output",
        source_lang="en",
        target_lang="zh",
    )

    print(f"双语版PDF: {result.dual_pdf_path}")
    print(f"单语版PDF: {result.mono_pdf_path}")


def example_with_progress_callback():
    """带进度回调的翻译示例"""
    print("\n示例2: 带进度回调")
    print("-" * 60)

    translator = PDFTranslator(config_path="config.json")

    def progress_callback(event):
        stage = event.get("stage", "")
        overall = event.get("overall_progress", 0)
        print(f"[{overall:5.1f}%] {stage}")

    result = translator.translate_pdf(
        input_pdf="document.pdf",
        output_dir="./output",
        progress_callback=progress_callback,
    )


def example_custom_config():
    """使用自定义配置"""
    print("\n示例3: 自定义配置")
    print("-" * 60)

    # 使用配置字典
    config = {
        "translation_engine": "openai",
        "openai_api_key": "your-api-key",
        "openai_base_url": "https://api.openai.com/v1",
        "openai_model": "gpt-4o-mini",
        "qps": 8,  # 提高并发
    }

    translator = PDFTranslator(config_dict=config)

    result = translator.translate_pdf(
        input_pdf="document.pdf",
        output_dir="./output",
        source_lang="en",
        target_lang="zh",
        # 自定义PDF处理选项
        no_dual=False,
        no_mono=False,
        watermark_output_mode="no_watermark",
        enhance_compatibility=True,
    )


def example_large_document():
    """处理大文档"""
    print("\n示例4: 处理大文档")
    print("-" * 60)

    translator = PDFTranslator(config_path="config.json")

    # 对于大文档，使用 max_pages_per_part 进行分批处理
    result = translator.translate_pdf(
        input_pdf="large_document.pdf",
        output_dir="./output",
        source_lang="en",
        target_lang="zh",
        max_pages_per_part=50,  # 每50页处理一次
    )


def example_specific_pages():
    """翻译特定页面"""
    print("\n示例5: 翻译特定页面")
    print("-" * 60)

    translator = PDFTranslator(config_path="config.json")

    # 只翻译第1-5页
    result = translator.translate_pdf(
        input_pdf="document.pdf",
        output_dir="./output",
        source_lang="en",
        target_lang="zh",
        pages="1-5",
    )


def example_without_watermark():
    """生成无水印版本"""
    print("\n示例6: 生成无水印版本")
    print("-" * 60)

    translator = PDFTranslator(config_path="config.json")

    result = translator.translate_pdf(
        input_pdf="document.pdf",
        output_dir="./output",
        source_lang="en",
        target_lang="zh",
        watermark_output_mode="both",  # 同时生成有水印和无水印版本
    )


if __name__ == "__main__":
    # 注意: 运行示例前请先配置 config.json 文件

    # 运行基本示例
    # example_basic_translation()

    # 运行其他示例...
    print("请取消注释要运行的示例代码")
    print("运行前请确保:")
    print("1. 已安装依赖: pip install -r requirements.txt")
    print("2. 已配置 config.json 文件，填入有效的API密钥")
    print("3. 准备好要翻译的PDF文件")
