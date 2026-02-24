#!/usr/bin/env python3
"""测试修复后的代码"""

import sys
sys.path.append('/workspace/projects/pdf-translation')

from pdf_translator import PDFTranslator
import json

# 创建测试配置
config = {
    "translation_engine": "openai",
    "openai_api_key": "sk-test123456",
    "openai_base_url": "https://api.openai.com/v1",
    "openai_model": "gpt-4o-mini",
    "qps": 4,
    "min_text_length": 5,
    "debug": False,
    "custom_system_prompt": None
}

print("测试修复后的代码...")
print("=" * 60)

try:
    # 1. 初始化翻译器
    print("\n1. 初始化翻译器...")
    translator = PDFTranslator(config_dict=config)
    print("   ✓ 成功")

    # 2. 创建配置
    print("\n2. 创建翻译配置...")
    settings = translator._create_settings(
        input_pdf="test.pdf",
        output_dir="./output",
        source_lang="en",
        target_lang="zh",
    )
    print("   ✓ 成功")

    # 3. 检查翻译引擎设置
    print("\n3. 检查翻译引擎设置...")
    engine = settings.translate_engine_settings
    print(f"   - 翻译引擎类型: {engine.translate_engine_type}")
    print(f"   - 模型: {engine.openai_model}")
    print(f"   - Base URL: {engine.openai_base_url}")
    print(f"   - API Key: {engine.openai_api_key[:10]}...")
    print("   ✓ 成功")

    # 4. 验证配置
    print("\n4. 验证配置...")
    settings.validate_settings()
    print("   ✓ 成功")

    print("\n" + "=" * 60)
    print("所有测试通过！修复成功！")
    print("=" * 60)

except Exception as e:
    print("\n" + "=" * 60)
    print(f"✗ 测试失败: {type(e).__name__}: {e}")
    print("=" * 60)
    import traceback
    traceback.print_exc()
    sys.exit(1)
