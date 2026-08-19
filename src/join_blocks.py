"""
Stage 2: Block-Aware Joiner
------------------------------
Takes the line roles from classify_lines.py and actually joins
CONTINUATION lines back into their parent block — turning:

    PROJECT_TITLE     "AI-Powered E-Commerce Platform | React, Node.js"
    BULLET_START       "- Built a full-stack e-commerce platform"
    CONTINUATION       "with a recommendation engine"
    BULLET_START       "- Deployed using Docker and"
    CONTINUATION       "AWS"

into:

    PROJECT_TITLE     "AI-Powered E-Commerce Platform | React, Node.js"
    BULLET            "Built a full-stack e-commerce platform with a
                        recommendation engine"
    BULLET            "Deployed using Docker and AWS"

Design rule: a CONTINUATION line merges into whatever block is
currently open, UNLESS that open block is a SECTION_HEADER. Headers
never absorb continuation text into themselves — this is the fix for
the "education layout" case identified during classifier validation
(e.g. "Education" followed by "Indian Institute of Technology, Delhi"
should NOT become one merged block "Education Indian Institute of
Technology, Delhi"). Instead, that continuation becomes its own
standalone block under the header.

This does whitespace/unicode normalization on the final joined text
too (previously validated separately in diagnose_stage2.py), since
there's no reason to keep that as a separate pass once we're already
touching every line.

Usage:
    python clean_text.py path/to/resume.pdf
    python clean_text.py path/to/resume.docx
"""

import sys
import unicodedata

from extract_text import extract_text
from classify_lines import classify_lines_stateful

# Roles that should NEVER have a CONTINUATION line merged into them.
# A continuation right after one of these becomes its own new block
# instead of being glued onto it.
NON_ABSORBING_ROLES = {"SECTION_HEADER"}


def normalize_text(text: str) -> str:
    """Same conservative normalization validated in diagnose_stage2.py:
    unicode NFKC + whitespace collapse. Applied once, on the fully
    joined block text, not per raw line."""
    normalized = unicodedata.normalize("NFKC", text)
    return " ".join(normalized.split())


def join_blocks(lines: list[str]) -> list[dict]:
    """
    Returns a list of blocks: [{"role": ..., "text": ...}, ...]
    BLANK lines are dropped entirely (they carry no content).
    """
    roles = classify_lines_stateful(lines)
    blocks = []
    current = None  # {"role": ..., "parts": [...]}

    for line, (role, _reason) in zip(lines, roles):
        stripped = line.strip()

        if role == "BLANK":
            continue

        if role == "CONTINUATION" and current is not None and current["role"] not in NON_ABSORBING_ROLES:
            current["parts"].append(stripped)
            continue

        # Otherwise: this line starts a NEW block (either it's a
        # non-CONTINUATION role, or it's a CONTINUATION with nowhere
        # valid to attach to — e.g. right after a SECTION_HEADER).
        if current is not None:
            blocks.append({
                "role": current["role"],
                "text": normalize_text(" ".join(current["parts"])),
            })
        current = {"role": role, "parts": [stripped]}

    if current is not None:
        blocks.append({
            "role": current["role"],
            "text": normalize_text(" ".join(current["parts"])),
        })

    return blocks


def clean(file_path: str) -> None:
    raw_text = extract_text(file_path)
    lines = raw_text.split("\n")
    blocks = join_blocks(lines)

    print(f"{'ROLE':<16} TEXT")
    print("-" * 100)
    for block in blocks:
        print(f"{block['role']:<16} {block['text']}")

    print("-" * 100)
    print(f"Raw lines: {len(lines)}  ->  Joined blocks: {len(blocks)}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python clean_text.py <path_to_resume>")
        sys.exit(1)

    clean(sys.argv[1])