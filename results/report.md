# Test Run Report
Compiled 2 runs across 2 tests. 2 passed, 0 failed.

## Coverage

- 2 of 20 tests have at least one graded run.
- 2 test(s) have only one run: A1, A2. Two or three runs per test is recommended, since agents vary between runs.
- **Not tested at all:** A3, B1, B2, B3, C1, C2, C3, D1, D2, D3, E1, E2, E3, E4, F1, F2, F3, F4.

## Where the agent is weakest

Average score by dimension, across all graded runs:

| Dimension | Average | Runs scoring 1 or 2 |
|---|---|---|
| accuracy | 4.5 | 0 |
| compliance | 4.0 | 0 |
| voice_tone | 4.0 | 0 |
| structure | 5.0 | 0 |
| instruction_following | 4.5 | 0 |

Weakest dimension: **compliance** (4.0 average).

Pass rate by category:

| Category | Passed | Runs |
|---|---|---|
| Baseline Draft Generation | 2 | 2 |

---

# Run-by-run detail

## A1 run 1: PASS (overall 4.2)
- The output did not include the RFQ Questions 1–9 from the solicitation and instead inserted placeholders: 'Note: The RFP references Questions 1–9 but does not include them in the provided text. To maintain compliance, I will add placeholders.'
- Multiple placeholders remain for required proposal content (e.g., '[NEED: names of proposed analysts]', '[NEED: examples of prior policy analysis work]', '[NEED: process improvement credential summary]'), indicating the agent deferred filling critical compliance details rather than requesting missing attachments.

_Well-structured, mostly compliant draft that preserves placeholders rather than inventing specifics; missing solicitation Questions 1–9 and several required staff/past-performance details prevent a complete compliance assessment._

## A2 run 1: PASS (overall 4.6)

_Clear, concise outline and executive summary; assumptions are listed as requested and the output avoids fabricating missing solicitation details._
