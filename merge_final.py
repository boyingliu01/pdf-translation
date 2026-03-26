"""Merge ALL translated pages into the final PDF."""

from pathlib import Path
import fitz  # PyMuPDF


def merge_all_translated_pages():
    # Base PDF (original translation)
    base_pdf = Path(
        "E:/2-booboo/Palantir/output/final/The Philosopher in the Valley Alex Karp, Palantir, and the Rise of the Surveillance State.no_watermark.zh.dual.pdf"
    )

    # All translated sensitive/missing pages
    translations = {
        13: Path(
            "E:/2-booboo/Palantir/output/sensitive_pages_bailian/The Philosopher in the Valley Alex Karp, Palantir, and the Rise of the Surveillance State.no_watermark.zh.dual.pdf"
        ),
        133: Path(
            "E:/2-booboo/Palantir/output/sensitive_pages_bailian_p133/The Philosopher in the Valley Alex Karp, Palantir, and the Rise of the Surveillance State.no_watermark.zh.dual.pdf"
        ),
        "184-200": Path(
            "E:/2-booboo/Palantir/output/sensitive_pages_bailian_p184-200/The Philosopher in the Valley Alex Karp, Palantir, and the Rise of the Surveillance State.no_watermark.zh.dual.pdf"
        ),
        100: Path(
            "E:/2-booboo/Palantir/output/missing_pages/The Philosopher in the Valley Alex Karp, Palantir, and the Rise of the Surveillance State.no_watermark.zh.dual.pdf"
        ),
        212: Path(
            "E:/2-booboo/Palantir/output/missing_pages/The Philosopher in the Valley Alex Karp, Palantir, and the Rise of the Surveillance State.no_watermark.zh.dual.pdf"
        ),
        215: Path(
            "E:/2-booboo/Palantir/output/missing_pages/The Philosopher in the Valley Alex Karp, Palantir, and the Rise of the Surveillance State.no_watermark.zh.dual.pdf"
        ),
        "228-229": Path(
            "E:/2-booboo/Palantir/output/missing_pages/The Philosopher in the Valley Alex Karp, Palantir, and the Rise of the Surveillance State.no_watermark.zh.dual.pdf"
        ),
    }

    output_path = Path(
        "E:/2-booboo/Palantir/output/The Philosopher in the Valley Alex Karp, Palantir, and the Rise of the Surveillance State.FINAL.zh.dual.pdf"
    )

    print("=== Merging All Translated Pages ===\n")

    if not base_pdf.exists():
        print(f"❌ Base PDF not found: {base_pdf}")
        return

    # Open the base PDF
    base_doc = fitz.open(str(base_pdf))
    print(f"Base PDF has {len(base_doc)} pages")

    # Replace page 13
    if translations[13].exists():
        print(f"Replacing page 13...")
        doc = fitz.open(str(translations[13]))
        if len(doc) >= 13:
            base_doc.delete_page(12)
            base_doc.insert_pdf(doc, from_page=12, to_page=12)
            print(f"✅ Page 13 replaced")
        doc.close()

    # Replace page 100
    if translations[100].exists():
        print(f"Replacing page 100...")
        doc = fitz.open(str(translations[100]))
        if len(doc) >= 100:
            base_doc.delete_page(99)
            base_doc.insert_pdf(doc, from_page=99, to_page=99)
            print(f"✅ Page 100 replaced")
        doc.close()

    # Replace page 133
    if translations[133].exists():
        print(f"Replacing page 133...")
        doc = fitz.open(str(translations[133]))
        if len(doc) >= 133:
            base_doc.delete_page(132)
            base_doc.insert_pdf(doc, from_page=132, to_page=132)
            print(f"✅ Page 133 replaced")
        doc.close()

    # Replace pages 184-200
    if translations["184-200"].exists():
        print(f"Replacing pages 184-200...")
        doc = fitz.open(str(translations["184-200"]))
        # Delete pages 184-200 from base (in reverse order)
        for page_num in range(200, 183, -1):
            base_doc.delete_page(page_num - 1)
        # Insert new pages 184-200
        base_doc.insert_pdf(doc, from_page=183, to_page=199)
        print(f"✅ Pages 184-200 replaced")
        doc.close()

    # Replace page 212
    if translations[212].exists():
        print(f"Replacing page 212...")
        doc = fitz.open(str(translations[212]))
        if len(doc) >= 212:
            base_doc.delete_page(211)
            base_doc.insert_pdf(doc, from_page=211, to_page=211)
            print(f"✅ Page 212 replaced")
        doc.close()

    # Replace page 215
    if translations[215].exists():
        print(f"Replacing page 215...")
        doc = fitz.open(str(translations[215]))
        if len(doc) >= 215:
            base_doc.delete_page(214)
            base_doc.insert_pdf(doc, from_page=214, to_page=214)
            print(f"✅ Page 215 replaced")
        doc.close()

    # Replace pages 228-229
    if translations["228-229"].exists():
        print(f"Replacing pages 228-229...")
        doc = fitz.open(str(translations["228-229"]))
        # Delete pages 228-229 from base (in reverse order)
        for page_num in range(229, 227, -1):
            base_doc.delete_page(page_num - 1)
        # Insert new pages 228-229
        base_doc.insert_pdf(doc, from_page=227, to_page=228)
        print(f"✅ Pages 228-229 replaced")
        doc.close()

    # Save the merged PDF
    print(f"\nSaving final PDF to: {output_path}")
    base_doc.save(str(output_path))
    base_doc.close()

    # Verify
    final_doc = fitz.open(str(output_path))
    file_size_mb = output_path.stat().st_size / 1024 / 1024

    print(f"\n✅ Final merge complete!")
    print(f"Output: {output_path}")
    print(f"Total pages: {len(final_doc)}")
    print(f"File size: {file_size_mb:.2f} MB")

    final_doc.close()


if __name__ == "__main__":
    merge_all_translated_pages()
