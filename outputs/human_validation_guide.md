# Independent human validation guide (G-P2)

**Status: NOT DONE.** Independent human validation has not happened. The Phase 1 trace and the
Phase 2 cell-by-cell xlsx check were run by the AI assistant and by code. They are automated
checks, not independent review. `manual_history_review_done` in
`outputs/generated/validation_flags.json` stays `false` until **you** finish the steps below and
change it by hand.

Until then, every Phase 2 estimate is labelled *EXPLORATORY — PENDING INDEPENDENT HUMAN
VALIDATION* and lives in `outputs/exploratory/`.

## 1. What the package contains (local and private)

Build it with:

```bash
python code/04_validation_package.py              # ~30 s
python code/04_validation_package.py --verify-xlsx  # optional: re-reads the .xlsx cells (~10 min)
```

Everything goes to `data/review/`, which is **gitignored**. Never commit, upload or share these
files: they are respondent-level survey data with the SCE respondent ID.

| File | Content |
| - | - |
| `validation_histories.csv` | One row per person-month (441 rows, 50 persons). Columns are described in §3 |
| `validation_key.csv` | `review_id` (R01…R50) → SCE `userid` and source workbook. Needed to find the rows in Excel |
| `validation_strata.csv` | Why each person was selected (stratum flags, entry year, months observed) |
| `review_form.csv` | One row per person, with empty columns for your verdicts |

The package is regenerated deterministically (seed 20261010). The same 50 persons come back
each time unless the data or the script change.

## 2. How the 50 histories were chosen

Persons were picked greedily until every stratum quota was met, then topped up across survey
entry years. One person can count toward several strata.

| Stratum (person-level) | Quota | Covered |
| - | - | - |
| First observed 2013-06 to 2013-10: around the Aug-2013 questionnaire change (Q12new introduced; Q22new no longer asked of the self-employed) | 6 | 8 |
| Employment transition (employment group changes during the panel) | 10 | 13 |
| Missing response (blank core item where asked, blank Q30new, or Q12new missing while employed) | 8 | 11 |
| Endpoint-heavy: ≥ 50% of analysis answers to Q22new/Q30new at 0, 50 or 100 | 6 | 17 |
| Large change in job-finding belief: \|ΔQ22new\| ≥ 50pp between consecutive months | 8 | 14 |
| Short panel (1–3 months) | 6 | 11 |
| Long panel (≥ 12 months) | 6 | 26 |
| Very long panel (13+ months) | 2 | 5 |
| Entry year: ≥ 2 persons per year 2013–2025 | 2 each | 3–8 each |

The 441 rows include 315 analysis-sample rows and 126 excluded rows:
* 98 not employed;
* 14 with Q12new missing;
* 12 self-employed;
* 1 with an invalid Q13new;
* 1 with an invalid Q30new.

## 3. Columns in `validation_histories.csv`

| Group | Columns | Meaning |
| - | - | - |
| Locator | `review_id`, `survey_month`, `source_file`, `excel_row` | `excel_row` is the 1-based row in the workbook's `Data` sheet. Row 1 is the attribution line, row 2 the header, data start in row 3 |
| Raw values (as in the workbook) | `date`, `tenure`, `weight`, `q10_1`…`q10_10`, `q11`, `q12new`, `q13new_raw`, `q22new_raw`, `q30new_raw` | Untransformed values |
| Derived | `emp_group`, `employed`, `employee`, `q13new`, `q22new`, `q30new`, `finding_difficulty`, `gap_months`, `d_q22_consecutive`, `analysis` | Pipeline output (`code/02_build_panel.py`, `sce_common.py`) |
| Decision | `routing_decision` | Which audit step (S3–S7) excludes the row, or ELIGIBLE |
| Explanations | `routing_explanation`, `transformations` | Plain-text reason, e.g. `finding_difficulty = 100 - Q22new = 100 - 40 = 60` |
| Questionnaire | `questionnaire_filter_implies` | Whether Q13new and Q22new *should* have been asked, given Q10, Q11, Q12new and the date |

## 4. Step-by-step review (about 3–4 hours for 50 persons)

**Materials.**
* The four workbooks and the questionnaire in `data/raw/2026-10-09/`. Check their SHA-256
  against `outputs/generated/download_manifest.csv` first (`sha256sum data/raw/2026-10-09/*`).
* The questionnaire PDF pages you need: Q10 (p. 11), Q11/Q12new (p. 12), Q13new (p. 14),
  Q22new (p. 17), Q30new (p. 21), error/help texts E1, H2, H7 (p. 42 onward).

