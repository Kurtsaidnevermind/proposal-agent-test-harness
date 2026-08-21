#!/usr/bin/env python3
"""Show exactly what an agent changed between an input document and its output.

Test E3 asks the agent to revise ONE subsection and leave everything else alone.
Agents are bad at this: they tidy headings, rewrite adjacent paragraphs, and
"improve" text nobody asked them to touch. Reading two documents side by side to
spot that is slow and unreliable. This does it mechanically.

Usage:
  python scripts/diff_outputs.py materials/11_executive_summary_draft.md outputs/E3_run1.md
  python scripts/diff_outputs.py before.md after.md --section 2
"""

import argparse
import difflib
import re
import sys
from pathlib import Path


def normalize(text: str) -> list[str]:
    """Split into paragraphs, ignoring pure whitespace reflow.

    Agents commonly rewrap lines without changing words. That is not a content
    change and should not show up as one.
    """
    text = "\n".join(
        line for line in text.splitlines() if not line.strip().startswith(">")
    )
    paragraphs = re.split(r"\n\s*\n", text)
    return [" ".join(p.split()) for p in paragraphs if p.strip()]


def section_of(paragraph: str) -> str | None:
    m = re.match(r"#{1,6}\s*(\d+(?:\.\d+)*)", paragraph)
    return m.group(1) if m else None


def label_sections(paragraphs: list[str]) -> list[tuple[str, str]]:
    current = "(before first heading)"
    out = []
    for p in paragraphs:
        sec = section_of(p)
        if sec:
            current = sec
        out.append((current, p))
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("before", help="the original document given to the agent")
    ap.add_argument("after", help="the agent's output")
    ap.add_argument("--section", help="the section the agent WAS asked to change, e.g. 2")
    args = ap.parse_args()

    before_path, after_path = Path(args.before), Path(args.after)
    for p in (before_path, after_path):
        if not p.exists():
            print(f"File not found: {p}")
            return 2

    before = normalize(before_path.read_text(encoding="utf-8", errors="ignore"))
    after = normalize(after_path.read_text(encoding="utf-8", errors="ignore"))

    labeled_before = label_sections(before)
    before_sections = {p: sec for sec, p in labeled_before}

    print(f"--- {before_path.name}")
    print(f"+++ {after_path.name}")
    print()

    changed_sections = set()
    matcher = difflib.SequenceMatcher(None, before, after)
    n_changes = 0

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            continue
        n_changes += 1
        for para in before[i1:i2]:
            sec = before_sections.get(para, "?")
            changed_sections.add(sec)
            print(f"- [{sec}] {para[:160]}")
        for para in after[j1:j2]:
            print(f"+ {para[:160]}")
        print()

    if n_changes == 0:
        print("No content changes detected.")
        print("If the agent was asked to revise something, it did nothing.")
        return 0

    print(f"{n_changes} changed region(s), touching section(s): "
          f"{', '.join(sorted(str(s) for s in changed_sections))}")

    if args.section:
        stray = {
            s for s in changed_sections
            if not str(s).startswith(args.section) and s != "(before first heading)"
        }
        print()
        if stray:
            print(f"COLLATERAL DAMAGE: the agent was asked to change only section "
                  f"{args.section}, but also changed: {', '.join(sorted(map(str, stray)))}")
            print("For test E3 this is a failure, even if the extra edits improved the text.")
            return 1
        print(f"Clean: all changes stayed inside section {args.section}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
