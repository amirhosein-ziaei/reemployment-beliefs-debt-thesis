"""Phase 2 step 4: the one prespecified prediction comparison (model_specification.md §7).

Target: the same person's Q30new in the next calendar month (t+1 exactly).
Baseline: Q30_t, Q13_t, tenure_t, calendar-month-of-year dummies.
Expanded: baseline + fd10_t + centred fd10_t x loss10_t (centring on training data).
Evaluation 1: 5-fold person-held-out CV; person-cluster bootstrap of loss differences.
Evaluation 2: expanding-window forward years 2016-2025; calendar-month block bootstrap.

EXPLORATORY — pending independent human validation. Output: outputs/exploratory/.

Usage: python code/06_prediction.py [--B 999]
"""
from __future__ import annotations

import argparse
import sys

import numpy as np
import pandas as pd

import phase2_lib as L
from sce_common import DERIVED_DIR, GEN_DIR, OUT_DIR, md_table

EXP = OUT_DIR / "exploratory"
SEED = 20261010
K = 5
TEST_YEARS = range(2016, 2026)
MOY = [f"moy_{m}" for m in range(2, 13)]
BASE = ["q30new", "q13new", "tenure", *MOY]
EXPANDED = [*BASE, "fd10", "fdxloss"]


def load_pairs() -> tuple[pd.DataFrame, dict]:
    a = pd.read_csv(DERIVED_DIR / "panel_analysis.csv.gz", low_memory=False)
    allr = pd.read_csv(DERIVED_DIR / "panel_all.csv.gz", low_memory=False)
    allr = allr[allr["key_ok"] & allr["key_first"]]
    for d in (a, allr):
        d["month"] = pd.PeriodIndex(d["month"], freq="M")
        d["mnum"] = L.month_num(d["month"])
    a["fd10"] = (100 - a["q22new"]) / 10
    a["loss10"] = a["q13new"] / 10
    for m in range(2, 13):
        a[f"moy_{m}"] = (a["month"].dt.month == m).astype(float)
    p = L.next_month_pairs(a, allr)
    later = allr[["userid", "mnum"]].rename(columns={"mnum": "m_later"})
    any_later = p[["userid", "mnum"]].merge(later, on="userid")
    any_later = any_later[any_later["m_later"] > any_later["mnum"]].groupby(["userid", "mnum"]).size()
    p = p.merge(any_later.rename("n_later").reset_index(), on=["userid", "mnum"], how="left")
    info = {
        "analysis_rows": len(p),
        "with_next_month_target": int(p["q30_next"].notna().sum()),
        "later_response_after_gap_only": int((p["q30_next"].isna() & p["n_later"].notna()).sum()),
        "no_later_response (exit/attrition)": int(p["n_later"].isna().sum()),
    }
    return p[p["q30_next"].notna()].copy(), info


