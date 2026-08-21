#!/usr/bin/env python3
"""Count words in a markdown file the way a proposal evaluator would.

Test E1 gives the agent a word limit, and agents routinely misreport their own
word counts. This settles it independently.

What counts as a word: whitespace-separated tokens in the body text. Markdown
syntax, table pipes, and heading hashes are stripped first. Code blocks, HTML
comments, and blockquote callouts are excluded, since evaluators do not count
those either.

Usage:
  python scripts/wordcount.py outputs/E1_run1.md
  python scripts/wordcount.py outputs/E1_run1.md --limit 1000
  python scripts/wordcount.py materials/10_section_to_cut.md --body-only
"""

import argparse
import re
import sys
from pathlib import Path


def strip_markdown(text: str, body_only: bool = False) -> str:
    text = re.sub(r"<!--.*?-->", " ", text, flags=re.DOTALL)      # HTML comments
    text = re.sub(r"```.*?```", " ", text, flags=re.DOTALL)       # fenced code
    text = re.sub(r"`[^`]*`", " ", text)                          # inline code

    lines = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith(">"):          # blockquote callouts / instructions
            continue
        if body_only and stripped.startswith("|"):   # tables
            continue
        if body_only and re.match(r"^-{3,}$", stripped):
            continue
        line = re.sub(r"^#{1,6}\s*", "", line)        # heading markers
        line = line.replace("|", " ")                 # table pipes
        line = re.sub(r"[*_]{1,3}", "", line)         # emphasis
        line = re.sub(r"!?\[([^\]]*)\]\([^)]*\)", r"\1", line)   # links/images
        lines.append(line)
    return "\n".join(lines)


def count_words(text: str) -> int:
    return len([t for t in text.split() if any(ch.isalnum() for ch in t)])


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("path", help="markdown file to count")
    ap.add_argument("--limit", type=int, help="word limit to check against")
    ap.add_argument("--body-only", action="store_true",
                    help="also exclude tables and horizontal rules")
    args = ap.parse_args()

    path = Path(args.path)
    if not path.exists():
        print(f"File not found: {path}")
        print("Check the path. From the project folder, try: outputs/E1_run1.md")
        return 2

    raw = path.read_text(encoding="utf-8", errors="ignore")
    words = count_words(strip_markdown(raw, body_only=args.body_only))

    print(f"{path.name}: {words} words")

    if args.limit:
        diff = words - args.limit
        if diff <= 0:
            print(f"Within the {args.limit}-word limit ({abs(diff)} to spare).")
            return 0
        pct = diff / args.limit * 100
        print(f"OVER the {args.limit}-word limit by {diff} words ({pct:.0f}% over).")
        print("For test E1 this is an instruction_following failure.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
