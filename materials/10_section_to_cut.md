# Technical Approach - Task Area 1: Data Quality and Validation

> **FICTIONAL TRAINING DOCUMENT.** Fixed test material for the Proposal Agent
> Test Harness.
>
> This section is deliberately overlong. Test E1 asks the agent to cut it to
> 1,000 words while preserving every requirement traced in the compliance matrix
> at the bottom. Verify the result with:
> `python scripts/wordcount.py outputs/E1_run1.md`

---

## 1. Our Understanding of the Validation Challenge

The Regional Mobility Data Program receives submissions from 47 metropolitan
transit authorities on a quarterly cycle. Those authorities differ enormously in
size, in the maturity of their internal data practices, and in the systems they
use to produce a submission. A large authority may run a modern automated
passenger counting system feeding a governed warehouse. A small authority may
still assemble its submission by hand in a spreadsheet maintained by a single
staff member. The consequence for ORM is that submission quality is not
distributed evenly, and a validation approach that treats all 47 authorities
identically will spend most of its effort in the wrong places.

Meridian Analytics Group has operated a validation function at exactly this scale
for the Federal Transit Administration since 2021, covering more than 700
reporting agencies for the National Transit Database. The lesson from that work
is that validation is not primarily a technical problem. The rule engine is the
easy part. The hard part is the loop between discovering an exception and getting
a corrected value back from the authority that produced it, fast enough that the
person who prepared the submission still remembers what they did. When that loop
is slow, exceptions pile up at the quarter boundary and the program absorbs a
surge it cannot staff for.

## 2. Validation Methodology

Our approach applies the MERIDIAN-QC validation framework, which MAG developed
and has refined across five years of Federal transit data work. MERIDIAN-QC
applies three sequential layers to every submission received.

The first layer is structural validation. Before any values are examined, the
framework confirms that the submission conforms to the expected schema: that all
required fields are present, that data types match specification, that reporting
period identifiers are well formed, and that the file itself is complete and
uncorrupted. Structural failures are returned to the authority immediately, since
no meaningful analysis can proceed on a malformed file, and holding it for
substantive review wastes days.

The second layer is rule-based validation. MERIDIAN-QC applies 340 discrete
rule-based checks derived from the program's reporting manual, from historical
exception patterns, and from the specific business logic of transit operations.
These checks include internal consistency tests, such as confirming that
unlinked passenger trips reconcile against reported boardings, and cross-period
tests, such as confirming that reported vehicle revenue miles have not shifted
implausibly from the prior period without an accompanying service change note.

The third layer is statistical screening. Rule-based checks catch known failure
modes. They do not catch novel ones. Our statistical pass compares each reported
value against that authority's own history and against a peer cohort of
similarly sized systems, flagging values that fall outside expected bounds even
when no explicit rule has been violated. This layer is how we find the errors
nobody anticipated when the rules were written.

## 3. Tools, Data Handling, and Environment

MERIDIAN-QC runs on a PostgreSQL data store with transformation logic managed in
dbt, and the rule and statistical layers implemented in Python using pandas and
Great Expectations. Every rule is expressed as version-controlled code rather
than as configuration held in a spreadsheet or embedded in an analyst's local
workbook, which means the full history of what was checked, when, and why is
recoverable at any point in the contract.

Submissions are ingested directly from the ORM Acquisition Portal and are never
transmitted outside it, consistent with the certification requirement in
Attachment C. Each ingested submission is written to an immutable snapshot before
any transformation occurs, so the original file as received remains available for
comparison for the life of the contract. Analysts work against derived tables and
never against the raw snapshot, which removes an entire class of accidental
overwrite errors that we have seen affect other programs.

Access is role-scoped. Data analysts can read the raw snapshot and write to
derived tables. Only the Lead Data Scientist can modify rule definitions, and
rule changes require a reviewed pull request with a written rationale. The QC
Reviewer has read access across the environment but cannot modify either rules
or derived data, which preserves the independence of the review.

Every published figure is bound to a query identifier that resolves to the exact
versioned query, the input snapshot, and the analyst who ran it. The publication
step rejects any figure that lacks a resolved identifier. This is what allows us
to commit to reproducing any published figure within three business days,
including the underlying query, as required by C.4.4. It is also the direct
answer to the reproducibility problem that ORM has been working to close since
2023.

## 4. Exception Handling and the Correction Loop

