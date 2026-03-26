"""Check specific paragraphs mentioned by user."""

from pathlib import Path
import fitz


def check_specific_paragraphs():
    pdf_path = Path(
        "E:/2-booboo/Palantir/output/regression_test/The Philosopher in the Valley Alex Karp, Palantir, and the Rise of the Surveillance State.no_watermark.zh.dual.pdf"
    )

    if not pdf_path.exists():
        print("PDF not found!")
        return

    doc = fitz.open(str(pdf_path))

    # Pages and paragraphs to check
    checks = [
        (13, -2, "倒数第2段"),
        (24, -1, "最后1段"),
        (28, 0, "第1段"),
        (170, -2, "倒数第2段"),
        (171, -1, "最后1段"),
        (172, -2, "倒数第2段"),
        (176, -1, "最后1段"),
    ]

    print("=== 检查未翻译段落 ===\n")

    for page_num, para_idx, desc in checks:
        if page_num > len(doc):
            continue

        page = doc[page_num - 1]
        text = page.get_text()

        # Split into paragraphs
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

        print(f"\n--- Page {page_num} ({desc}) ---")

        if para_idx == 0:
            target_para = paragraphs[0] if paragraphs else None
        elif para_idx == -1:
            target_para = paragraphs[-1] if paragraphs else None
        elif para_idx == -2:
            target_para = paragraphs[-2] if len(paragraphs) >= 2 else None
        else:
            target_para = None

        if target_para:
            chinese_chars = sum(1 for c in target_para if "\u4e00" <= c <= "\u9fff")
            english_chars = sum(1 for c in target_para if c.isascii() and c.isalpha())

            print(f"中文字符: {chinese_chars}, 英文字符: {english_chars}")
            print(f"内容前200字符:")
            print(target_para[:200])

            if chinese_chars < 10 and english_chars > 50:
                print("⚠️ 疑似未翻译")
            else:
                print("✅ 已翻译或混合内容")
        else:
            print("未找到段落")

    doc.close()


if __name__ == "__main__":
    check_specific_paragraphs()
