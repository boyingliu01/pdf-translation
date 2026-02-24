#!/usr/bin/env python3
"""测试翻译功能 - 尝试重现错误"""

import sys
import os
sys.path.append('/workspace/projects/pdf-translation')

from pdf_translator import PDFTranslator, create_example_config
import json

# 创建测试配置
print("创建测试配置...")
config = {
    "translation_engine": "openai",
    "openai_api_key": "test-key-placeholder",  # 测试用的假密钥
    "openai_base_url": "https://api.openai.com/v1",
    "openai_model": "gpt-4o-mini",
    "qps": 4,
    "min_text_length": 5,
    "debug": False,
    "custom_system_prompt": None
}

print(f"配置: {json.dumps(config, indent=2)}")
print()

# 创建翻译器
print("初始化翻译器...")
translator = PDFTranslator(config_dict=config)
print("✓ 翻译器初始化成功")
print()

# 创建一个最小的测试PDF（实际上不需要真实文件，只需要检查配置）
print("测试创建配置...")
try:
    settings = translator._create_settings(
        input_pdf="test.pdf",
        output_dir="./output",
        source_lang="en",
        target_lang="zh",
    )
    print(f"✓ 配置创建成功")
    print(f"  基本设置: {settings.basic}")
    print(f"  翻译设置: {settings.translation}")
    print(f"  PDF设置: {settings.pdf}")
    print(f"  翻译引擎: {settings.translate_engine_settings}")
except Exception as e:
    print(f"✗ 错误: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

print()

# 尝试验证配置
print("测试验证配置...")
try:
    settings.validate_settings()
    print("✓ 配置验证成功")
except Exception as e:
    print(f"✗ 错误: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