Every exception MERIDIAN-QC raises is written to the ORM Data Exception Register
within five business days of discovery. The register entry records the flagging
rule, the offending value, the reporting authority, the analyst who reviewed the
flag, the recommended disposition, and the current status of the correction.

We do not batch exception reporting to the end of the quarter. Under our rolling
intake model, validation begins on each authority's submission the day it
arrives rather than waiting for all 47 to be received. This matters because it
converts a single end-of-quarter surge into a manageable continuous flow, and
because it returns exceptions to authorities while the submission is still fresh
in the preparer's mind. On our current FTA contract, this change alone cut median
correction turnaround from nineteen days to six.

Not every exception is a data error. Some flagged values are correct but unusual,
reflecting a genuine service change, a fare policy shift, or a one-time event.
Our analysts disposition each flag rather than mechanically returning it, because
a validation function that cries wolf trains reporting authorities to ignore it.
Where a flagged value is confirmed correct, we record the confirmation and the
explanation in the register so that the same value is not re-flagged in a
subsequent cycle.

## 5. Quality Control of the Validation Function Itself

A validation function needs its own quality control, or it becomes the
unexamined step in the chain. MAG applies an independent second-pass review to
every validation cycle. Aisha Rahman, our QC Reviewer, samples dispositioned
exceptions and re-adjudicates them without seeing the original analyst's
decision. Disagreement rates above five percent trigger a rule review, on the
theory that persistent analyst disagreement usually indicates an ambiguous rule
rather than a careless analyst.

Elena Vasquez, our Quality Manager, owns this gate and reports outside the
delivery chain of command, to the Chief Analytics Officer rather than to the
Program Manager. That reporting line exists specifically so that schedule
pressure cannot override a quality hold, because the person applying schedule
pressure does not write her performance review.

We commit to maintaining a validation error rate below two percent across all
reviewed submissions, consistent with the performance standard in Attachment B.
On the FTA National Transit Database contract, MERIDIAN-QC reduced the equivalent
error rate from 4.7 percent to 1.2 percent across the first two reporting cycles.
We achieved that by tightening the correction loop, not by loosening the rules.

## 6. Risk and Mitigation

The principal risk to Task Area 1 is late or malformed submissions from
individual authorities, which compress the validation window and push exception
resolution past the quarter boundary. Our mitigation is the rolling intake model
described above, combined with named escalation: authorities that miss the intake
window are escalated to the Contracting Officer's Representative by name at day
ten, rather than being absorbed silently into our own schedule float.

We are candid that this mitigation depends on ORM's willingness to apply pressure
to reporting authorities. Our escalation is a notification, not an enforcement
mechanism. On our FTA contract, four agencies accounted for roughly sixty percent
of all late exceptions in the most recent reporting year. Naming them early is
what allowed the program office to intervene.

A secondary risk is rule drift: as the reporting manual evolves, validation rules
that once matched specification quietly stop matching it. We mitigate this with a
scheduled annual rule reconciliation against the current manual, with results
documented and provided to ORM.

## 7. Staffing for Task Area 1

Task Area 1 is staffed by Dr. Samuel Okonkwo as Lead Data Scientist at 0.4 FTE
allocated to this task area, four Data Analysts at a combined 2.6 FTE, and Aisha
Rahman as QC Reviewer at 0.4 FTE. Dr. Okonkwo architected MERIDIAN-QC and led the
data quality workstream that produced the FTA results cited above.

---

## Compliance Matrix for This Section

Every row below must still be satisfied after any cut. Losing a row is a
compliance failure regardless of how well the shortened version reads.

| # | Requirement | RFP Ref | Where addressed |
|---|---|---|---|
| 1 | Quarterly data quality reviews of all 47 submissions | C.3.1 | Sections 1, 2 |
| 2 | Document every exception in the Data Exception Register within 5 business days | C.3.2 | Section 4 |
| 3 | Maintain validation error rate below 2% | C.3.3 | Section 5 |
| 4 | Described methodology including tools and data handling | M.2.1 | Sections 2, 3 |
| 5 | Worked example from prior performance | M.2.1 | Sections 2, 5, 6 |
| 6 | Quantified quality control mechanism with stated threshold | M.2.1 | Section 5 |
| 7 | Identified risk with specific mitigation | M.2.1 | Section 6 |
| 8 | Staffing by labor category with allocation | M.2.1 | Section 7 |
