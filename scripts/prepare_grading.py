#!/usr/bin/env python3
"""Prepare grading prompts for the coding agent to evaluate with its own model.

Reads agent outputs from outputs/<TEST_ID>_run<N>.md, fills the grading
template for each, and writes grading/<TEST_ID>_run<N>_prompt.md.

The coding agent (VS Code / GitHub Copilot agent mode) then reads each
prompt file, performs the evaluation itself, and writes the resulting JSON
to grades/<TEST_ID>_run<N>.json. No API keys involved.

Usage:
  python scripts/prepare_grading.py                 # all outputs
  python scripts/prepare_grading.py --tests B1 C1   # subset
  python scripts/prepare_grading.py --regression    # A1 B1 C1 E1 F3
"""

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REGRESSION_SET = ["A1", "B1", "C1", "E1", "F3"]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tests", nargs="*")
    ap.add_argument("--regression", action="store_true")
    args = ap.parse_args()

    suite = json.loads((ROOT / "tests" / "test_cases.json").read_text())
    template = (ROOT / "grader" / "grading_prompt.md").read_text().split("---", 1)[1]
    ctx_file = ROOT / "tests" / "grading_context.json"
    contexts = json.loads(ctx_file.read_text()) if ctx_file.exists() else {}

    outputs_dir = ROOT / "outputs"
    grading_dir = ROOT / "grading"
    grading_dir.mkdir(exist_ok=True)
    (ROOT / "grades").mkdir(exist_ok=True)

    wanted = set(REGRESSION_SET) if args.regression else set(args.tests or [])
    tests = {t["id"]: t for t in suite["tests"] if not wanted or t["id"] in wanted}

    made = 0
    for t in tests.values():
        pattern = re.compile(rf"^{re.escape(t['id'])}(_run(\d+))?\.md$")
        for path in sorted(outputs_dir.iterdir()):
            m = pattern.match(path.name)
            if not m:
                continue
            run_n = int(m.group(2) or 1)
            filled = (
                template
                .replace("{TEST_ID}", t["id"])
                .replace("{TEST_NAME}", t["name"])
                .replace("{CATEGORY}", t["category"])
                .replace("{GRADING_CONTEXT}", contexts.get(t["id"], "none recorded"))
                .replace("{TEST_PROMPT}", t["prompt"])
                .replace("{AGENT_OUTPUT}", path.read_text())
                .replace("{WATCH_FOR}", t["watch_for"])
                .replace("{PRIMARY_DIMENSIONS}", ", ".join(t["primary_dimensions"]))
            )
            out = grading_dir / f"{t['id']}_run{run_n}_prompt.md"
            out.write_text(filled)
            made += 1
            print(f"prepared {out.relative_to(ROOT)}")

    if not made:
        print("No matching outputs found in outputs/. Name files <TEST_ID>_run<N>.md")
        return 1
    print(f"\n{made} grading prompt(s) ready in grading/.")
    print("Next: grade each one and save JSON to grades/<TEST_ID>_run<N>.json,")
    print("then run: python scripts/compile_results.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
