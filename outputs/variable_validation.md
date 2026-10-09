# Variable validation: SCE core public microdata (G-P2 Phase 1)

## Verification status legend

| Tag | Meaning |
| - | - |
| **RAW-P1** | Checked in Phase 1 against the downloaded raw workbooks (retrieved 2026-10-09; hashes in `outputs/generated/download_manifest.csv`; tables in `outputs/generated/`) |
| **DOC-P1** | Checked in Phase 1 against the official core questionnaire PDF (retrieved 2026-10-09, © 2013-2024, `Last-Modified` 2024-02-09) or the SCE FAQ |
| **ADJ** | Reported in the October 2026 adjudication report. **Not re-verified here** |
| **BK** | Working assumption from background knowledge. **Unverified** |
| **OPEN** | Checked, but not settled; needs a decision or further evidence |

**Caveat on the questionnaire.** The PDF is the current version of the core questionnaire. Its
routing notes include dated changes (e.g. "as of August 2013"). It does not give a full
version history, so wording and routing in earlier months are checked against the data
patterns rather than assumed from the PDF.

## 1. Identifiers, dates, design variables

| Variable | Finding | Status |
| - | - | - |
| `userid` | Present and non-missing in every row of all four files. No duplicate userid×month keys, within or across files. 24,592 distinct IDs. 3,432 IDs appear in two adjacent files (respondents straddling a file boundary), with consecutive months, so IDs are stable across releases | RAW-P1 |
| `date` | Integer `YYYYMM` in every row; all rows parse (audit step S1 drops 0 rows) | RAW-P1 |
| `weight` | Present in all files; non-missing in 99.9–100% of rows. Used only for weighted descriptive means; models unweighted | RAW-P1 (meaning: ADJ/BK) |
| `tenure` | Present in all files; values 1–16. It **counts completed surveys, not calendar months**: in 12 of the traced histories the month gap is 2+ while `tenure` rises by 1. Within the analysis sample, tenure quantiles 10/50/90% are 1/5/11 | RAW-P1 |

**Panel length.** The FAQ (DOC-P1) says respondents stay "for up to twelve months". In the data,
31% of persons are observed for exactly 12 months and 16% only once. **774 persons (3.1%) appear
for 13–16 months**, and the provider's own `tenure` agrees with the observed count for them.
This is a property of the provider data, not a merge error. (`panel_length.csv`)

## 2. Employment status and eligibility

| Variable | Verified content | Status |
| - | - | - |
| `Q10_1` … `Q10_10` | "What is your current employment situation?" Instruction H7 "Please select all that apply." 1 Working full-time (for someone or self-employed); 2 Working part-time (for someone or self-employed); 3 Not working, but would like to work; 4 Temporarily laid off; 5 On sick or other leave; 6 Permanently disabled or unable to work; 7 Retiree or early retiree; 8 Student, at school or in training; 9 Homemaker; 10 Other. Error E8 forbids ticking a "working" option together with option 3 | DOC-P1 |
| `Q10_*` coding | **0/1 in every row** (not blank/1). 82 rows have no box ticked | RAW-P1 |
| `Q11` | Asked if Q10 includes 1, 2, 4 or 5: "Altogether, how many jobs do you have…". Mostly 1–3. There is a tail of implausible job counts (about 1,000 rows above 5, e.g. 122 rows = 40, 21 rows = 30), probably hours typed into the jobs box. These do not affect eligibility, only whether the item text said "main" or "current". `Q11 = 0` occurs in 1,387 employed rows | DOC-P1, RAW-P1 |
| `Q12new` | Asked if Q11 > 0: "In your [current/main] job, do you work for someone else or are you self-employed?" | DOC-P1 |
| `Q12new` codes | **1 = work for someone else, 2 = self-employed.** The questionnaire lists the options in that order but gives no numeric codes. The coding is confirmed by routing: rows with `Q12new = 2` never answer Q13new or Q22new, exactly as the questionnaire's "NOT self-employed" filter requires | RAW-P1 + DOC-P1 |
| `Q12new` availability | **Blank in every row of 2013-06 and 2013-07** (2,450 rows). The field begins 2013-08 | RAW-P1 |

**Phase 1 eligibility rule** (`code/sce_common.py`, unchanged):

