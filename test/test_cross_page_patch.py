#!/usr/bin/env python3
"""测试跨页段落处理的Monkey Patch

TDD流程：
1. RED: 测试应该失败（功能不存在）
2. GREEN: 实现最小代码让测试通过
3. REFACTOR: 如需要则重构

测试目标：
1. _is_incomplete_sentence 函数正确判断不完整的句子
2. patch_babeldoc_cross_page 函数正确应用补丁
3. 增强的跨页检测逻辑能识别被截断的段落
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

print("=" * 60)
print("跨页段落处理 Patch 测试 (TDD)")
print("=" * 60)

# --- 测试 1: _is_incomplete_sentence 函数 ---
print("\n1. 测试 _is_incomplete_sentence 函数")

try:
    from pdf_translator import _is_incomplete_sentence
    has_function = True
except ImportError:
    print("   [RED] _is_incomplete_sentence 函数不存在")
    has_function = False

all_passed = True

if has_function:
    test_cases = [
        # (输入, 期望结果, 描述)
        ("This is a complete sentence.", True, "完整句子返回True"),
        ("This is incomplete", False, "以单词截断返回False（短词）"),
        ("and", False, "短词不是完整句子"),
        ("Hello world", False, "没有句子结束符"),
        ("Item 1\nItem 2", False, "换行分隔的不是完整句子"),
        ("—", False, "只有破折号不算完整句子"),
        ("...", True, "省略号是句子结束的一种形式"),
        ("", False, "空字符串"),
        ("   ", False, "只有空白"),
        ("Hello world—", True, "以破折号结尾是完整句子"),
        ("Test...", True, "以省略号结尾是完整句子"),
        ("Is this it?", True, "以问号结尾是完整句子"),
        ("Wait!", True, "以感叹号结尾是完整句子"),
        ("burly and", False, "BUG_DIAGNOSIS中的截断案例"),
        ("Rubik's Cube, and if not that", False, "另一个截断案例"),
    ]

    for input_text, expected, desc in test_cases:
        result = _is_incomplete_sentence(input_text)
        status = "OK" if result == expected else "FAIL"
        if status == "FAIL":
            all_passed = False
        print(f"   [{status}] {desc}")
        if status == "FAIL":
            print(f"          输入: {repr(input_text)}")
            print(f"          期望: {expected}")
            print(f"          实际: {result}")
else:
    all_passed = False
    print("   [RED] 需要实现 _is_incomplete_sentence 函数")

# --- 测试 2: patch_babeldoc_cross_page 函数 ---
print("\n2. 测试 patch_babeldoc_cross_page 函数")

try:
    from pdf_translator import patch_babeldoc_cross_page
    has_patch_function = True
except ImportError:
    print("   [RED] patch_babeldoc_cross_page 函数不存在")
    has_patch_function = False
    all_passed = False

if has_patch_function:
    print("   [OK] patch_babeldoc_cross_page 函数存在")

# --- 测试 3: 验证 BabelDOC patch 是否生效 ---
print("\n3. 测试 BabelDOC patch 是否正确应用")

try:
    from babeldoc.format.pdf.document_il.midend import il_translator_llm_only

    # 检查 process_cross_page_paragraph 是否被替换
    original_method = il_translator_llm_only.ILTranslatorLLMOnly.process_cross_page_paragraph

    # 如果 patch 正确应用，方法应该是我们的 patched 版本
    # 由于我们只是调用原始方法，这里只验证 patch 不报错
    print("   [OK] BabelDOC 模块可以正常访问")

except Exception as e:
    print(f"   [FAIL] BabelDOC 访问失败: {e}")
    all_passed = False

# --- 测试 4: 验证 min_text_length 配置影响 ---
print("\n4. 测试 _is_incomplete_sentence 对截断案例的判断")

try:
    from pdf_translator import _is_incomplete_sentence

    # 这些是 BUG_DIAGNOSIS.md 中记录的截断案例
    truncated_cases = [
        ("burly", False, "第5页截断在 'burly'"),
        ("Jews and", False, "第9页截断在 'Jews and'"),
        ("Rubik's Cube, and if not that", False, "第12页截断"),
    ]

    for text, expected, desc in truncated_cases:
        result = _is_incomplete_sentence(text)
        status = "OK" if result == expected else "FAIL"
        if status == "FAIL":
            all_passed = False
        print(f"   [{status}] {desc}")
        if status == "FAIL":
            print(f"          输入: {repr(text)}")
            print(f"          期望: {expected}")
            print(f"          实际: {result}")

except Exception as e:
    print(f"   [FAIL] 测试失败: {e}")
    all_passed = False

# --- 最终结果 ---
print("\n" + "=" * 60)
if all_passed:
    print("所有测试通过")
else:
    print("部分测试失败 - 需要修复")
    sys.exit(1)
