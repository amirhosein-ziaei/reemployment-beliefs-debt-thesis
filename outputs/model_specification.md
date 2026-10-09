# G-P2 Phase 2: prespecified analysis

**Status:** written and committed **before** any regression or prediction model was run on SCE
data. The git history shows this file was committed before the first commit containing model
output. Any later change to this file is listed under "Amendments" at the bottom, with its
reason. Results that depart from this plan are labelled as deviations.

**What had been seen before this was written:** only the Phase 1 descriptives
(`outputs/preliminary_descriptives.md`): distributions, binned means, person-demeaned bin
means and first-difference bin means. They showed a strong cross-sectional Q13–Q30 gradient
and little within-person co-movement of finding difficulty and Q30. No regression
coefficient, standard error or prediction metric had been computed on SCE data.

**Label on all output:** *EXPLORATORY — PENDING INDEPENDENT HUMAN VALIDATION. Associational,
not causal.* Output goes to `outputs/exploratory/`, never to the validated-model path. The
existing gate in `code/03_descriptives.py` (`validated_for_preliminary_model` **and**
`manual_history_review_done`) is not changed or bypassed. The Phase 2 scripts refuse to run
unless the automated checks pass (`validated_for_preliminary_model = true`).

## 1. Variables and horizons

| Role | Item | Question (verbatim core, see `variable_validation.md`) | Horizon | Scale used |
| - | - | - | - | - |
| Outcome | `Q30new` | Percent chance of NOT being able to make one of your debt payments (minimum required payments) | next **3 months** | 0–100 pp |
| Main predictor | `Q22new` | Percent chance of finding a job you will accept within the following 3 months, *if you lost your main job this month* | **3 months, conditional on a hypothetical loss now** | `fd10 = (100 − Q22new)/10` |
| Main control | `Q13new` | Percent chance of losing your main job | next **12 months** | `loss10 = Q13new/10` |

* `fd10` is **reemployment difficulty as a belief**: one unit is a 10pp *decrease* in the
  stated conditional finding probability. It is not an observed or expected unemployment
  duration.
* The three horizons differ (3m outcome; 12m loss; 3m conditional finding). The product of
  loss and difficulty is an **index**, never the probability of a 3-month income interruption.
* Every coefficient is in **percentage points of Q30new per 10pp change in the belief**.

## 2. Sample

* **Main sample:** the Phase 1 analysis sample (`data/derived/panel_analysis.csv.gz`).
  * Employed full- or part-time (`Q10_1` or `Q10_2`).
  * Works for someone else (`Q12new = 1`).
  * Valid 0–100 answers to Q13new, Q22new and Q30new.
  * 2013-08 to 2025-10: 108,388 person-months, 15,673 persons.
* Models with person effects identify only from persons with ≥ 2 months (12,933 persons).
  Singletons are dropped from those models and the counts are reported.
* Unit: person-month. Unweighted is primary (see §5).

## 3. Main estimand and models

**Main estimand:** β_fd, the change in Q30new (pp) associated with a 10pp decrease in Q22new,
holding Q13new fixed, **within person** (Model B).

| Model | Specification | Role |
| - | - | - |
| **A** | Q30 = β_fd·fd10 + β_loss·loss10 + month FE | Pooled association (between and within) |
| **B** | A + person FE | **Primary**: within-person association |
| **C** | B + β_int·(fd10 − mean)(loss10 − mean), centred at estimation-sample means | **The one prespecified interaction** |

* Fixed effects are absorbed by an iterative within-transformation (alternating projections),
  not by dummy columns.
* **Model C reporting.** Report the marginal effect of fd10 at Q13new = **0, 5, 20 and 50**,
  with delta-method 95% CIs: β_fd + β_int·(L/10 − mean loss10). These are roughly the 10th
  percentile, median, 75th percentile and a high-risk value. Also report the difference
  between L = 50 and L = 5.
* **Within-person variation reported alongside:** within-person SD and share of variance of
  fd10 and Q30 in the estimation sample.