* *Employed* means `Q10_1 == 1` or `Q10_2 == 1`.
* *Main sample* additionally requires `Q12new == 1`.
* **Consequence (RAW-P1): the main sample starts in 2013-08.** In 2013-06/07, employment type
  is unknown, so employees cannot be separated from the self-employed.
* The questionnaire universe for Q13new and Q22new (DOC-P1) is wider than the main sample.
  It is: Q10 includes 1, 2, 4 **or 5**; Q12new not self-employed; Q11 > 0. Temporarily
  laid-off (Q10_4) and on-leave (Q10_5) respondents are therefore asked Q13new/Q22new when they
  report a job. The data show this: about 70% and 62% of those groups answer them. The main
  sample excludes them by design (sensitivity only).

## 3. Survey routing (data vs questionnaire)

From `outputs/generated/routing_by_group.csv` (all de-duplicated rows; groups mutually
exclusive, priority order):

| Group | Rows | Q11 | Q12new | Q13new | Q22new | Q30new | Consistent with questionnaire? |
| - | - | - | - | - | - | - | - |
| employed, works for someone else | 108,588 | 100% | 100% | 99.85% | 99.86% | 99.86% | Yes (E1 is a soft prompt, so ~0.15% skips are expected) |
| employed, self-employed | 14,257 | 100% | 100% | 0% | 0% | 99.87% | Yes (Q13new, Q22new filtered on "NOT self-employed") |
| employed, Q12new missing | 3,063 | 98% | 0% | 47% | 54% | 99% | Yes. 1,621 rows are 2013-06/07 (Q12new not yet fielded); 1,372 of the rest have Q11 = 0, which routes out Q12new/Q13new/Q22new |
| sick/other leave only | 857 | 100% | 69% | 62% | 62% | 100% | Yes (code 5 is in the Q13/Q22 universe) |
| temporarily laid off | 1,059 | 100% | 79% | 70% | 70% | 99.7% | Yes (code 4 is in the universe) |
| not working, would like to work | 6,580 | 0% | 0% | 0% | 0% | 99.8% | Yes |
| retired | 37,263 | 0% | 0% | 0% | 0% | 99.9% | Yes |
| other not employed | 14,911 | 0% | 0% | 0% | 0% | 99.8% | Yes |
| Q10 nothing ticked | 82 | 0% | 0% | 0% | 0% | 44% | Yes (break-off or skipped Q10) |

**Q22 routing change "as of August 2013" (DOC-P1, now resolved).** The questionnaire's Q22new
filter reads: "if Q12new does NOT equal 'self-employed' (as of August 2013) AND if Q10 includes
codes 1,2,4 or 5 and Q11 ne 0". So the change is that **the self-employed stopped being asked
Q22new from August 2013**. Before that, Q22new was asked of all workers. In 2013-06/07, 98% of
employed rows answer Q22new but only 88% answer Q13new. That fits the self-employed being asked
Q22new but not Q13new in those months (a data pattern consistent with the routing note, since
Q12new itself is missing then). Because the main sample starts in 2013-08, **the change does not
affect the main sample**. Among eligible employees, the monthly answer rate for all three items
is 98.6–100% in every month from 2013-08 to 2025-10, with no break
(`q22_routing_by_month.csv`).

## 4. Core probability variables

| Variable | Verbatim wording (DOC-P1) | Universe (DOC-P1) |
| - | - | - |
| `Q13new` | "What do you think is the percent chance that you will lose your [main/current] job during the next 12 months?" | Q10 includes 1, 2, 4 or 5 AND Q12new not self-employed AND Q11 > 0 |
| `Q22new` | "Suppose you were to lose your [main] job this month. What do you think is the percent chance that within the following 3 months, you will find a job that you will accept, considering the pay and type of work?" | As Q13new, with the self-employed filter dated "as of August 2013" |
| `Q30new` | "What do you think is the percent chance that, over the next 3 months, you will NOT be able to make one of your debt payments (that is, the minimum required payments on credit and retail cards, auto loans, student loans, mortgages, or any other debt you may have)?" | **Everyone.** No filter and no "no debt" option |

