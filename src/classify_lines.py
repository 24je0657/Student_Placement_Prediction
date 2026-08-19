"""
Line Role Classifier (context-aware)
----------------------------------------
Classifies every extracted line into a structural role. Unlike the
first version, this is now a STATEFUL pass — role depends not just on
the line's own text, but on:
  - position in the document (first line = NAME)
  - whether we're still in the header zone (before the first section)
  - which section we're currently inside (Projects vs Education etc.)
  - whether the previous line was blank/header (start of a new block)
    vs. mid-block (likely a wrapped continuation)

This does NOT join anything — still a pure labeling/validation pass.

Roles:
    NAME              - first non-blank line in the whole document
    CONTACT_INFO       - in the header zone (before first section header)
    SECTION_HEADER      - known section name or all-caps short line
    LABELED_FIELD       - "Label: value, value" structure
    BULLET_START        - starts with a bullet marker or number
    NEW_CLAUSE_START    - starts with an action verb or degree keyword
    PROJECT_TITLE        - first line of a new block inside a Projects
                          section, not matching any of the above
    CATEGORY_LABEL       - short, Title Case, starts a new block
                          (elsewhere, not inside Projects)
    CONTINUATION        - default: wrapped continuation of the previous
                          line (including label-like fragments found
                          MID-block, e.g. "Algorithms." after a bullet
                          wrap)

Usage:
    python classify_lines.py path/to/resume.pdf
    python classify_lines.py path/to/resume.docx
"""

import sys
from collections import Counter

from extract_text import extract_text
from flag_broken_lines import (
    looks_like_contact_info,
    looks_like_header,
    is_known_section_header,
    is_labeled_field,
    looks_like_label_or_header,
    starts_with_bullet_or_number,
)

ACTION_VERBS = {
    "built", "designed", "developed", "implemented", "trained", "created",
    "managed", "led", "achieved", "performed", "conducted", "addressed",
    "deployed", "automated", "analyzed", "engineered", "optimized",
    "integrated", "collaborated", "presented", "reduced", "improved",
    "increased", "decreased", "generated", "established", "coordinated",
    "executed", "delivered", "maintained", "configured", "utilized",
    "applied", "constructed", "devised", "enhanced", "evaluated",
    "facilitated", "formulated", "founded", "initiated", "launched",
    "organized", "pioneered", "planned", "produced", "programmed",
    "researched", "resolved", "spearheaded", "streamlined", "supervised",
    "tested", "wrote", "fine-tuned", "authored", "architected",
}

DEGREE_KEYWORDS = {
    "bachelor", "bachelors", "master", "masters", "b.tech", "m.tech",
    "b.e", "m.e", "b.sc", "m.sc", "mba", "phd", "diploma", "b.a", "m.a",
    "b.tech.", "m.tech.",
}


def looks_like_project_title_content(line: str) -> bool:
    """
    Content-based signal for 'this line is a new project title', usable
    even when no blank line preceded it (which we now know doesn't
    reliably survive PDF extraction). Two signals:
      - a pipe character ("Title | Tech, Stack, Here") — pipes almost
        never appear in a wrapped bullet continuation
      - a high title-case ratio, WITHOUT excluding lines that contain a
        comma (unlike CATEGORY_LABEL's check) — project titles commonly
        list technologies after the title, e.g. "..., Node.js, MongoDB"
    """
    stripped = line.strip()
    if not stripped:
        return False
    if "|" in stripped:
        return True

    words = [
        w for w in stripped.split()
        if w.lower().strip("&,") not in CONNECTOR_WORDS_FOR_TITLES and w != "&"
    ]
    if len(words) < 3:
        return False  # too short to trust a ratio-based signal alone
    capitalized = sum(1 for w in words if w[0].isupper())
    return (capitalized / len(words)) >= 0.7


CONNECTOR_WORDS_FOR_TITLES = {"and", "of", "the", "for", "in", "to", "a", "an", "or"}


