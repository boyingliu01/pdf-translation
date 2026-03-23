# Cross-Page Paragraph Translation Fix Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix cross-page paragraph translation issues where paragraphs spanning pages are either not translated or have mixed English/Chinese with incorrect fonts.

**Architecture:** The fix involves completely rewriting the `patch_babeldoc_cross_page()` function in `pdf_translator.py` to properly detect and handle cross-page paragraphs, including those not classified as "body text". The new implementation will detect incomplete paragraphs at page boundaries and merge them with the following page's first paragraph for unified translation.

**Tech Stack:** Python 3.12+, BabelDOC (PDF processing library), pdf2zh-next

---

## Root Cause Analysis

### Problem 1: `enhanced_filter_paragraphs` Side Effect
When we replaced `_filter_paragraphs`:
- Original `process_cross_page_paragraph` calls `_filter_paragraphs(require_body_text=True)`
- Our `enhanced_filter_paragraphs` returns ALL paragraphs when no body text is found
- This causes non-body-text paragraphs to be incorrectly processed as cross-page paragraphs

### Problem 2: `patched_process_cross_page` Only Logs, Doesn't Process
The patch detects incomplete paragraphs but only logs them without actual processing.

### Problem 3: Original BabelDOC Logic Limitation
Original `process_cross_page_paragraph` only handles paragraphs with `layout_label` in `("text", "plain text", "paragraph_hybrid")`. Paragraphs with other labels that span pages are ignored.

---

## File Structure

**Modify:**
- `pdf_translator.py:124-235` - Complete rewrite of `patch_babeldoc_cross_page()`

**Test:**
- `test/test_cross_page_patch.py` - Update tests for new implementation

---

## Task 1: Remove Broken Patch and Design Clean Implementation

**Files:**
- Modify: `pdf_translator.py:124-235`

- [ ] **Step 1: Remove the broken patch implementation**

Delete lines 124-235 in `pdf_translator.py` (the current `patch_babeldoc_cross_page` function and related code).

- [ ] **Step 2: Design clean patch approach**

The new approach should:
1. NOT replace `_filter_paragraphs` (avoid side effects)
2. Replace `process_cross_page_paragraph` completely
3. Detect incomplete paragraphs using `_is_incomplete_sentence()`
4. Submit cross-page paragraph batches for translation
5. Mark paragraphs as translated to avoid double-processing

---

## Task 2: Implement New `patch_babeldoc_cross_page()`

**Files:**
- Modify: `pdf_translator.py`

- [ ] **Step 1: Write the new patch function structure**

```python
def patch_babeldoc_cross_page():
    """Apply BabelDOC cross-page paragraph handling patch.

    This patch fixes cross-page paragraph translation by:
    1. Detecting incomplete paragraphs at page boundaries
    2. Merging them with the next page's first paragraph
    3. Submitting them for translation as a batch

    The original BabelDOC only handles 'body text' paragraphs.
    This patch extends detection to all translatable paragraphs.
    """
    _logger = logging.getLogger(__name__)

    try:
        from babeldoc.format.pdf.document_il.midend import il_translator_llm_only

        # Save original method for reference (not used, but kept for potential rollback)
        original_method = il_translator_llm_only.ILTranslatorLLMOnly.process_cross_page_paragraph

        def patched_process_cross_page_paragraph(
            self,
            docs,
            executor,
            pbar=None,
            tracker=None,
            executor2=None,
            translated_ids=None,
        ):
            """Process cross-page paragraphs with enhanced detection.

            Key differences from original:
            1. Uses all translatable paragraphs, not just body text
            2. Checks paragraph completeness before merging
            3. Handles cases where original method misses cross-page paragraphs
            """
            self.translation_config.raise_if_cancelled()

            if tracker is None:
                tracker = DocumentTranslateTracker()

            if translated_ids is None:
                translated_ids = set()

            # Process all adjacent page pairs
            for i in range(len(docs.page) - 1):
                page_curr = docs.page[i]
                page_next = docs.page[i + 1]

                # Get all translatable paragraphs (not just body text)
                curr_paragraphs = self._filter_paragraphs(
                    page_curr, translated_ids, require_body_text=False
                )
                next_paragraphs = self._filter_paragraphs(
                    page_next, translated_ids, require_body_text=False
                )

                if not curr_paragraphs or not next_paragraphs:
                    continue

                last_curr = curr_paragraphs[-1]
                first_next = next_paragraphs[0]

                # Skip if already translated
                if id(last_curr) in translated_ids or id(first_next) in translated_ids:
                    continue

                # Check if the last paragraph is incomplete (possibly truncated)
                is_incomplete = _is_incomplete_sentence(last_curr.unicode) if last_curr.unicode else False

                if not is_incomplete:
                    continue

                _logger.info(
                    f"Cross-page: merging incomplete paragraph ending with '"
                    f"{last_curr.unicode[-30:] if last_curr.unicode else ''}'"
                )

                # Build font maps
                curr_font_map, curr_xobj_font_map = self._build_font_maps(page_curr)
                next_font_map, next_xobj_font_map = self._build_font_maps(page_next)
                merged_font_map = {**curr_font_map, **next_font_map}
                merged_xobj_font_map = {**curr_xobj_font_map, **next_xobj_font_map}

                # Calculate token count
                total_token_count = (
                    self.calc_token_count(last_curr.unicode)
                    + self.calc_token_count(first_next.unicode)
                )

                # Create and submit batch
                cross_page_paragraphs = [last_curr, first_next]
                cross_page_pages = [page_curr, page_next]
                batch_paragraph = BatchParagraph(
                    cross_page_paragraphs, cross_page_pages, tracker.new_cross_page()
                )

                self.mid += 1
                executor.submit(
                    self.translate_paragraph,
                    batch_paragraph,
                    pbar,
                    merged_font_map,
                    merged_xobj_font_map,
                    self.translation_config.shared_context_cross_split_part.first_paragraph,
                    self.translation_config.shared_context_cross_split_part.recent_title_paragraph,
                    executor2,
                    priority=1048576 - total_token_count,
                    paragraph_token_count=total_token_count,
                    mp_id=self.mid,
                )

                # Mark as translated
                translated_ids.add(id(last_curr))
                translated_ids.add(id(first_next))

        # Apply patch
        il_translator_llm_only.ILTranslatorLLMOnly.process_cross_page_paragraph = patched_process_cross_page_paragraph
        _logger.info("BabelDOC cross-page patch applied successfully")

    except Exception as e:
        _logger.warning(f"BabelDOC cross-page patch failed: {e}")
```

