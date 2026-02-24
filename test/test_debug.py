#!/usr/bin/env python3
"""调试脚本 - 测试可能出现的问题"""

import sys
sys.path.append('/workspace/projects/pdf-translation')

from pdf_translator import PDFTranslator
from pdf2zh_next.config.model import SettingsModel, BasicSettings

# 测试1: 创建SettingsModel，不设置input_files
print("测试1: 创建SettingsModel，不设置input_files")
try:
    basic = BasicSettings()
    print(f"  input_files = {basic.input_files}")
    print(f"  input_files type = {type(basic.input_files)}")
    if basic.input_files:
        print(f"  input_files length = {len(basic.input_files)}")
    print("  ✓ 测试通过")
except Exception as e:
    print(f"  ✗ 错误: {e}")

print()

# 测试2: 创建SettingsModel，input_files=None
print("测试2: 尝试设置input_files=None")
try:
    basic = BasicSettings(input_files=None)
    print(f"  input_files = {basic.input_files}")
    print(f"  input_files type = {type(basic.input_files)}")
    print("  ✓ 测试通过")
except Exception as e:
    print(f"  ✗ 错误: {type(e).__name__}: {e}")

print()

# 测试3: 使用None调用validate_settings
print("测试3: 模拟可能导致错误的场景")
try:
    settings = SettingsModel()
    settings.basic = BasicSettings()
    # 尝试设置input_files为None（虽然不应该这样做）
    print(f"  input_files = {settings.basic.input_files}")
    settings.validate_settings()
    print("  ✓ 测试通过")
except Exception as e:
    print(f"  ✗ 错误: {type(e).__name__}: {e}")

print()

# 测试4: 正常使用
print("测试4: 正常使用（应该成功）")
try:
    basic = BasicSettings(input_files={"test.pdf"})
    print(f"  input_files = {basic.input_files}")
    print("  ✓ 测试通过")
except Exception as e:
    print(f"  ✗ 错误: {e}")
