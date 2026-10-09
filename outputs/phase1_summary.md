# G-P2 Phase 1 summary: reemployment beliefs and debt-payment distress

**Date:** 2026-10-09. **Scope:** feasibility only; no thesis analysis, no association model.

## What happened

* **First attempt (earlier the same day):** `www.newyorkfed.org` was denied by the session's
  network policy (proxy HTTP 403). The pipeline was built and smoke-tested on a synthetic
  fixture, and the work was committed as unverified.
* **After the environment's network access was changed:**
  * A single test request succeeded (`robots.txt`, HTTP 200).
  * `code/01_download.py` retrieved all four official core microdata workbooks, the core
    questionnaire, the Data Bank page and the FAQ (all HTTP 200; SHA-256 in
    `outputs/generated/download_manifest.csv`).
  * The existing `02_build_panel.py` and `03_descriptives.py` were then run on the real files.
* **Code changes:** small fixes found while validating against the real data. No rewrites.
  * `Q10_*` boxes are coded 0/1, so "any box ticked" must test `== 1`. This changes only
    routing-table labels, not the sample.
  * The person-history sampler now tops up to 50 persons. With 32 strata it returned 32.
  * `within_person.csv` gains the share of changes that are 0↔50↔100 jumps, needed for the
    pre-stated stop rule.
  * The model gate also requires `manual_history_review_done`, as the existing docs already
    demanded before any estimate is quoted.
  * A markdown-breaking label is fixed.
* **No association model was run** and no coefficient exists in this repository.

Every SCE number in `outputs/` is now computed from the retrieved files (tag RAW-P1) or quoted
from the questionnaire or FAQ (DOC-P1). Remaining ADJ and BK tags are marked as such.

## Deliverables

| File | Status |
| - | - |
| `outputs/data_availability.md` | **Verified:** retrieval, hashes, coverage of all four files, licence text |
| `outputs/variable_validation.md` | **Verified:** verbatim wording, universes and codes; routing table; Q30 universe; Aug-2013 change; history trace |
| `outputs/sample_audit.csv` | **Computed:** waterfall S0–S8 overall, by year and by release |
| `outputs/preliminary_descriptives.md` | **Run on SCE data:** distributions, by year, binned, within-person, first differences, noise |
| `outputs/generated/*` | Machine-written aggregate tables from the real data |
| `outputs/literature_overlap.md` | Unchanged; full texts still to be re-read in Phase 2 |
| `outputs/phase1_feasibility.md` | **Updated:** data gate passed with caveat; signal gate warning |

## Answers to the seven Phase 1 questions

**1. Are the three core variables usable?**
*Yes, with one material caveat.* `Q13new` (lose job, 12 months), `Q22new` (find an
acceptable job within 3 months of losing the job this month) and `Q30new` (not able to make a
minimum debt payment, next 3 months):
* exist in all four files with identical names;
* lie in 0–100 with zero invalid entries;
* have verbatim wording and universes confirmed in the questionnaire.

The caveat: **`Q30new` is asked of everyone, with no debt filter**, and the core file has no
debt-holding variable. Its zeros (32–39% of answers) mix "no debt" with "certain to pay".

**2. How many eligible employed respondents and observations exist?**
**108,388 person-months from 15,673 persons, 2013-08 to 2025-10.** 12,933 of those persons
(105,648 rows) have ≥ 2 analysis months. The full files hold 186,660 rows from 24,592
persons, 2013-06 to 2025-10. The 2013–16 and latest file counts match the adjudication
exactly. The end month is consistent with the FAQ's nine-month microdata lag.

**3. Is within-person analysis feasible?**
*Structurally yes; substantively doubtful on raw descriptives.*
* Persons have a median of 7 analysis months (mean 6.9); 31% of all persons stay exactly 12
  months.
* 95.6% of multi-month persons change `Q22new`, and changes are not focal-point jumps (1.9%).
* But month-to-month `Q22new` changes are large: 51% are ≥ 10pp.
* Person-demeaned `Q30new` is flat across person-demeaned finding difficulty (+0.13 to
  −0.17pp, slightly negative), and first differences are symmetric.

Noise in `Q22new` may be attenuating a real relation. Phase 2 has to quantify that before
drawing a conclusion.

**4. What survey-routing problems remain?**
Each of the six problems listed in the first pass is now settled:
* (a) The Aug-2013 `Q22` change stopped asking the self-employed. `Q12new` only exists from
  2013-08, so the main sample starts there and is unaffected.
* (b) Self-employed respondents are never asked `Q13new` or `Q22new` (verified in data and
  questionnaire).
* (c) `Q30new` has a universal universe (see 1).
* (d) Multi-ticks are allowed. Temporarily laid-off and on-leave respondents with a job are in
  the questionnaire universe but excluded from the main sample by design.
* (e) There are no explicit missing codes, only blanks.
* (f) No overlap between "latest" and 2020–24; names are stable.

Small remaining items:
* about 1,000 implausible `Q11` job counts (cosmetic);
* `tenure` counts completed surveys, not months;
* 774 persons stay 13–16 months.

**5. Can this project realistically produce a master's thesis?**
*Yes as a completion-oriented project; the substantive story is now riskier.* Data, routing
and sample are solid, and the pipeline is done. The open question is whether there is any
within-person signal to report. A well-measured "finding beliefs add little beyond job-loss
fear" is still a legitimate thesis result. Its novelty is weaker, though, because it agrees
with Mitra (2026), where search responds to job-loss fear rather than finding beliefs.

**6. What is the most serious novelty obstacle?**
Unchanged: **Mitra (June 2026)** uses the same SCE job-loss and job-finding beliefs. The Phase 1
descriptives point the same way as Mitra's finding. That makes the "beyond Q13new" increment
the thing that must be shown, and it is not visible in raw descriptives.

**7. What should be tested in Phase 2?**
1. **Researcher's own trace** of the 50 histories in
   `data/derived/person_histories_for_manual_review.csv`. Then set
   `manual_history_review_done` by hand.
2. **Re-set the magnitude of interest** against the descriptive scale (raw within-person
   spread of about 0.3pp across ±15pp finding bins). Write it down *before* running M0–M3.
3. **Reliability of `Q22new`:** persistence of changes, test–retest within short gaps.
   Optionally a measurement-error-corrected within estimate (e.g. lagged Q22 as an instrument
   for the current value), labelled as associational.
4. **Q30 zeros:** sensitivity excluding always-zero persons. Check whether the SCE Credit
   Access module can identify debt holders (IDs, timing, sample loss).
5. Pre-specify the held-out prediction test: next-month `Q30new` from current `Q30new` +
   `Q13new`, with vs without `Q22new`.
6. Re-read the Mitra and Hartmann–Leth-Petersen full texts and confirm the overlap table.
