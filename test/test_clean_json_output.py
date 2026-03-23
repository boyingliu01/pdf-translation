"""
测试控制字符清理功能

这个测试验证 _clean_json_output 方法是否能正确处理控制字符。
控制字符（ASCII 0-31）会导致 JSON 解析失败，触发 fallback 机制，
从而导致译文中出现 "th"、"ft" 等残留字符。
"""

import unittest
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestControlCharacterCleaning(unittest.TestCase):
    """测试控制字符清理功能"""

    def setUp(self):
        """导入需要测试的方法"""
        from pdf_translator import clean_json_output
        self.clean_json_output = clean_json_output

    def test_clean_normal_json(self):
        """测试正常的JSON输出"""
        input_str = '[{"id": 0, "output": "你好世界"}]'
        result = self.clean_json_output(input_str)
        self.assertEqual(result, input_str)

    def test_clean_json_with_json_wrapper(self):
        """测试移除<json>包装标签"""
        input_str = '<json>[{"id": 0, "output": "你好世界"}]</json>'
        expected = '[{"id": 0, "output": "你好世界"}]'
        result = self.clean_json_output(input_str)
        self.assertEqual(result, expected)

    def test_clean_json_with_code_block(self):
        """测试移除代码块包装"""
        input_str = '```json\n[{"id": 0, "output": "你好世界"}]\n```'
        expected = '[{"id": 0, "output": "你好世界"}]'
        result = self.clean_json_output(input_str)
        self.assertEqual(result, expected)

    def test_clean_control_characters_null(self):
        """测试清理空字符（ASCII 0）"""
        # 使用真正的控制字符
        input_str = '[{"id": 0, "output": "你好' + chr(0) + '世界"}]'
        result = self.clean_json_output(input_str)
        self.assertNotIn(chr(0), result)
        self.assertIn('你好世界', result)

    def test_clean_control_characters_tab(self):
        """测试保留制表符（ASCII 9）"""
        # 制表符应该保留
        input_str = '[{"id": 0, "output": "你好' + chr(9) + '世界"}]'
        result = self.clean_json_output(input_str)
        self.assertIn(chr(9), result)

    def test_clean_control_characters_newline(self):
        """测试保留换行符（ASCII 10）"""
        # 换行符应该保留
        input_str = '[{"id": 0, "output": "你好' + chr(10) + '世界"}]'
        result = self.clean_json_output(input_str)
        self.assertIn(chr(10), result)

    def test_clean_control_characters_carriage_return(self):
        """测试保留回车符（ASCII 13）"""
        # 回车符应该保留
        input_str = '[{"id": 0, "output": "你好' + chr(13) + '世界"}]'
        result = self.clean_json_output(input_str)
        self.assertIn(chr(13), result)

    def test_clean_control_characters_various(self):
        """测试清理各种控制字符"""
        # 测试各种控制字符（ASCII 0-31，除了 \t \n \r）
        for char_code in range(32):
            char = chr(char_code)
            if char in ('\t', '\n', '\r'):
                continue  # 这些应该保留
            input_str = '[{"id": 0, "output": "你好' + char + '世界"}]'
            result = self.clean_json_output(input_str)
            self.assertNotIn(char, result,
                f"控制字符 ASCII {char_code} 未被清理")

    def test_clean_th_ft_residual(self):
        """测试清理导致th/ft残留的控制字符场景"""
        # 模拟可能导致 "th" 残留的场景
        # 退格符 (ASCII 8) 和 ESC符 (ASCII 27)
        input_str = '[{"id": 0, "output": "这是一个测试th' + chr(8) + chr(27) + '世界"}]'
        result = self.clean_json_output(input_str)
        # 控制字符应该被移除
        self.assertNotIn(chr(8), result)  # 退格符
        self.assertNotIn(chr(27), result)  # ESC符
        self.assertIn('这是一个测试th世界', result)

    def test_clean_multiple_control_chars(self):
        """测试清理多个连续控制字符"""
        input_str = '[{"id": 0, "output": "你好' + chr(0) + chr(1) + chr(2) + '世界"}]'
        result = self.clean_json_output(input_str)
        self.assertNotIn(chr(0), result)
        self.assertNotIn(chr(1), result)
        self.assertNotIn(chr(2), result)
        self.assertIn('你好世界', result)

    def test_json_parseable_after_clean(self):
        """测试清理后的JSON可以被正确解析"""
        import json
        input_str = '[{"id": 0, "output": "你好' + chr(0) + '世界"}]'
        cleaned = self.clean_json_output(input_str)
        # 应该能够成功解析
        try:
            parsed = json.loads(cleaned)
            self.assertEqual(parsed[0]['id'], 0)
            self.assertEqual(parsed[0]['output'], '你好世界')
        except json.JSONDecodeError as e:
            self.fail(f"清理后的JSON无法解析: {e}")

    def test_clean_real_world_case(self):
        """测试真实场景：控制字符导致JSON解析失败"""
        import json
        # 模拟真实场景：文本中包含多个控制字符
        # 这些控制字符会导致 "Invalid control character" 错误
        input_str = '[{"id": 0, "output": "This is' + chr(1) + chr(2) + chr(3) + 'a test"}]'
        cleaned = self.clean_json_output(input_str)
        # 清理后应该能解析
        try:
            parsed = json.loads(cleaned)
            self.assertEqual(parsed[0]['output'], 'This isa test')
        except json.JSONDecodeError as e:
            self.fail(f"清理后的JSON无法解析: {e}")


class TestCleanJsonOutputImport(unittest.TestCase):
    """测试从babeldoc导入的功能"""

    def test_import_from_babeldoc(self):
        """测试是否可以从babeldoc导入并monkey patch"""
        try:
            from babeldoc.format.pdf.document_il.midend.il_translator_llm_only import (
                ILTranslatorLLMOnly,
            )
            # 检查方法存在
            self.assertTrue(hasattr(ILTranslatorLLMOnly, '_clean_json_output'))
        except ImportError as e:
            self.skipTest(f"无法导入babeldoc模块: {e}")

    def test_babeldoc_method_signature(self):
        """测试babeldoc中的方法签名是否匹配"""
        try:
            from babeldoc.format.pdf.document_il.midend.il_translator_llm_only import (
                ILTranslatorLLMOnly,
            )
            import inspect
            sig = inspect.signature(ILTranslatorLLMOnly._clean_json_output)
            params = list(sig.parameters.keys())
            # 应该有 self 和 llm_output 参数
            self.assertIn('llm_output', params)
        except ImportError as e:
            self.skipTest(f"无法导入babeldoc模块: {e}")


class TestMonkeyPatch(unittest.TestCase):
    """测试monkey patch功能"""

    def test_apply_patch(self):
        """测试是否可以成功应用monkey patch"""
        try:
            from babeldoc.format.pdf.document_il.midend.il_translator_llm_only import (
                ILTranslatorLLMOnly,
            )
            from pdf_translator import clean_json_output

            # 保存原始方法
            original_method = ILTranslatorLLMOnly._clean_json_output

            # 应用patch
            ILTranslatorLLMOnly._clean_json_output = clean_json_output

            # 验证patch生效 - 创建模拟实例
            class MockInstance:
                pass
            mock_self = MockInstance()

            test_input = '[{"id": 0, "output": "test' + chr(0) + '"}]'
            result = clean_json_output(mock_self, test_input)
            self.assertNotIn(chr(0), result)

            # 恢复原始方法
            ILTranslatorLLMOnly._clean_json_output = original_method

        except ImportError as e:
            self.skipTest(f"无法导入babeldoc模块: {e}")


if __name__ == '__main__':
    unittest.main()