"""Phase 2 step 3 + 5: preliminary association models and the prespecified
measurement-sensitivity list (outputs/model_specification.md §3-§5, §8).

EXPLORATORY — pending independent human validation. Writes only to
outputs/exploratory/; never to the validated-model path, and never edits
validation_flags.json.

Usage: python code/05_phase2_models.py
"""
from __future__ import annotations

import sys

import numpy as np
import pandas as pd

import phase2_lib as L
from sce_common import DERIVED_DIR, GEN_DIR, HEAP_POINTS, OUT_DIR, md_table

EXP = OUT_DIR / "exploratory"
LOSS_POINTS = [0, 5, 20, 50]
COVID = (pd.Period("2020-03", "M"), pd.Period("2020-12", "M"))


def load() -> tuple[pd.DataFrame, pd.DataFrame]:
    a = pd.read_csv(DERIVED_DIR / "panel_analysis.csv.gz", low_memory=False)
    allr = pd.read_csv(DERIVED_DIR / "panel_all.csv.gz", low_memory=False)
    allr = allr[allr["key_ok"] & allr["key_first"]].copy()
    for d in (a, allr):
        d["month"] = pd.PeriodIndex(d["month"], freq="M")
        d["mnum"] = L.month_num(d["month"])
        d["fd10"] = (100 - d["q22new"]) / 10
        d["loss10"] = d["q13new"] / 10
    return a, allr


def add_interaction(d: pd.DataFrame) -> pd.DataFrame:
    d = d.copy()
    d["fd10_c"] = d["fd10"] - d["fd10"].mean()
    d["loss10_c"] = d["loss10"] - d["loss10"].mean()
    d["fd_x_loss_c"] = d["fd10_c"] * d["loss10_c"]
    return d


def row(label, fit: L.Fit, term="fd10", **extra) -> dict:
    t = fit.table().set_index("term").loc[term]
    r = dict(spec=label, term=term, coef=t["coef"], se=t["se"], ci95_lo=t["ci95_lo"], ci95_hi=t["ci95_hi"],
             n_obs=fit.n, n_persons=fit.n_persons,
             classification=L.classify(t["coef"], t["ci95_lo"], t["ci95_hi"]) if term in ("fd10", "d_fd10") else "")
    r.update(extra)
    return r


def within_variation(d: pd.DataFrame) -> pd.DataFrame:
    d = L.drop_singletons(d, "userid")
    g = [L.codes(d["userid"])]
    g2 = [L.codes(d["userid"]), L.codes(d["month"])]
    out = []
    for v in ["q30new", "fd10", "loss10"]:
        x = d[v].to_numpy(float)
        w1 = L.absorb(x, g)[:, 0]
        w2 = L.absorb(x, g2)[:, 0]
        out.append(dict(variable=v, n_obs=len(d), n_persons=d["userid"].nunique(), sd_total=x.std(),
                        sd_within_person=w1.std(), share_var_within_person=w1.var() / x.var(),
                        sd_within_person_and_month=w2.std(), share_var_within_person_and_month=w2.var() / x.var()))
    # Correlation of the identifying (two-way demeaned) variation of fd10 and loss10
    a = L.absorb(d[["fd10", "loss10"]].to_numpy(float), g2)
    out.append(dict(variable="corr(fd10, loss10) within person & month", n_obs=len(d),
                    n_persons=d["userid"].nunique(), sd_total=np.corrcoef(a.T)[0, 1]))
    return pd.DataFrame(out)


