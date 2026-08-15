"""
Stage 1: Raw Text Extraction
-----------------------------
Extracts raw text from a resume file (PDF or DOCX) with no cleaning/
normalization applied yet — that's Stage 2. Keeping this stage isolated
means you can test extraction quality independently of downstream parsing
logic (if something goes wrong later, you'll know whether it's an
extraction problem or a parsing problem).

Usage:
    python extract_text.py path/to/resume.pdf
    python extract_text.py path/to/resume.docx

Or import directly:
    from extract_text import extract_text
    text = extract_text("resume.pdf")
"""

import sys
from pathlib import Path

import pdfplumber
from docx import Document


MIN_CHARS_PER_PAGE = 25  # below this, treat the page as likely scanned/image-based


def classify_pdf(file_path: str, x_tolerance: float = 0.5) -> dict:
    """
    Determine whether a PDF is text-based, scanned, or mixed, without
    doing any OCR. This is the fork-point decision: text-based pages
    go through pdfplumber extraction (already built), scanned pages
    will need OCR (not built yet).

    A page is flagged "likely_scanned" if its extracted text is under
    MIN_CHARS_PER_PAGE characters. This is more reliable than a plain
    None check — some scanned pages leak a few stray characters
    (watermarks, page numbers) even with no real extractable content.

    Returns a dict:
        {
            "total_pages": int,
            "text_pages": [page numbers with real text],
            "scanned_pages": [page numbers likely needing OCR],
            "overall": "text-based" | "scanned" | "mixed"
        }
    """
    text_pages = []
    scanned_pages = []

    with pdfplumber.open(file_path) as pdf:
        total_pages = len(pdf.pages)
        for page_num, page in enumerate(pdf.pages, start=1):
            text = page.extract_text(x_tolerance=x_tolerance) or ""
            char_count = len(text.strip())
            if char_count < MIN_CHARS_PER_PAGE:
                scanned_pages.append(page_num)
            else:
                text_pages.append(page_num)

    if scanned_pages and text_pages:
        overall = "mixed"
    elif scanned_pages:
        overall = "scanned"
    else:
        overall = "text-based"

    return {
        "total_pages": total_pages,
        "text_pages": text_pages,
        "scanned_pages": scanned_pages,
        "overall": overall,
    }


def extract_text_from_pdf(file_path: str, x_tolerance: float = 0.5) -> str:
    """
    Extract text from a PDF, page by page, in reading order as best as
    pdfplumber can determine it.

    x_tolerance controls how large a horizontal gap must be before
    pdfplumber treats it as a word boundary rather than the same word.
    Default of 0.5 was chosen based on diagnostic testing on a resume
    where the default (3) caused words to merge together. This value
    may not generalize to every resume/font — if you see over-split
    words (e.g. "CGPA:" splitting into "CGPA" ":"), try a higher value
    for that specific file.

    Note: multi-column resumes can still extract out of visual order —
    this is a known limitation of PDF text extraction in general, not
    specific to this library. Worth eyeballing output on a 2-column
    resume before trusting it blindly.
    """
    pages_text = []
    with pdfplumber.open(file_path) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            text = page.extract_text(x_tolerance=x_tolerance)
            if text:
                pages_text.append(text)
            else:
                # Page extracted nothing — likely an image-based/scanned
                # page. Flagging rather than silently dropping it, since
                # you'll want to know if OCR is needed later.
                print(f"  [warn] page {page_num}: no extractable text "
                      f"(possibly scanned/image-based)", file=sys.stderr)
    return "\n".join(pages_text)


def extract_text_from_docx(file_path: str) -> str:
    """
    Extract text from a DOCX file, paragraph by paragraph.

    Note: this only pulls paragraph text. It won't pick up text inside
    tables (some resumes use tables for layout, e.g. skills grids) —
    that's a deliberate scope cut for Stage 1. We can extend this once
    you test on real resumes and see if tables matter for your dataset.
    """
    doc = Document(file_path)
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    return "\n".join(paragraphs)


def extract_text(file_path: str, x_tolerance: float = 0.5) -> str:
    """Dispatch to the right extractor based on file extension."""
    path = Path(file_path)
    suffix = path.suffix.lower()

    if not path.exists():
        raise FileNotFoundError(f"No such file: {file_path}")

    if suffix == ".pdf":
        return extract_text_from_pdf(str(path), x_tolerance=x_tolerance)
    elif suffix == ".docx":
        return extract_text_from_docx(str(path))
    else:
        raise ValueError(
            f"Unsupported file type: {suffix}. Expected .pdf or .docx"
        )


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python extract_text.py <path_to_resume>")
        sys.exit(1)

    input_path = sys.argv[1]
    try:
        raw_text = extract_text(input_path)
        print(f"--- Extracted {len(raw_text)} characters ---\n")
        print(raw_text)
    except Exception as e:
        print(f"Error extracting text: {e}", file=sys.stderr)
        sys.exit(1)