All three use instruction H2 (box or 0–100 ruler) and soft prompt E1 ("Please provide an answer
even if you are not sure").

**Q30new universe (DOC-P1 + RAW-P1): OPEN as an interpretation problem, settled as a fact.**
Q30new is asked of all respondents, with no debt filter. Every employment group with a valid Q10
answers it at 99.5–100%. The wording ("any other debt you may have") does not
exclude respondents without debt, and nothing routes them out. The core file has no debt-holding variable. So **a 0 mixes "no
debt" with "certain to pay"**. Among analysis rows, 31.7–38.6% of Q30new answers are exactly 0,
depending on the file. This is the most important measurement caveat for the outcome. Options
for Phase 2: a sensitivity excluding persons who always answer 0, or a link to the SCE Credit
Access module (separate release; IDs and timing unverified).

**Ranges and codes (RAW-P1).** All three items lie in [0, 100] in every file. **Zero**
non-numeric or out-of-range entries were found (`invalid_and_missing.csv`), so the public file
uses blanks only, with no sentinel codes. 5–6 analysis values per item are non-integers. Missing
shares among employees are 0.14–0.16%.

**Heaping (RAW-P1, `heaping.csv`, analysis rows).**

| Item | = 0 | = 50 | = 100 | multiple of 10 | multiple of 5 |
| - | - | - | - | - | - |
| Q13new | 18–21% | 4–5% | ≤ 1% | 47–57% | 64–76% |
| Q22new | 3–5% | 10–12% | 8–9% | 56–66% | 71–84% |
| Q30new | 32–39% | 2–3% | 1–2% | 52–64% | 63–77% |

Ranges are across the four files. Rounding falls over time: the share at multiples of 5
declines from the 2013–16 file to the 2020+ files for all three items.

**"new" suffix.** No columns named `q13`, `q22` or `q30` appear in any file (RAW-P1), so
there is no older-named version to harmonise.

## 5. Harmonisation across releases (RAW-P1)

* Variable names are identical across the four files, except for 9 added columns from 2020 on
  (`q1a`, `q1apart2`, `q9new2_*`), none of which are used.
* No overlapping userid×month keys, so the "prefer complete file" rule never fires.
* Means in the analysis sample by file (`cross_file_consistency.csv`):

| File | Rows | Persons | mean Q13 | mean Q22 | mean Q30 | median Q30 |
| - | - | - | - | - | - | - |
| 2013–16 | 31,118 | 5,301 | 14.9 | 52.3 | 12.4 | 2 |
| 2017–19 | 27,527 | 4,659 | 13.9 | 59.0 | 11.5 | 2 |
| 2020–24 | 43,376 | 6,364 | 12.5 | 56.0 | 10.3 | 2 |
| latest (2025) | 6,367 | 1,386 | 14.5 | 51.1 | 12.6 | 3 |

  Differences are moderate and move with the business cycle (see `desc_by_year.csv`). There is
  no level break that would suggest a coding change between files.

## 6. Person-history trace (50 persons; automated checks + reading)

`data/derived/person_histories_for_manual_review.csv` (microdata; not committed) holds 50
persons (379 rows). They are stratified by file × employment-transition × Q22 missingness ×
Q30 endpoint use, then topped up at random. Automated checks on all 379 rows found:

* 0 employee rows missing Q13new or Q22new;
* 0 self-employed, retired or not-working rows with Q13new or Q22new;
* 0 differences between the raw and cleaned values;
* 0 analysis-flag errors (flagged with missing core items, or eligible but unflagged);
* 0 rows with both "working" and "not working, would like to work" ticked (E8 is enforced).

Reading the histories showed:

* plausible employment transitions, e.g. employee → on leave (Q12new switches to 2) → employee
  → not employed, with Q13/Q22 appearing and disappearing exactly as routing implies;
* the `tenure` step behaviour noted in §1;
* noisy responders: 2 of 37 analysis persons flip Q13new or Q22new between 0 and 100 from one
  month to the next.

**This review was done by the AI assistant, not by the researcher.** Therefore
`manual_history_review_done` stays **false** in `validation_flags.json` until the researcher
traces the histories personally.

## 7. Constructs and prohibited interpretations (unchanged)

* `finding_difficulty = 100 − Q22new`: a reported conditional difficulty, **not** an expected
  unemployment duration.
* An interaction `Q13new × finding_difficulty` (centred in models) is an **index**. It is **never**
  the probability of a 3-month income interruption. Horizons differ (12 months vs 3 months
  after a hypothetical loss "this month"; DOC-P1), and the two answers are not a joint
  distribution.
* `Q30new` is a **subjective expectation** asked of everyone, borrowers or not. No realised
  delinquency is observed in the core file (RAW-P1: column list).
