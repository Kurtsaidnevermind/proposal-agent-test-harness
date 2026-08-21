# Proposal Agent Test Harness

Automated grading for a Copilot proposal-drafting agent — **no admin access, no
IT install, no API keys**. Your VS Code coding agent (GitHub Copilot agent mode)
does the grading with its own loaded model; `AGENTS.md` tells it exactly how.

**New here and not a coder?** Read [GETTING_STARTED.md](GETTING_STARTED.md)
instead. It assumes no technical background and walks through every step.

## Start here

```bash
python check_setup.py
```

That one command checks your Python version, confirms the folder is complete,
validates the config files, and tells you what to do next. Run it first, and any
time something looks wrong. It changes nothing.

## How it works

1. **You run test prompts** against your Copilot agent. The prompts live in
   `tests/test_cases.json`; the documents to attach live in `materials/`.
2. **You save each output** in `outputs/` as `<TEST_ID>_run<N>.md` (e.g.
   `C1_run1.md`).
3. **Your coding agent grades everything.** `prepare_grading.py` builds one
   filled evaluation prompt per output, the agent scores each against the fixed
   5-dimension rubric and writes a JSON grade, and `compile_results.py`
   validates the JSONs, recomputes pass/fail, and produces `results/scores.csv`
   plus a readable failure report.

The compile step recomputes overall scores and pass/fail itself rather than
trusting the grader's arithmetic, and rejects malformed grades — so results stay
consistent even across different grading models.

## Quickstart (in VS Code)

1. Open this folder in VS Code with Copilot agent mode enabled.
2. Run `python check_setup.py` in the terminal.
3. Open `materials/README.md` to see which documents each test needs.
4. Run a test against your proposal agent and save the answer in `outputs/`.
5. Tell the VS Code agent:

   > Read AGENTS.md, then grade all outputs and summarize the results.

That's the whole workflow. The agent runs the scripts itself. To do it by hand:

```bash
python scripts/prepare_grading.py            # builds grading/*.md
# grade each grading/ file with any model; save JSON to grades/<ID>_run<N>.json
python scripts/compile_results.py            # builds results/scores.csv + report.md
```

Python 3.10+, standard library only. `pytest` is needed only to run the harness
self-tests.

## Test materials are included

`materials/` holds a complete fictional bid package — a 35-requirement RFP, a
capability statement, staffing bios, past performance write-ups, a flawed draft,
an amendment, and more. **17 of the 20 tests need these documents**, so they ship
with the harness rather than being something you assemble yourself.

They contain deliberately planted errors: compliance gaps, numeric
inconsistencies, buried requirements, a Section L vs Section M conflict, and a
prompt-injection line. Every planted error is recorded in
`materials/SEEDED_ERRORS_ANSWER_KEY.md` and pre-loaded into
`tests/grading_context.json`, so the grader can check whether your agent caught
them.

`materials/README.md` lists exactly which files to attach for each test. Two
rules matter most: never attach the answer key, and give test F1 the base RFP
only.

## Useful commands

```bash
python check_setup.py                                # health check + next step
python scripts/prepare_grading.py --regression       # A1 B1 C1 E1 F3 only
python scripts/prepare_grading.py --tests B1 C1 F3   # subset
python scripts/scan_outputs.py                       # advisory scan of outputs/
python -m pytest -q                                  # harness self-tests
```

Three helpers exist so you can check the agent's claims instead of trusting them:

```bash
python scripts/count_requirements.py --list          # the RFP's 35 requirements (test B1)
python scripts/wordcount.py outputs/E1_run1.md --limit 1000   # real word count (test E1)
python scripts/diff_outputs.py materials/11_executive_summary_draft.md \
       outputs/E3_run1.md --section 2                # collateral damage (test E3)
```

Run 2-3 fresh sessions per test (`_run1`, `_run2`, `_run3`) — agents are
non-deterministic, and single runs mislead.

## Sharing it with the team

```bash
python make_zip.py
```

Builds `proposal-agent-test-harness.zip`, the file `GETTING_STARTED.md` tells new
users to expect. It ships a clean slate (no outputs, grades, or results) and
refuses to build if a required file is missing. Use `--with-results` to include
the current score history.

Prefer the zip over a git clone for teammates: `AGENTS.md` is excluded by many
developers' global gitignore rules, and without it the harness has no grading
instructions. `make_zip.py` includes it explicitly.

## When IT installs the Copilot Studio Kit

This harness stays useful as your grading layer, and the test set transfers: ask
your coding agent to generate the kit's Excel import spreadsheet from
`tests/test_cases.json`. Keep committing `results/scores.csv` in the meantime so
you have score history to compare against once kit-based runs begin.

## Repository layout

```
check_setup.py              run this first; health check and next step
make_zip.py                 builds the distributable zip for teammates
AGENTS.md                   instructions for the coding agent (it is the grader)
GETTING_STARTED.md          step-by-step guide for non-technical users
README.md                   this file

tests/test_cases.json       the 20-test suite (source of truth)
tests/grading_context.json  what was seeded per test; read by the grader
grader/grading_prompt.md    evaluation template with rubric and score caps
materials/                  documents to attach when running tests
materials/README.md         which files to attach for which test
materials/SEEDED_ERRORS_ANSWER_KEY.md   every planted error (never attach)

scripts/prepare_grading.py  builds one grading prompt per output
scripts/compile_results.py  validates grades, writes scores.csv + report.md
scripts/scan_outputs.py     advisory heuristic scan of outputs/
scripts/count_requirements.py   counts RFP requirements (test B1)
scripts/wordcount.py        independent word count (test E1)
scripts/diff_outputs.py     detects unrequested edits (test E3)
scripts/guardrail_wrapper.py    prepends hardening instructions to a prompt
scripts/run_with_guardrails.py  applies the wrapper to a prompt file

outputs/                    Copilot agent outputs   (<TEST_ID>_run<N>.md)
grading/                    generated grading prompts (consumed by the agent)
grades/                     agent-written grade JSONs (<TEST_ID>_run<N>.json)
results/                    compiled scores.csv + report.md
tests/test_harness.py       self-tests for the harness itself
```
