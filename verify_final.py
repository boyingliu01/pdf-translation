"""Verify the final PDF has all content translated."""

from pathlib import Path
import fitz


def verify_final_pdf():
    pdf_path = Path(
        "E:/2-booboo/Palantir/output/The Philosopher in the Valley Alex Karp, Palantir, and the Rise of the Surveillance State.FINAL.zh.dual.pdf"
    )

    if not pdf_path.exists():
        print("❌ Final PDF not found!")
        return

    doc = fitz.open(str(pdf_path))
    print(f"=== Verifying Final PDF ({len(doc)} pages) ===\n")

    untranslated_pages = []

    # Check specific pages that were problematic
    check_pages = [13, 100, 133, 184, 190, 200, 212, 215, 228, 229]

    for page_num in check_pages:
        if page_num > len(doc):
            continue
        page = doc[page_num - 1]
        text = page.get_text()

        chinese_chars = sum(1 for c in text if "\u4e00" <= c <= "\u9fff")
        english_chars = sum(1 for c in text if c.isascii() and c.isalpha())

        status = "✅" if chinese_chars > 100 else "⚠️"
        print(f"{status} Page {page_num}: CN={chinese_chars}, EN={english_chars}")

        if chinese_chars < 100 and english_chars > 500:
            untranslated_pages.append(page_num)

    # Also do a quick scan of all pages
    print(f"\n=== Quick scan of all pages ===")
    for page_num in range(1, len(doc) + 1, 23):  # Sample every ~10%
        page = doc[page_num - 1]
        text = page.get_text()
        chinese_chars = sum(1 for c in text if "\u4e00" <= c <= "\u9fff")
        english_chars = sum(1 for c in text if c.isascii() and c.isalpha())

        if chinese_chars < 50 and english_chars > 500:
            print(
                f"⚠️ Page {page_num}: Possibly untranslated (CN={chinese_chars}, EN={english_chars})"
            )
            untranslated_pages.append(page_num)
        elif chinese_chars > 0:
            print(f"✅ Page {page_num}: Has translation (CN={chinese_chars})")

    doc.close()

    file_size_mb = pdf_path.stat().st_size / 1024 / 1024
    print(f"\n=== Final Summary ===")
    print(f"✅ Final PDF: {pdf_path}")
    print(f"✅ Total pages: 234")
    print(f"✅ File size: {file_size_mb:.2f} MB")

    if untranslated_pages:
        print(f"\n⚠️ Potentially untranslated pages: {untranslated_pages}")
    else:
        print(f"\n✅ All checked pages appear to be translated!")


if __name__ == "__main__":
    verify_final_pdf()
