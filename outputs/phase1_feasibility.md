# Phase 1 feasibility assessment: G-P2

## Bottom line

**Gate not passed: undetermined, not failed.** The deciding Phase 1 work (actual data
verification) could not be done in this session: the provider host was blocked by the session's
network policy. Everything that does not need the raw files is done:

* the reproducible pipeline;
* the routing and validation checks, coded with explicit pass/fail rules;
* the literature overlap memo;
* the documentation of variables, horizons and prohibited interpretations.

The project's feasibility rests on the adjudication report's raw-file checks (two of four
releases) plus documentation. Nothing in this session contradicts them, and nothing here
independently confirms them.

## Continuation criteria (from the adjudication report) and current status

| Criterion | Evidence needed | Status |
| - | - | - |
| Variables stable enough across releases | `file_schema.csv`, `cross_file_consistency.csv`, `cross_file_overlap.csv` | **PENDING** (2 of 4 releases checked by adjudication for field presence only) |
| Routing produces a credible employed sample | `routing_by_group.csv`, `q22_routing_by_month.csv`, questionnaire re-read | **PENDING** |
| Useful within-person variation remains | `within_person.csv`, `desc_within_person_binned.csv`, `desc_first_differences.csv` | **PENDING**. Adjudication: 4,267 of 5,327 eligible persons in 2013–16 have ≥ 2 observations. Number of observations is not the same as variation in the beliefs |
| Informative uncertainty around a 2pp-per-10pp contrast | Precision of M1/M2 from the actual joint distribution, not raw N | **PENDING** |
| Manual tracing of person histories (adjudication: 50, stratified) | `person_histories_for_manual_review.csv` (generated, not committed) | **PENDING** |

## Feasibility judgement by dimension

| Dimension | Judgement | Reason |
| - | - | - |
| Data access | **Feasible, unconfirmed here** | Free public files; adjudication downloaded two without login. Blocked only by this session's egress policy. Student's access from Iran is untested |
| Measurement | **Plausible with caveats** | Three items exist with documented horizons (12m / 3m-conditional / 3m). The universe of `Q30new` (borrowers vs all) is the main open measurement question |
| Identification | **Associational only** | Person FE absorb stable pessimism but not changing pessimism, anticipated separation or changing debts. No instrument |
| Scale of thesis | **Realistic** | Bounded design: one main association, one held-out prediction comparison, a small sensitivity set. Fits the April–May 2027 main-results target if Phase 2 starts promptly |
| Novelty | **Incremental / weak** | See `literature_overlap.md`. The outcome is the only new element |
| Engineering risk | **Low** | Pipeline is ~600 lines, dependency-light, and smoke-tested |

## Stop and continue rules for Phase 2 (proposed)

* **Stop** if `Q30new` turns out to be asked only of a small or selected subset (e.g. borrowers
  identified only in a non-core module), with no defensible way to separate non-borrowers.
* **Stop** if within-person variation in `Q22new` is mostly noise or heaping. Example: most
  persons never change, or changes are dominated by 0↔50↔100 jumps.
* **Stop** if routing cannot be reconciled with the questionnaire across releases.
* **Re-scope (do not silently substitute)** if pre-2013-08 or particular releases must be dropped.
* **Do not stop** because a preliminary coefficient is small or insignificant. A precise small
  increment is a usable thesis result.