**Workbook columns** (row 2 holds the names):

| Field | 13-16 and 17-19 files | 20-24 and latest files |
| - | - | - |
| date / userid / tenure / weight | A / B / C / D | A / B / C / D |
| Q10_1, Q10_2, Q10_3, Q10_4, Q10_5, Q10_7 | AW, AX, AY, AZ, BA, BC | BF, BG, BH, BI, BJ, BL |
| Q11 / Q12new | BG / BH | BP / BQ |
| Q13new / Q22new / Q30new | BQ / BZ / DB | BZ / CI / DK |

**For each `review_id`** (record results in `review_form.csv`):

1. **Locate.**
   * Look up the `userid` in `validation_key.csv` and open the `source_file` workbook.
   * For each row of the history, go to `excel_row` (Excel: Ctrl+G, e.g. `B2056`).
   * Confirm that column B is the `userid` and column A is the `date` (YYYYMM).
   * Spot-check that searching the userid in column B finds no *other* rows that are missing
     from the history. Months in the next file count only for persons who straddle a file
     boundary; the history spans files.
2. **Raw values.**
   * Compare the Q10 boxes, Q11, Q12new, Q13new, Q22new and Q30new cells with the `raw`
     columns. Blanks in Excel should be blank (NaN) in the package.
   * Mark `raw_values_match_xlsx` = yes/no.
3. **Routing decision.** Apply the rule yourself:
   * **Employed** = Q10_1 = 1 or Q10_2 = 1 (otherwise excluded at S3).
   * **Employee** = Q12new = 1. Q12new = 2 is self-employed (S4); Q12new blank is S4.
     Q12new is blank in every row before 2013-08 and when Q11 = 0.
   * Then Q13new, Q22new and Q30new must each be numeric and within 0–100 (S5, S6, S7).
   * Mark `routing_decision_correct`.
4. **Questionnaire consistency.**
   * Using pp. 11–21, check that Q13new and Q22new are answered only when the filter allows:
     Q10 includes 1, 2, 4 or 5; Q11 > 0; Q12new not self-employed (for Q22new, "as of
     August 2013").
   * Check that Q30new is answered regardless of employment.
   * Mark `questionnaire_filter_consistent`. A respondent skipping an allowed item is fine
     (E1 is only a soft prompt). An answer where the filter forbids one is an issue.
5. **Transformations.** Recompute by hand:
   * `finding_difficulty = 100 − Q22new`;
   * the month gap from the previous response (`tenure` counts surveys, not months, so they
     can differ);
   * the change in Q22new from the previous **calendar** month (blank if there is a gap).

   Mark `transformations_correct`.
6. **Anything odd** (implausible Q11, 0↔100 flips, weights, duplicated months) goes in
   `issues_found`, with the row's `survey_month`.

## 5. Sample-level checks (about 30 minutes; aggregate files only)

* `outputs/sample_audit.csv`: every step's `rows_excluded` equals the previous minus the
  current `n_rows`. S0 per release matches the row counts of the four workbooks (Excel: last
  row number − 2).
* `outputs/generated/routing_by_group.csv`: self-employed and non-workers answer Q13new and
  Q22new at 0%; Q30new is answered by every group.
* `outputs/generated/q22_routing_by_month.csv`: the first month is 2013-08.

## 6. Pass criteria and what to do next

| Outcome | Rule | Action |
| - | - | - |
| **Pass** | All 50 persons have correct raw values and routing; any issues are documented anomalies in the provider data, not pipeline errors | Set `"manual_history_review_done": true` in `outputs/generated/validation_flags.json` **by hand**, commit it with your initials and date in the message, and keep the filled `review_form.csv` privately |
| **Fix needed** | Any raw-value mismatch or wrong routing decision caused by the code | Do not set the flag. Record the review_id and month, fix the code, rerun 02 → 04, and re-review the affected persons plus 10 new ones |
| **Provider anomaly** | The data contradict the questionnaire (e.g. an answer where the filter forbids it) | Document it in `variable_validation.md`. It is not a pipeline failure, but decide whether those rows should be excluded |

Note: `02_build_panel.py` rewrites `validation_flags.json` with
`manual_history_review_done = false` each time it runs. Set the flag after the last rebuild.

Once the flag is true, `code/03_descriptives.py` runs the gated model on the validated path.
Only then may Phase 2 estimates be re-labelled as validated. That requires re-running and
re-reading them; exploratory outputs are not relabelled in place.
