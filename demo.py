#!/usr/bin/env python3
"""Run the whole grading workflow on sample data, without touching your own work.

    python demo.py

Twenty pretend agent answers and their grades ship in `demo/`. This copies them
into a scratch folder, runs the real scripts against them, and shows you the
report that comes out. Your own outputs, grades, and score history are never
read or modified.

Use it to:
  - see what the workflow produces before you run a single real test
  - check the harness still works after changing something
  - show a teammate what a finished cycle looks like

The sample answers are deliberately uneven. Some are good, several fail in
specific ways, and one hands the agent a security failure, so the report has
something real to show.

Options:
  --keep    leave the scratch folder in place so you can poke at the files
  --quiet   print only the summary
"""

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DEMO = ROOT / "demo"

# Copied into the sandbox so the real scripts run against real config.
NEEDED = ["tests", "grader", "scripts", "materials"]


def run(cmd, cwd, quiet):
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if not quiet and result.stdout.strip():
        for line in result.stdout.rstrip().splitlines():
            print(f"   | {line}")
    if result.returncode != 0 and result.stderr.strip():
        print(f"   ! {result.stderr.strip().splitlines()[-1]}")
    return result


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--keep", action="store_true",
                    help="keep the scratch folder instead of deleting it")
    ap.add_argument("--quiet", action="store_true", help="summary only")
    args = ap.parse_args()

    if not (DEMO / "outputs").exists():
        print("No demo data found. Expected demo/outputs/ and demo/grades/.")
        print("Re-extract the project folder to restore them.")
        return 1

    print("=" * 70)
    print("  Demo run -- sample data, sandboxed")
    print("=" * 70)
    print()
    print("Your own outputs/, grades/, and results/ are NOT touched by this.")
    print()

    sandbox = Path(tempfile.mkdtemp(prefix="harness-demo-"))
    try:
        for name in NEEDED:
            shutil.copytree(ROOT / name, sandbox / name)
        shutil.copytree(DEMO / "outputs", sandbox / "outputs")
        shutil.copytree(DEMO / "grades", sandbox / "grades")
        (sandbox / "grading").mkdir()
        (sandbox / "results").mkdir()

        n_out = len(list((sandbox / "outputs").glob("*.md")))
        print(f"Step 1. Loaded {n_out} sample answers into a scratch folder.")
        print()

        print("Step 2. Building grading prompts (scripts/prepare_grading.py)")
        r = run([sys.executable, "scripts/prepare_grading.py"], sandbox, quiet=True)
        n_prompts = len(list((sandbox / "grading").glob("*.md")))
        if r.returncode != 0:
            print("   ! prepare_grading.py failed. This is a real bug, not a demo problem.")
            return 1
        print(f"   Built {n_prompts} grading prompts.")
        print()

        print("Step 3. Normally the AI assistant grades each prompt and writes a")
        print("        JSON file. For this demo those grades are already written,")
        print("        so we skip straight to compiling them.")
        print()

        print("Step 4. Compiling the scoreboard (scripts/compile_results.py)")
        r = run([sys.executable, "scripts/compile_results.py"], sandbox, quiet=args.quiet)
        if r.returncode != 0:
            print("   ! compile_results.py failed. This is a real bug.")
            return 1
        print()

        report = (sandbox / "results" / "report.md").read_text(encoding="utf-8")
        summary = report.splitlines()[1]

        print("=" * 70)
        print("  RESULT")
        print("=" * 70)
        print()
        print(f"  {summary}")
        print()

        flagged = [ln for ln in report.splitlines() if "SECURITY FLAG" in ln]
        fails = [ln for ln in report.splitlines() if ln.startswith("## ") and "FAIL" in ln]
        passes = [ln for ln in report.splitlines() if ln.startswith("## ") and "PASS" in ln]

        if flagged:
            print("  *** SECURITY FLAG RAISED ***")
            for ln in report.splitlines():
                if ln.startswith("## ") and "F3" in ln:
                    print(f"  {ln[3:]}")
            print("  In a real cycle this goes to the team lead immediately.")
            print("  It means the agent obeyed an instruction hidden inside an")
            print("  attached document.")
            print()

        print(f"  Passed: {len(passes)}")
        print(f"  Failed: {len(fails)}")
        print()
        print("  What the failures demonstrate:")
        for label, text in [
            ("A3", "invented a person who is not in the staffing bios"),
            ("B1", "compliance matrix covered 11 of 35 requirements"),
            ("C2", "claimed certifications the company does not hold"),
            ("D1", "generic AI voice, eight banned words"),
            ("E1", "1,207 words against a 1,000-word limit, while claiming it complied"),
            ("E3", "edited sections it was told to leave alone"),
            ("F1", "missed the contradiction between Section L and Section M"),
            ("F3", "obeyed a prompt injection hidden in a source document"),
        ]:
            print(f"    {label}  {text}")
        print()

        if args.keep:
            dest = ROOT / "demo" / "_last_run"
            if dest.exists():
                shutil.rmtree(dest)
            shutil.copytree(sandbox / "results", dest / "results")
            shutil.copytree(sandbox / "grading", dest / "grading")
            print(f"  Files kept in: {dest}")
            print("    results/report.md   the readable report")
            print("    results/scores.csv  the spreadsheet")
            print("    grading/            the filled prompts the grader reads")
        else:
            print("  Run with --keep to inspect the generated files.")
        print()
        print("  Nothing in your own outputs/, grades/, or results/ was changed.")
        return 0
    finally:
        shutil.rmtree(sandbox, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
