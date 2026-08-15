"""
Diagnose Why a Page Has No Extractable Text
----------------------------------------------
When extract_text() returns nothing, this checks what's actually on
the page to figure out WHY:

- page.images non-empty, page.chars empty  -> genuinely scanned/image page
- page.images empty, page.chars empty, but page.rects/curves present
  -> text was likely rendered as vector outlines (no real text layer)
- page.chars non-empty but extract_text() still returned nothing
  -> font encoding issue, characters exist but aren't mapping right

Usage:
    python diagnose_no_text.py path/to/resume.pdf [page_number]
"""

import sys

import pdfplumber


def diagnose(file_path: str, page_number: int = 1) -> None:
    with pdfplumber.open(file_path) as pdf:
        if page_number > len(pdf.pages):
            print(f"PDF only has {len(pdf.pages)} page(s).")
            return

        page = pdf.pages[page_number - 1]

        extracted_text = page.extract_text() or ""
        num_chars = len(page.chars)
        num_images = len(page.images)
        num_rects = len(page.rects)
        num_curves = len(page.curves)
        num_lines = len(page.lines)

        print(f"Page {page_number} diagnostic:")
        print(f"  extract_text() result length:          {len(extracted_text.strip())} chars")
        print(f"  chars (extractable text characters):   {num_chars}")
        print(f"  images embedded on page:               {num_images}")
        print(f"  rects (vector rectangles):             {num_rects}")
        print(f"  curves (vector paths):                 {num_curves}")
        print(f"  lines (vector lines):                  {num_lines}")
        print()

        if len(extracted_text.strip()) > 0:
            print("DIAGNOSIS: extract_text() actually succeeded — this page")
            print("  is not the problem. (If you expected a failure here,")
            print("  double check you pointed this at the right page number.)")
        elif num_images > 0 and num_chars == 0:
            print("DIAGNOSIS: Genuinely scanned/image-based page.")
            print("  -> Needs OCR. No text layer exists to extract.")
        elif num_chars == 0 and (num_curves > 20 or num_rects > 20):
            print("DIAGNOSIS: Likely text rendered as vector outlines")
            print("  (common with certain PDF exporters/design tools).")
            print("  -> No real text layer despite looking like text visually.")
            print("  -> Needs OCR, same as scanned pages, different root cause.")
        elif num_chars > 0:
            print("DIAGNOSIS: Characters DO exist on this page, but")
            print("  extract_text() returned nothing anyway.")
            print("  -> Likely a font encoding issue, not a scanned page.")
            print("  -> Try page.chars directly to inspect raw character data.")
        else:
            print("DIAGNOSIS: Unclear — very little content detected at all.")
            print("  -> Worth opening the PDF visually to confirm what's")
            print("     actually on this page.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python diagnose_no_text.py <path_to_resume.pdf> [page_number]")
        sys.exit(1)

    path = sys.argv[1]
    page_num = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    diagnose(path, page_num)