def add_centred(train: pd.DataFrame, test: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    mf, ml = train["fd10"].mean(), train["loss10"].mean()  # training data only
    out = []
    for d in (train, test):
        d = d.copy()
        d["fdxloss"] = (d["fd10"] - mf) * (d["loss10"] - ml)
        out.append(d)
    return out[0], out[1]


def evaluate(p: pd.DataFrame, B: int) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    rows, by_unit = [], []
    y = p["q30_next"].to_numpy(float)

    # ---- Evaluation 1: person held out
    p = p.assign(fold=L.person_folds(p["userid"], K, SEED).to_numpy())
    pb, pe = np.empty(len(p)), np.empty(len(p))
    for k in range(K):
        tr, te = add_centred(p[p["fold"] != k], p[p["fold"] == k])
        idx = (p["fold"] == k).to_numpy()
        pb[idx] = L.ols_fit_predict(tr, te, BASE, "q30_next")
        pe[idx] = L.ols_fit_predict(tr, te, EXPANDED, "q30_next")
        s = L.loss_summary(y[idx], pb[idx], pe[idx])
        by_unit.append(dict(evaluation="person held out", unit=f"fold {k}", **s))
    s = L.loss_summary(y, pb, pe)
    bs = L.loss_diff_bootstrap(y - pb, y - pe, p["userid"].to_numpy(), B, SEED)
    rows.append(dict(evaluation="1. person held out (5 folds)", **s, **bs,
                     classification=L.classify_prediction(s["rmse_rel"], *bs["rmse_rel_ci"])))

    # ---- Evaluation 2: forward calendar time (expanding window)
    for drop_seen in (False, True):
        ys, pbs, pes, months = [], [], [], []
        for Y in TEST_YEARS:
            tr = p[p["mnum"] + 1 <= (Y - 1) * 12 + 11]          # target month <= Dec(Y-1)
            te = p[p["month"].dt.year == Y]
            if drop_seen:
                te = te[~te["userid"].isin(tr["userid"])]
            if te.empty:
                continue
            tr, te = add_centred(tr, te)
            b_, e_ = L.ols_fit_predict(tr, te, BASE, "q30_next"), L.ols_fit_predict(tr, te, EXPANDED, "q30_next")
            yy = te["q30_next"].to_numpy(float)
            if not drop_seen:
                by_unit.append(dict(evaluation="forward", unit=f"test year {Y} (train n={len(tr)})",
                                    **L.loss_summary(yy, b_, e_)))
            ys.append(yy), pbs.append(b_), pes.append(e_), months.append(te["mnum"].to_numpy())
        yy, b_, e_, mm = map(np.concatenate, (ys, pbs, pes, months))
        s = L.loss_summary(yy, b_, e_)
        bs = L.loss_diff_bootstrap(yy - b_, yy - e_, mm, B, SEED)
        lab = ("2b. forward years 2016-2025, test persons unseen in training (secondary)" if drop_seen
               else "2. forward years 2016-2025 (expanding window)")
        rows.append(dict(evaluation=lab, **s, **bs, classification=L.classify_prediction(s["rmse_rel"], *bs["rmse_rel_ci"])))

    # Full-sample expanded fit, for interpretation only (not an evaluation)
    tr, _ = add_centred(p, p.head(1))
    X = np.column_stack([np.ones(len(tr)), tr[EXPANDED].to_numpy(float)])
    b = np.linalg.lstsq(X, tr["q30_next"].to_numpy(float), rcond=None)[0]
    coefs = pd.DataFrame(dict(term=["const", *EXPANDED], coef=b))
    coefs = coefs[~coefs["term"].str.startswith("moy_")]
    return pd.DataFrame(rows), pd.DataFrame(by_unit), coefs


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--B", type=int, default=999)
    args = ap.parse_args()
    L.require_automated_checks(GEN_DIR)
    EXP.mkdir(parents=True, exist_ok=True)
    p, info = load_pairs()
    res, units, coefs = evaluate(p, args.B)
    flat = res.copy()
    for c in [c for c in flat.columns if c.endswith("_ci")]:
        flat[c + "_lo"], flat[c + "_hi"] = zip(*flat.pop(c))
    flat.to_csv(EXP / "prediction_results.csv", index=False)
    units.to_csv(EXP / "prediction_by_fold_and_year.csv", index=False)
    coefs.to_csv(EXP / "prediction_full_sample_coefficients.csv", index=False)
    pd.Series(info).to_csv(EXP / "prediction_sample.csv", header=["n"])
    show = ["evaluation", "n", "rmse_base", "rmse_exp", "rmse_diff", "rmse_diff_ci_lo", "rmse_diff_ci_hi", "rmse_rel",
            "rmse_rel_ci_lo", "rmse_rel_ci_hi", "mae_base", "mae_exp", "mae_diff", "mae_diff_ci_lo", "mae_diff_ci_hi",
            "mae_rel", "classification"]
    parts = ["# Phase 2 prediction comparison (generated; do not edit)\n", f"**{L.EXPLORATORY_LABEL}**\n",
             "Target: Q30new at t+1 (next calendar month). Differences are baseline minus expanded "
             "(positive = adding Q22new helps). *_rel are fractions of the baseline metric.\n",
             "\n## Sample\n", md_table(pd.Series(info).rename("n").reset_index()),
             "\n## Results\n", md_table(flat[show], "{:.4f}"),
             "\n## By fold and test year\n", md_table(units, "{:.4f}"),
             "\n## Full-sample expanded model coefficients (interpretation only)\n", md_table(coefs, "{:.4f}")]
    (EXP / "prediction_tables.md").write_text("\n".join(parts) + "\n")
    print("\n".join(parts))
    return 0


if __name__ == "__main__":
    sys.exit(main())
