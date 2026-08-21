#!/usr/bin/env python3
"""Count requirement statements in an RFP so test B1 can be graded objectively.

Test B1 asks the agent to build a compliance matrix covering every "shall",
"must", "will", and "required" statement. To grade that, you need to know the
real number. This counts them the same way every time.

The default target is the harness RFP. Point it at your own RFP with a path.

Usage:
  python scripts/count_requirements.py
  python scripts/count_requirements.py --list
  python scripts/count_requirements.py path/to/your_rfp.md --list
"""

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_RFP = ROOT / "materials" / "01_RFP_DOT-ORM-2026-R-0147.md"

# A requirement sentence contains one of these obligation words.
SENTENCE_RE = re.compile(
    r"[^.\n]*\b(?:shall|must|will be required|is required|are required)\b[^.]*\.",
    re.IGNORECASE,
)


def load_body(path: Path) -> str:
    """Read the document, dropping blockquote callouts (test-harness notes)."""
    lines = [
        line for line in path.read_text(encoding="utf-8", errors="ignore").splitlines()
        if not line.strip().startswith(">")
    ]
    return "\n".join(lines)


def find_requirements(text: str) -> list[str]:
    return [" ".join(m.split()) for m in SENTENCE_RE.findall(text)]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("path", nargs="?", default=str(DEFAULT_RFP),
                    help="RFP file to scan (defaults to the harness RFP)")
    ap.add_argument("--list", action="store_true", help="print every statement found")
    args = ap.parse_args()

    path = Path(args.path)
    if not path.exists():
        print(f"File not found: {path}")
        if path == DEFAULT_RFP:
            print("The harness RFP is missing from materials/. Re-extract the project folder.")
        return 2

    reqs = find_requirements(load_body(path))
    print(f"{path.name}: {len(reqs)} requirement statements")

    if args.list:
        print()
        for i, r in enumerate(reqs, 1):
            print(f"{i:3d}. {r[:150]}")

    print()
    print("Record this number in tests/grading_context.json under the B1 entry so")
    print("the grader can check the agent's compliance matrix for completeness.")
    print()
    print("Note: this counts obligation SENTENCES. One sentence can carry more than")
    print("one distinct requirement -- Section L.6 packs five format rules into a")
    print("single paragraph. Treat this as the floor, not the ceiling.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
