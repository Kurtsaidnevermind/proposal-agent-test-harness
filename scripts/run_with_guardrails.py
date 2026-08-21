#!/usr/bin/env python3
"""
Apply the guardrail wrapper to a prompt file and write the wrapped prompt.

Usage:
  python scripts/run_with_guardrails.py prompt.txt wrapped_prompt.txt

If only one argument is provided, prints to stdout.
This helper is intended to be integrated with whatever agent runner you use;
replace the agent's direct prompt input with the wrapped prompt produced by
this script.
"""
import sys
from pathlib import Path

# Allow running this file directly (python scripts/run_with_guardrails.py ...)
# as well as importing it as a module. Without this, Python puts scripts/ on
# sys.path instead of the repo root and the import below fails.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.guardrail_wrapper import wrap_prompt


USAGE = ("Usage: python scripts/run_with_guardrails.py <input_prompt> [output_file]\n"
         "\n"
         "Writes the prompt with guardrail instructions prepended. With no\n"
         "output file, prints to standard output.\n")


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if not argv or argv[0] in ("-h", "--help"):
        print(USAGE)
        return 0 if argv else 2

    src = Path(argv[0])
    if not src.exists():
        # A missing file used to raise a raw traceback at the user.
        print(f"File not found: {src}\n\n{USAGE}")
        return 2

    wrapped = wrap_prompt(src.read_text(encoding='utf-8'))
    if len(argv) > 1:
        Path(argv[1]).write_text(wrapped, encoding='utf-8')
        print(f"Wrote wrapped prompt to {argv[1]}")
    else:
        sys.stdout.write(wrapped)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
