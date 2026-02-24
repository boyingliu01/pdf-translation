#!/usr/bin/env python3
"""
最终验证测试 - 确保所有功能正常工作
"""

import sys
import os
sys.path.append('/workspace/projects/pdf-translation')

print("=" * 70)
print("PDF翻译工具 - 最终验证测试")
print("=" * 70)

# 测试计数
total_tests = 0
passed_tests = 0
failed_tests = 0

def test(name, func):
    """运行测试函数"""
    global total_tests, passed_tests, failed_tests
    total_tests += 1
    print(f"\n测试 {total_tests}: {name}")
    print("-" * 70)
    try:
        func()
        passed_tests += 1
        print("✓ 通过")
        return True
    except Exception as e:
        failed_tests += 1
        print(f"✗ 失败: {type(e).__name__}: {e}")
        return False

# 测试1: 导入模块
def test_import():
    from pdf_translator import PDFTranslator, create_example_config
    from pdf2zh_next.config.model import SettingsModel
    from pdf2zh_next.config.translate_engine_model import OpenAISettings
    print("  所有模块导入成功")

test("模块导入", test_import)

# 测试2: 创建翻译器
def test_translator_init():
    from pdf_translator import PDFTranslator
    config = {
        "translation_engine": "openai",
        "openai_api_key": "test-key",
        "openai_base_url": "https://api.openai.com/v1",
        "openai_model": "gpt-4o-mini",
    }
    translator = PDFTranslator(config_dict=config)
    print(f"  翻译器创建成功")

test("创建翻译器", test_translator_init)

# 测试3: 创建OpenAISettings
def test_openai_settings():
    from pdf2zh_next.config.translate_engine_model import OpenAISettings
    settings = OpenAISettings(
        openai_api_key="sk-test",
        openai_base_url="https://api.openai.com/v1",
        openai_model="gpt-4o-mini",
    )
    assert settings.openai_api_key == "sk-test"
    assert settings.openai_base_url == "https://api.openai.com/v1"
    assert settings.openai_model == "gpt-4o-mini"
    print(f"  OpenAISettings创建成功")
    print(f"    - API Key: {settings.openai_api_key}")
    print(f"    - Base URL: {settings.openai_base_url}")
    print(f"    - Model: {settings.openai_model}")

test("创建OpenAISettings", test_openai_settings)

# 测试4: 创建配置
def test_create_settings():
    from pdf_translator import PDFTranslator
    translator = PDFTranslator(
        config_dict={
            "translation_engine": "openai",
            "openai_api_key": "test-key",
            "openai_base_url": "https://api.openai.com/v1",
            "openai_model": "gpt-4o-mini",
        }
    )
    settings = translator._create_settings(
        input_pdf="test.pdf",
        output_dir="./output",
        source_lang="en",
        target_lang="zh",
    )
    assert settings.translate_engine_settings is not None
    assert settings.translate_engine_settings.openai_model == "gpt-4o-mini"
    print(f"  配置创建成功")
    print(f"    - 翻译引擎: {settings.translate_engine_settings.translate_engine_type}")
    print(f"    - 模型: {settings.translate_engine_settings.openai_model}")

test("创建翻译配置", test_create_settings)

# 测试5: 配置验证
def test_validate_settings():
    from pdf_translator import PDFTranslator
    translator = PDFTranslator(
        config_dict={
            "translation_engine": "openai",
            "openai_api_key": "sk-test-123",
            "openai_base_url": "https://api.openai.com/v1",
            "openai_model": "gpt-4o-mini",
        }
    )
    settings = translator._create_settings(
        input_pdf="test.pdf",
        output_dir="./output",
    )
    # 临时清空input_files以避免文件存在检查
    original_files = settings.basic.input_files
    settings.basic.input_files = set()
    settings.validate_settings()
    settings.basic.input_files = original_files
    print(f"  配置验证成功")

test("验证配置", test_validate_settings)

# 测试6: 检查命令行工具
def test_cli():
    import subprocess
    result = subprocess.run(
        ["python", "translate_pdf.py", "--help"],
        cwd="/workspace/projects/pdf-translation",
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "PDF翻译工具" in result.stdout
    print(f"  命令行工具可用")

test("命令行工具", test_cli)

# 测试7: 检查文件完整性
def test_file_integrity():
    import os
    required_files = [
        "pdf_translator.py",
        "translate_pdf.py",
        "example_usage.py",
        "README.md",
        "QUICKSTART.md",
        "INTEGRATION.md",
        "requirements.txt",
    ]
    base_dir = "/workspace/projects/pdf-translation"
    for file in required_files:
        path = os.path.join(base_dir, file)
        assert os.path.exists(path), f"文件不存在: {file}"
    print(f"  所有必需文件存在")
    print(f"    - 检查了 {len(required_files)} 个文件")

test("文件完整性", test_file_integrity)

# 打印结果
print("\n" + "=" * 70)
print("测试结果")
print("=" * 70)
print(f"总计: {total_tests} 个测试")
print(f"通过: {passed_tests} 个 ✓")
print(f"失败: {failed_tests} 个 ✗")

if failed_tests == 0:
    print("\n🎉 所有测试通过！PDF翻译工具已准备就绪！")
    print("\n下一步:")
    print("1. 编辑 config.json，填入你的API密钥")
    print("2. 使用 python translate_pdf.py 翻译PDF文档")
    sys.exit(0)
else:
    print("\n❌ 有测试失败，请检查错误信息")
    sys.exit(1)
