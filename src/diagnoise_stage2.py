"""
Stage 2 Diagnostic: Raw Line -> Normalized Line
--------------------------------------------------
Deliberately NOT a full cleaning pipeline. This only applies basic,
safe normalization (whitespace + unicode) and prints each line
before/after, so you can visually inspect what's happening on real
resumes before deciding what more aggressive cleaning (line-joining,
bullet standardization, section detection) actually needs to do.

Usage:
    python diagnose_stage2.py path/to/resume.pdf
    python diagnose_stage2.py path/to/resume.docx
"""

import sys
import unicodedata

from extract_text import extract_text


def normalize_line(line: str) -> str:
    """
    Basic, conservative normalization only:
    - Unicode normalization (handles weird PDF character encodings,
      e.g. ligatures like 'fi' extracting as a single glyph)
    - Collapse internal whitespace (multiple spaces/tabs -> single space)
    - Strip leading/trailing whitespace

    Deliberately NOT doing here: line joining, bullet standardization,
    section detection. Those come after you've seen what real lines
    look like.
    """
    normalized = unicodedata.normalize("NFKC", line)
    normalized = " ".join(normalized.split())  # collapses all whitespace runs
    return normalized


def diagnose(file_path: str) -> None:
    raw_text = extract_text(file_path)
    raw_lines = raw_text.split("\n")

    print(f"{'#':<4} {'RAW LINE':<50} -> NORMALIZED LINE")
    print("-" * 100)

    for i, raw_line in enumerate(raw_lines):
        normalized = normalize_line(raw_line)
        changed_marker = "  [changed]" if normalized != raw_line else ""
        # repr() so you can actually see trailing spaces/tabs/weird chars
        print(f"{i:<4} {raw_line!r:<50} -> {normalized!r}{changed_marker}")

    print("-" * 100)
    print(f"Total lines: {len(raw_lines)}")
    changed_count = sum(
        1 for l in raw_lines if normalize_line(l) != l
    )
    print(f"Lines changed by normalization: {changed_count}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python diagnose_stage2.py <path_to_resume>")
        sys.exit(1)

    diagnose(sys.argv[1])