# Preliminary descriptives (G-P2 Phase 1)

## Status: RUN on the real SCE core microdata (descriptives only)

`code/03_descriptives.py` was run on the panel built from the four official workbooks retrieved
2026-10-09 (see `data_availability.md`). All numbers below are copied from
`outputs/generated/descriptives_tables.md` and the CSVs next to it. **They are descriptive, not
causal.** No association model was run (see "Preliminary association model" below).

**Analysis sample:** employees (`Q10_1` or `Q10_2` ticked and `Q12new = 1`) with valid
Q13new, Q22new and Q30new. That is **108,388 person-months from 15,673 persons, 2013-08 to
2025-10**. 105,648 rows (12,933 persons) belong to persons with ≥ 2 analysis months.
Waterfall: `sample_audit.csv`.

### Distributions (unweighted; weighted mean in brackets)

| Item | mean | p10 | p25 | median | p75 | p90 |
| - | - | - | - | - | - | - |
| Q13new (lose job, 12m) | 13.7 [13.9] | 0 | 1 | 5 | 20 | 41 |
| Q22new (find acceptable job within 3m of a loss) | 55.4 [54.6] | 10 | 30 | 55 | 81 | 99 |
| Q30new (miss a minimum debt payment, 3m) | 11.3 [12.6] | 0 | 0 | 2 | 10 | 40 |

Q30new is very right-skewed: the median is 2, and 32–39% of answers are exactly 0 (zeros
include respondents with no debt; see `variable_validation.md` §4).

### Over time (`desc_by_year.csv`)

Q22new rises from 47.6 (2013) to 60.1 (2019), falls to 51.7 in 2020, recovers to 59.4 in 2022,
and drifts down to 51.1 in 2025. Q30new falls from about 12–13 (2013–16) to a low of 8.2 in
2021, then returns to 12.6 by 2025. Year composition matters for any pooled comparison;
models must keep month fixed effects.

### Cross-sectional: Q30new by job-loss belief × finding difficulty (`desc_binned_q30.csv`)

Mean Q30new (pp); finding difficulty = 100 − Q22new:

| Q13new bin | 0–25 (easy) | 26–50 | 51–75 | 76–100 (hard) |
| - | - | - | - | - |
| 0 | 6.1 | 9.1 | 7.7 | 7.7 |
| 1–10 | 7.8 | 8.9 | 9.8 | 9.8 |
| 11–25 | 12.5 | 14.3 | 15.8 | 14.8 |
| 26–50 | 18.4 | 22.6 | 23.7 | 20.8 |
| 51–100 | 19.9 | 25.7 | 22.7 | 20.8 |

Every cell has ≥ 879 rows and ≥ 600 persons. Mean Q30new rises steeply with the job-loss belief
(about 6–9pp in the 0 bin vs 20–26pp in the 51–100 bin). **Within a job-loss bin, the
finding-difficulty gradient is small and not monotone.** Q30new is usually highest in the
middle difficulty bins and lower in the "hard" bin. The share of Q30new = 0 is U-shaped across
difficulty bins in four of the five job-loss bins. That pattern is consistent with
response-style clustering at endpoints.

### Within person (`desc_within_person_binned.csv`, `desc_first_differences.csv`)

| Person-demeaned finding difficulty | rows | mean demeaned Q30new | mean demeaned Q13new |
| - | - | - | - |
| < −15 (easier than own average) | 15,349 | +0.13 | +0.20 |
| −15..−5 | 20,731 | −0.01 | +0.09 |
| −5..5 | 37,568 | +0.03 | −0.05 |
| 5..15 | 17,187 | −0.03 | −0.02 |
| > 15 (harder than own average) | 14,813 | −0.17 | −0.20 |

| Month-to-month change in finding difficulty | pairs | mean ΔQ30new | share ΔQ30 > 0 | share ΔQ30 < 0 | mean ΔQ13new |
| - | - | - | - | - | - |
| got easier (> 10pp) | 16,085 | +0.15 | 31% | 31% | +0.42 |
| stable (−10..10pp) | 51,524 | −0.08 | 26% | 26% | −0.10 |
| got harder (> 10pp) | 16,669 | −0.16 | 31% | 31% | −0.23 |

**Within person, Q30new barely moves with finding difficulty.** Months in which a person
reports finding a job harder than usual show Q30new within ±0.2pp of their own average. The
sign is slightly *negative*. Up- and down-moves in Q30new are equally frequent whatever the
direction of the finding change. Q13new moves by a similarly small amount in the same
direction: it is slightly *lower* in months when finding is reported as harder.

### Variation and noise (`within_person.csv`, `heaping.csv`)

Among multi-month persons, 95.6% change Q22new at least once and 81.4% change Q30new. Variation
exists. But much of it may be response noise:

* 51% of consecutive-month Q22new pairs move by ≥ 10pp (mean absolute change 14.8pp).
* 56–66% of Q22new answers are multiples of 10.
* Changes are *not* mainly focal-point jumps: only 1.9% of month-to-month Q22new changes go
  between 0, 50 and 100 (1.0% for Q13new, 1.2% for Q30new). The variation is spread over the
  scale, mostly on multiples of 5 and 10.
* The within-person share of variance is 30% for Q22new, 28% for Q30new and 39% for Q13new.

Classical noise in Q22new would bias within-person associations toward zero. The flat
within-person pattern therefore cannot, on its own, be read as "no relationship".

### What this means for the thesis question (descriptive reading only)

1. The cross-sectional pattern is dominated by Q13new. The increment of finding difficulty
   *given* job-loss belief is small and non-monotone, even before person effects.
2. The within-person co-movement of finding difficulty and Q30new is close to zero in raw
   descriptives.
3. The magnitude of interest proposed by the adjudication (2pp of Q30new per 10pp of finding
   belief) should be re-set against this scale **before** any model is run (Phase 2 step 5).
   The descriptives do not show a gradient anywhere near that size within person.

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

## Preliminary association model: gated, NOT run

The model now runs only if `validation_flags.json` has **both**
`validated_for_preliminary_model = true` and `manual_history_review_done = true`.

* On the real data, the first flag is **true**: all required variables are present in every
  file, keys are unique, and routing is consistent.
* The second flag is **false**. The person-history trace was done by the AI assistant, not the
  researcher (`variable_validation.md` §6).

The project plan also requires the magnitude of interest to be fixed *before* model output is
seen. So the run on real data deliberately produced no estimates, and none are reported
anywhere in this repository.

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

## Interpretive hazards (now checkable against the tables)

1. **Common pessimism / response style.** Respondents who answer every probability question
   pessimistically, or who heap at 50, will produce a positive cross-sectional slope with no
   financial content. Compare M0 with M1, and look at the first-difference table.
2. **Zeros in Q30new.** Verified: Q30new is asked of everyone and the core file has no debt
   filter, so zeros (32–39% of answers) mix "no debt" with "safe borrower"
   (`variable_validation.md` §4).
3. **Co-movement.** If Q13new and Q22new move together within person, the increment of Q22new is
   weakly identified. Check `mean_d_q13` in the first-difference table.
4. **Composition.** The share of each release and year in the pooled sample changes over time.
   Compare by-year means before pooling.