def is_new_clause_start(line: str) -> bool:
    stripped = line.strip()
    if not stripped:
        return False
    first_word = stripped.split()[0].strip(".,:;()").lower()
    return first_word in ACTION_VERBS or first_word in DEGREE_KEYWORDS


def normalize_section_name(line: str) -> str:
    return line.strip().rstrip(":").lower()


def classify_lines_stateful(lines: list[str]) -> list[tuple[str, str]]:
    """
    Single forward pass over all lines, carrying state:
      - seen_name: has the NAME line already been assigned?
      - in_header_zone: are we still before the first section header?
      - current_section: normalized text of the most recent section header
      - prev_role: role of the previous non-blank line (used to detect
        "start of a new block" vs "mid-block continuation")
    """
    results = []
    seen_name = False
    in_header_zone = True
    current_section = ""
    prev_role = None

    for line in lines:
        stripped = line.strip()

        if not stripped:
            results.append(("BLANK", ""))
            prev_role = "BLANK"
            continue

        block_start = prev_role in (None, "BLANK", "SECTION_HEADER")

        # 1. First non-blank line in the whole document -> NAME
        if not seen_name:
            seen_name = True
            results.append(("NAME", "first non-blank line in document"))
            prev_role = "NAME"
            continue

        # 2. Section header check (always run — ends the header zone,
        #    and updates which section we're currently inside)
        if looks_like_header(stripped) or is_known_section_header(stripped):
            current_section = normalize_section_name(stripped)
            in_header_zone = False
            results.append(("SECTION_HEADER", "matched header pattern or known section name"))
            prev_role = "SECTION_HEADER"
            continue

        # 3. Still in the header zone (before first section) -> contact info
        if in_header_zone:
            results.append(("CONTACT_INFO", "in header zone (before first section header)"))
            prev_role = "CONTACT_INFO"
            continue

        # 4. Labeled field ("Label: value, value")
        if is_labeled_field(stripped):
            results.append(("LABELED_FIELD", "matched 'Label: value' pattern"))
            prev_role = "LABELED_FIELD"
            continue

        # 5. Bullet start
        if starts_with_bullet_or_number(stripped):
            results.append(("BULLET_START", "starts with bullet marker or number"))
            prev_role = "BULLET_START"
            continue

        # 6. New clause start (action verb / degree keyword)
        if is_new_clause_start(stripped):
            results.append(("NEW_CLAUSE_START", "starts with an action verb or degree keyword"))
            prev_role = "NEW_CLAUSE_START"
            continue

        # 7. Context-dependent: project title / category label / continuation
        is_label_like = looks_like_label_or_header(stripped)
        in_wrap_context = prev_role in ("BULLET_START", "CONTINUATION")

        if "project" in current_section and (
            block_start or (in_wrap_context and looks_like_project_title_content(stripped))
        ):
            role, reason = "PROJECT_TITLE", "new project title (blank-line boundary or content signal: pipe/title-case)"
        elif is_label_like and in_wrap_context:
            role, reason = "CONTINUATION", "label-like but follows an active bullet wrap (likely a wrapped fragment)"
        elif is_label_like:
            role, reason = "CATEGORY_LABEL", "short, Title Case, standalone label"
        else:
            role, reason = "CONTINUATION", "no structural marker found (default)"

        results.append((role, reason))
        prev_role = role

    return results


def diagnose(file_path: str) -> None:
    raw_text = extract_text(file_path)
    lines = raw_text.split("\n")
    classified = classify_lines_stateful(lines)

    role_counts = Counter()
    print(f"{'#':<4} {'ROLE':<18} LINE")
    print("-" * 100)
    for i, (line, (role, reason)) in enumerate(zip(lines, classified)):
        role_counts[role] += 1
        print(f"{i:<4} {role:<18} {line!r}")

    print("-" * 100)
    print("Role counts:")
    for role, count in role_counts.most_common():
        print(f"  {role:<18} {count}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python classify_lines.py <path_to_resume>")
        sys.exit(1)

    diagnose(sys.argv[1])