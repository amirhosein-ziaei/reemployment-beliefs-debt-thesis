# Phase 2 exploratory regression tables (generated; do not edit)

**EXPLORATORY — PENDING INDEPENDENT HUMAN VALIDATION. Associational, not causal. Not the validated-model output.**

Outcome: Q30new (pp). fd10 = (100 - Q22new)/10, so its coefficient is the change in Q30new for a 10pp *decrease* in the job-finding probability. loss10 = Q13new/10.


## Models A-C

| model | inference | term | coef | se | ci95_lo | ci95_hi | z | n_obs | n_persons |
|---|---|---|---|---|---|---|---|---|---|
| A | person-clustered | fd10 | 0.299 | 0.041 | 0.218 | 0.380 | 7.234 | 108388 | 15673 |
| A | person-clustered | loss10 | 2.372 | 0.083 | 2.211 | 2.534 | 28.753 | 108388 | 15673 |
| A | two-way person+month clustered | fd10 | 0.299 | 0.041 | 0.218 | 0.379 | 7.265 | 108388 | 15673 |
| A | two-way person+month clustered | loss10 | 2.372 | 0.083 | 2.210 | 2.535 | 28.592 | 108388 | 15673 |
| B | person-clustered | fd10 | -0.049 | 0.027 | -0.103 | 0.005 | -1.791 | 105648 | 12933 |
| B | person-clustered | loss10 | 1.085 | 0.051 | 0.985 | 1.184 | 21.387 | 105648 | 12933 |
| B | two-way person+month clustered | fd10 | -0.049 | 0.028 | -0.104 | 0.005 | -1.774 | 105648 | 12933 |
| B | two-way person+month clustered | loss10 | 1.085 | 0.052 | 0.983 | 1.186 | 20.965 | 105648 | 12933 |
| C | person-clustered | fd10 | -0.041 | 0.028 | -0.096 | 0.014 | -1.462 | 105648 | 12933 |
| C | person-clustered | loss10 | 1.086 | 0.051 | 0.987 | 1.185 | 21.469 | 105648 | 12933 |
| C | person-clustered | fd_x_loss_c | 0.039 | 0.013 | 0.013 | 0.065 | 2.913 | 105648 | 12933 |
| C | two-way person+month clustered | fd10 | -0.041 | 0.029 | -0.097 | 0.015 | -1.445 | 105648 | 12933 |
| C | two-way person+month clustered | loss10 | 1.086 | 0.052 | 0.985 | 1.187 | 21.040 | 105648 | 12933 |
| C | two-way person+month clustered | fd_x_loss_c | 0.039 | 0.013 | 0.013 | 0.065 | 2.922 | 105648 | 12933 |
| B | person-clustered; excludes 2020-03..2020-12 | fd10 | -0.072 | 0.028 | -0.127 | -0.016 | -2.535 | 98882 | 12669 |
| B | person-clustered; excludes 2020-03..2020-12 | loss10 | 1.054 | 0.051 | 0.954 | 1.154 | 20.677 | 98882 | 12669 |
| A | person-clustered; WLS with SCE weight | fd10 | 0.282 | 0.054 | 0.175 | 0.388 | 5.200 | 108367 | 15658 |
| A | person-clustered; WLS with SCE weight | loss10 | 2.806 | 0.111 | 2.589 | 3.024 | 25.297 | 108367 | 15658 |
| B | person-clustered; WLS with SCE weight | fd10 | -0.035 | 0.042 | -0.116 | 0.047 | -0.833 | 105640 | 12931 |
| B | person-clustered; WLS with SCE weight | loss10 | 1.308 | 0.079 | 1.153 | 1.463 | 16.493 | 105640 | 12931 |

## Model C: effect of a 10pp lower Q22new at given Q13new

| inference | q13new | effect_of_10pp_lower_q22 | se | ci95_lo | ci95_hi | classification | note |
|---|---|---|---|---|---|---|---|
| person-clustered | 0 | -0.094 | 0.029 | -0.151 | -0.038 | precisely small | centring mean of loss10 = 1.3588 (estimation sample) |
| person-clustered | 5 | -0.075 | 0.027 | -0.128 | -0.021 | precisely small | centring mean of loss10 = 1.3588 (estimation sample) |
| person-clustered | 20 | -0.016 | 0.032 | -0.078 | 0.046 | precisely small | centring mean of loss10 = 1.3588 (estimation sample) |
| person-clustered | 50 | 0.101 | 0.063 | -0.022 | 0.224 | precisely small | centring mean of loss10 = 1.3588 (estimation sample) |
| person-clustered | difference 50 vs 5 | 0.176 | 0.060 | 0.057 | 0.294 | precisely small | centring mean of loss10 = 1.3588 (estimation sample) |
| two-way | 0 | -0.094 | 0.028 | -0.149 | -0.040 | precisely small | centring mean of loss10 = 1.3588 (estimation sample) |
| two-way | 5 | -0.075 | 0.027 | -0.127 | -0.022 | precisely small | centring mean of loss10 = 1.3588 (estimation sample) |
| two-way | 20 | -0.016 | 0.033 | -0.080 | 0.048 | precisely small | centring mean of loss10 = 1.3588 (estimation sample) |
| two-way | 50 | 0.101 | 0.065 | -0.026 | 0.228 | precisely small | centring mean of loss10 = 1.3588 (estimation sample) |
| two-way | difference 50 vs 5 | 0.176 | 0.060 | 0.058 | 0.294 | precisely small | centring mean of loss10 = 1.3588 (estimation sample) |

