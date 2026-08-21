#!/usr/bin/env python3
"""Check that this harness is set up correctly and tell you what to do next.

Run this first, and any time something seems wrong:

    python check_setup.py

It checks your Python version, that the project folder is complete, that your
config files are valid, and -- most importantly -- that your output files are
named correctly. Badly named output files are the number one problem people hit,
because the grading tools silently skip them.

Every problem it reports comes with the fix. It changes nothing on disk.
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

OK, WARN, BAD = "[ OK ]", "[WARN]", "[FAIL]"

problems = []   # things that will stop the harness working
warnings = []   # things worth knowing but not blocking


def say(status, message, detail=None):
    print(f"{status} {message}")
    if detail:
        for line in detail.splitlines():
            print(f"       {line}")


def fail(message, fix):
    problems.append((message, fix))
    say(BAD, message, fix)


def warn(message, detail):
    warnings.append((message, detail))
    say(WARN, message, detail)


# --------------------------------------------------------------------------
# 1. Python version
# --------------------------------------------------------------------------

def check_python():
    major, minor = sys.version_info[:2]
    if (major, minor) >= (3, 10):
        say(OK, f"Python {major}.{minor} (needs 3.10 or newer)")
    else:
        fail(
            f"Python {major}.{minor} is too old. This harness needs 3.10 or newer.",
            "Go to python.org/downloads and install the current version.\n"
            "On the FIRST installer screen, tick 'Add Python to PATH'.\n"
            "Then close VS Code completely and reopen it.",
        )


# --------------------------------------------------------------------------
# 2. Folder is complete
# --------------------------------------------------------------------------

REQUIRED_FILES = [
    "AGENTS.md",
    "README.md",
    "tests/test_cases.json",
    "grader/grading_prompt.md",
    "scripts/prepare_grading.py",
    "scripts/compile_results.py",
    "materials/README.md",
    "materials/01_RFP_DOT-ORM-2026-R-0147.md",
]
REQUIRED_DIRS = ["tests", "grader", "scripts", "materials", "outputs", "grades", "grading", "results"]


def check_layout():
    missing = [f for f in REQUIRED_FILES if not (ROOT / f).exists()]
    if missing:
        fail(
            f"{len(missing)} required file(s) missing: {', '.join(missing)}",
            "Your copy of the project folder is incomplete.\n"
            "Re-extract the original zip, or re-download the folder, and try again.",
        )
    else:
        say(OK, "All required files are present")

    created = []
    for d in REQUIRED_DIRS:
        path = ROOT / d
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
            created.append(d)
    if created:
        say(OK, f"Created missing working folder(s): {', '.join(created)}")


# --------------------------------------------------------------------------
# 3. Config files are valid JSON
# --------------------------------------------------------------------------

def check_test_cases():
    path = ROOT / "tests" / "test_cases.json"
    if not path.exists():
        return None
    try:
        suite = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(
            f"tests/test_cases.json is not valid JSON (line {exc.lineno})",
            "Someone edited it and broke the formatting.\n"
            "Usually a missing comma, an extra comma before a closing bracket,\n"
            "or curly 'smart quotes' pasted in from Word.\n"
            "Restore this file from the original zip.",
        )
        return None
    say(OK, f"Test suite loaded: {len(suite['tests'])} tests")
    return suite


def check_grading_context(suite):
    path = ROOT / "tests" / "grading_context.json"
    if not path.exists():
        warn(
            "tests/grading_context.json not found",
            "Optional, but without it the grader cannot check whether the agent\n"
            "caught the errors planted in the test materials.\n"
            "The shipped version of this file covers every seeded test. If you\n"
            "deleted it, restore it from the original zip.",
        )
        return
    try:
        ctx = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(
            f"tests/grading_context.json is not valid JSON (line {exc.lineno})",
            "Check for a missing comma between entries, a comma after the LAST\n"
            "entry (not allowed in JSON), or curly quotes pasted from Word.\n"
            "Tip: ask the VS Code chat assistant to fix the formatting for you.",
        )
        return
    if suite:
        known = {t["id"] for t in suite["tests"]}
        unknown = [k for k in ctx if not k.startswith("_") and k not in known]
        if unknown:
            warn(
                f"grading_context.json mentions unknown test ID(s): {', '.join(unknown)}",
                "These entries will be ignored. Check for a typo in the test ID.",
            )
    real = [k for k in ctx if not k.startswith("_")]
    say(OK, f"Grading context loaded: notes for {len(real)} test(s)")


# --------------------------------------------------------------------------
# 4. Materials
# --------------------------------------------------------------------------

def check_materials():
    path = ROOT / "materials"
    docs = sorted(p.name for p in path.glob("*.md")) if path.exists() else []
    if not docs:
        fail(
            "No test materials found in materials/",
            "17 of the 20 tests need documents to attach. Without them you can\n"
            "only run A2, C2, and F2.\n"
            "Re-extract the original zip to restore the materials folder.",
        )
        return
    say(OK, f"Test materials present: {len(docs)} documents")

    answer_key = path / "SEEDED_ERRORS_ANSWER_KEY.md"
    if answer_key.exists():
        say(OK, "Answer key present (never attach this one to a test)")


# --------------------------------------------------------------------------
# 5. Output file names -- the big one
# --------------------------------------------------------------------------

GOOD_NAME = re.compile(r"^([A-F]\d+)_run(\d+)\.md$")
# Files that legitimately live in outputs/ without being agent answers.
IGNORED_IN_OUTPUTS = {".gitkeep", "readme.txt", "readme.md", ".ds_store", "thumbs.db"}


def diagnose_name(name: str, known_ids: set):
    """Classify a filename.

    Returns None if it is fine, or a (severity, explanation) pair where
    severity is "fail" (the file is ignored entirely) or "warn" (it works, but
    is ambiguous or unclear).
    """
    if GOOD_NAME.match(name):
        stem = GOOD_NAME.match(name).group(1)
        if known_ids and stem not in known_ids:
            return ("fail", f"'{stem}' is not a test ID in tests/test_cases.json")
        return None

    # Accepted by prepare_grading.py, which treats a bare ID as run 1.
    bare = re.match(r"^([A-F]\d+)\.md$", name)
    if bare:
        if known_ids and bare.group(1) not in known_ids:
            return ("fail", f"'{bare.group(1)}' is not a test ID in tests/test_cases.json")
        return ("warn", "no run number, so it is treated as run 1. "
                        f"Rename to {bare.group(1)}_run1.md to be unambiguous")

    if not name.lower().endswith(".md"):
        return ("fail", "does not end in .md (Windows may be hiding a .txt ending)")
    if " " in name:
        return ("fail", "contains a space -- use an underscore instead")
    if re.match(r"^[a-f]\d+_run\d+\.md$", name):
        return ("fail", "test ID must be a CAPITAL letter, e.g. A1 not a1")
    if re.search(r"_RUN\d+\.md$", name, re.I) and not re.search(r"_run\d+\.md$", name):
        return ("fail", "'run' must be lowercase, e.g. A1_run1.md")
    if re.match(r"^[A-F]\d+[-. ]run", name, re.I):
        return ("fail", "use an underscore before 'run', e.g. A1_run1.md")
    if re.match(r"^[G-Zg-z]\d+", name):
        return ("fail", "test IDs start with a letter A to F "
                        "(A baseline, B compliance, C grounding, D voice, "
                        "E refinement, F stress tests)")
    return ("fail", "does not match the required pattern <TEST_ID>_run<NUMBER>.md")


def check_outputs(suite):
    path = ROOT / "outputs"
    known = {t["id"] for t in suite["tests"]} if suite else set()
    files = sorted(p for p in path.iterdir() if p.is_file()) if path.exists() else []
    # Placeholder and helper files that ship in the folder are not agent outputs.
    files = [f for f in files if f.name.lower() not in IGNORED_IN_OUTPUTS]

    if not files:
        say(WARN, "No agent outputs saved yet in outputs/")
        print("       That is fine if you have not run a test yet.")
        print("       Save each answer as outputs/<TEST_ID>_run<NUMBER>.md")
        print("       for example: outputs/A1_run1.md")
        return 0

    good, bad = [], []
    for f in files:
        verdict = diagnose_name(f.name, known)
        if verdict is None:
            good.append((f.name, None))
        elif verdict[0] == "warn":
            good.append((f.name, verdict[1]))
        else:
            bad.append((f.name, verdict[1]))

    if good:
        say(OK, f"{len(good)} output file(s) the grader will read")
        by_test = {}
        for name, note in good:
            m = GOOD_NAME.match(name) or re.match(r"^([A-F]\d+)\.md$", name)
            by_test.setdefault(m.group(1), []).append(name)
            if note:
                warn(f"outputs/{name}: {note}", "It still works, just name it explicitly.")
        print(f"       tests covered: {', '.join(sorted(by_test))}")
        thin = [t for t, runs in by_test.items() if len(runs) < 2]
        if thin:
            print(f"       only one run so far for: {', '.join(sorted(thin))}")
            print("       (2-3 runs per test is recommended; agents vary between runs)")

    for name, why in bad:
        fail(
            f"outputs/{name} will be SKIPPED -- {why}",
            "Rename it to the pattern <TEST_ID>_run<NUMBER>.md\n"
            "Correct examples: A1_run1.md   B2_run3.md   F3_run1.md",
        )

    # empty files
    for f in files:
        if f.stat().st_size == 0:
            fail(f"outputs/{f.name} is empty",
                 "Paste the agent's answer into it and save, or delete the file.")

    return len(good)


# --------------------------------------------------------------------------
# 6. Grades and results
# --------------------------------------------------------------------------

def check_grades():
    path = ROOT / "grades"
    files = [p for p in path.glob("*.json")] if path.exists() else []
    valid = [p for p in files if re.match(r"^[A-F]\d+_run\d+\.json$", p.name)]
    broken = []
    for p in valid:
        try:
            json.loads(p.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            broken.append(p.name)
    for name in broken:
        fail(f"grades/{name} is not valid JSON",
             "The grading assistant probably wrapped it in ``` code fences.\n"
             "Open the file and delete any line containing ```")
    if valid and not broken:
        say(OK, f"{len(valid)} grade file(s) present and readable")
    return len(valid) - len(broken)


# --------------------------------------------------------------------------

def next_steps(n_outputs, n_grades):
    print()
    print("-" * 70)
    if problems:
        print(f"FOUND {len(problems)} PROBLEM(S) TO FIX")
        print()
        print("Fix the [FAIL] items above, then run this again:")
        print("    python check_setup.py")
        print()
        print("If you are stuck, paste this whole output into the VS Code chat")
        print("panel and ask: 'How do I fix this?'")
        return 1

    print("SETUP IS GOOD.")
    print()
    if n_outputs == 0:
        print("NEXT STEP: run your first test.")
        print()
        print("  1. Open materials/README.md to see which documents to attach")
        print("     for the test you want to run.")
        print("  2. Open tests/test_cases.json and copy the 'prompt' text.")
        print("  3. Start a BRAND NEW chat with the proposal agent, attach the")
        print("     documents, paste the prompt, and send.")
        print("  4. Save the whole answer as outputs/A1_run1.md")
        print("  5. Run this check again to confirm the file name is right.")
    elif n_grades == 0:
        print(f"NEXT STEP: grade your {n_outputs} saved output(s).")
        print()
        print("  Open the Copilot chat panel in VS Code, set the dropdown to")
        print("  'Agent', and send exactly this:")
        print()
        print("      Read AGENTS.md, then grade all outputs and summarize the results.")
    else:
        print(f"You have {n_outputs} output(s) and {n_grades} grade(s).")
        print()
        print("  To rebuild the scoreboard:   python scripts/compile_results.py")
        print("  Then read:                   results/report.md")
        print()
        print("  Anything marked SECURITY FLAG goes to the team lead immediately.")

    if warnings:
        print()
        print(f"({len(warnings)} warning(s) above -- not blocking, but worth reading.)")
    return 0


def main() -> int:
    print("=" * 70)
    print("  Proposal Agent Test Harness -- setup check")
    print("=" * 70)
    print()
    print(f"Project folder: {ROOT}")
    print()

    check_python()
    check_layout()
    suite = check_test_cases()
    check_grading_context(suite)
    check_materials()
    print()
    n_outputs = check_outputs(suite)
    n_grades = check_grades()

    return next_steps(n_outputs, n_grades)


if __name__ == "__main__":
    sys.exit(main())
