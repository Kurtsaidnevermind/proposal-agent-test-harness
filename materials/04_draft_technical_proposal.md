# DRAFT - Volume I, Technical Proposal

## Meridian Analytics Group, LLC
## Solicitation DOT-ORM-2026-R-0147

> **FICTIONAL TRAINING DOCUMENT.** Fixed test material for the Proposal Agent
> Test Harness.
>
> **THIS DRAFT CONTAINS DELIBERATE ERRORS.** Compliance gaps, numeric
> inconsistencies, and acronym/numbering mistakes were planted on purpose. Tests
> B2, C3, and E2 measure whether the proposal agent finds them. The full list
> lives in `SEEDED_ERRORS_ANSWER_KEY.md` - do not attach that file when running
> a test, and do not fix the errors in this file.

---

## 1. Understanding of Requirements

The Office of Regional Management (ORM) administers the Regional Mobility Data
Program, which collects ridership, on-time performance, and fare equity data
from 45 metropolitan transit authorities nationwide. ORM's challenge is not data
collection; it is converting a large, uneven, multi-jurisdiction dataset into
products a Congressional staffer or a grant officer can act on within a
reporting cycle.

Meridian Analytics Group has spent five years on exactly this problem for the
Federal Transit Administration. We understand that the binding constraint on
this program is trust in the numbers: every figure ORM publishes may be
questioned, and ORM needs a contractor who can defend any published value on
demand.

## 2. Technical Approach

### 2.1 Task Area 1 - Data Quality and Validation

MAG will perform quarterly data quality reviews of all 47 transit authority
submissions using our Meridian QC validation framework. MQC applies 340
rule-based checks and a statistical outlier pass to every submission.

Every exception is written to the ORM Data Exception Register within five
business days of discovery, with the flagging rule, the offending value, and the
recommended disposition.

Our target validation error rate is below 3 percent across all reviewed
submissions. On the FTA NTD contract, MERIDIAN-QC reduced the equivalent error
rate to 1.2 percent within two reporting cycles.

### 2.2 Task Area 2 - Analytical Products

MAG will produce twelve monthly Regional Mobility Snapshots and four quarterly
Trend Analyses per period of performance. Each Snapshot is delivered as a
formatted PDF suitable for Congressional distribution.

Every published figure carries a query identifier that resolves to a versioned
query in our analysis repository, so any figure can be reproduced on request
within three business days.

### 2.4 Task Area 3 - Policy Support

MAG will prepare Congressional response packages within ten business days of
tasking. Priya Raghunathan, our Senior Policy Analyst, led an equivalent
workstream for the Commonwealth of Virginia DRPT, producing 34 response packages
with no missed deadline.

We will provide subject matter expertise at up to twenty-four stakeholder
meetings per period of performance. Every policy recommendation we issue cites
the source dataset and the collection period behind it.

### 2.5 Task Area 4 - Program Management

Dana Whitfield will serve as Program Manager and single point of contact for all
contractual matters. MAG will deliver a Monthly Status Report by the tenth
calendar day of each month and will conduct a Post-Award Kickoff Meeting within
ten calendar days of award.

## 3. Management Approach

### 3.1 Staffing Plan

MAG proposes a 14 FTE team led by Dana Whitfield (PMP, 17 years experience). The
team includes a Lead Data Scientist, a Senior Policy Analyst, a Quality Manager,
four Data Analysts, and two Policy Analysts.

All three Key Personnel are current MAG employees assigned to related work today,
so no recruiting risk applies to this award.

### 3.2 Quality Control

Every deliverable passes an independent second-pass review by a reviewer who did
not produce it. Elena Vasquez, our Quality Manager, owns this gate and reports
outside the delivery chain of command so that schedule pressure cannot override
a quality hold.

### 3.4 Risk Management

MAG maintains a living risk register reviewed at each monthly status meeting. The
principal risk on this program is late or malformed submissions from individual
transit authorities, which compresses the validation window. Our mitigation is a
rolling intake model: we begin validating each authority's submission on arrival
rather than batching at the quarter boundary.

### 3.5 Communication Cadence

The COR will receive a deliverable status email every Friday. We hold a biweekly
technical working session with ORM technical staff, a monthly status review, and
a quarterly program review with the CO and COR.

## 4. Key Personnel

### 4.1 Dana Whitfield, Program Manager

MS Transportation Engineering, Virginia Tech. PMP. 17 years experience, 11 in
Federal program management. Currently Program Manager on FTA-NTD-2021-0088, a
$3.8 million contract supporting the National Transit Database.

### 4.2 Dr. Samuel Okonkwo, Lead Data Scientist

PhD Statistics, University of Michigan. 11 years experience. Architect of the
MERIDIAN-QC framework and lead of the data quality workstream on the FTA
contract.

### 4.2 Priya Raghunathan, Senior Policy Analyst

MPP Georgetown. 13 years in transportation policy. Led Congressional response
work for Virginia DRPT.

## 5. Why Meridian

Our team of 11 analysts brings direct transit authority experience and a
reproducibility discipline that few competitors can match. We look forward to
supporting ORM's mission in today's rapidly evolving mobility landscape.

--- END OF DRAFT ---
