# Variable validation: SCE core public microdata (G-P2 Phase 1)

## Verification status legend

| Tag | Meaning |
| - | - |
| **RAW-P1** | Checked in this Phase 1 session against downloaded raw workbooks (see `outputs/generated/`) |
| **DOC-P1** | Checked in this session against the official questionnaire or FAQ |
| **ADJ** | Reported as checked (raw or documentation) in the October 2026 adjudication report. **Not re-verified here** |
| **BK** | Working assumption from background knowledge of the SCE. **Unverified** |
| **PENDING** | Cannot be checked until raw files or the questionnaire are retrieved |

**Session status.** `www.newyorkfed.org` was blocked by this session's egress policy (HTTP 403 at
the proxy, logged 2026-10-09 ~09:53–10:28 UTC). Neither the workbooks nor the questionnaire PDF
could be retrieved. **No RAW-P1 or DOC-P1 tags can be assigned yet.** Every substantive statement
below is ADJ or BK. The code (`code/02_build_panel.py`) runs each check as soon as the files
are present.

## 1. Identifiers, dates, design variables

| Variable | Role | Expected content | Status | Check implemented |
| - | - | - | - | - |
| `userid` | person identifier | Stable respondent ID within and across releases | ADJ (exists) | uniqueness of `userid`×month; cross-file overlap agreement (`cross_file_overlap.csv`) |
| `date` | survey month | Integer `YYYYMM` | ADJ (exists); format BK | `parse_date`; unparseable dates excluded at step S1 |
| `weight` | survey weight | Cross-sectional respondent weight | ADJ (exists) | used only for weighted descriptive means; models unweighted |
| `tenure` | panel position | Months the respondent has been in the panel (BK). Panel is rotating, up to ~12 months (ADJ) | ADJ (exists); meaning BK | quantiles in `panel_length.csv`; compare with observed month count |

## 2. Employment status and eligibility

| Variable | Expected wording (BK, to verify verbatim) | Status |
| - | - | - |
| `Q10_1` … `Q10_10` | "Which of the following best describes your current employment situation? (check all that apply)": 1 full-time, 2 part-time, 3 not working but would like to work, 4 temporarily laid off, 5 sick or other leave, 6 disabled, 7 retired, 8 student, 9 homemaker, 10 other | ADJ (`Q10_1` onward exist); categories BK |
| `Q11` | Number of jobs currently held (asked of workers) | ADJ (exists); wording BK |
| `Q12new` | Works for someone else (1) vs self-employed (2) | ADJ (exists); codes BK |

**Phase 1 eligibility rule** (`code/sce_common.py`):

* *Employed* means `Q10_1 == 1` or `Q10_2 == 1`. Multiple ticks are allowed and flagged
  (`multi_status`), e.g. a full-time worker who is also a student.
* *Main sample* additionally requires `Q12new == 1` (works for someone else). Reason: the job-loss
  item asks about losing one's job. For the self-employed that is a different event, and routing
  may skip them. This is a substantive choice. Report the self-employed separately once routing
  is known.
* Sensitivity: `Q10_5` (sick or other leave) is counted as employed in the NY Fed labour charts
  (search result: SCE labour chart glossary). It is excluded from the main sample and kept as a
  sensitivity flag.

**Routing verification (data-driven).** `routing_by_group.csv` reports the answer rate of
`Q11, Q12new, Q13new, Q22new, Q30new` for mutually exclusive employment groups. Expected pattern
(BK): `Q13new` and `Q22new` answered by working employees, blank for non-workers; `Q30new` asked
of everyone. Any departure (e.g. self-employed answering `Q13new`, non-workers answering
`Q22new`) is a routing finding to reconcile with the questionnaire. `validation_flags.json`
encodes pass/fail thresholds (answer rate > 90% for eligible employees; < 5% for non-workers).
These thresholds are screening rules, not survey facts. Status: **PENDING**.

## 3. Core probability variables

