# G-P2 Phase 2 summary: initial econometric evidence and predictive value

**Date:** 2026-10-09/10. **Status:** EXPLORATORY — PENDING INDEPENDENT HUMAN VALIDATION.
Associational only; no causal claims. Outcome is a subjective expectation, not delinquency.

## What was done

| Step | Output | Status |
| - | - | - |
| 1. Human-validation package | `code/04_validation_package.py` → `data/review/` (gitignored; 50 persons, 441 person-months); `outputs/human_validation_guide.md` | Package built. Automated cell-by-cell check against the provider `.xlsx` passed for all 441 rows. **Independent human validation NOT done**; flag stays `false` |
| 2. Prespecification | `outputs/model_specification.md` | Committed in `a08c1e0` **before** any regression or prediction run |
| 3. Association models A–C | `code/05_phase2_models.py`, `outputs/preliminary_regressions.md` | Run; results in `outputs/exploratory/` |
| 4. Prediction comparison | `code/06_prediction.py`, `outputs/prediction_comparison.md` | Run once as specified |
| 5. Measurement sensitivity | `outputs/measurement_sensitivity.md` | Prespecified list S1–S7, run in full |
| 6. Decision | `outputs/phase2_feasibility_decision.md` | Recommendation: **narrow** |
| Tests | `tests/test_phase2.py` (16 tests, unittest) | Pass. FE and cluster-SE code agrees with brute-force dummy regressions; pair construction, folds, classification rules and routing logic are tested |

**Gate and labelling.**
* The validated-model gate in `code/03_descriptives.py` was not changed or bypassed. It
  stays closed.
* Phase 2 scripts check only that the automated data checks passed, and write only to
  `outputs/exploratory/`.

**Deviations from the specification:** none in estimation.
* `05_phase2_models.py` was run twice; the second run only added the decision-rule label to
  the first-difference rows (S3c). Estimates were identical.
* No unplanned specifications were run.

## Key numbers

pp of Q30new per 10pp lower Q22new; 95% CIs, person-clustered:

| | Estimate | CI | Benchmark-rule verdict |
| - | - | - | - |
| Model A (pooled, month FE) | +0.30 | [0.22, 0.38] | precisely small |
| **Model B (person + month FE)** | **−0.05** | **[−0.10, 0.005]** | **precisely small** |
| Model C at Q13 = 50 | +0.10 | [−0.02, 0.22] | precisely small |
| Model C difference, Q13 50 vs 5 | +0.18 | [0.06, 0.29] | precisely small |
| Job-loss belief, B (per 10pp) | +1.09 | [0.99, 1.18] | (control) |
| Prediction, person held out: relative RMSE gain | 0.018% | [0.003%, 0.033%] | negligible |
| Prediction, forward years: relative RMSE gain | 0.022% | [0.012%, 0.033%] | negligible |
| Noise-corrected within estimate (S3c IV) | +0.83 | [−0.58, 2.24] | inconclusive |

## Answers to the ten questions

**1. Does reemployment difficulty have an incremental relationship with subjective
debt-payment risk after controlling for job-loss expectations?**
Pooled: a small positive one, +0.30pp per 10pp lower finding probability [0.22, 0.38]. Within
person: none, −0.05pp [−0.10, 0.005]. Next-month prediction: a statistically detectable but
negligible increment.

**2. Is the estimated relationship economically meaningful or precisely small?**
Precisely small. Every CI for the main estimand lies far inside ±2pp. The pooled upper bound
is 0.38pp (19% of the benchmark); the within upper bound is about 0.

**3. How much does the estimate change with person fixed effects?**
Completely. It goes from +0.30 to −0.05, so the pooled association is entirely between
persons. The job-loss coefficient halves (2.37 → 1.09) but survives.

**4. Is the interaction between job-loss and finding beliefs informative?**
Statistically yes; economically no. Finding difficulty matters slightly more when job loss is
likely, but even at a 50% job-loss belief the effect is ≤ 0.22pp per 10pp (CI upper bound).
The 50-vs-5 difference is 0.18pp [0.06, 0.29].

**5. Does adding reemployment beliefs improve out-of-sample prediction of next-month
debt-payment expectations?**
Not materially. RMSE falls by about 0.003pp (0.02%) for held-out persons and for later years.
CI upper bounds are about 0.03%, against a 1% materiality threshold set in advance.

**6. Could measurement noise or sample selection explain a weak relationship?**
* **Sample selection:** unlikely. Results are unchanged for:
  * non-zero Q30 respondents;
  * a stable-employment cohort;
  * a wider eligibility definition;
  * longer panels;
  * person-equal weights;
  * respondents with a next-month response.

  Attrition is selective on Q30new (+0.7pp non-response per 10pp), so prediction results
  describe stayers.
* **Measurement noise:** cannot be ruled out for the *true* beliefs. Outlier swings and
  heaping do not matter. But the first-difference IV, which corrects for serially
  uncorrelated reporting error, gives +0.83 with CI [−0.58, 2.24]. That is imprecise and
  relies on assumptions that may fail.

**7. Can the results distinguish a meaningful null from low statistical power?**
For **reported** beliefs, yes: it is a meaningful null. The minimum detectable effect is about
0.08pp, 4% of the benchmark. For the **latent** beliefs behind noisy reports, no: the
noise-corrected within estimate is too imprecise to separate 0 from 2pp.

**8. Does the project remain suitable for a master's thesis?**
Yes, as a narrowed thesis. A transparent, prespecified, precisely estimated small increment,
with a measurement-error analysis, is a complete thesis. The data pipeline and audit are done,
and completion risk is low. It is not suitable under the original "finding difficulty
amplifies debt distress" framing.

**9. What is the strongest remaining obstacle to a publishable paper?**
* The main result is a null on a subjective outcome, consistent with existing work (Mitra
  2026: loss fear, not finding beliefs, drives behaviour; not re-read this session).
* There is no realised debt behaviour or debt-holding indicator.
* The only route to a stronger claim is a precise noise-corrected within estimate, and
  current instruments are too weak for one.

**10. Should we continue, narrow the question, or stop?**
**Narrow.** Re-frame as the incremental-information and measurement question. First complete
independent human validation. Then allow one prespecified measurement-error extension and
write up. Stop extending if that extension stays inconclusive. See
`phase2_feasibility_decision.md`.

## Not claimed

* No causal effect of beliefs on debt distress.
* No statement about actual delinquency or default.
* No independent human validation.
* No publication potential from statistical significance (the significant pooled and
  interaction coefficients are economically negligible).

## Reproduce

```bash
python code/04_validation_package.py           # local, gitignored review package
python code/05_phase2_models.py                # ~4 min
python code/06_prediction.py                   # ~15 s
python -m unittest discover -s tests -v        # 16 tests
```
