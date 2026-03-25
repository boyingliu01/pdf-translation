"""Merge translated sensitive pages into the original PDF."""

from pathlib import Path
import fitz  # PyMuPDF
import shutil


def merge_translated_pages():
    # Paths
    original_pdf = Path(
        "E:/2-booboo/Palantir/output/final/The Philosopher in the Valley Alex Karp, Palantir, and the Rise of the Surveillance State.no_watermark.zh.dual.pdf"
    )

    # Translated sensitive pages
    page_13 = Path(
        "E:/2-booboo/Palantir/output/sensitive_pages_bailian/The Philosopher in the Valley Alex Karp, Palantir, and the Rise of the Surveillance State.no_watermark.zh.dual.pdf"
    )
    page_133 = Path(
        "E:/2-booboo/Palantir/output/sensitive_pages_bailian_p133/The Philosopher in the Valley Alex Karp, Palantir, and the Rise of the Surveillance State.no_watermark.zh.dual.pdf"
    )
    pages_184_200 = Path(
        "E:/2-booboo/Palantir/output/sensitive_pages_bailian_p184-200/The Philosopher in the Valley Alex Karp, Palantir, and the Rise of the Surveillance State.no_watermark.zh.dual.pdf"
    )

    output_path = Path(
        "E:/2-booboo/Palantir/output/The Philosopher in the Valley Alex Karp, Palantir, and the Rise of the Surveillance State.COMPLETE.zh.dual.pdf"
    )

    print("=== Merging Translated Pages ===\n")

    # Verify source files exist
    if not original_pdf.exists():
        print(f"❌ Original PDF not found: {original_pdf}")
        return

    # Open the original PDF
    original_doc = fitz.open(str(original_pdf))
    print(f"Original PDF has {len(original_doc)} pages")

    # Replace page 13
    if page_13.exists():
        print(f"\nReplacing page 13...")
        page_13_doc = fitz.open(str(page_13))
        if len(page_13_doc) >= 13:
            original_doc.delete_page(12)  # 0-indexed, page 13
            original_doc.insert_pdf(page_13_doc, from_page=12, to_page=12)
            print(f"✅ Page 13 replaced")
        page_13_doc.close()

    # Replace page 133
    if page_133.exists():
        print(f"\nReplacing page 133...")
        page_133_doc = fitz.open(str(page_133))
        if len(page_133_doc) >= 133:
            original_doc.delete_page(132)  # 0-indexed, page 133
            original_doc.insert_pdf(page_133_doc, from_page=132, to_page=132)
            print(f"✅ Page 133 replaced")
        page_133_doc.close()

    # Replace pages 184-200
    if pages_184_200.exists():
        print(f"\nReplacing pages 184-200...")
        pages_184_200_doc = fitz.open(str(pages_184_200))
        # Delete pages 184-200 from original (in reverse order to avoid index shift)
        for page_num in range(200, 183, -1):  # 200 to 184
            original_doc.delete_page(page_num - 1)  # 0-indexed

        # Insert new pages 184-200
        original_doc.insert_pdf(pages_184_200_doc, from_page=183, to_page=199)
        print(f"✅ Pages 184-200 replaced")
        pages_184_200_doc.close()

    # Save the merged PDF
    print(f"\nSaving merged PDF to: {output_path}")
    original_doc.save(str(output_path))
    original_doc.close()

    print(f"\n✅ Merge complete!")
    print(f"Output: {output_path}")
    print(f"Total pages: {len(fitz.open(str(output_path)))}")


if __name__ == "__main__":
    merge_translated_pages()
