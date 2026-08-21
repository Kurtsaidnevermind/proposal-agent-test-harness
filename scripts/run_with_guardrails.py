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

from scripts.guardrail_wrapper import wrap_prompt


def main(argv=None):
    argv = argv or sys.argv[1:]
    if not argv:
        print("Usage: run_with_guardrails.py <input_prompt> [output_file]")
        return 2
    inp = Path(argv[0]).read_text(encoding='utf-8')
    wrapped = wrap_prompt(inp)
    if len(argv) > 1:
        Path(argv[1]).write_text(wrapped, encoding='utf-8')
        print(f"Wrote wrapped prompt to {argv[1]}")
    else:
        sys.stdout.write(wrapped)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
