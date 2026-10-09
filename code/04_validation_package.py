"""Phase 2 step 1: build the independent human-validation package.

Selects 50 respondent histories, stratified to cover survey years, employment
transitions, missing responses, probability endpoints (0/50/100), large changes
in Q22new, short and long panels, and months around the August-2013
questionnaire change. For every person-month it writes the raw workbook values,
the workbook row number, the derived values, the routing decision and a plain
explanation of each transformation, so a reviewer can check the pipeline
against the provider's Excel files by hand.

Everything written here is respondent-level and stays in data/review/
(gitignored). Only aggregate coverage counts are printed.

Usage: python code/04_validation_package.py [--n 50] [--seed 20261010] [--verify-xlsx]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from sce_common import CORE_VARS, DERIVED_DIR, EMP_STATUS_VARS, HEAP_POINTS, MICRODATA_FILES, RAW_DIR, REPO

REVIEW_DIR = REPO / "data" / "review"
CORE = list(CORE_VARS)
EXCEL_FIRST_DATA_ROW = 3  # row 1 = attribution preamble, row 2 = header (file_schema.csv: header_row = 1)
Q12_FIRST_MONTH = pd.Period("2013-08", "M")
NEAR_CHANGE = (pd.Period("2013-06", "M"), pd.Period("2013-10", "M"))
BIG_Q22_JUMP = 50

# Minimum number of persons per stratum; persons may count toward several strata.
QUOTAS = {
    "near_aug2013_change": 6,
    "employment_transition": 10,
    "missing_response": 8,
    "endpoint_heavy": 6,
    "large_q22_change": 8,
    "short_panel_1to3": 6,
    "long_panel_12plus": 6,
    "panel_13plus": 2,
}
MIN_PER_ENTRY_YEAR = 2


def excel_rows(raw_files: dict[str, Path]) -> pd.DataFrame:
    """userid × date → (file, Excel row) from the cached sheet, which keeps sheet order."""
    out = []
    for rel, cache in raw_files.items():
        df = pd.read_csv(cache, usecols=lambda c: c.strip().lower() in ("userid", "date"), low_memory=False)
        df.columns = [c.strip().lower() for c in df.columns]
        df["excel_row"] = np.arange(len(df)) + EXCEL_FIRST_DATA_ROW
        df["source_file"] = MICRODATA_FILES[rel]
        out.append(df)
    return pd.concat(out, ignore_index=True)


def person_features(d: pd.DataFrame) -> pd.DataFrame:
    d = d.sort_values(["userid", "month"])
    g = d.groupby("userid")
    gap1 = g["month"].diff().apply(lambda x: getattr(x, "n", np.nan)) == 1
    dq22 = g["q22new"].diff().abs().where(gap1)
    asked = d["emp_group"].isin(["employed: works for someone else"])
    endpoint = d[["q22new", "q30new"]].isin(HEAP_POINTS)
    f = pd.DataFrame({
        "first_year": g["month"].min().dt.year,
        "n_months": g.size(),
        "near_aug2013_change": g["month"].min().le(NEAR_CHANGE[1]) & g["month"].min().ge(NEAR_CHANGE[0]),
        "employment_transition": g["emp_group"].nunique() > 1,
        "missing_response": (asked & d[CORE].isna().any(axis=1)).groupby(d["userid"]).any()
        | d["q30new"].isna().groupby(d["userid"]).any()
        | d["emp_group"].eq("employed: Q12new missing").groupby(d["userid"]).any(),
        "endpoint_heavy": endpoint.where(d["analysis"]).mean(axis=1).groupby(d["userid"]).mean() >= 0.5,
        "large_q22_change": (dq22 >= BIG_Q22_JUMP).groupby(d["userid"]).any(),
    })
    f["short_panel_1to3"] = f["n_months"] <= 3
    f["long_panel_12plus"] = f["n_months"] >= 12
    f["panel_13plus"] = f["n_months"] >= 13
    return f


def select(f: pd.DataFrame, n: int, seed: int) -> list:
    rng = np.random.default_rng(seed)
    order = list(rng.permutation(f.index.to_numpy()))
    picks: list = []
    need = dict(QUOTAS)
    years = sorted(f["first_year"].unique())
    year_need = {y: MIN_PER_ENTRY_YEAR for y in years}

    def unmet(pid):
        r = f.loc[pid]
        return sum(need[k] > 0 and bool(r[k]) for k in need) + (year_need.get(r["first_year"], 0) > 0)

    # Greedy: repeatedly take the person who covers the most still-unmet strata.
    while len(picks) < n and (any(v > 0 for v in need.values()) or any(v > 0 for v in year_need.values())):
        cand = [p for p in order if p not in picks]
        scores = np.array([unmet(p) for p in cand[:4000]])
        if scores.max() == 0:
            break
        pid = cand[int(scores.argmax())]
        picks.append(pid)
        r = f.loc[pid]
        for k in need:
            if r[k]:
                need[k] -= 1
        year_need[r["first_year"]] = year_need.get(r["first_year"], 0) - 1
    # Fill the remainder at random, spreading across entry years.
    for y in years * n:
        if len(picks) >= n:
            break
        pool = [p for p in order if p not in picks and f.loc[p, "first_year"] == y]
        if pool:
            picks.append(pool[0])
    return picks[:n]


def routing(row) -> tuple[str, str]:
    """Return (decision, explanation) for one person-month, mirroring 02_build_panel.py."""
    ticks = [str(i) for i in range(1, 11) if row.get(f"q10_{i}") == 1]
    q10 = "Q10 ticks: " + (",".join(ticks) if ticks else "none")
    if not row["employed"]:
        return "EXCLUDED at S3 (not employed)", f"{q10}; neither 1 (full-time) nor 2 (part-time) ticked."
    if pd.isna(row["q12new"]):
        if row["month"] < Q12_FIRST_MONTH:
            why = "Q12new is not fielded before 2013-08, so employee status is unknown."
        elif row.get("q11") == 0:
            why = "Q11 = 0 jobs, so the questionnaire routes Q12new/Q13new/Q22new out."
        else:
            why = "Q12new blank (item non-response)."
        return "EXCLUDED at S4 (Q12new missing)", f"{q10}; {why}"
    if row["q12new"] != 1:
        return "EXCLUDED at S4 (self-employed)", f"{q10}; Q12new = {row['q12new']:.0f} (2 = self-employed); Q13new/Q22new not asked."
    for step, v in (("S5", "q13new"), ("S6", "q22new"), ("S7", "q30new")):
        if pd.isna(row[v]):
            raw = row[v + "_raw"]
            why = "blank" if pd.isna(raw) else f"raw value '{raw}' is non-numeric or outside 0-100"
            return f"EXCLUDED at {step} ({v} invalid)", f"{q10}; Q12new = 1; {v} {why}."
    return "ELIGIBLE (analysis sample)", f"{q10}; Q12new = 1; Q13new, Q22new, Q30new all valid 0-100."


def explain(row) -> str:
    parts = []
    if pd.notna(row["q22new"]):
        parts.append(f"finding_difficulty = 100 - Q22new = 100 - {row['q22new']:g} = {100 - row['q22new']:g}")
    for v in CORE:
        raw, clean = row[v + "_raw"], row[v]
        if pd.notna(raw) and pd.notna(clean) and float(raw) != clean:
            parts.append(f"{v}: raw {raw} -> {clean}")
    if pd.notna(row.get("d_q22_consecutive")):
        parts.append(f"change in Q22new from previous calendar month = {row['d_q22_consecutive']:+g}")
    if row.get("gap_months", 1) > 1:
        parts.append(f"gap of {int(row['gap_months'])} months since previous response (tenure counts surveys, not months)")
    if row["month"] < NEAR_CHANGE[1]:
        parts.append("near Aug-2013 questionnaire change (Q12new introduced; Q22new no longer asked of self-employed)")
    return "; ".join(parts)


def expected_routing(row) -> str:
    """What the questionnaire filter implies for Q13new/Q22new (DOC-P1)."""
    universe = any(row.get(f"q10_{i}") == 1 for i in (1, 2, 4, 5))
    if not universe:
        return "Q13/Q22 not asked (Q10 has none of 1,2,4,5)"
    if row.get("q11") == 0:
        return "Q13/Q22 not asked (Q11 = 0)"
    if row["month"] < Q12_FIRST_MONTH:
        return "Q22 asked of all workers; Q13 asked unless self-employed (Q12new not in public file)"
    if row["q12new"] == 2:
        return "Q13/Q22 not asked (self-employed)"
    return "Q13/Q22 asked"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=50)
    ap.add_argument("--seed", type=int, default=20261010)
    ap.add_argument("--derived", default=str(DERIVED_DIR))
    ap.add_argument("--out", default=str(REVIEW_DIR))
    ap.add_argument("--verify-xlsx", action="store_true",
                    help="re-read the selected rows directly from the provider .xlsx files and compare")
    args = ap.parse_args()
    derived, out = Path(args.derived), Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    d = pd.read_csv(derived / "panel_all.csv.gz", low_memory=False)
    d["month"] = pd.PeriodIndex(d["month"], freq="M")
    f = person_features(d)
    picks = select(f, args.n, args.seed)

    h = d[d["userid"].isin(picks)].sort_values(["userid", "month"]).copy()
    g = h.groupby("userid")
    h["gap_months"] = g["month"].diff().apply(lambda x: getattr(x, "n", np.nan))
    h["d_q22_consecutive"] = g["q22new"].diff().where(h["gap_months"] == 1)
    h["finding_difficulty"] = 100 - h["q22new"]
    caches = {rel: derived / (Path(fn).stem + ".csv.gz") for rel, fn in MICRODATA_FILES.items()}
    rows = excel_rows({k: v for k, v in caches.items() if v.exists()})
    h = h.merge(rows, on=["userid", "date"], how="left")
    h["routing_decision"], h["routing_explanation"] = zip(*h.apply(routing, axis=1))
    h["questionnaire_filter_implies"] = h.apply(expected_routing, axis=1)
    h["transformations"] = h.apply(explain, axis=1)
    rid = {u: f"R{i + 1:02d}" for i, u in enumerate(sorted(picks, key=lambda u: (f.loc[u, "first_year"], u)))}
    h.insert(0, "review_id", h["userid"].map(rid))
    h["survey_month"] = h["month"].astype(str)

    cols = (["review_id", "survey_month", "source_file", "excel_row", "date", "tenure", "weight",
             *EMP_STATUS_VARS, "q11", "q12new", "q13new_raw", "q22new_raw", "q30new_raw",
             "emp_group", "employed", "employee", "q13new", "q22new", "q30new", "finding_difficulty",
             "gap_months", "d_q22_consecutive", "analysis", "routing_decision", "routing_explanation",
             "questionnaire_filter_implies", "transformations"])
    h = h.sort_values(["review_id", "survey_month"])
    h[cols].to_csv(out / "validation_histories.csv", index=False)
    h[["review_id", "userid", "source_file"]].drop_duplicates().to_csv(out / "validation_key.csv", index=False)

    strata = f.loc[picks].copy()
    strata.insert(0, "review_id", strata.index.map(rid))
    strata = strata.sort_values("review_id")
    strata.to_csv(out / "validation_strata.csv", index=False)
    form = strata[["review_id", "first_year", "n_months"]].copy()
    for c in ["raw_values_match_xlsx", "routing_decision_correct", "transformations_correct",
              "questionnaire_filter_consistent", "issues_found", "reviewer_initials", "review_date"]:
        form[c] = ""
    form.to_csv(out / "review_form.csv", index=False)

    if args.verify_xlsx:
        verify(h)

    cov = {k: int(strata[k].sum()) for k in QUOTAS}
    print(f"Selected {len(picks)} persons, {len(h)} person-months -> {out}")
    print("Coverage (persons):", cov)
    print("Entry years:", strata["first_year"].value_counts().sort_index().to_dict())
    print("Routing decisions (rows):", h["routing_decision"].value_counts().to_dict())
    return 0


def verify(h: pd.DataFrame) -> None:
    """Compare selected rows with the provider workbooks cell by cell (slow; read-only)."""
    from openpyxl import load_workbook
    raw_dir = max(p for p in RAW_DIR.glob("*") if p.is_dir())
    check = ["userid", "date", "q10_1", "q10_2", "q12new", "q13new", "q22new", "q30new"]
    bad = 0
    for fn, sub in h.groupby("source_file"):
        ws = load_workbook(raw_dir / fn, read_only=True)["Data"]
        header = [str(c.value).strip().lower() for c in next(ws.iter_rows(min_row=2, max_row=2))]
        idx = {c: header.index(c) for c in check}
        want = dict(zip(sub["excel_row"], sub.to_dict("records")))
        for r_i, row in enumerate(ws.iter_rows(min_row=EXCEL_FIRST_DATA_ROW, values_only=True),
                                  start=EXCEL_FIRST_DATA_ROW):
            if r_i in want:
                rec = want.pop(r_i)
                for c in check:
                    a = row[idx[c]]
                    b = rec[c + "_raw"] if c in CORE else rec[c]
                    if not ((a is None and pd.isna(b)) or (a is not None and pd.notna(b) and float(a) == float(b))):
                        bad += 1
                        print(f"MISMATCH {rec['review_id']} {fn} row {r_i} {c}: xlsx={a!r} package={b!r}")
            if not want:
                break
        bad += len(want)
    print(f"xlsx verification: {'all selected rows match' if bad == 0 else f'{bad} mismatches'}")


if __name__ == "__main__":
    sys.exit(main())
