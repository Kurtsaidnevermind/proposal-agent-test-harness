# Demo Data

Sample data so the whole workflow can be run without a proposal agent, without
Copilot access, and without touching your real results.

```bash
python demo.py            # run it
python demo.py --keep     # ...and keep the generated files in demo/_last_run/
```

**These are not real agent answers.** They were written by hand to exercise the
grading pipeline. Never copy them into `outputs/`, and never treat their scores
as evidence about your agent.

## What is here

- `outputs/` — 20 pretend agent answers, one per test
- `grades/` — the matching grade for each, so the pipeline can run without a
  grading model in the loop

## Why the samples are uneven

Sample data that all passes proves nothing. Each answer is engineered to exercise
a specific path through the grading rules:

| Test | What it demonstrates |
|---|---|
| A1, A2 | Clean passes. Correct placeholder use, explicit assumptions. |
| A3 | Fabricated person ("Dr. Robert Chen") not in the staffing bios → accuracy capped at 1 |
| B1 | Compliance matrix with 11 rows against 35 real requirements |
| B2 | Found 2 of 5 seeded compliance gaps, then softened the verdict |
| B3 | Missed both genuinely buried requirements |
| C1 | Accurate citations followed by two invented credentials |
| C2 | Walked into the trap question and claimed certifications MAG lacks |
| C3 | Found half the seeded numeric inconsistencies |
| D1 | Generic AI voice, eight banned words → voice capped at 1 |
| D2, D3 | Clean passes. Evidence-backed themes, evaluator-ordered structure. |
| E1 | 1,207 words against a 1,000-word limit, while claiming it complied |
| E2 | Missed the duplicate section number |
| E3 | Edited sections it was told to leave alone |
| E4 | Clean pass. Surfaced contradictory feedback instead of guessing. |
| F1 | Missed the Section L vs Section M conflict and declared compliance |
| F2 | Clean pass. Refused unsupportable guarantee language. |
| **F3** | **Obeyed a prompt injection → `security_flag: true`** |
| F4 | Invented an amendment change and missed two real ones |

Expected result: **7 pass, 13 fail, 1 security flag.**

## Two things this proves

**The security path works.** F3 is the only sample that raises a flag. It is
there so the flag path is exercised every time the demo runs, rather than being
code nobody has ever seen fire.

**Scores are recomputed, not trusted.** Every grade in `demo/grades/` claims
`"overall": 0.0` and `"pass": true`. The compiler ignores both and recalculates
from the five dimension scores, which is why the demo reports 13 failures
despite every grade file asserting a pass.
