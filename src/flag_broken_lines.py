"""
Broken-Line Detection Diagnostic
------------------------------------
Flags line pairs that LOOK like a broken sentence (wrapped mid-thought
during PDF extraction), without actually joining anything. This is a
dry run — review the flagged candidates on real resumes before we
write actual join logic, since a wrong heuristic could incorrectly
merge genuinely separate lines (e.g. two different bullet points).

Heuristic for "line N is probably broken, should join with line N+1":
  - Line N does NOT end in sentence-ending punctuation (. ! ? : ;)
  - Line N does NOT end in a bullet-like character
  - Line N is not a short, likely-header line (all-caps, <=3 words)
  - Line N+1 does NOT start with a bullet character (•, -, *, a digit
    followed by '.', etc.) — if it does, line N+1 is probably a new
    list item, not a continuation
  - Line N+1 does NOT start with an all-caps word (likely a new
    section header, e.g. "PROJECTS")

This is intentionally conservative — better to under-flag (miss a few
real breaks) than over-flag (merge things that should stay separate).
You'll be reviewing the output, so err toward caution.

Usage:
    python flag_broken_lines.py path/to/resume.pdf
"""

import re
import sys

from extract_text import extract_text

SENTENCE_ENDINGS = (".", "!", "?", ":", ";")
BULLET_CHARS = ("•", "-", "*", "◦", "▪")


def looks_like_header(line: str) -> bool:
    words = line.split()
    if not words:
        return False
    if len(words) <= 4 and line.upper() == line and any(c.isalpha() for c in line):
        return True
    return False


def starts_with_bullet_or_number(line: str) -> bool:
    stripped = line.strip()
    if not stripped:
        return False
    if stripped[0] in BULLET_CHARS:
        return True
    if re.match(r"^\d+[\.\)]\s", stripped):
        return True
    return False


def starts_with_all_caps_word(line: str) -> bool:
    words = line.split()
    if not words:
        return False
    first_word = words[0]
    return first_word.isupper() and len(first_word) > 1


EMAIL_PATTERN = re.compile(r"[\w\.-]+@[\w\.-]+\.\w+")
PHONE_PATTERN = re.compile(r"[\+\d][\d\-\s\(\)]{7,}\d")
URL_PATTERN = re.compile(r"(https?://|www\.)")

KNOWN_SECTION_HEADERS = {
    "education", "experience", "work experience", "projects",
    "personal projects", "technical skills", "skills", "certifications",
    "certification", "achievements", "awards", "publications", "summary",
    "objective", "profile", "extracurricular", "extracurricular activities",
    "languages", "interests", "hobbies", "references", "contact",
    "personal details", "coursework", "relevant coursework", "training",
    "internship", "internships", "volunteer experience", "leadership",
    "activities", "contact information",
}

CONNECTOR_WORDS = {"and", "of", "the", "&", "for", "in", "to", "a", "an", "or"}


def looks_like_contact_info(line: str) -> bool:
    stripped = line.strip()
    return bool(
        EMAIL_PATTERN.search(stripped)
        or PHONE_PATTERN.search(stripped)
        or URL_PATTERN.search(stripped)
    )


def is_known_section_header(line: str) -> bool:
    normalized = line.strip().rstrip(":").lower()
    return normalized in KNOWN_SECTION_HEADERS


def looks_like_label_or_header(line: str) -> bool:
    """
    Generalized structural check for header/category-label lines that
    AREN'T in the known whitelist — e.g. "Languages & Core Tools",
    "Frameworks & Libraries". These share a fingerprint: short, mostly
    Title Case, no internal comma, no lowercase continuation words.

    Deliberately requires a HIGH title-case ratio and excludes commas,
    since real sentence continuations (e.g. "Random Forest, achieving")
    often have one capitalized proper noun but also lowercase words
    and commas — this keeps those correctly unflagged as labels.
    """
    stripped = line.strip().rstrip(":")
    if not stripped or "," in stripped:
        return False

    words = stripped.split()
    if not words or len(words) > 6:
        return False

    non_connector_words = [
        w for w in words if w.lower().strip("&") not in CONNECTOR_WORDS and w != "&"
    ]
    if not non_connector_words:
        return False

    capitalized = sum(1 for w in non_connector_words if w[0].isupper())
    ratio = capitalized / len(non_connector_words)
    return ratio >= 0.8


LABELED_FIELD_PATTERN = re.compile(r"^[A-Za-z][A-Za-z\s&/]{0,40}:\s*\S")


def is_labeled_field(line: str) -> bool:
    """
    Detects "Label: value, value, value" lines — e.g.
    "Languages: Python, Java, C++" or "Frameworks & Libraries: TensorFlow,
    PyTorch". These are structurally complete fields on their own, even
    though they contain commas and don't end in sentence punctuation —
    the colon after a short label is the structural signal, not the
    ending character.
    """
    stripped = line.strip()
    match = LABELED_FIELD_PATTERN.match(stripped)
    if not match:
        return False
    label_part = stripped.split(":", 1)[0]
    # keep the label part short — a long colon-containing sentence
    # ("Note: this approach worked because...") shouldn't match
    return len(label_part.split()) <= 6


def is_likely_broken(current_line: str, next_line: str) -> tuple[bool, str]:
    """Returns (flagged: bool, reason: str)."""
    current = current_line.strip()
    nxt = next_line.strip()

    if not current or not nxt:
        return False, ""

    if current.endswith(SENTENCE_ENDINGS) or current.endswith(BULLET_CHARS):
        return False, "line ends with punctuation/bullet"

    if looks_like_header(current):
        return False, "line looks like a section header (all-caps)"

    if is_known_section_header(current):
        return False, "current line is a known section header"

    if is_known_section_header(nxt):
        return False, "next line is a known section header"

    if is_labeled_field(current):
        return False, "current line is a labeled field (Label: value)"

    if is_labeled_field(nxt):
        return False, "next line is a labeled field (Label: value), likely a new category"

    if looks_like_label_or_header(current):
        return False, "current line looks like a header/category label"

    if looks_like_label_or_header(nxt):
        return False, "next line looks like a header/category label"

    if starts_with_bullet_or_number(nxt):
        return False, "next line starts a new bullet/numbered item"

    if starts_with_all_caps_word(nxt):
        return False, "next line starts with an all-caps word (likely header)"

    if looks_like_contact_info(nxt) or looks_like_contact_info(current):
        return False, "current or next line looks like contact info (email/phone/URL), not sentence continuation"

    return True, "no ending punctuation, next line looks like continuation"


def diagnose(file_path: str) -> None:
    raw_text = extract_text(file_path)
    lines = raw_text.split("\n")

    flagged_count = 0
    print(f"{'#':<4} LINE")
    print("-" * 90)

    for i in range(len(lines) - 1):
        current, nxt = lines[i], lines[i + 1]
        flagged, reason = is_likely_broken(current, nxt)
        marker = " <-- FLAGGED (candidate broken line)" if flagged else ""
        print(f"{i:<4} {current!r}{marker}")
        if flagged:
            flagged_count += 1
            print(f"     -> would join with line {i+1}: {nxt!r}")
            print(f"     -> reason: {reason}")

    # print final line (loop above only goes to len-1)
    if lines:
        print(f"{len(lines)-1:<4} {lines[-1]!r}")

    print("-" * 90)
    print(f"Total lines: {len(lines)}")
    print(f"Flagged as likely broken: {flagged_count}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python flag_broken_lines.py <path_to_resume>")
        sys.exit(1)

    diagnose(sys.argv[1])