def main() -> int:
    L.require_automated_checks(GEN_DIR)
    EXP.mkdir(parents=True, exist_ok=True)
    a, allr = load()
    a = add_interaction(a)
    xs = ["fd10", "loss10"]
    reg, me, sens = [], [], []

    # ---------------------------------------------------------------- Models A, B, C (§3-§4)
    fits = {
        "A": L.ols_fe(a, "q30new", xs, fe=("month",)),
        "B": L.ols_fe(a, "q30new", xs, fe=("userid", "month")),
        "C": L.ols_fe(a, "q30new", ["fd10", "loss10", "fd_x_loss_c"], fe=("userid", "month")),
    }
    fits2 = {
        "A": L.ols_fe(a, "q30new", xs, fe=("month",), cluster=("userid", "month")),
        "B": L.ols_fe(a, "q30new", xs, fe=("userid", "month"), cluster=("userid", "month")),
        "C": L.ols_fe(a, "q30new", ["fd10", "loss10", "fd_x_loss_c"], fe=("userid", "month"),
                      cluster=("userid", "month")),
    }
    for m in "ABC":
        for inf, f in (("person-clustered", fits[m]), ("two-way person+month clustered", fits2[m])):
            t = f.table()
            t.insert(0, "inference", inf)
            t.insert(0, "model", m)
            reg.append(t)
    noncovid = a[(a["month"] < COVID[0]) | (a["month"] > COVID[1])]
    f = L.ols_fe(noncovid, "q30new", xs, fe=("userid", "month"))
    t = f.table()
    t.insert(0, "inference", "person-clustered; excludes 2020-03..2020-12")
    t.insert(0, "model", "B")
    reg.append(t)

    # Weighted sensitivity (§5)
    for m, fe in (("A", ("month",)), ("B", ("userid", "month"))):
        f = L.ols_fe(a, "q30new", xs, fe=fe, weights="weight")
        t = f.table()
        t.insert(0, "inference", "person-clustered; WLS with SCE weight")
        t.insert(0, "model", m)
        reg.append(t)
    reg = pd.concat(reg, ignore_index=True)
    reg.to_csv(EXP / "regressions.csv", index=False)

    # Model C marginal effects of fd10 at interpretable Q13new values
    C = fits["C"]
    mu = a.loc[a["userid"].isin(L.drop_singletons(a, "userid")["userid"]), "loss10"].mean()
    for inf, fit in (("person-clustered", C), ("two-way", fits2["C"])):
        for L13 in LOSS_POINTS:
            est, se = fit.lincom({"fd10": 1, "fd_x_loss_c": L13 / 10 - mu})
            me.append(dict(inference=inf, q13new=L13, effect_of_10pp_lower_q22=est, se=se, ci95_lo=est - 1.96 * se,
                           ci95_hi=est + 1.96 * se, classification=L.classify(est, est - 1.96 * se, est + 1.96 * se)))
        est, se = fit.lincom({"fd_x_loss_c": (50 - 5) / 10})
        me.append(dict(inference=inf, q13new="difference 50 vs 5", effect_of_10pp_lower_q22=est, se=se,
                       ci95_lo=est - 1.96 * se, ci95_hi=est + 1.96 * se,
                       classification=L.classify(est, est - 1.96 * se, est + 1.96 * se)))
    me = pd.DataFrame(me)
    me["note"] = f"centring mean of loss10 = {mu:.4f} (estimation sample)"
    me.to_csv(EXP / "interaction_marginal_effects.csv", index=False)

    wv = within_variation(a)
    wv.to_csv(EXP / "within_variation.csv", index=False)

    # ---------------------------------------------------------------- Sensitivity list (§8)
    B = lambda d, extra=(), **kw: L.ols_fe(d, "q30new", [*xs, *extra], fe=("userid", "month"), **kw)
    sens.append(row("B main", fits["B"]))
    sens.append(row("A main", fits["A"]))

    always0 = a.groupby("userid")["q30new"].transform("max") == 0
    sens.append(row("S1 drop persons with Q30=0 in every month", B(a[~always0]),
                    persons_dropped=int(a.loc[always0, "userid"].nunique())))
    any50 = a[["q13new", "q22new", "q30new"]].eq(50).any(axis=1)
    sens.append(row("S2a drop rows with any core item = 50", B(a[~any50]), rows_dropped=int(any50.sum())))
    endq22 = a["q22new"].isin([0, 100])
    sens.append(row("S2b drop rows with Q22 in {0,100}", B(a[~endq22]), rows_dropped=int(endq22.sum())))

    lagd = L.add_neighbour(a, ["fd10", "loss10", "q22new"], -1, "_l1")
    big = (lagd["q22new"] - lagd["q22new_l1"]).abs() >= 50
    sens.append(row("S3a drop rows with |dQ22| >= 50 vs previous month", B(lagd[~big]), rows_dropped=int(big.sum())))

    s3 = lagd.dropna(subset=["fd10_l1", "loss10_l1"])
    ols_s = L.ols_fe(s3, "q30new", xs, fe=("month",))
    iv_s = L.iv_fe(s3, "q30new", [], xs, ["fd10_l1", "loss10_l1"], fe=("month",))
    sens.append(row("S3b same-sample OLS (Model A, rows with t-1)", ols_s))
    sens.append(row("S3b 2SLS Model A, beliefs instrumented by t-1 values", iv_s,
                    first_stage_F=str({k: round(v, 1) for k, v in iv_s.extra["first_stage_F"].items()})))

    fdd = L.add_neighbour(lagd, ["fd10", "loss10"], -2, "_l2")
    fdd = L.add_neighbour(fdd, ["q30new"], -1, "_l1")
    fdd["d_q30"] = fdd["q30new"] - fdd["q30new_l1"]
    fdd["d_fd10"] = fdd["fd10"] - fdd["fd10_l1"]
    fdd["d_loss10"] = fdd["loss10"] - fdd["loss10_l1"]
    s3c = fdd.dropna(subset=["d_q30", "d_fd10", "d_loss10", "fd10_l2", "loss10_l2"])
    fd_ols = L.ols_fe(s3c, "d_q30", ["d_fd10", "d_loss10"], fe=("month",))
    fd_iv = L.iv_fe(s3c, "d_q30", [], ["d_fd10", "d_loss10"], ["fd10_l2", "loss10_l2"], fe=("month",))
    sens.append(row("S3c same-sample first-difference OLS", fd_ols, term="d_fd10"))
    sens.append(row("S3c first-difference 2SLS, instruments at t-2", fd_iv, term="d_fd10",
                    first_stage_F=str({k: round(v, 1) for k, v in fd_iv.extra["first_stage_F"].items()})))

    allr_s = allr.sort_values(["userid", "month"])
    in_main = allr_s["analysis"].astype(bool)
    stayers = in_main.groupby(allr_s["userid"]).all()
    stay_ids = stayers.index[stayers]
    sens.append(row("S4a baseline-employed cohort (in main sample every observed month)",
                    B(a[a["userid"].isin(stay_ids)])))
    wide = allr[(allr[["q10_1", "q10_2", "q10_4", "q10_5"]].eq(1).any(axis=1)) & (allr["q12new"] == 1)
                & allr[["q13new", "q22new", "q30new"]].notna().all(axis=1)].copy()
    sens.append(row("S4b add on-leave / temporarily laid off with Q12new = 1", B(wide),
                    rows_added=int(len(wide) - len(a))))

    nT = a.groupby("userid")["userid"].transform("size")
    sens.append(row("S5a persons with >= 6 analysis months", B(a[nT >= 6])))
    a["w_person_equal"] = 1.0 / nT
    sens.append(row("S5b person-equal weights (1/T_i)", B(a, weights="w_person_equal")))

    nxt = allr[["userid", "mnum"]].assign(has_next=1)
    nxt["mnum"] -= 1
    att = a.merge(nxt, on=["userid", "mnum"], how="left")
    att["has_next"] = att["has_next"].fillna(0)
    sens.append(row("S6a rows with an observed next-calendar-month response", B(att[att["has_next"] == 1])))
    pre = att[att["tenure"] < 12].copy()
    pre["no_next"] = 1 - pre["has_next"]
    pre["q30_10"] = pre["q30new"] / 10
    lpm = L.ols_fe(pre, "no_next", ["fd10", "loss10", "q30_10"], fe=("month",))
    for term in ["fd10", "loss10", "q30_10"]:
        r = row("S6b LPM: P(no response next month), tenure < 12", lpm, term=term,
                mean_outcome=float(pre["no_next"].mean()))
        r["classification"] = "(attrition model; pp of probability x100 not applicable)"
        sens.append(r)

    s7 = a.dropna(subset=["q4new", "q1", "q2"]).copy()
    s7["q4_10"] = s7["q4new"] / 10
    dums = pd.get_dummies(s7[["q1", "q2"]].astype(int).astype(str), drop_first=True, dtype=float)
    s7 = pd.concat([s7, dums], axis=1)
    sens.append(row("S7a same-sample Model B (rows with sentiment controls)", B(s7)))
    sens.append(row("S7a + Q4new/10 + Q1, Q2 dummies", B(s7, extra=["q4_10", *dums.columns])))
    lead = L.add_neighbour(a, ["fd10"], 1, "_f1").dropna(subset=["fd10_f1"])
    sens.append(row("S7b same-sample Model B (rows with t+1 belief)", B(lead)))
    f7b = B(lead, extra=["fd10_f1"])
    sens.append(row("S7b Model B + fd10 at t+1 (placebo)", f7b))
    r = row("S7b Model B + fd10 at t+1 (placebo)", f7b, term="fd10_f1")
    r["classification"] = "placebo coefficient"
    sens.append(r)

    sens = pd.DataFrame(sens)
    sens.to_csv(EXP / "sensitivity.csv", index=False)

    # ---------------------------------------------------------------- tables
    parts = [f"# Phase 2 exploratory regression tables (generated; do not edit)\n", f"**{L.EXPLORATORY_LABEL}**\n",
             "Outcome: Q30new (pp). fd10 = (100 - Q22new)/10, so its coefficient is the change in Q30new for a "
             "10pp *decrease* in the job-finding probability. loss10 = Q13new/10.\n",
             "\n## Models A-C\n", md_table(reg, "{:.3f}"),
             "\n## Model C: effect of a 10pp lower Q22new at given Q13new\n", md_table(me, "{:.3f}"),
             "\n## Within-person variation (Model B/C estimation sample)\n", md_table(wv, "{:.3f}"),
             "\n## Prespecified sensitivity list (§8)\n", md_table(sens.drop(columns=[c for c in sens.columns if c not in
                ["spec", "term", "coef", "se", "ci95_lo", "ci95_hi", "n_obs", "n_persons", "classification",
                 "first_stage_F"]]), "{:.3f}")]
    (EXP / "phase2_regression_tables.md").write_text("\n".join(parts) + "\n")
    print("\n".join(parts))
    return 0


if __name__ == "__main__":
    sys.exit(main())
