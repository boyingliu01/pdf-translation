"""Find all pages with untranslated English content in the merged PDF."""

from pathlib import Path
import fitz


def find_untranslated_pages():
    pdf_path = Path(
        "E:/2-booboo/Palantir/output/The Philosopher in the Valley Alex Karp, Palantir, and the Rise of the Surveillance State.COMPLETE.zh.dual.pdf"
    )

    if not pdf_path.exists():
        print("PDF not found!")
        return

    doc = fitz.open(str(pdf_path))
    print(f"=== Scanning {len(doc)} pages for untranslated content ===\n")

    untranslated_pages = []

    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text()

        # Count Chinese and English characters
        chinese_chars = sum(1 for c in text if "\u4e00" <= c <= "\u9fff")
        english_chars = sum(1 for c in text if c.isascii() and c.isalpha())

        # If page has substantial English but very little Chinese, it's likely untranslated
        # Skip pages that are mostly images or titles
        if english_chars > 500 and chinese_chars < 200:
            untranslated_pages.append(
                {
                    "page": page_num + 1,
                    "chinese": chinese_chars,
                    "english": english_chars,
                }
            )
            print(
                f"Page {page_num + 1}: ⚠️ Likely untranslated (CN: {chinese_chars}, EN: {english_chars})"
            )
        elif english_chars > 200 and chinese_chars < 50:
            # Also catch pages with moderate English but very little Chinese
            untranslated_pages.append(
                {
                    "page": page_num + 1,
                    "chinese": chinese_chars,
                    "english": english_chars,
                }
            )
            print(
                f"Page {page_num + 1}: ⚠️ Possibly untranslated (CN: {chinese_chars}, EN: {english_chars})"
            )

    doc.close()

    print(f"\n=== Summary ===")
    print(f"Found {len(untranslated_pages)} pages with potential untranslated content")

    if untranslated_pages:
        pages_list = [str(p["page"]) for p in untranslated_pages]
        print(
            f"Pages: {','.join(pages_list[:20])}{'...' if len(pages_list) > 20 else ''}"
        )

        # Group into ranges
        ranges = []
        pages = sorted([p["page"] for p in untranslated_pages])
        if pages:
            start = pages[0]
            end = start

            for page in pages[1:]:
                if page == end + 1:
                    end = page
                else:
                    if start == end:
                        ranges.append(str(start))
                    else:
                        ranges.append(f"{start}-{end}")
                    start = end = page

            if start == end:
                ranges.append(str(start))
            else:
                ranges.append(f"{start}-{end}")

            print(f"\nPage ranges: {','.join(ranges)}")

    return untranslated_pages


if __name__ == "__main__":
    find_untranslated_pages()
