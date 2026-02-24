#!/usr/bin/env python3
"""测试配置创建（不验证文件）"""

import sys
sys.path.append('/workspace/projects/pdf-translation')

from pdf_translator import PDFTranslator
from pdf2zh_next.config.model import SettingsModel, BasicSettings, TranslationSettings, PDFSettings
from pdf2zh_next.config.translate_engine_model import OpenAISettings

print("测试配置创建...")
print("=" * 60)

try:
    # 1. 测试OpenAISettings创建
    print("\n1. 测试OpenAISettings创建...")
    engine_settings = OpenAISettings(
        openai_api_key="sk-test",
        openai_base_url="https://api.openai.com/v1",
        openai_model="gpt-4o-mini",
    )
    print(f"   ✓ 成功创建")
    print(f"   - translate_engine_type: {engine_settings.translate_engine_type}")
    print(f"   - openai_model: {engine_settings.openai_model}")
    print(f"   - openai_base_url: {engine_settings.openai_base_url}")
    print(f"   - openai_api_key: {engine_settings.openai_api_key[:10]}...")

    # 2. 测试SettingsModel创建
    print("\n2. 测试SettingsModel创建...")
    basic = BasicSettings(
        input_files={"test.pdf"},
        debug=False,
    )

    translation = TranslationSettings(
        lang_in="en",
        lang_out="zh",
        output="./output",
        qps=4,
    )

    pdf = PDFSettings()

    settings = SettingsModel(
        basic=basic,
        translation=translation,
        pdf=pdf,
        translate_engine_settings=engine_settings,
    )
    print(f"   ✓ 成功创建")

    # 3. 测试validate_settings（不检查文件存在）
    print("\n3. 测试validate_settings...")
    # 临时移除文件检查
    original_files = settings.basic.input_files
    settings.basic.input_files = set()  # 空集合，避免文件检查

    try:
        settings.validate_settings()
        print(f"   ✓ 配置验证通过")
    except ValueError as e:
        if "File does not exist" in str(e):
            # 这是预期的，因为输入文件为空
            print(f"   ✓ 部分验证通过（跳过文件检查）")
        else:
            raise

    # 恢复
    settings.basic.input_files = original_files

    print("\n" + "=" * 60)
    print("所有配置创建测试通过！")
    print("=" * 60)

except Exception as e:
    print("\n" + "=" * 60)
    print(f"✗ 测试失败: {type(e).__name__}: {e}")
    print("=" * 60)
    import traceback
    traceback.print_exc()
    sys.exit(1)
