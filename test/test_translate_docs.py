#!/usr/bin/env python3
"""
PDF翻译测试脚本
演示如何翻译examples目录下的PDF文档
"""

import os
import sys
import subprocess

def main():
    print("=" * 70)
    print("PDF翻译工具 - 测试文档翻译")
    print("=" * 70)

    base_dir = "/workspace/projects/pdf-translation"
    examples_dir = os.path.join(base_dir, "examples")
    output_dir = os.path.join(examples_dir, "output")

    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)

    # 检查PDF文件
    pdf_files = [
        "01 - Body.pdf",
        "00 Color Front Matter SA (V.4.5.1)-A4.pdf"
    ]

    print("\n📁 找到的测试文档:")
    for pdf_file in pdf_files:
        pdf_path = os.path.join(examples_dir, pdf_file)
        if os.path.exists(pdf_path):
            size = os.path.getsize(pdf_path) / 1024  # KB
            print(f"  ✓ {pdf_file} ({size:.1f} KB)")
        else:
            print(f"  ✗ {pdf_file} (不存在)")

    # 检查配置
    config_path = os.path.join(base_dir, "config.json")
    print(f"\n🔧 配置文件: {config_path}")

    if os.path.exists(config_path):
        print("  ✓ 配置文件存在")

        # 读取配置
        import json
        with open(config_path, 'r') as f:
            config = json.load(f)

        api_key = config.get("openai_api_key", "")
        model = config.get("openai_model", "")
        base_url = config.get("openai_base_url", "")

        if api_key and not api_key.startswith("your-"):
            print(f"  ✓ API密钥已配置: {api_key[:20]}...")
            print(f"  ✓ 模型: {model}")
            print(f"  ✓ Base URL: {base_url}")
        else:
            print(f"  ⚠️  API密钥未配置（使用占位符）")
            print(f"\n💡 请先配置API密钥：")
            print(f"   方案1: 使用智谱AI（免费）")
            print(f"     1. 访问: https://open.bigmodel.cn")
            print(f"     2. 注册并获取API密钥")
            print(f"     3. 编辑 config.json，填入密钥")
            print(f"\n   方案2: 使用火山引擎（你已订阅）")
            print(f"     1. 访问: https://console.volcengine.com/ark")
            print(f"     2. 获取API密钥和模型ID")
            print(f"     3. 编辑 config.json，填入密钥")
            print(f"\n   方案3: 提供你的API密钥，我可以帮你配置")
            return
    else:
        print("  ✗ 配置文件不存在")
        print("\n💡 请先创建配置文件:")
        print(f"   cp config.zhipu.json config.json  # 智谱AI")
        print(f"   或")
        print(f"   cp config.volcengine.json config.json  # 火山引擎")
        return

    print(f"\n📤 输出目录: {output_dir}")

    # 选择翻译哪个文档
    print(f"\n🎯 选择要翻译的文档:")
    print(f"  1. 01 - Body.pdf (650 KB - 推荐，快速测试)")
    print(f"  2. 00 Color Front Matter SA (V.4.5.1)-A4.pdf (8.2 MB - 完整测试)")
    print(f"  3. 全部翻译")

    choice = input("\n请输入选择 (1/2/3): ").strip()

    # 准备翻译命令
    translate_cmd = [
        "python", "translate_pdf.py",
        "--config", config_path,
        "--output", output_dir,
        "--lang-in", "en",
        "--lang-out", "zh"
    ]

    if choice == "1":
        pdf_file = pdf_files[0]
        print(f"\n📖 准备翻译: {pdf_file}")
        translate_cmd.extend(["--input", os.path.join(examples_dir, pdf_file)])
    elif choice == "2":
        pdf_file = pdf_files[1]
        print(f"\n📖 准备翻译: {pdf_file}")
        translate_cmd.extend([
            "--input", os.path.join(examples_dir, pdf_file),
            "--max-pages-per-part", "50"  # 大文档分批处理
        ])
    elif choice == "3":
        print(f"\n📖 准备翻译所有文档...")
    else:
        print("\n❌ 无效选择")
        return

    print(f"\n🚀 翻译命令:")
    print(f"   {' '.join(translate_cmd)}")

    confirm = input("\n是否开始翻译? (y/n): ").strip().lower()
    if confirm != 'y':
        print("已取消")
        return

    # 执行翻译
    print(f"\n{'=' * 70}")
    print("开始翻译...")
    print(f"{'=' * 70}\n")

    try:
        if choice == "3":
            # 翻译所有文档
            for pdf_file in pdf_files:
                print(f"\n翻译: {pdf_file}")
                cmd = translate_cmd.copy()
                cmd.extend(["--input", os.path.join(examples_dir, pdf_file)])
                if "Body" not in pdf_file:
                    cmd.extend(["--max-pages-per-part", "50"])

                subprocess.run(cmd, cwd=base_dir, check=True)
                print(f"✓ {pdf_file} 翻译完成")
        else:
            subprocess.run(translate_cmd, cwd=base_dir, check=True)

        print(f"\n{'=' * 70}")
        print("翻译完成！")
        print(f"{'=' * 70}")
        print(f"\n📂 输出文件位置: {output_dir}")
        print(f"\n生成的文件:")
        for file in os.listdir(output_dir):
            if file.endswith('.pdf'):
                size = os.path.getsize(os.path.join(output_dir, file)) / 1024
                print(f"  ✓ {file} ({size:.1f} KB)")

        print(f"\n💡 提示:")
        print(f"  - *.dual.pdf 是双语对照版本（推荐查看）")
        print(f"  - *.mono.pdf 是单语版本")
        print(f"  - 可以将PDF文件下载到本地查看")

    except subprocess.CalledProcessError as e:
        print(f"\n❌ 翻译失败: {e}")
        print(f"\n💡 请检查:")
        print(f"  1. API密钥是否正确")
        print(f"  2. 网络连接是否正常")
        print(f"  3. API配额是否充足")
        sys.exit(1)

if __name__ == "__main__":
    main()
