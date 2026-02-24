#!/usr/bin/env python3
"""
翻译引擎测试脚本
用于测试不同的翻译服务是否配置正确
"""

import sys
import os
sys.path.append('/workspace/projects/pdf-translation')

from pdf_translator import PDFTranslator
import json

def test_engine(config_file, engine_name):
    """测试翻译引擎配置"""
    print(f"\n{'=' * 70}")
    print(f"测试引擎: {engine_name}")
    print(f"配置文件: {config_file}")
    print('=' * 70)

    try:
        # 读取配置
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)

        # 显示配置信息
        print(f"\n配置信息:")
        print(f"  - Base URL: {config.get('openai_base_url', 'N/A')}")
        print(f"  - Model: {config.get('openai_model', 'N/A')}")
        print(f"  - API Key: {config.get('openai_api_key', 'N/A')[:20]}...")

        # 创建翻译器
        print(f"\n初始化翻译器...")
        translator = PDFTranslator(config_dict=config)
        print("  ✓ 翻译器初始化成功")

        # 创建配置
        print(f"\n创建翻译配置...")
        settings = translator._create_settings(
            input_pdf="test.pdf",
            output_dir="./output",
            source_lang="en",
            target_lang="zh",
        )
        print("  ✓ 配置创建成功")

        # 检查翻译引擎设置
        print(f"\n翻译引擎设置:")
        engine = settings.translate_engine_settings
        print(f"  - 引擎类型: {engine.translate_engine_type}")
        print(f"  - 模型: {engine.openai_model}")
        print(f"  - Base URL: {engine.openai_base_url}")

        # 验证配置
        print(f"\n验证配置...")
        settings.basic.input_files = set()  # 跳过文件检查
        settings.validate_settings()
        print("  ✓ 配置验证成功")

        print(f"\n{'=' * 70}")
        print(f"✅ {engine_name} 测试通过！配置正确。")
        print(f"{'=' * 70}")
        return True

    except FileNotFoundError:
        print(f"\n{'=' * 70}")
        print(f"❌ 配置文件不存在: {config_file}")
        print(f"{'=' * 70}")
        return False
    except ValueError as e:
        if "API key is required" in str(e):
            print(f"\n{'=' * 70}")
            print(f"❌ {engine_name} 配置错误: API密钥未配置")
            print(f"请编辑配置文件，填入正确的API密钥")
            print(f"{'=' * 70}")
        else:
            print(f"\n{'=' * 70}")
            print(f"❌ {engine_name} 配置错误: {e}")
            print(f"{'=' * 70}")
        return False
    except Exception as e:
        print(f"\n{'=' * 70}")
        print(f"❌ {engine_name} 测试失败: {type(e).__name__}: {e}")
        print(f"{'=' * 70}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("=" * 70)
    print("PDF翻译工具 - 翻译引擎测试")
    print("=" * 70)

    # 定义测试引擎
    engines = [
        ("config.openai.json", "OpenAI"),
        ("config.zhipu.json", "智谱AI GLM-4-Flash"),
        ("config.volcengine.json", "火山引擎豆包"),
        ("config.siliconflow.json", "硅基流动 DeepSeek"),
    ]

    results = {}

    # 测试每个引擎
    for config_file, engine_name in engines:
        config_path = os.path.join("/workspace/projects/pdf-translation", config_file)
        results[engine_name] = test_engine(config_path, engine_name)

    # 打印总结
    print(f"\n{'=' * 70}")
    print("测试总结")
    print('=' * 70)

    for engine_name, success in results.items():
        status = "✅ 通过" if success else "❌ 失败"
        print(f"{engine_name:30s} {status}")

    print('=' * 70)

    # 统计
    passed = sum(results.values())
    total = len(results)
    print(f"总计: {passed}/{total} 个引擎测试通过")

    if passed == 0:
        print("\n💡 提示: 请先配置至少一个翻译引擎")
        print("   1. 选择一个配置文件: config.zhipu.json（推荐，免费）")
        print("   2. 编辑配置文件，填入API密钥")
        print("   3. 再次运行此测试脚本")
    elif passed < total:
        print(f"\n✅ 有 {passed} 个引擎配置正确，可以使用！")
    else:
        print(f"\n🎉 所有引擎配置都正确！")

if __name__ == "__main__":
    main()
