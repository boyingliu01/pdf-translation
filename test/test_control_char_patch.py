#!/usr/bin/env python3
"""验证控制字符 Monkey Patch 是否正确应用。

测试目标：
1. _remove_control_chars 函数正确移除控制字符
2. Patch 1：ILTranslatorLLMOnly._clean_json_output 清理控制字符
3. Patch 2：ILTranslator.get_paragraph_unicode 清理控制字符
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pdf_translator
from pdf_translator import _remove_control_chars

print("=" * 60)
print("控制字符 Patch 测试")
print("=" * 60)

# --- 测试 _remove_control_chars ---
print("\n1. 测试 _remove_control_chars 函数")

test_cases = [
    # (输入, 期望输出, 描述)
    ("hello", "hello", "正常文本不变"),
    ("th\x08e", "the", "移除 backspace (0x08)"),
    ("f\x0ct", "ft", "移除 form feed (0x0c)"),
    ("\x00hello\x01", "hello", "移除 NUL 和 SOH"),
    ("line1\nline2", "line1\nline2", "保留换行符"),
    ("col1\tcol2", "col1\tcol2", "保留制表符"),
    ("text\r\n", "text\r\n", "保留 CR+LF"),
    ("a\x1bb", "ab", "移除 ESC (0x1b)"),
    ("th\x08e word", "the word", "实际 'th'+'backspace'+'e' 场景"),
]

all_passed = True
for input_text, expected, desc in test_cases:
    result = _remove_control_chars(input_text)
    status = "OK" if result == expected else "FAIL"
    if status == "FAIL":
        all_passed = False
    print(f"   [{status}] {desc}")
    if status == "FAIL":
        print(f"          输入: {repr(input_text)}")
        print(f"          期望: {repr(expected)}")
        print(f"          实际: {repr(result)}")

# --- 测试 Patch 1 ---
print("\n2. 测试 Patch 1: ILTranslatorLLMOnly._clean_json_output")
try:
    from babeldoc.format.pdf.document_il.midend.il_translator_llm_only import (
        ILTranslatorLLMOnly,
    )

    # 创建一个最小 mock 对象来调用方法
    class MockSelf:
        pass

    mock_self = MockSelf()
    patched_fn = ILTranslatorLLMOnly._clean_json_output

    # 测试含控制字符的 JSON
    test_output = '[{"id": 0, "output": "th\x08e text"}]'
    result = patched_fn(mock_self, test_output)
    has_control = any(ord(c) < 32 and c not in "\t\n\r" for c in result)
    status = "OK" if not has_control else "FAIL"
    if status == "FAIL":
        all_passed = False
    print(f"   [{status}] 控制字符已从输出中移除")
    if status == "FAIL":
        print(f"          结果仍含控制字符: {repr(result)}")

    # 测试正常 JSON 不受影响
    normal_output = '[{"id": 0, "output": "正常文本"}]'
    result2 = patched_fn(mock_self, normal_output)
    status2 = "OK" if result2.strip() == normal_output else "FAIL"
    if status2 == "FAIL":
        all_passed = False
    print(f"   [{status2}] 正常文本通过不受影响")
    if status2 == "FAIL":
        print(f"          期望: {repr(normal_output)}")
        print(f"          实际: {repr(result2)}")

except Exception as e:
    print(f"   [FAIL] 无法测试: {e}")
    all_passed = False

# --- 测试 Patch 2 ---
print("\n3. 测试 Patch 2: ILTranslator.get_paragraph_unicode")
try:
    from babeldoc.format.pdf.document_il.midend import il_translator

    patched_gpu = il_translator.get_paragraph_unicode

    # 验证它是我们的 patched 版本（通过闭包检查）
    # 直接检查函数名
    fn_name = patched_gpu.__name__
    is_patched = fn_name == "patched_get_paragraph_unicode"
    status = "OK" if is_patched else "FAIL"
    if not is_patched:
        all_passed = False
    print(f"   [{status}] get_paragraph_unicode 已被替换为 patched 版本")
    if not is_patched:
        print(f"          当前函数名: {fn_name}")

except Exception as e:
    print(f"   [FAIL] 无法测试: {e}")
    all_passed = False

# --- 最终结果 ---
print("\n" + "=" * 60)
if all_passed:
    print("所有测试通过")
else:
    print("部分测试失败")
    sys.exit(1)
