#!/usr/bin/env python3
"""
为PDF添加页码的脚本
使用方法: python add_page_numbers.py <input.pdf> <output.pdf>
"""

import sys
import fitz


def add_page_numbers(input_path: str, output_path: str, font_size: int = 10) -> None:
    """
    为PDF添加页码

    Args:
        input_path: 输入PDF路径
        output_path: 输出PDF路径
        font_size: 页码字体大小
    """
    doc = fitz.open(input_path)
    total_pages = len(doc)

    for page_num in range(total_pages):
        page = doc[page_num]
        rect = page.rect

        # 计算页码位置 (右下角)
        # 添加边距
        margin_right = 50
        margin_bottom = 30

        x = rect.width - margin_right
        y = rect.height - margin_bottom

        point = fitz.Point(x, y)

        # 页码文本
        page_text = str(page_num + 1)

        # 添加页码 (黑色)
        page.insert_text(
            point,
            page_text,
            fontsize=font_size,
            color=(0, 0, 0)
        )

    doc.save(output_path)
    doc.close()

    print(f"已添加页码到 {total_pages} 页")
    print(f"输出文件: {output_path}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("用法: python add_page_numbers.py <input.pdf> <output.pdf>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    add_page_numbers(input_file, output_file)