## 4. Inference

* **Primary:** person-clustered SEs (CR1), 95% CI = estimate ± 1.96·SE.
* **Common calendar-time shocks** (reported for A, B and C):
  1. two-way clustering by person and calendar month (Cameron–Gelbach–Miller);
  2. Model B excluding 2020-03 to 2020-12 (pandemic shock months).
* p-values are reported, but **conclusions are drawn from magnitudes and CIs** (§6).

## 5. Survey weights (sensitivity only)

* The SCE `weight` variable is the provider's respondent-month survey weight (BK: designed to
  make each monthly cross-section representative of US household heads; documentation not
  re-read).
* It is **not** designed for the employed subpopulation or for panel/within-person
  estimation.
* Unweighted estimates are primary. The regression estimand is a slope, and weights are not
  needed for consistency if the slope is homogeneous.
* Sensitivity: Models A and B re-estimated by WLS. The same weights are used in the
  within-transformation and in the estimation, and rows with missing weight are dropped.
  A large weighted–unweighted gap is read as **slope heterogeneity** across the population,
  not as a correction.

## 6. Benchmark magnitude and decision rules (fixed now; not to be changed after results)

**Benchmark: 2pp of Q30new per 10pp decrease in Q22new** (adjudication report, adopted
unchanged).

**Justification from the outcome scale** (Phase 1 descriptives, analysis sample):
* Q30new has mean 11.3, median 2, SD 20.7 and within-person SD 10.9.
* 2pp is ≈ 18% of the mean, ≈ 0.10 total SD and ≈ 0.18 within-person SD.
* A 10pp move in Q22new is ≈ 0.31 of its SD (31.8). Within person, 51% of consecutive-month
  Q22new changes are already ≥ 10pp, so a 10pp contrast is a common, not an extreme,
  movement.
* In the raw cross-section, mean Q30new is about 15pp higher for Q13new 51–100 (22.3) than for
  Q13new = 0 (7.1). That is very roughly 2pp per 10pp of *job-loss* belief. A finding-difficulty
  effect of 2pp per 10pp would therefore be of the same order as the raw job-loss gradient:
  substantive for a household-finance reader and a demanding bar.

**Justification from the literature:** limited. The closest papers (Mitra 2026; Hartmann &
Leth-Petersen 2024) were not re-read in this session (`literature_overlap.md`), and no
verified published estimate maps job-finding beliefs into debt-payment expectations. The
benchmark is therefore a **scale-based** threshold of practical relevance, not a
literature-calibrated one. This is stated as a limitation, and the threshold is kept exactly
as the adjudication proposed.

**Decision rules for β_fd** (Model B primary; applied identically to A):

| Classification | Rule |
| - | - |
| Economically meaningful | point estimate ≥ 2 **and** 95% CI lower bound > 0 |
| Precisely small (meaningful null relative to the benchmark) | entire 95% CI inside (−2, +2) |
| Inconclusive (low power relative to the benchmark) | anything else |

Statistical significance (CI excludes 0) is reported separately and is **not** the
classification. The same rules apply to the Model C difference in marginal effects between
Q13new = 50 and Q13new = 5: the interaction is "informative" if that difference is meaningful
by the rule above.

## 7. Prediction exercise (one prespecified comparison)

**Pairs.** (i, t) such that:
* person i is in the main sample in month t;
* person i responds in month **t+1** (the next calendar month exactly) with a valid Q30new,
  whatever their employment status at t+1.

Rows whose next response comes after a gap, and rows with no later response (rotation exit or
attrition), have no target and are excluded. Their share is reported.

**Target:** Q30new at t+1, the reported subjective expectation, not delinquency.

**Models** (OLS, no regularisation, no tuning; predictions clipped to [0, 100] for both):

| | Predictors (all dated t) |
| - | - |
| Baseline | Q30new_t, Q13new_t, tenure_t (survey count), 11 calendar-month-of-year dummies |
| Expanded | Baseline + fd10_t + centred fd10_t × loss10_t (centring constants from the training data only) |

