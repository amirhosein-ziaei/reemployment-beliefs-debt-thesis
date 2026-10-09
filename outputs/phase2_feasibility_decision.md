# Phase 2 feasibility decision: G-P2

> All evidence is **EXPLORATORY — PENDING INDEPENDENT HUMAN VALIDATION**, associational, and
> about *reported subjective expectations*. Independent human validation has not happened
> (`human_validation_guide.md`).

## Recommendation: **narrow the question** (do not stop; do not continue as framed)

The original framing asked whether perceived reemployment difficulty predicts debt-payment
distress beyond job-loss risk, and whether that strengthens when recovery is expected to be
hard. The data answer it clearly, **for reported beliefs**:

| Evidence | Result | Against the 2pp benchmark |
| - | - | - |
| Pooled association (A) | +0.30pp per 10pp lower finding prob. [0.22, 0.38] | Precisely small (≤ 19% of benchmark) |
| Within person (B, primary) | −0.05pp [−0.10, 0.005] | Precisely small; effectively zero |
| Interaction (C), Q13 = 50 vs 5 | +0.18pp [0.06, 0.29] | Statistically non-zero, economically negligible |
| Next-month prediction, new persons | RMSE −0.018% [0.003%, 0.033%] | Negligible (rule: < 1%) |
| Next-month prediction, later years | RMSE −0.022% [0.012%, 0.033%] | Negligible |
| 16 of 17 sensitivity estimates (S1–S7, incl. same-sample comparisons) | precisely small | Robust |
| Noise-corrected within estimate (S3c, first-difference IV) | +0.83pp [−0.58, 2.24] | **Inconclusive** |

Job-loss beliefs carry the signal: +2.4pp per 10pp pooled and +1.1pp within person. Finding
beliefs add essentially nothing that is usable.

**Why narrow rather than stop.**
* A precisely estimated small increment is a legitimate, finishable master's-thesis result.
  The adjudication anticipated this: "a credible bound if the added information is small".
* The pipeline, audit and estimates already exist, so completion risk is low.

**Why not continue as framed.**
* The headline mechanism is not present in reported beliefs within person.
* The interaction is negligible.
* The predictive increment is about 0.02%.
* Building the thesis around "finding difficulty amplifies debt distress" would mean arguing
  against the project's own evidence.

## Narrowed question (proposed for your decision)

> *Do employed households' reemployment beliefs contain debt-service information beyond
> job-loss fears? Evidence on incremental association, prediction and measurement error in
> the SCE.*

Contribution:
1. a bound on the incremental content of finding beliefs for payment expectations:
   precisely small pooled, zero within, negligible predictive value;
2. a decomposition showing that the pooled association is a between-person (stable
   pessimism / financial position) phenomenon;
3. a measurement-error analysis of whether the null is a property of noisy reports or of the
   beliefs themselves.

Item 3 is the only open empirical question (S3c).

## What Phase 3 would need to do (bounded; about 4–6 weeks)

1. **Independent human validation** of the 50 histories, then set the flag by hand. Gate for
   everything else.
2. **One measurement-error extension, prespecified before running:**
   * a more efficient noise-robust within estimator, e.g. instrumenting with the average of
     t−2 and t−3 beliefs; or
   * an external report of the same belief, only if a linkable SCE module exists (IDs, timing
     and sample loss unverified).

   If the corrected within estimate stays inconclusive, report it as "the data cannot
   separate a small true effect from noise" and stop there.
3. **Literature:** re-read Mitra (2026) and Hartmann & Leth-Petersen (2024) full texts.
   Position the result as consistent with Mitra's finding that loss fear, not finding beliefs,
   drives behaviour. Confirm it is not already shown for debt expectations.
4. **Writing:** the thesis can be largely drafted from the Phase 1–2 outputs.

## Stop rules for Phase 3

* **Stop** if the human validation finds pipeline errors that change the sample by more than
  a few percent and the re-run changes the conclusions. In that case, report the correction
  instead.
* **Stop extending** (and write up) if the measurement-error extension remains inconclusive.
  Do not search further instruments.
* **Do not** relabel the pooled 0.30pp coefficient as a finding: it is between-person and
  disappears within person.

## Publication outlook

**Weak.** The result is a well-measured null on a subjective outcome, and it agrees with the
closest existing paper. No realised debt behaviour or debt-holding indicator is available. A
working paper is credible only if the measurement-error analysis gives a precise answer for
the true beliefs. Even then, the audience is narrow.

The decision between narrowing G-P2 and switching to the primary candidate (E-N01) is yours.
Nothing here depends on that choice.
