"""
Word Coordinate Diagnostic
----------------------------
Inspects word-level bounding boxes from pdfplumber to figure out WHY
word boundaries are being lost. Two different root causes look similar
in the final text but need different fixes:

1. GAP-DETECTION PROBLEM: pdfplumber's extract_text() decides where
   word breaks go based on horizontal gap size between characters.
   If gaps are small (font/kerning-dependent), it can merge two words
   into one. Fixable by tuning x_tolerance, no restructuring needed.

2. LAYOUT/COLUMN PROBLEM: text from two different columns has
   overlapping y-coordinates, so words from different columns get
   sorted onto what looks like the same "line." This needs genuine
   layout-aware extraction (grouping words by x-position clusters
   before reconstructing lines) — a bigger fix.

This script prints each word with its bounding box so you can tell
which one you're actually looking at.

Usage:
    python inspect_word_coords.py path/to/resume.pdf [page_number]
"""

import sys

import pdfplumber


def inspect(file_path: str, page_number: int = 1) -> None:
    with pdfplumber.open(file_path) as pdf:
        if page_number > len(pdf.pages):
            print(f"PDF only has {len(pdf.pages)} page(s).")
            return

        page = pdf.pages[page_number - 1]
        words = page.extract_words()

        if not words:
            print("No words extracted on this page (possibly scanned/image-based).")
            return

        print(f"Page {page_number} — {len(words)} words extracted\n")
        print(f"{'TEXT':<25} {'x0':>7} {'x1':>7} {'top':>7} {'bottom':>7}")
        print("-" * 60)
        for w in words:
            print(f"{w['text']:<25} {w['x0']:>7.1f} {w['x1']:>7.1f} "
                  f"{w['top']:>7.1f} {w['bottom']:>7.1f}")

        # --- Gap analysis: group words into rows by similar 'top', then
        # look at horizontal gaps between consecutive words in that row.
        print("\n--- Row-by-row horizontal gap analysis ---")
        rows = {}
        for w in words:
            row_key = round(w["top"] / 3) * 3  # bucket similar tops together
            rows.setdefault(row_key, []).append(w)

        for row_key in sorted(rows.keys()):
            row_words = sorted(rows[row_key], key=lambda w: w["x0"])
            if len(row_words) < 2:
                continue
            gaps = []
            for a, b in zip(row_words, row_words[1:]):
                gap = round(b["x0"] - a["x1"], 1)
                gaps.append(gap)
            line_preview = " ".join(w["text"] for w in row_words)
            print(f"top~{row_key:<5} gaps={gaps}  -> {line_preview}")

        print("\nWhat to look for:")
        print("  - Very small/negative gaps between words that SHOULD have a "
              "space -> gap-detection problem (fixable with x_tolerance)")
        print("  - Two clusters of x0 values that never overlap, appearing "
              "on the same 'top' row -> likely two columns merged into one "
              "line (layout problem, needs column-aware extraction)")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python inspect_word_coords.py <path_to_resume.pdf> [page_number]")
        sys.exit(1)

    path = sys.argv[1]
    page_num = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    inspect(path, page_num)