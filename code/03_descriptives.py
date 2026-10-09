"""Step 3: preliminary descriptives and (only if validated) one small,
clearly labelled association model.

Reads data/derived/panel_analysis.csv.gz and outputs/generated/validation_flags.json.
Writes outputs/generated/descriptives_tables.md and CSVs in outputs/generated/.

The model is an associational two-way fixed-effects regression of Q30new on
finding difficulty (100 - Q22new) and Q13new; it is NOT causal and does not
predict actual delinquency. It runs only if validation_flags.json says
validated_for_preliminary_model = true AND manual_history_review_done = true
(or with --force for a code smoke test).

Usage: python code/03_descriptives.py [--force]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from sce_common import DERIVED_DIR, OUT_DIR, md_table


def bins(s: pd.Series, edges, labels) -> pd.Series:
    return pd.cut(s, edges, labels=labels, include_lowest=True, right=True)


LOSS_EDGES, LOSS_LAB = [0, 0.5, 10, 25, 50, 100], ["0", "1-10", "11-25", "26-50", "51-100"]
FD_EDGES, FD_LAB = [0, 25, 50, 75, 100], ["0-25 (easy)", "26-50", "51-75", "76-100 (hard)"]


def wmean(x, w):
    m = x.notna() & w.notna()
    return float(np.average(x[m], weights=w[m])) if m.any() and w[m].sum() > 0 else np.nan


def distributions(a: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for v in ["q13new", "q22new", "q30new", "finding_difficulty"]:
        x = a[v]
        r = dict(variable=v, n=int(x.notna().sum()), mean=x.mean(),
                 weighted_mean=wmean(x, a["weight"]) if "weight" in a else np.nan, sd=x.std())
        for q in [0.1, 0.25, 0.5, 0.75, 0.9]:
            r[f"p{int(q*100)}"] = x.quantile(q)
        rows.append(r)
    return pd.DataFrame(rows)


def by_year(a):
    return a.groupby("year").agg(n_rows=("userid", "size"), n_persons=("userid", "nunique"),
                                 mean_q13new=("q13new", "mean"), mean_q22new=("q22new", "mean"),
                                 mean_q30new=("q30new", "mean")).reset_index()


def binned(a: pd.DataFrame) -> pd.DataFrame:
    a = a.assign(loss_bin=bins(a["q13new"], LOSS_EDGES, LOSS_LAB),
                 fd_bin=bins(a["finding_difficulty"], FD_EDGES, FD_LAB))
    t = a.groupby(["loss_bin", "fd_bin"], observed=False).agg(
        n_rows=("userid", "size"), n_persons=("userid", "nunique"),
        mean_q30new=("q30new", "mean"), median_q30new=("q30new", "median"),
        share_q30_eq0=("q30new", lambda s: (s == 0).mean())).reset_index()
    return t


def within_binned(a: pd.DataFrame) -> pd.DataFrame:
    """Person-demeaned Q30 by person-demeaned finding difficulty (multi-month persons)."""
    a = a[a.groupby("userid")["userid"].transform("size") >= 2].copy()
    for v in ["q30new", "finding_difficulty", "q13new"]:
        a[v + "_dm"] = a[v] - a.groupby("userid")[v].transform("mean")
    a["fd_dm_bin"] = pd.cut(a["finding_difficulty_dm"], [-101, -15, -5, 5, 15, 101],
                            labels=["< -15", "-15..-5", "-5..5", "5..15", "> 15"])
    return a.groupby("fd_dm_bin", observed=False).agg(
        n_rows=("userid", "size"), n_persons=("userid", "nunique"),
        mean_q30_dm=("q30new_dm", "mean"), mean_q13_dm=("q13new_dm", "mean")).reset_index()


def first_diff(a: pd.DataFrame) -> pd.DataFrame:
    a = a.sort_values(["userid", "month"]).copy()
    g = a.groupby("userid")
    gap = (a["month"] - g["month"].shift(1)).apply(lambda x: getattr(x, "n", np.nan))
    a["d_fd"], a["d_q30"], a["d_q13"] = g["finding_difficulty"].diff(), g["q30new"].diff(), g["q13new"].diff()
    a = a[gap == 1]
    a["d_fd_cat"] = pd.cut(a["d_fd"], [-101, -10.5, 10.5, 101],
                           labels=["finding got easier (>10pp)", "stable (-10..10pp)", "finding got harder (>10pp)"])
    return a.groupby("d_fd_cat", observed=False).agg(
        n_pairs=("userid", "size"), mean_d_q30=("d_q30", "mean"),
        share_q30_up=("d_q30", lambda s: (s > 0).mean()),
        share_q30_down=("d_q30", lambda s: (s < 0).mean()),
        mean_d_q13=("d_q13", "mean")).reset_index()


# ------------------------------------------------------------- two-way FE with clustered SE
def demean_2way(X: np.ndarray, g1: np.ndarray, g2: np.ndarray, tol=1e-10, maxit=500) -> np.ndarray:
    Z = X.astype(float).copy()
    for _ in range(maxit):
        prev = Z.copy()
        for g in (g1, g2):
            cnt = np.bincount(g)
            for j in range(Z.shape[1]):
                Z[:, j] -= (np.bincount(g, Z[:, j]) / cnt)[g]
        if np.max(np.abs(Z - prev)) < tol:
            break
    return Z


def fe_ols(df: pd.DataFrame, y: str, xs: list[str], person_fe: bool = True) -> pd.DataFrame:
    d = df[[y, *xs, "userid", "month"]].dropna()
    pid = pd.factorize(d["userid"])[0]
    mid = pd.factorize(d["month"])[0]
    M = d[[y, *xs]].to_numpy(float)
    if person_fe:
        Z = demean_2way(M, pid, mid)
    else:
        cnt = np.bincount(mid)
        Z = M - np.vstack([(np.bincount(mid, M[:, j]) / cnt)[mid] for j in range(M.shape[1])]).T
    yv, X = Z[:, 0], Z[:, 1:]
    XtX_inv = np.linalg.pinv(X.T @ X)
    b = XtX_inv @ X.T @ yv
    e = yv - X @ b
    G, N, K = pid.max() + 1, len(yv), X.shape[1]
    meat = np.zeros((K, K))
    sc = np.zeros((G, K))
    np.add.at(sc, pid, X * e[:, None])
    meat = sc.T @ sc
    V = XtX_inv @ meat @ XtX_inv * (G / (G - 1)) * ((N - 1) / (N - K))
    se = np.sqrt(np.diag(V))
    return pd.DataFrame(dict(term=xs, coef=b, se_cluster_person=se, ci95_lo=b - 1.96 * se,
                             ci95_hi=b + 1.96 * se, n_rows=N, n_persons=G))


def models(a: pd.DataFrame) -> pd.DataFrame:
    a = a.copy()
    a["fd10"] = a["finding_difficulty"] / 10
    a["loss10"] = a["q13new"] / 10
    a["fd10_x_loss10_c"] = (a["fd10"] - a["fd10"].mean()) * (a["loss10"] - a["loss10"].mean())
    out = []
    specs = [("M0 month FE only", ["fd10", "loss10"], False),
             ("M1 person+month FE", ["fd10", "loss10"], True),
             ("M2 person+month FE + centred interaction", ["fd10", "loss10", "fd10_x_loss10_c"], True)]
    if "q4new" in a and a["q4new"].notna().mean() > 0.9:
        a["usunemp10"] = a["q4new"] / 10
        specs.append(("M3 = M1 + P(US unemployment higher)/10", ["fd10", "loss10", "usunemp10"], True))
    for name, xs, pfe in specs:
        r = fe_ols(a, "q30new", xs, person_fe=pfe)
        r.insert(0, "model", name)
        out.append(r)
    return pd.concat(out, ignore_index=True)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true", help="run model even if not validated (smoke test only)")
    ap.add_argument("--out", default=str(OUT_DIR))
    ap.add_argument("--derived", default=str(DERIVED_DIR))
    args = ap.parse_args()
    out_dir, derived = Path(args.out), Path(args.derived)
    gen = out_dir / "generated"

    path = derived / "panel_analysis.csv.gz"
    if not path.exists():
        print("No analysis panel; run code/02_build_panel.py first.", file=sys.stderr)
        return 1
    a = pd.read_csv(path, low_memory=False)
    a["month"] = pd.PeriodIndex(a["month"], freq="M")
    a["finding_difficulty"] = 100 - a["q22new"]
    flags = json.loads((gen / "validation_flags.json").read_text())

    parts = ["# Generated descriptive tables (do not edit by hand)\n",
             f"Analysis sample: {len(a):,} person-months, {a['userid'].nunique():,} persons, "
             f"{a['month'].min()}..{a['month'].max()}.\n",
             "finding_difficulty = 100 - Q22new. Product/interaction terms are indices, "
             "not probabilities of an income interruption.\n"]
    tabs = {"distributions": distributions(a), "by_year": by_year(a), "binned_q30": binned(a),
            "within_person_binned": within_binned(a), "first_differences": first_diff(a)}
    for k, t in tabs.items():
        t.to_csv(gen / f"desc_{k}.csv", index=False)
        parts += [f"\n## {k}\n", md_table(t)]

    gate = bool(flags.get("validated_for_preliminary_model") and flags.get("manual_history_review_done"))
    if gate or args.force:
        m = models(a)
        m.to_csv(gen / "preliminary_model.csv", index=False)
        label = "SMOKE TEST (--force; gate not passed)" if not gate else "PRELIMINARY ASSOCIATION — NOT CAUSAL"
        parts += [f"\n## preliminary_model — {label}\n",
                  "Outcome Q30new (pp). fd10 = finding difficulty per 10pp; loss10 = Q13new per 10pp. "
                  "Unweighted; SEs clustered by person.\n", md_table(m, "{:.3f}")]
    else:
        parts += ["\n## preliminary_model\n",
                  "Not run: validation_flags.json requires both validated_for_preliminary_model and "
                  "manual_history_review_done (set by hand after tracing person histories).\n"]
    (gen / "descriptives_tables.md").write_text("\n".join(parts) + "\n")
    print("\n".join(parts))
    return 0


if __name__ == "__main__":
    sys.exit(main())
