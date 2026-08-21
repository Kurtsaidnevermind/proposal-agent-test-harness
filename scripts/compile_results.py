#!/usr/bin/env python3
"""Compile grades written by the coding agent into scores.csv and report.md.

Reads grades/<TEST_ID>_run<N>.json, validates each against the schema,
recomputes 'overall' and 'pass' (never trusting the stored values), and
writes results/scores.csv and results/report.md.

Usage:
  python scripts/compile_results.py
"""

import csv
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIMS = ["accuracy", "compliance", "voice_tone", "structure", "instruction_following"]


def validate(grade: dict, test: dict, name: str) -> list[str]:
    problems = []
    scores = grade.get("scores", {})
    for d in DIMS:
        v = scores.get(d)
        if not isinstance(v, int) or not 1 <= v <= 5:
            problems.append(f"{name}: score '{d}' must be an integer 1-5, got {v!r}")
    if not isinstance(grade.get("failures"), list):
        problems.append(f"{name}: 'failures' must be a list")
    if grade.get("security_flag") not in (True, False):
        problems.append(f"{name}: 'security_flag' must be true or false")
    return problems


def main() -> int:
    suite = json.loads((ROOT / "tests" / "test_cases.json").read_text(encoding="utf-8"))
    tests = {t["id"]: t for t in suite["tests"]}
    grades_dir = ROOT / "grades"
    results_dir = ROOT / "results"
    results_dir.mkdir(exist_ok=True)

    pattern = re.compile(r"^([A-F]\d+)_run(\d+)\.json$")
    rows, report, errors = [], [], []

    for path in sorted(grades_dir.iterdir()) if grades_dir.exists() else []:
        m = pattern.match(path.name)
        if not m:
            continue
        test_id, run_n = m.group(1), int(m.group(2))
        test = tests.get(test_id)
        if not test:
            errors.append(f"{path.name}: unknown test id {test_id}")
            continue
        try:
            grade = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"{path.name}: invalid JSON ({exc})")
            continue
        problems = validate(grade, test, path.name)
        if problems:
            errors.extend(problems)
            continue

        scores = grade["scores"]
        overall = round(sum(scores[d] for d in DIMS) / len(DIMS), 1)
        passed = (
            all(scores[d] >= suite["pass_threshold"] for d in test["primary_dimensions"])
            and not grade.get("security_flag", False)
        )
        rows.append({
            "test_id": test_id,
            "run": run_n,
            "category": test["category"],
            "name": test["name"],
            **{d: scores[d] for d in DIMS},
            "overall": overall,
            "pass": passed,
            "security_flag": grade.get("security_flag", False),
            "notes": grade.get("notes", ""),
        })
        status = "PASS" if passed else "FAIL"
        report.append(f"## {test_id} run {run_n}: {status} (overall {overall})")
        if grade.get("security_flag"):
            report.append("**SECURITY FLAG RAISED — escalate this finding.**")
        for f in grade.get("failures", []):
            report.append(f"- {f}")
        report.append(f"\n_{grade.get('notes', '')}_\n")

    if errors:
        print("Validation problems (fix these grade files and rerun):")
        for e in errors:
            print(f"  ! {e}")
    if not rows:
        print("No valid grades found in grades/.")
        return 1

    rows.sort(key=lambda r: (r["test_id"], r["run"]))
    with (results_dir / "scores.csv").open("w", newline="", encoding="utf-8-sig") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    passed_n = sum(1 for r in rows if r["pass"])
    flags = [r for r in rows if r["security_flag"]]
    header = [
        "# Test Run Report",
        f"Compiled {len(rows)} runs across {len({r['test_id'] for r in rows})} tests. "
        f"{passed_n} passed, {len(rows) - passed_n} failed."
        + (f" **{len(flags)} security flag(s).**" if flags else ""),
        "",
    ]
    (results_dir / "report.md").write_text("\n".join(header + report), encoding="utf-8")
    print(f"\n{passed_n}/{len(rows)} runs passed.")
    print(f"  {results_dir / 'scores.csv'}\n  {results_dir / 'report.md'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
