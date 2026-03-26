"""Deep inspection of problematic pages."""

from pathlib import Path
import fitz


def deep_inspect():
    pdf_path = Path(
        "E:/2-booboo/Palantir/output/regression_test/The Philosopher in the Valley Alex Karp, Palantir, and the Rise of the Surveillance State.no_watermark.zh.dual.pdf"
    )

    doc = fitz.open(str(pdf_path))

    # Check pages with issues
    pages_to_check = [13, 24, 28, 170, 171, 172, 176]

    for page_num in pages_to_check:
        print(f"\n{'=' * 60}")
        print(f"PAGE {page_num}")
        print("=" * 60)

        page = doc[page_num - 1]
        text = page.get_text()

        chinese_chars = sum(1 for c in text if "\u4e00" <= c <= "\u9fff")
        english_chars = sum(1 for c in text if c.isascii() and c.isalpha())

        print(f"Total Chinese: {chinese_chars}, English: {english_chars}")
        print(f"\nFull text (first 3000 chars):\n")
        print(text[:3000])
        print("\n" + "-" * 60)

    doc.close()


if __name__ == "__main__":
    deep_inspect()
