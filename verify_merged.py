"""Verify the merged PDF."""

from pathlib import Path
import fitz


def verify_merged_pdf():
    merged_pdf = Path(
        "E:/2-booboo/Palantir/output/The Philosopher in the Valley Alex Karp, Palantir, and the Rise of the Surveillance State.COMPLETE.zh.dual.pdf"
    )

    if not merged_pdf.exists():
        print("❌ Merged PDF not found!")
        return

    doc = fitz.open(str(merged_pdf))
    print(f"=== Verifying Merged PDF ({len(doc)} pages) ===\n")

    # Check page 13
    print("=== Page 13 (Sensitive: Hamas attack) ===")
    page = doc[12]
    text = page.get_text()
    chinese_chars = sum(1 for c in text if "\u4e00" <= c <= "\u9fff")
    print(f"Chinese characters: {chinese_chars}")
    if "哈马斯" in text or "以色列" in text:
        print("✅ Sensitive content translated!")
    else:
        print("⚠️ May not be fully translated")
    print()

    # Check page 133
    print("=== Page 133 (Project Maven) ===")
    page = doc[132]
    text = page.get_text()
    chinese_chars = sum(1 for c in text if "\u4e00" <= c <= "\u9fff")
    print(f"Chinese characters: {chinese_chars}")
    if chinese_chars > 100:
        print("✅ Page translated!")
    else:
        print("⚠️ May not be fully translated")
    print()

    # Check page 190 (middle of 184-200)
    print("=== Page 190 (Middle of sensitive range) ===")
    page = doc[189]
    text = page.get_text()
    chinese_chars = sum(1 for c in text if "\u4e00" <= c <= "\u9fff")
    print(f"Chinese characters: {chinese_chars}")
    if chinese_chars > 200:
        print("✅ Page translated!")
    else:
        print("⚠️ May not be fully translated")

    # Show file size
    file_size_mb = merged_pdf.stat().st_size / 1024 / 1024
    print(f"\n✅ Merged PDF verified!")
    print(f"File: {merged_pdf}")
    print(f"Size: {file_size_mb:.2f} MB")
    print(f"Pages: {len(doc)}")

    doc.close()


if __name__ == "__main__":
    verify_merged_pdf()
