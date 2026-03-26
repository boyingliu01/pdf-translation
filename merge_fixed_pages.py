"""Merge fixed pages into regression test PDF."""

from pathlib import Path
import fitz
import shutil


def merge_fixed_pages():
    # Source PDF
    base_pdf = Path(
        "E:/2-booboo/Palantir/output/regression_test/The Philosopher in the Valley Alex Karp, Palantir, and the Rise of the Surveillance State.no_watermark.zh.dual.pdf"
    )

    # Fixed pages
    batch1 = Path(
        "E:/2-booboo/Palantir/output/fix_pages_batch1/The Philosopher in the Valley Alex Karp, Palantir, and the Rise of the Surveillance State.no_watermark.zh.dual.pdf"
    )
    batch2 = Path(
        "E:/2-booboo/Palantir/output/fix_pages_batch2/The Philosopher in the Valley Alex Karp, Palantir, and the Rise of the Surveillance State.no_watermark.zh.dual.pdf"
    )

    output_path = Path(
        "E:/2-booboo/Palantir/output/The Philosopher in the Valley Alex Karp, Palantir, and the Rise of the Surveillance State.FINAL_FIXED.zh.dual.pdf"
    )

    print("=== Merging Fixed Pages ===\n")

    # Open base PDF
    base_doc = fitz.open(str(base_pdf))
    print(f"Base PDF: {len(base_doc)} pages")

    # Replace pages from batch1 (13, 24, 28)
    if batch1.exists():
        print("Replacing pages 13, 24, 28 from batch1...")
        batch1_doc = fitz.open(str(batch1))
        pages_to_replace = [13, 24, 28]
        for page_num in pages_to_replace:
            if page_num <= len(base_doc) and page_num <= len(batch1_doc):
                base_doc.delete_page(page_num - 1)
                base_doc.insert_pdf(
                    batch1_doc,
                    from_page=page_num - 1,
                    to_page=page_num - 1,
                    start_at=page_num - 1,
                )
                print(f"  ✅ Page {page_num} replaced")
        batch1_doc.close()

    # Replace pages from batch2 (170, 171, 172, 176)
    if batch2.exists():
        print("Replacing pages 170, 171, 172, 176 from batch2...")
        batch2_doc = fitz.open(str(batch2))
        # Replace in reverse order to maintain correct indices
        pages_to_replace = [176, 172, 171, 170]
        for page_num in pages_to_replace:
            if page_num <= len(base_doc) and page_num <= len(batch2_doc):
                base_doc.delete_page(page_num - 1)
                base_doc.insert_pdf(
                    batch2_doc,
                    from_page=page_num - 1,
                    to_page=page_num - 1,
                    start_at=page_num - 1,
                )
                print(f"  ✅ Page {page_num} replaced")
        batch2_doc.close()

    # Save merged PDF
    print(f"\nSaving to: {output_path}")
    base_doc.save(str(output_path))
    base_doc.close()

    # Add page numbers manually
    print("\nAdding page numbers...")
    add_page_numbers(str(output_path))

    # Verify
    final_doc = fitz.open(str(output_path))
    file_size_mb = output_path.stat().st_size / 1024 / 1024

    print(f"\n✅ Merge complete!")
    print(f"Output: {output_path}")
    print(f"Pages: {len(final_doc)}")
    print(f"Size: {file_size_mb:.2f} MB")

    final_doc.close()


def add_page_numbers(pdf_path: str, font_size: int = 10) -> None:
    """为PDF添加页码"""
    pdf_path = Path(pdf_path)
    temp_path = pdf_path.parent / f"{pdf_path.stem}.temp{pdf_path.suffix}"

    doc = fitz.open(str(pdf_path))
    total_pages = len(doc)

    for page_num in range(total_pages):
        page = doc[page_num]
        rect = page.rect

        margin_right = 50
        margin_bottom = 30

        x = rect.width - margin_right
        y = rect.height - margin_bottom

        point = fitz.Point(x, y)
        page_text = str(page_num + 1)

        page.insert_text(point, page_text, fontsize=font_size, color=(0, 0, 0))

    doc.save(str(temp_path))
    doc.close()

    shutil.move(str(temp_path), str(pdf_path))
    print(f"✅ 已添加页码到 {total_pages} 页")


if __name__ == "__main__":
    merge_fixed_pages()
