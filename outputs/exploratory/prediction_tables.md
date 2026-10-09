# Phase 2 prediction comparison (generated; do not edit)

**EXPLORATORY — PENDING INDEPENDENT HUMAN VALIDATION. Associational, not causal. Not the validated-model output.**

Target: Q30new at t+1 (next calendar month). Differences are baseline minus expanded (positive = adding Q22new helps). *_rel are fractions of the baseline metric.


## Sample

| index | n |
|---|---|
| analysis_rows | 108388 |
| with_next_month_target | 87320 |
| later_response_after_gap_only | 6723 |
| no_later_response (exit/attrition) | 14345 |

## Results

| evaluation | n | rmse_base | rmse_exp | rmse_diff | rmse_diff_ci_lo | rmse_diff_ci_hi | rmse_rel | rmse_rel_ci_lo | rmse_rel_ci_hi | mae_base | mae_exp | mae_diff | mae_diff_ci_lo | mae_diff_ci_hi | mae_rel | classification |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1. person held out (5 folds) | 87320 | 13.6016 | 13.5991 | 0.0024 | 0.0004 | 0.0045 | 0.0002 | 0.0000 | 0.0003 | 7.3407 | 7.3345 | 0.0062 | 0.0026 | 0.0098 | 0.0008 | negligible |
| 2. forward years 2016-2025 (expanding window) | 70030 | 13.4942 | 13.4912 | 0.0030 | 0.0016 | 0.0045 | 0.0002 | 0.0001 | 0.0003 | 7.2426 | 7.2318 | 0.0108 | 0.0086 | 0.0130 | 0.0015 | negligible |
| 2b. forward years 2016-2025, test persons unseen in training (secondary) | 48681 | 13.9811 | 13.9780 | 0.0031 | 0.0016 | 0.0048 | 0.0002 | 0.0001 | 0.0003 | 7.5823 | 7.5718 | 0.0105 | 0.0076 | 0.0132 | 0.0014 | negligible |

## By fold and test year

| evaluation | unit | n | rmse_base | rmse_exp | rmse_diff | rmse_rel | mae_base | mae_exp | mae_diff | mae_rel |
|---|---|---|---|---|---|---|---|---|---|---|
| person held out | fold 0 | 17495 | 13.1312 | 13.1260 | 0.0052 | 0.0004 | 7.1072 | 7.0969 | 0.0103 | 0.0015 |
| person held out | fold 1 | 17447 | 13.5597 | 13.5565 | 0.0032 | 0.0002 | 7.3972 | 7.3952 | 0.0020 | 0.0003 |
| person held out | fold 2 | 17510 | 13.6175 | 13.6140 | 0.0036 | 0.0003 | 7.3830 | 7.3744 | 0.0086 | 0.0012 |
| person held out | fold 3 | 17285 | 13.8872 | 13.8857 | 0.0015 | 0.0001 | 7.4800 | 7.4677 | 0.0123 | 0.0016 |
| person held out | fold 4 | 17583 | 13.8020 | 13.8030 | -0.0010 | -0.0001 | 7.3378 | 7.3400 | -0.0022 | -0.0003 |
| forward | test year 2016 (train n=16719) | 7339 | 14.2634 | 14.2628 | 0.0006 | 0.0000 | 7.7898 | 7.7861 | 0.0037 | 0.0005 |
| forward | test year 2017 (train n=24002) | 7356 | 14.0025 | 14.0000 | 0.0024 | 0.0002 | 7.4845 | 7.4719 | 0.0126 | 0.0017 |
| forward | test year 2018 (train n=31405) | 7244 | 13.2441 | 13.2436 | 0.0005 | 0.0000 | 7.2787 | 7.2671 | 0.0116 | 0.0016 |
| forward | test year 2019 (train n=38611) | 7344 | 14.1975 | 14.1946 | 0.0028 | 0.0002 | 7.5380 | 7.5175 | 0.0205 | 0.0027 |
| forward | test year 2020 (train n=45972) | 6835 | 13.3203 | 13.3239 | -0.0035 | -0.0003 | 7.1916 | 7.2023 | -0.0107 | -0.0015 |
| forward | test year 2021 (train n=52810) | 7399 | 11.3622 | 11.3559 | 0.0063 | 0.0006 | 5.9670 | 5.9555 | 0.0115 | 0.0019 |
| forward | test year 2022 (train n=60168) | 7834 | 12.0775 | 12.0713 | 0.0063 | 0.0005 | 6.4559 | 6.4323 | 0.0236 | 0.0037 |
| forward | test year 2023 (train n=68021) | 7351 | 14.0877 | 14.0805 | 0.0072 | 0.0005 | 7.4662 | 7.4475 | 0.0187 | 0.0025 |
| forward | test year 2024 (train n=75387) | 6536 | 14.4858 | 14.4792 | 0.0066 | 0.0005 | 7.8115 | 7.8007 | 0.0108 | 0.0014 |
| forward | test year 2025 (train n=82057) | 4792 | 13.8907 | 13.8903 | 0.0004 | 0.0000 | 7.7356 | 7.7357 | -0.0000 | -0.0000 |

## Full-sample expanded model coefficients (interpretation only)

| term | coef |
|---|---|
| const | 1.5859 |
| q30new | 0.7307 |
| q13new | 0.0395 |
| tenure | -0.0424 |
| fd10 | 0.0858 |
| fdxloss | -0.0062 |