- [ ] **Step 2: Add required imports at top of file**

The function uses `BatchParagraph`, `DocumentTranslateTracker` from babeldoc. Add imports if not present:
```python
# These are used inside the function via the babeldoc module, no new imports needed
```

- [ ] **Step 3: Verify `_is_incomplete_sentence` function exists**

Check that `_is_incomplete_sentence()` function (defined around line 86) is working correctly. It should return `True` for incomplete sentences.

---

## Task 3: Update Tests

**Files:**
- Modify: `test/test_cross_page_patch.py`

- [ ] **Step 1: Update test to verify new patch behavior**

Add tests that verify:
1. Cross-page paragraphs are detected
2. Paragraphs are marked as translated after processing
3. Non-body-text paragraphs are handled

- [ ] **Step 2: Run tests to verify patch works**

```bash
cd /e/2-booboo/pdf-translation && python test/test_cross_page_patch.py
```

---

## Task 4: Integration Test

**Files:**
- Run translation on test PDF

- [ ] **Step 1: Run translation with debug mode**

```bash
cd /e/2-booboo/pdf-translation && python translate_pdf.py -i "/e/2-booboo/Palantir/The Philosopher in the Valley Alex Karp, Palantir, and the Rise of the Surveillance State.pdf" -o "/e/2-booboo/Palantir/output/fix-test" --no-mono --pages "4-6,9-10,12-13" --config config/config.json
```

- [ ] **Step 2: Add page numbers to output**

```bash
python add_page_numbers.py "/e/2-booboo/Palantir/output/fix-test/*.dual.pdf" "/e/2-booboo/Palantir/output/fix-test/with-page-numbers.pdf"
```

- [ ] **Step 3: Manually verify results**

Check pages 5, 9-10, 12-13 for:
- Complete translation of cross-page paragraphs
- No mixed English/Chinese
- Correct font sizes

---

## Verification

### Success Criteria
1. Cross-page paragraphs are fully translated (no English remnants)
2. No double-translation (English + Chinese appearing together)
3. Font sizes are consistent
4. All tests pass

### Failure Indicators
- "th"/"ft" residual characters (control character issue)
- Mixed English/Chinese in same paragraph
- Paragraphs missing translation entirely

---

## Notes

### Key BabelDOC Classes
- `BatchParagraph`: Wraps multiple paragraphs for batch translation
- `DocumentTranslateTracker`: Tracks translation progress
- `PageTranslateTracker`: Per-page tracking

### Translation Flow
1. `process_cross_page_paragraph` - Merges cross-page paragraphs
2. `process_cross_column_paragraph` - Handles multi-column layouts
3. `process_page` - Processes remaining paragraphs
4. `translate_paragraph` - Actually translates via LLM

### Why Not Modify `_filter_paragraphs`
Modifying `_filter_paragraphs` causes side effects because it's called from multiple places. The original `process_page` also uses it, so changing its behavior affects non-cross-page processing.

---

## Rollback Plan

If the new patch causes issues:
1. Simply comment out the `patch_babeldoc_cross_page()` call
2. The original BabelDOC behavior will be restored (only body text cross-page handling)

```python
# In pdf_translator.py, line ~239:
# patch_babeldoc_cross_page()  # Disable if causing issues
```