| Variable | Construct | Horizon / conditioning | Scale | Status |
| - | - | - | - | - |
| `Q13new` | Percent chance of **losing main job** | next **12 months** | 0–100 percent chance | ADJ (exists; horizon from questionnaire) |
| `Q22new` | Percent chance of **finding a job one would accept** (pay and type of work considered), **conditional on losing the main job this month** | within the following **3 months** | 0–100 | ADJ (exists; horizon and conditioning from questionnaire) |
| `Q30new` | Percent chance of **not being able to make a minimum debt payment** | next **3 months** | 0–100 | ADJ (exists; horizon from questionnaire) |

Points to verify verbatim from the questionnaire (all **PENDING**):

1. Exact wording, including whether `Q13new` refers to the "main job" and whether `Q22new` says
   "acceptable" or "would accept".
2. Universe of `Q30new`. The adjudication notes that the questionnaire "does not make every
   respondent a confirmed borrower". Respondents without debt may answer 0, or may be routed out.
   Check for a "no debt" filter question or instruction. If none exists, zeros mix "no debt"
   with "certain to pay". This is the most important interpretive issue for the outcome.
3. **Q22 routing change in August 2013** (ADJ). Determine what changed (universe? wording?), and
   whether pre-August-2013 `Q22new` values are comparable or should be dropped.
   `q22_routing_by_month.csv` shows the monthly answer rate among eligible employees, so a
   break would be visible.
4. Whether the "new" suffix marks a re-worded version replacing an older item (BK). Check whether
   older-named columns (e.g. `Q13`, `Q22`) appear in any release.

## 4. Missing-value codes and valid ranges

* Valid range: **[0, 100]**. Non-numeric entries and values outside the range are set to missing
  and counted (`invalid_and_missing.csv`). Sentinel codes such as -99, 999 or 9999 would be caught
  by this rule. Their presence would itself be a finding.
* Blank cells are treated as item non-response or a routing skip, not as invalid. The routing
  table separates the two.
* `heaping.csv` reports the share of answers at exactly 0, 50 and 100, at multiples of 5 and 10,
  and non-integer answers. Mass at 50 is a known "epistemic uncertainty" response in probability
  questions (BK). It must be shown, not cleaned away.
* **PENDING**: whether the public file uses blanks only, or explicit codes for "don't know" and
  refusal.

## 5. Harmonisation across releases

Releases (ADJ: file names; coverage per the adjudication audit):

| Release key | File | Coverage reported by adjudication |
| - | - | - |
| `2013_2016` | `frbny-sce-public-microdata-complete-13-16.xlsx` | 56,444 rows; 8,735 IDs; 43 months, 2013-06 to 2016-12 |
| `2017_2019` | `frbny-sce-public-microdata-complete-17-19.xlsx` | not downloaded in adjudication |
| `2020_2024` | `frbny-sce-public-microdata-20-24.xlsx` | not downloaded in adjudication |
| `latest` | `frbny-sce-public-microdata-latest.xlsx` | 10,559 rows; 2,159 IDs; 2025-01 to 2025-10 |

Implemented checks: column names lower-cased; header row found by locating `userid`, with the
preamble (licence text) kept in `file_schema.csv`; presence and answer share of every variable
by file (`file_schema.csv`); means and medians by file (`cross_file_consistency.csv`); identical
`userid`×month keys across files, with value agreement (`cross_file_overlap.csv`). On overlap the
historical "complete" file is kept, and the overlap count is reported at audit step S2.

## 6. Constructs and prohibited interpretations

* `finding_difficulty = 100 − Q22new`: a reported conditional difficulty, **not** an expected
  unemployment duration.
* An interaction `Q13new × finding_difficulty` (centred in models) is an **index**. It is **never**
  the probability of a 3-month income interruption. Horizons differ (12 months vs 3 months after a
  hypothetical loss "this month"), and the two answers are not a joint distribution.
* `Q30new` is a **subjective expectation**. No realised delinquency is observed in the core file
  (ADJ).
