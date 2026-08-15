"""
x_tolerance Sweep
-------------------
pdfplumber's default x_tolerance (used to decide "is this gap a new
word or the same word?") is 3. If your PDF's actual character spacing
is smaller than that, words merge. This script runs extraction at
several tolerance values so you can see where merged words start
separating correctly — and where it goes too far and starts merging
things that were legitimately two separate words.

Usage:
    python test_x_tolerance.py path/to/resume.pdf [page_number]
"""

import sys

import pdfplumber

TOLERANCES_TO_TEST = [0.5, 1, 1.5, 2, 3, 5]


def sweep(file_path: str, page_number: int = 1) -> None:
    with pdfplumber.open(file_path) as pdf:
        if page_number > len(pdf.pages):
            print(f"PDF only has {len(pdf.pages)} page(s).")
            return

        page = pdf.pages[page_number - 1]

        for tol in TOLERANCES_TO_TEST:
            text = page.extract_text(x_tolerance=tol)
            print(f"\n{'='*20} x_tolerance = {tol} {'='*20}")
            print(text)

        print(f"\n{'='*60}")
        print("Compare the outputs above. Pick the SMALLEST x_tolerance")
        print("where previously-merged words become correctly separated —")
        print("going higher than necessary risks merging words that were")
        print("already correctly separated (e.g. splitting a real two-word")
        print("phrase back together incorrectly).")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_x_tolerance.py <path_to_resume.pdf> [page_number]")
        sys.exit(1)

    path = sys.argv[1]
    page_num = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    sweep(path, page_num)