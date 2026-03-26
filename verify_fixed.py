"""Verify the fixed pages."""

from pathlib import Path
import fitz


def verify_fixed_pages():
    pdf_path = Path(
        "E:/2-booboo/Palantir/output/The Philosopher in the Valley Alex Karp, Palantir, and the Rise of the Surveillance State.FINAL_FIXED.zh.dual.pdf"
    )

    if not pdf_path.exists():
        print("PDF not found!")
        return

    doc = fitz.open(str(pdf_path))

    # Pages that were fixed
    fixed_pages = [13, 24, 28, 170, 171, 172, 176]

    print("=== Verification of Fixed Pages ===\n")

    all_good = True
    for page_num in fixed_pages:
        page = doc[page_num - 1]
        text = page.get_text()

        chinese_chars = sum(1 for c in text if "\u4e00" <= c <= "\u9fff")
        english_chars = sum(1 for c in text if c.isascii() and c.isalpha())

        # Check if page has substantial Chinese content
        if chinese_chars > 500:
            status = "✅"
        elif chinese_chars > 100:
            status = "⚠️ Partial"
            all_good = False
        else:
            status = "❌"
            all_good = False

        print(f"{status} Page {page_num}: CN={chinese_chars}, EN={english_chars}")

    doc.close()

    print(f"\n{'=' * 50}")
    if all_good:
        print("✅ All fixed pages verified successfully!")
    else:
        print("⚠️ Some pages may need further attention")

    print(f"\nFinal PDF: {pdf_path}")
    print(f"Size: {pdf_path.stat().st_size / 1024 / 1024:.2f} MB")


if __name__ == "__main__":
    verify_fixed_pages()