No fixed-effects model with a lagged outcome is used.

**Evaluation 1, person held out.**
* 5 folds, assigned by person (seed 20261010). No person appears in both training and test.
* RMSE and MAE are computed on pooled out-of-fold predictions.

**Evaluation 2, forward in calendar time (expanding window).**
* For each test year Y = 2016, …, 2025, train on pairs whose *target* month is ≤ December
  of Y−1, and test on pairs with t in year Y.
* All training information is dated before the test period. The same person may appear in
  training (earlier year) and test (later year); that uses only past data. As a secondary
  check, results are also reported dropping test persons who appear in that year's training
  data.

**Improvement:** Δ = metric(baseline) − metric(expanded), in pp (positive = expanded better),
and Δ / metric(baseline) in %.

**Uncertainty:**
* Evaluation 1: person-cluster bootstrap of the out-of-fold error differences (999
  resamples of persons; fitted models held fixed).
* Evaluation 2: calendar-block bootstrap resampling test months (999 resamples).
* 95% percentile intervals in both cases.

**Classification:**

| Classification | Rule |
| - | - |
| Material | relative RMSE improvement ≥ 1% with CI lower bound > 0 |
| Negligible | CI upper bound of the relative RMSE improvement < 1% |
| Inconclusive | otherwise |

## 8. Measurement sensitivity (fixed list; each reports β_fd from Model B unless stated)

| ID | Limitation | Check |
| - | - | - |
| S1 | No debt-ownership indicator | Drop persons whose Q30new = 0 in every analysis month (proxy for "no debt") |
| S2a | Focal answers | Drop rows where any of Q13new, Q22new, Q30new = 50 |
| S2b | Endpoints | Drop rows where Q22new ∈ {0, 100} |
| S3a | Large month-to-month changes | Drop rows whose Q22new changed by ≥ 50pp from the previous calendar month |
| S3b | Measurement error (pooled) | Model A estimated by 2SLS: fd10_t and loss10_t instrumented by their values at t−1 (consecutive months), versus OLS on the same sample. Valid if reporting error is serially uncorrelated |
| S3c | Measurement error (within) | First-difference 2SLS: Δfd10 and Δloss10 instrumented by fd10 and loss10 at t−2 (three consecutive months), month FE, versus first-difference OLS on the same sample. First-stage strength reported |
| S4a | Changing eligibility | Baseline-employed cohort: persons who are in the main sample in every month they are observed |
| S4b | Eligibility definition | Add respondents on leave or temporarily laid off with Q12new = 1 (the questionnaire universe) |
| S5a | Short panels | Persons with ≥ 6 analysis months |
| S5b | Short panels | Person-equal weights (1/T_i) |
| S6a | Attrition | Model B on rows that have an observed next-calendar-month response |
| S6b | Attrition | Linear probability model of "no response next month" (rows with tenure < 12, i.e. before scheduled rotation) on fd10, loss10, Q30/10, month FE; person-clustered |
| S7a | Common pessimism | Model B + Q4new/10 (P US unemployment higher) + Q1 and Q2 category dummies (own finances, past and expected) |
| S7b | Placebo future belief | Model B + fd10 at t+1 (consecutive months): a future belief "explaining" current Q30 as much as the current one points to shared trends or response style |

No other specifications will be searched. Anything run beyond this list is reported as
unplanned and is not used for conclusions.

## 9. Execution order

1. `code/04_validation_package.py`: human-validation package (no estimation).
2. Commit this file.
3. `code/05_phase2_models.py`: Models A–C, inference variants, weights, S1–S7 →
   `outputs/exploratory/`.
4. `code/06_prediction.py`: the prediction comparison → `outputs/exploratory/`.
5. Write `preliminary_regressions.md`, `prediction_comparison.md`,
   `measurement_sensitivity.md`, `phase2_summary.md`, `phase2_feasibility_decision.md` from
   the generated tables.

## Amendments

None yet.