## Within-person variation (Model B/C estimation sample)

| variable | n_obs | n_persons | sd_total | sd_within_person | share_var_within_person | sd_within_person_and_month | share_var_within_person_and_month |
|---|---|---|---|---|---|---|---|
| q30new | 105648 | 12933 | 20.583 | 10.871 | 0.279 | 10.843 | 0.278 |
| fd10 | 105648 | 12933 | 3.177 | 1.741 | 0.300 | 1.732 | 0.297 |
| loss10 | 105648 | 12933 | 1.920 | 1.193 | 0.386 | 1.189 | 0.383 |
| corr(fd10, loss10) within person & month | 105648 | 12933 | -0.011 |  |  |  |  |

## Prespecified sensitivity list (§8)

| spec | term | coef | se | ci95_lo | ci95_hi | n_obs | n_persons | classification | first_stage_F |
|---|---|---|---|---|---|---|---|---|---|
| B main | fd10 | -0.049 | 0.027 | -0.103 | 0.005 | 105648 | 12933 | precisely small |  |
| A main | fd10 | 0.299 | 0.041 | 0.218 | 0.380 | 108388 | 15673 | precisely small |  |
| S1 drop persons with Q30=0 in every month | fd10 | -0.053 | 0.032 | -0.116 | 0.010 | 89723 | 10806 | precisely small |  |
| S2a drop rows with any core item = 50 | fd10 | -0.037 | 0.029 | -0.093 | 0.019 | 87474 | 12113 | precisely small |  |
| S2b drop rows with Q22 in {0,100} | fd10 | -0.066 | 0.030 | -0.124 | -0.008 | 92132 | 12111 | precisely small |  |
| S3a drop rows with |dQ22| >= 50 vs previous month | fd10 | -0.037 | 0.034 | -0.104 | 0.030 | 99940 | 12855 | precisely small |  |
| S3b same-sample OLS (Model A, rows with t-1) | fd10 | 0.247 | 0.045 | 0.159 | 0.336 | 84278 | 12422 | precisely small |  |
| S3b 2SLS Model A, beliefs instrumented by t-1 values | fd10 | 0.329 | 0.063 | 0.206 | 0.452 | 84278 | 12422 | precisely small | {'fd10': 16689.2, 'loss10': 4616.0} |
| S3c same-sample first-difference OLS | d_fd10 | -0.059 | 0.031 | -0.121 | 0.002 | 68100 | 10697 | precisely small |  |
| S3c first-difference 2SLS, instruments at t-2 | d_fd10 | 0.831 | 0.719 | -0.579 | 2.240 | 68100 | 10697 | inconclusive | {'d_fd10': 30.0, 'd_loss10': 53.6} |
| S4a baseline-employed cohort (in main sample every observed month) | fd10 | -0.023 | 0.029 | -0.081 | 0.035 | 81469 | 9382 | precisely small |  |
| S4b add on-leave / temporarily laid off with Q12new = 1 | fd10 | -0.041 | 0.028 | -0.095 | 0.013 | 106881 | 13036 | precisely small |  |
| S5a persons with >= 6 analysis months | fd10 | -0.044 | 0.029 | -0.100 | 0.013 | 92891 | 9000 | precisely small |  |
| S5b person-equal weights (1/T_i) | fd10 | -0.060 | 0.033 | -0.125 | 0.004 | 105648 | 12933 | precisely small |  |
| S6a rows with an observed next-calendar-month response | fd10 | -0.038 | 0.030 | -0.096 | 0.020 | 85718 | 11218 | precisely small |  |
| S6b LPM: P(no response next month), tenure < 12 | fd10 | -0.002 | 0.000 | -0.003 | -0.001 | 103053 | 15645 | (attrition model; pp of probability x100 not applicable) |  |
| S6b LPM: P(no response next month), tenure < 12 | loss10 | -0.002 | 0.001 | -0.003 | -0.001 | 103053 | 15645 | (attrition model; pp of probability x100 not applicable) |  |
| S6b LPM: P(no response next month), tenure < 12 | q30_10 | 0.007 | 0.001 | 0.005 | 0.008 | 103053 | 15645 | (attrition model; pp of probability x100 not applicable) |  |
| S7a same-sample Model B (rows with sentiment controls) | fd10 | -0.049 | 0.027 | -0.103 | 0.005 | 105538 | 12932 | precisely small |  |
| S7a + Q4new/10 + Q1, Q2 dummies | fd10 | -0.078 | 0.027 | -0.130 | -0.025 | 105538 | 12932 | precisely small |  |
| S7b same-sample Model B (rows with t+1 belief) | fd10 | -0.036 | 0.029 | -0.094 | 0.021 | 82781 | 10925 | precisely small |  |
| S7b Model B + fd10 at t+1 (placebo) | fd10 | -0.037 | 0.029 | -0.094 | 0.020 | 82781 | 10925 | precisely small |  |
| S7b Model B + fd10 at t+1 (placebo) | fd10_f1 | 0.006 | 0.028 | -0.049 | 0.061 | 82781 | 10925 | placebo coefficient |  |
