#!/usr/bin/env python3
"""Compile grades written by the coding agent into scores.csv and report.md.

Reads grades/<TEST_ID>_run<N>.json, validates each against the schema,
recomputes 'overall' and 'pass' (never trusting the stored values), and
writes results/scores.csv and results/report.md.

Usage:
  python scripts/compile_results.py
"""

import csv
import datetime
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIMS = ["accuracy", "compliance", "voice_tone", "structure", "instruction_following"]


def validate(grade: dict, name: str) -> list[str]:
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


OUTPUT_NAME = re.compile(r"^([A-F]\d+)(?:_run(\d+))?\.md$")
IGNORED_IN_OUTPUTS = {".gitkeep", "readme.txt", "readme.md", ".ds_store", "thumbs.db"}


def find_ungraded(outputs_dir, rows, tests) -> list[str]:
    """Outputs that exist but have no grade.

    Without this, a partly-graded batch reports a healthy-looking pass rate over
    whatever happened to be graded, and silently omits the rest. The number looks
    fine, which makes it worse than an obvious error.
    """
    if not outputs_dir.exists():
        return []
    graded = {(r["test_id"], r["run"]) for r in rows}
    missing = []
    for path in sorted(outputs_dir.iterdir()):
        if not path.is_file() or path.name.lower() in IGNORED_IN_OUTPUTS:
            continue
        m = OUTPUT_NAME.match(path.name)
        if not m or m.group(1) not in tests:
            continue        # bad names are check_setup.py's job to report
        if (m.group(1), int(m.group(2) or 1)) not in graded:
            missing.append(path.name)
    return missing


def archive_scores(results_dir, rows) -> Path:
    """Keep a dated copy of every compiled batch.

    scores.csv is overwritten on each run. Teams working from a shared folder
    have no version control to fall back on, so without this the previous
    batch's numbers are simply gone and score trends cannot be compared.

    Same-day recompiles overwrite that day's file rather than piling up.
    """
    history = results_dir / "history"
    history.mkdir(exist_ok=True)
    stamp = datetime.date.today().isoformat()
    dest = history / f"scores_{stamp}.csv"
    with dest.open("w", newline="", encoding="utf-8-sig") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    return dest


def security_section(flags) -> list[str]:
    """Security flags go at the top. A reader must not have to scroll to find one."""
    if not flags:
        return []
    out = ["## SECURITY FLAGS — READ FIRST", ""]
    out.append(f"{len(flags)} run(s) raised a security flag. This means the agent "
               "followed an instruction hidden inside a source document. Escalate "
               "to the team lead before acting on anything else in this report.")
    out.append("")
    for r in flags:
        out.append(f"- **{r['test_id']} run {r['run']}** ({r['name']}) — see the detail section below.")
    out.append("")
    return out


def coverage_section(ungraded, rows, tests) -> list[str]:
    """Say plainly how much of the suite these numbers actually cover."""
    covered = {r["test_id"] for r in rows}
    out = ["## Coverage", ""]
    out.append(f"- {len(covered)} of {len(tests)} tests have at least one graded run.")
    thin = sorted(t for t in covered if sum(1 for r in rows if r["test_id"] == t) < 2)
    if thin:
        out.append(f"- {len(thin)} test(s) have only one run: {', '.join(thin)}. "
                   "Two or three runs per test is recommended, since agents vary "
                   "between runs.")
    never = sorted(t for t in tests if t not in covered)
    if never:
        out.append(f"- **Not tested at all:** {', '.join(never)}.")
    if ungraded:
        out.append("")
        out.append(f"- **{len(ungraded)} output file(s) have no grade and are NOT "
                   "counted in the totals above:** " + ", ".join(ungraded[:15])
                   + (" ..." if len(ungraded) > 15 else ""))
        out.append("  Until these are graded, the pass rate describes only part of "
                   "your test run.")
    out.append("")
    return out


def patterns_section(rows, tests) -> list[str]:
    """The recurring-failure view a team lead needs, computed rather than eyeballed."""
    if not rows:
        return []
    out = ["## Where the agent is weakest", ""]

    out.append("Average score by dimension, across all graded runs:")
    out.append("")
    out.append("| Dimension | Average | Runs scoring 1 or 2 |")
    out.append("|---|---|---|")
    means = []
    for d in DIMS:
        vals = [r[d] for r in rows]
        mean = sum(vals) / len(vals)
        low = sum(1 for v in vals if v <= 2)
        means.append((mean, d))
        out.append(f"| {d} | {mean:.1f} | {low} |")
    out.append("")
    worst_mean, worst = min(means)
    out.append(f"Weakest dimension: **{worst}** ({worst_mean:.1f} average).")
    out.append("")

    by_cat = {}
    for r in rows:
        c = by_cat.setdefault(r["category"], [0, 0])
        c[0] += 1
        c[1] += 1 if r["pass"] else 0
    out.append("Pass rate by category:")
    out.append("")
    out.append("| Category | Passed | Runs |")
    out.append("|---|---|---|")
    for cat in sorted(by_cat):
        total, passed = by_cat[cat]
        out.append(f"| {cat} | {passed} | {total} |")
    out.append("")

    # A test that fails repeatedly is a real gap; one bad run may be noise.
    repeat = []
    for tid in sorted({r["test_id"] for r in rows}):
        runs = [r for r in rows if r["test_id"] == tid]
        failed = [r for r in runs if not r["pass"]]
        if len(runs) >= 2 and len(failed) >= 2:
            repeat.append(f"{tid} ({len(failed)} of {len(runs)} runs)")
    if repeat:
        out.append("**Failed in more than one run — treat these as real, not noise:** "
                   + ", ".join(repeat))
        out.append("")
    return out


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
        problems = validate(grade, path.name)
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

    archived = archive_scores(results_dir, rows)

    passed_n = sum(1 for r in rows if r["pass"])
    flags = [r for r in rows if r["security_flag"]]
    ungraded = find_ungraded(ROOT / "outputs", rows, tests)

    header = [
        "# Test Run Report",
        f"Compiled {len(rows)} runs across {len({r['test_id'] for r in rows})} tests. "
        f"{passed_n} passed, {len(rows) - passed_n} failed."
        + (f" **{len(flags)} security flag(s).**" if flags else ""),
        "",
    ]
    header += security_section(flags)
    header += coverage_section(ungraded, rows, tests)
    header += patterns_section(rows, tests)
    header += ["---", "", "# Run-by-run detail", ""]

    (results_dir / "report.md").write_text("\n".join(header + report), encoding="utf-8")

    # Console summary. Security first, then anything that makes the numbers
    # mean less than they appear to.
    print()
    if flags:
        # ASCII only: the Windows console is cp1252 and mangles an em dash here.
        print("*** SECURITY FLAG RAISED - escalate before reading anything else ***")
        for r in flags:
            print(f"    {r['test_id']} run {r['run']}: {r['name']}")
        print()
    print(f"{passed_n}/{len(rows)} runs passed.")
    if ungraded:
        print()
        print(f"WARNING: {len(ungraded)} output file(s) have no grade, so they are")
        print("NOT included in the numbers above:")
        for name in ungraded[:10]:
            print(f"  - {name}")
        if len(ungraded) > 10:
            print(f"  ... and {len(ungraded) - 10} more")
        print("Grade them, or the pass rate describes only part of your test run.")
    print()
    print(f"  {results_dir / 'scores.csv'}\n  {results_dir / 'report.md'}")
    print(f"  {archived}")
    print("  (dated copy, so this batch survives the next compile)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
