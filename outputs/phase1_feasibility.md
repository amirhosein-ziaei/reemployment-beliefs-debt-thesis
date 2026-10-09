# Phase 1 feasibility assessment: G-P2

## Bottom line

**Data and measurement gate: passed, with one material caveat.**
**Substantive-signal gate: warning, not decided.**

The official SCE core microdata (all four releases, 2013-06 to 2025-10) and the core
questionnaire were retrieved on 2026-10-09 and run through the existing pipeline:

* The three core items exist in every file, with verbatim wording and routing confirmed.
* Routing in the data matches the questionnaire for every employment group.
* There are no invalid codes and no duplicate keys.
* The eligible employee sample is **108,388 person-months from 15,673 persons**.

The caveat is that `Q30new` is asked of everyone, with no debt filter, so its zeros mix
non-borrowers with safe borrowers.

The warning is that raw descriptives show **almost no within-person co-movement** between
finding difficulty and `Q30new`. Cross-sectionally, the finding-difficulty gradient given
job-loss belief is small and non-monotone. That does not end the project: noise in `Q22new`
attenuates within-person contrasts, and no model has been run. But it is the central risk for
Phase 2 and should shape the magnitude of interest and the stop rules.

## Continuation criteria (from the adjudication report) and status

| Criterion | Evidence | Status |
| - | - | - |
| Variables stable enough across releases | `file_schema.csv`, `cross_file_consistency.csv`, `cross_file_overlap.csv` | **Met (RAW-P1).** Identical names in all four files; 9 unused columns added from 2020; no key overlap; means move with the cycle, with no level breaks |
| Routing produces a credible employed sample | `routing_by_group.csv`, `q22_routing_by_month.csv`, questionnaire | **Met (RAW-P1 + DOC-P1).** Employees answer all three items at 99.85%; self-employed and non-workers never answer Q13/Q22. The Aug-2013 Q22 change concerns the self-employed and falls before the sample start (Q12new is only fielded from 2013-08) |
| Useful within-person variation remains | `within_person.csv`, `desc_within_person_binned.csv`, `desc_first_differences.csv` | **Variation: met. Usefulness: open.** 95.6% of multi-month persons change Q22new; only 1.9% of changes are 0/50/100 jumps. But 51% of month pairs move ≥ 10pp, and raw within-person co-movement with Q30new is about zero (±0.2pp across bins) |
| Informative uncertainty around a 2pp-per-10pp contrast | Precision of M1/M2 | **Not assessed.** The model was deliberately not run (gate below). Descriptive scale suggests 2pp per 10pp is far above anything visible within person, so the magnitude of interest needs re-setting first |
| Manual tracing of 50 stratified person histories | `person_histories_for_manual_review.csv` (not committed) | **Partly done.** Automated checks plus reading by the AI assistant found no routing or construction errors (`variable_validation.md` §6). The researcher's own review is still required; `manual_history_review_done = false` |

## Sample (RAW-P1, `sample_audit.csv`)

| Step | Rows | Persons |
| - | - | - |
| S0 all respondent-months | 186,660 | 24,592 |
| S1 valid id and date | 186,660 | 24,592 |
| S2 unique userid×month | 186,660 | 24,592 |
| S3 employed (full- or part-time) | 125,908 | 18,069 |
| S4 works for someone else | 108,588 | 15,698 |
| S5–S7 valid Q13new, Q22new, Q30new | 108,388 | 15,673 |
| S8 persons with ≥ 2 analysis months | 105,648 | 12,933 |

The analysis sample has 8,020–9,240 rows in each full year 2014–2024 (2013: 4,428 for Aug–Dec; 2025: 6,367 for ten months).
For 2013–16 the count is 31,118 rows from 5,301 persons; the adjudication's preliminary filter
gave 31,396 from 5,327 (definitions not identical). The Phase 1 planning guess of "on the
order of 100,000" is confirmed by the actual count.

## Feasibility judgement by dimension

| Dimension | Judgement | Reason |
| - | - | - |
| Data access | **Confirmed** | All files free and downloadable without login (from a cloud host). Access from the student's network in Iran remains untested |
| Measurement | **Usable with a material caveat** | Wording, horizons and universes verified. `Q30new` has no debt filter, and 32–39% of answers are 0. Heavy rounding (63–84% at multiples of 5) |
| Identification | **Associational only** | Unchanged. Person FE absorb stable pessimism, not changing pessimism |
| Within-person signal | **Weak in raw descriptives** | Flat demeaned Q30 across demeaned finding-difficulty bins; first differences symmetric. Noise attenuation is plausible but not yet quantified |
| Scale of thesis | **Realistic** | Bounded design; data pipeline done |
| Novelty | **Incremental / weak** | Unchanged (`literature_overlap.md`, not re-verified in this session) |
| Engineering risk | **Low** | Full pipeline runs on the real files in a few minutes once the xlsx cache exists |

## Stop and continue rules for Phase 2 (updated with Phase 1 evidence)

* ~~Stop if `Q30new` is asked only of a small or selected subset.~~ **Resolved:** it is asked of
  everyone. Replace with: **re-scope** if results depend entirely on the always-zero group.
  Test by excluding persons with Q30new = 0 in every month.
* **Stop** if within-person variation in `Q22new` is mostly noise. The focal-point test passes:
  only 1.9% of changes are 0↔50↔100 jumps. Still to do: a reliability check, e.g. whether
  Q22new changes predict the person's *next* Q22new (persistence) or are mean-reverting.
* ~~Stop if routing cannot be reconciled.~~ **Resolved:** routing reconciles.
* **Re-scope (do not silently substitute):** 2013-06/07 are already excluded by construction
  (no Q12new); report this.
* **Do not stop** because a preliminary coefficient is small or insignificant. A precise small
  increment is a usable result. The magnitude of interest must be set *before* model output
  is seen.
