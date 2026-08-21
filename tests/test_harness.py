"""Unit tests for the harness itself.

These test the tools, not the agent under test. A green run here means your
installation works and the scoring maths is correct. It says nothing about how
well the proposal agent performed -- that is what the grading workflow is for.

Run:  python -m pytest -q
"""

import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

DIMS = ["accuracy", "compliance", "voice_tone", "structure", "instruction_following"]
REQUIRED_TEST_FIELDS = [
    "id", "category", "name", "prompt", "requires_attachments",
    "setup_notes", "watch_for", "primary_dimensions",
]


def load_script(name):
    """Import a file from scripts/ without needing it to be a package."""
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def suite():
    return json.loads((ROOT / "tests" / "test_cases.json").read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def compile_results():
    return load_script("compile_results")


# --- the test suite definition is well formed -------------------------------

def test_suite_json_is_valid_and_complete(suite):
    assert suite["pass_threshold"] == 3
    assert suite["rubric_dimensions"] == DIMS
    assert len(suite["tests"]) >= 1
    for t in suite["tests"]:
        for field in REQUIRED_TEST_FIELDS:
            assert field in t, f"test {t.get('id', '?')} is missing '{field}'"


def test_test_ids_are_unique_and_well_formed(suite):
    ids = [t["id"] for t in suite["tests"]]
    assert len(ids) == len(set(ids)), "duplicate test IDs in test_cases.json"
    for tid in ids:
        assert tid[0] in "ABCDEF" and tid[1:].isdigit(), (
            f"test ID {tid!r} must be a category letter A-F followed by a number; "
            "compile_results.py will ignore grades that do not match this shape"
        )


def test_primary_dimensions_are_real_dimensions(suite):
    for t in suite["tests"]:
        assert t["primary_dimensions"], f"{t['id']} has no primary dimensions"
        for d in t["primary_dimensions"]:
            assert d in DIMS, f"{t['id']} names unknown dimension {d!r}"


# --- the grading template lines up with the filler --------------------------

def test_grading_template_has_every_placeholder():
    template = (ROOT / "grader" / "grading_prompt.md").read_text(encoding="utf-8")
    body = template.split("---", 1)
    assert len(body) == 2, (
        "grading_prompt.md must contain a '---' separating the explanation from "
        "the template; prepare_grading.py keeps only what comes after it"
    )
    for placeholder in ["{TEST_ID}", "{TEST_NAME}", "{CATEGORY}", "{GRADING_CONTEXT}",
                        "{TEST_PROMPT}", "{AGENT_OUTPUT}", "{WATCH_FOR}",
                        "{PRIMARY_DIMENSIONS}"]:
        assert placeholder in body[1], f"template lost {placeholder}"


def test_prepare_grading_fills_every_placeholder():
    """End-to-end: a prepared prompt must have no {PLACEHOLDER} left in it."""
    if not list((ROOT / "outputs").glob("A1*.md")):
        pytest.skip("no A1 output present; add outputs/A1_run1.md to cover this")

    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "prepare_grading.py"), "--tests", "A1"],
        capture_output=True, text=True, cwd=ROOT,
    )
    # Do NOT skip on a non-zero exit. An earlier version of this test did, and it
    # hid a real crash: prepare_grading.py read files without an encoding, so on
    # Windows it died on any output containing a curly quote or em dash.
    assert result.returncode == 0, (
        "prepare_grading.py failed on a real output file:\n"
        f"{result.stdout}\n{result.stderr}"
    )
    prepared = ROOT / "grading" / "A1_run1_prompt.md"
    assert prepared.exists(), "prepare_grading.py reported success but wrote nothing"

    text = prepared.read_text(encoding="utf-8")
    leftovers = re.findall(r"\{[A-Z_]+\}", text)
    assert not leftovers, f"unfilled placeholders in prepared prompt: {set(leftovers)}"


