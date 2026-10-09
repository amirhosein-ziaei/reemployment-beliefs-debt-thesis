# Preliminary descriptives (G-P2 Phase 1)

## Status: NOT RUN on SCE data

The SCE workbooks could not be retrieved in this session (`www.newyorkfed.org` blocked by the
session's network policy; see `data_availability.md`). **This file contains no SCE estimates.**
It specifies exactly what `code/03_descriptives.py` produces, so the tables can be generated
and reviewed unchanged once the data are available. No numbers have been substituted from any
other source.

The pipeline has been **smoke-tested end-to-end on a synthetic fixture**
(`tests/make_synthetic_fixture.py`, random numbers labelled as synthetic). That test shows only
that the code runs and the checks fire: an out-of-range value, a non-numeric entry and
cross-file duplicate keys are each caught at the intended audit step. Its outputs are written
to a scratch directory and are **not** committed or reported.

## Tables produced (to `outputs/generated/`)

| Output | Content | Purpose |
| - | - | - |
| `file_schema.csv` | Rows, IDs, first and last month, variable presence and answer share, licence preamble, per file | Coverage and harmonisation |
| `sample_audit.csv` (in `outputs/`) | Exclusion waterfall S0–S8, overall, by calendar year and by release | Sample counts and every exclusion |
| `routing_by_group.csv` | Answer rates of Q11, Q12new, Q13new, Q22new, Q30new, Q4new by mutually exclusive employment group | Routing verification |
| `q22_routing_by_month.csv` | Monthly answer rates among eligible employees | Detect the Aug-2013 Q22 change and any later breaks |
| `invalid_and_missing.csv` | Missing share and invalid count per variable (employees) | Missing and invalid responses |
| `heaping.csv` | Shares at 0, 50 and 100, multiples of 5 and 10, non-integers, by release | Rounding and focal answers |
| `within_person.csv` | Share of persons whose answer ever changes; within vs between SD; month-to-month changes; joint variation of Q22 and Q30 | Within-person feasibility |
| `panel_length.csv` | Months per person (all rows; analysis sample); exits from eligibility; last-month share; tenure quantiles | Panel length and attrition |
| `cross_file_consistency.csv`, `cross_file_overlap.csv` | Means and medians by release; agreement on duplicated keys | Consistency across releases |
| `desc_distributions.csv` | Mean, weighted mean, SD and quantiles of Q13new, Q22new, Q30new and finding difficulty | Variable distributions |
| `desc_by_year.csv` | Rows, persons and means by year | Coverage by year |
| `desc_binned_q30.csv` | Mean and median Q30new and share at 0, by Q13new bin (0, 1–10, 11–25, 26–50, 51–100) × finding-difficulty bin (0–25 … 76–100), with row and person counts | Descriptive comparison across loss and finding beliefs |
| `desc_within_person_binned.csv` | Person-demeaned Q30new by person-demeaned finding-difficulty bin | Same comparison within person |
| `desc_first_differences.csv` | Month-to-month ΔQ30new by direction of Δ finding difficulty (>10pp easier / stable / >10pp harder), with mean ΔQ13new | Within-person co-movement; shows whether loss beliefs move at the same time |
| `preliminary_model.csv` | See below (only if validated) | |

Cross-sectional (binned) and within-person tables are kept separate, as the adjudication report
requires.

## Preliminary association model: gated

Runs **only if** `validation_flags.json` has `validated_for_preliminary_model = true`. That
requires all required variables present in every release, unique person-month keys, and
routing consistent with the screening thresholds. The flag `manual_history_review_done` must
also be set by hand after tracing the person histories in
`data/derived/person_histories_for_manual_review.csv` before any estimate is quoted.

Specification (unweighted; person-clustered SEs):

* M0: Q30new on fd10 and loss10, month FE only.
* M1: as M0, plus person FE.
* M2: M1 plus the centred interaction fd10 × loss10 (an index, not a probability).
* M3: M1 plus P(US unemployment higher)/10 (`Q4new`), a single general-pessimism control.

Here fd10 = (100 − Q22new)/10 and loss10 = Q13new/10. Each coefficient is the change in reported
payment-distress probability (pp) associated with a 10pp change in the belief. Labels on output:
**"PRELIMINARY ASSOCIATION — NOT CAUSAL"**. Nothing here predicts actual delinquency.

The adjudication sets a provisional magnitude of interest: **2pp in Q30new per 10pp contrast in
finding belief**. It must be justified or revised from descriptive scale *before* preferred
results are inspected.

## Known interpretive hazards to check when the tables exist

1. **Common pessimism / response style.** Respondents who answer every probability question
   pessimistically, or who heap at 50, will produce a positive cross-sectional slope with no
   financial content. Compare M0 with M1, and look at the first-difference table.
2. **Zeros in Q30new.** If non-borrowers answer 0, the outcome mixes "no debt" with "safe
   borrower" (see `variable_validation.md` §3).
3. **Co-movement.** If Q13new and Q22new move together within person, the increment of Q22new is
   weakly identified. Check `mean_d_q13` in the first-difference table.
4. **Composition.** The share of each release and year in the pooled sample changes over time.
   Compare by-year means before pooling.