def test_scripts_never_read_files_without_an_encoding():
    """Guard against the cp1252 crash class on Windows.

    Python defaults to the locale encoding, which on Windows is cp1252. Agent
    outputs routinely contain curly quotes and em dashes, which cp1252 cannot
    decode, so an unencoded read_text() is a crash waiting to happen.
    """
    offenders = []
    for path in list((ROOT / "scripts").glob("*.py")) + [ROOT / "check_setup.py"]:
        for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if re.search(r"\.read_text\(\s*\)", line) or re.search(r"\.write_text\([^,)]*\)\s*$", line):
                offenders.append(f"{path.name}:{n}: {line.strip()}")
    assert not offenders, (
        "these file operations do not specify encoding='utf-8':\n" + "\n".join(offenders)
    )


# --- grade validation rejects bad input -------------------------------------

def good_grade(**overrides):
    grade = {
        "test_id": "A1",
        "scores": {d: 4 for d in DIMS},
        "overall": 4.0,
        "pass": True,
        "security_flag": False,
        "failures": [],
        "notes": "fine",
    }
    grade.update(overrides)
    return grade


def test_validate_accepts_a_good_grade(compile_results):
    assert compile_results.validate(good_grade(), {}, "A1_run1.json") == []


@pytest.mark.parametrize("bad_score", [0, 6, 3.5, "4", None])
def test_validate_rejects_out_of_range_scores(compile_results, bad_score):
    grade = good_grade()
    grade["scores"]["accuracy"] = bad_score
    problems = compile_results.validate(grade, {}, "A1_run1.json")
    assert problems, f"{bad_score!r} should have been rejected"


def test_validate_rejects_missing_dimension(compile_results):
    grade = good_grade()
    del grade["scores"]["compliance"]
    assert compile_results.validate(grade, {}, "A1_run1.json")


def test_validate_rejects_bad_failures_and_flag(compile_results):
    assert compile_results.validate(good_grade(failures="oops"), {}, "x.json")
    assert compile_results.validate(good_grade(security_flag="yes"), {}, "x.json")


# --- the scoring maths compile_results.py performs --------------------------

def recompute(scores, primary, security_flag, threshold=3):
    """Mirror of the logic in compile_results.main()."""
    overall = round(sum(scores[d] for d in DIMS) / len(DIMS), 1)
    passed = all(scores[d] >= threshold for d in primary) and not security_flag
    return overall, passed


def test_overall_is_the_mean_rounded_to_one_decimal():
    scores = dict(zip(DIMS, [4, 4, 4, 5, 4]))
    assert recompute(scores, ["accuracy"], False)[0] == 4.2


def test_pass_ignores_non_primary_dimensions():
    """A 1 in a dimension this test does not grade on must not fail the run."""
    scores = dict(zip(DIMS, [5, 5, 1, 5, 5]))
    _, passed = recompute(scores, ["accuracy", "compliance"], False)
    assert passed is True


def test_pass_requires_every_primary_dimension_at_threshold():
    scores = dict(zip(DIMS, [5, 2, 5, 5, 5]))
    _, passed = recompute(scores, ["accuracy", "compliance"], False)
    assert passed is False


def test_security_flag_always_fails_the_run():
    """Perfect scores plus a security flag is still a failure."""
    scores = {d: 5 for d in DIMS}
    _, passed = recompute(scores, ["accuracy"], security_flag=True)
    assert passed is False


# --- optional context file, if the user made one ----------------------------

def test_grading_context_is_valid_if_present(suite):
    ctx_file = ROOT / "tests" / "grading_context.json"
    if not ctx_file.exists():
        pytest.skip("tests/grading_context.json not present (it is optional)")
    try:
        ctx = json.loads(ctx_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        pytest.fail(
            f"tests/grading_context.json is not valid JSON: {exc}\n"
            "Most likely a missing comma, a trailing comma, or a curly quote."
        )
    known = {t["id"] for t in suite["tests"]}
    for key in ctx:
        if key.startswith("_"):
            continue  # JSON has no comments; keys like "_comment" are notes to self
        assert key in known, (
            f"grading_context.json mentions {key!r}, which is not a test ID in "
            "tests/test_cases.json. Check for a typo."
        )
