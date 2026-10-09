"""Estimation and prediction helpers for G-P2 Phase 2 (see outputs/model_specification.md).

* `absorb` removes any number of fixed effects by (weighted) alternating
  projections: no dummy columns are ever built.
* `ols_fe` / `iv_fe` return coefficients with one- or two-way cluster-robust
  (CR1) covariance matrices.
* Prediction helpers build exact next-calendar-month pairs, person folds and
  cluster/block bootstrap intervals for out-of-sample loss differences.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd

EXPLORATORY_LABEL = ("EXPLORATORY — PENDING INDEPENDENT HUMAN VALIDATION. "
                     "Associational, not causal. Not the validated-model output.")
BENCHMARK_PP = 2.0  # model_specification.md §6; fixed before estimation


def require_automated_checks(gen_dir: Path) -> dict:
    """Phase 2 runs only after the automated Phase 1 checks pass. Never edits the flags."""
    flags = json.loads((gen_dir / "validation_flags.json").read_text())
    if not flags.get("validated_for_preliminary_model"):
        raise SystemExit("Automated data checks have not passed (validation_flags.json); not estimating.")
    return flags


# ----------------------------------------------------------------------------- FE absorption
def codes(s: pd.Series) -> np.ndarray:
    return pd.factorize(s, sort=True)[0]


def absorb(M: np.ndarray, groups: list[np.ndarray], w: np.ndarray | None = None,
           tol: float = 1e-10, maxit: int = 2000) -> np.ndarray:
    """Residualise columns of M on the fixed effects in `groups` (weighted means if w given)."""
    Z = np.asarray(M, float).copy()
    if Z.ndim == 1:
        Z = Z[:, None]
    if not groups:
        return Z
    w = np.ones(len(Z)) if w is None else np.asarray(w, float)
    wsum = [np.bincount(g, w) for g in groups]
    scale = max(1.0, float(np.abs(Z).max()))
    for _ in range(maxit if len(groups) > 1 else 1):
        delta = 0.0
        for g, ws in zip(groups, wsum):
            for j in range(Z.shape[1]):
                m = np.bincount(g, w * Z[:, j]) / ws
                Z[:, j] -= m[g]
                delta = max(delta, float(np.abs(m).max()))
        if delta < tol * scale:
            break
    return Z


def drop_singletons(df: pd.DataFrame, col: str) -> pd.DataFrame:
    return df[df.groupby(col)[col].transform("size") > 1]


# ----------------------------------------------------------------------------- results
@dataclass
class Fit:
    names: list[str]
    coef: np.ndarray
    vcov: np.ndarray
    n: int
    n_persons: int
    n_clusters: dict = field(default_factory=dict)
    extra: dict = field(default_factory=dict)

    def se(self) -> np.ndarray:
        return np.sqrt(np.clip(np.diag(self.vcov), 0, None))

    def table(self) -> pd.DataFrame:
        se = self.se()
        return pd.DataFrame(dict(term=self.names, coef=self.coef, se=se, ci95_lo=self.coef - 1.96 * se,
                                 ci95_hi=self.coef + 1.96 * se, z=self.coef / se,
                                 n_obs=self.n, n_persons=self.n_persons))

    def lincom(self, w: dict[str, float]) -> tuple[float, float]:
        a = np.array([w.get(n, 0.0) for n in self.names])
        return float(a @ self.coef), float(np.sqrt(max(a @ self.vcov @ a, 0.0)))


def classify(est: float, lo: float, hi: float, bench: float = BENCHMARK_PP) -> str:
    """Decision rule of model_specification.md §6 (sign: positive = more distress)."""
    if est >= bench and lo > 0:
        return "economically meaningful"
    if lo > -bench and hi < bench:
        return "precisely small"
    return "inconclusive"


def _cluster_meat(S: np.ndarray, cl: np.ndarray) -> tuple[np.ndarray, int]:
    G = int(cl.max()) + 1
    agg = np.zeros((G, S.shape[1]))
    np.add.at(agg, cl, S)
    return agg.T @ agg, G


def sandwich(Xb: np.ndarray, Xs: np.ndarray, e: np.ndarray, w: np.ndarray, clusters: list[np.ndarray],
             k_df: int) -> tuple[np.ndarray, dict]:
    """CR1 covariance. Xb builds the bread, Xs the scores (equal for OLS; X-hat for 2SLS).

    Two-way: V = V_a + V_b - V_ab (Cameron, Gelbach & Miller 2011), with V_ab clustered on the
    intersection (observation level here, since person × month is unique).
    """
    N = len(e)
    bread = np.linalg.pinv((Xb * w[:, None]).T @ Xb)
    S = Xs * (w * e)[:, None]
    adj_n = (N - 1) / max(N - k_df, 1)

    def one(cl):
        meat, G = _cluster_meat(S, cl)
        return bread @ meat @ bread * G / (G - 1) * adj_n, G

    if len(clusters) == 1:
        V, G = one(clusters[0])
        return V, {"G1": G}
    (Va, Ga), (Vb, Gb) = one(clusters[0]), one(clusters[1])
    inter = codes(pd.Series(clusters[0]).astype(str) + "_" + pd.Series(clusters[1]).astype(str))
    Vab, Gab = one(inter)
    return Va + Vb - Vab, {"G1": Ga, "G2": Gb}


def _prep(df, cols, fe, weights):
    d = df.dropna(subset=[c for c in cols if c is not None])
    if weights:
        d = d[d[weights].notna() & (d[weights] > 0)]
    if "userid" in fe:
        d = drop_singletons(d, "userid")
    w = d[weights].to_numpy(float) if weights else np.ones(len(d))
    groups = [codes(d[f]) for f in fe]
    return d, w, groups


def _k_df(n_x: int, d: pd.DataFrame, fe, cluster) -> int:
    # FE nested in a cluster variable (person FE with person clusters) do not use up dof.
    return n_x + sum(d[f].nunique() - 1 for f in fe if f not in cluster)


def ols_fe(df: pd.DataFrame, y: str, xs: list[str], fe=("month",), cluster=("userid",),
           weights: str | None = None) -> Fit:
    d, w, groups = _prep(df, [y, *xs], list(fe), weights)
    Z = absorb(d[[y, *xs]].to_numpy(float), groups, w)
    yv, X = Z[:, 0], Z[:, 1:]
    XtWX = (X * w[:, None]).T @ X
    b = np.linalg.solve(XtWX, (X * w[:, None]).T @ yv)
    e = yv - X @ b
    cl = [codes(d[c]) for c in cluster]
    V, G = sandwich(X, X, e, w, cl, _k_df(len(xs), d, fe, cluster))
    return Fit(list(xs), b, V, len(d), d["userid"].nunique(), G)


def iv_fe(df: pd.DataFrame, y: str, exog: list[str], endog: list[str], instr: list[str], fe=("month",),
          cluster=("userid",)) -> Fit:
    """2SLS after absorbing FE. Reports a cluster-robust first-stage F for each endogenous regressor."""
    d, w, groups = _prep(df, [y, *exog, *endog, *instr], list(fe), None)
    Z = absorb(d[[y, *endog, *exog, *instr]].to_numpy(float), groups, w)
    k1, k2 = len(endog), len(exog)
    yv, X, Zi = Z[:, 0], Z[:, 1:1 + k1 + k2], np.hstack([Z[:, 1 + k1:1 + k1 + k2], Z[:, 1 + k1 + k2:]])
    pi = np.linalg.lstsq(Zi, X, rcond=None)[0]
    Xhat = Zi @ pi
    b = np.linalg.solve(Xhat.T @ X, Xhat.T @ yv)
    e = yv - X @ b
    cl = [codes(d[c]) for c in cluster]
    k_df = _k_df(k1 + k2, d, fe, cluster)
    V, G = sandwich(Xhat, Xhat, e, w, cl, k_df)
    first = {}
    for j, name in enumerate(endog):
        u = X[:, j] - Xhat[:, j]
        Vfs, _ = sandwich(Zi, Zi, u, w, cl, Zi.shape[1])
        idx = list(range(k2, Zi.shape[1]))
        g = pi[idx, j]
        first[name] = float(g @ np.linalg.pinv(Vfs[np.ix_(idx, idx)]) @ g / len(idx))
    return Fit([*endog, *exog], b, V, len(d), d["userid"].nunique(), G, {"first_stage_F": first})


# ----------------------------------------------------------------------------- panel helpers
def month_num(p: pd.Series) -> np.ndarray:
    """Calendar month as an integer (year*12 + month) for exact-gap arithmetic."""
    p = pd.PeriodIndex(p, freq="M")
    return (p.year * 12 + p.month - 1).to_numpy()


def add_neighbour(d: pd.DataFrame, cols: list[str], k: int, suffix: str) -> pd.DataFrame:
    """Attach values of `cols` from the same person exactly k calendar months away (k=-1: lag)."""
    key = d[["userid", "mnum", *cols]].copy()
    key["mnum"] = key["mnum"] - k
    return d.merge(key.rename(columns={c: c + suffix for c in cols}), on=["userid", "mnum"], how="left")


def next_month_pairs(analysis: pd.DataFrame, all_rows: pd.DataFrame) -> pd.DataFrame:
    """Analysis rows at t matched to the same person's valid Q30new at exactly t+1 (any status at t+1)."""
    a = analysis.copy()
    nxt = all_rows.loc[all_rows["q30new"].notna(), ["userid", "mnum", "q30new"]].copy()
    nxt["mnum"] -= 1
    out = a.merge(nxt.rename(columns={"q30new": "q30_next"}), on=["userid", "mnum"], how="left")
    return out


def person_folds(ids: pd.Series, k: int, seed: int) -> pd.Series:
    uniq = np.sort(ids.unique())
    perm = np.random.default_rng(seed).permutation(len(uniq))
    fold = pd.Series(perm % k, index=uniq)
    return ids.map(fold)


def ols_fit_predict(train: pd.DataFrame, test: pd.DataFrame, xs: list[str], y: str) -> np.ndarray:
    Xtr = np.column_stack([np.ones(len(train)), train[xs].to_numpy(float)])
    b = np.linalg.lstsq(Xtr, train[y].to_numpy(float), rcond=None)[0]
    Xte = np.column_stack([np.ones(len(test)), test[xs].to_numpy(float)])
    return np.clip(Xte @ b, 0, 100)


def loss_diff_bootstrap(err_base: np.ndarray, err_exp: np.ndarray, cluster: np.ndarray, B: int, seed: int) -> dict:
    """Cluster bootstrap of RMSE/MAE differences (baseline − expanded), models held fixed."""
    cl = codes(pd.Series(cluster))
    G = cl.max() + 1
    agg = np.zeros((G, 5))
    np.add.at(agg, cl, np.column_stack([err_base ** 2, err_exp ** 2, np.abs(err_base), np.abs(err_exp),
                                        np.ones_like(err_base)]))
    rng = np.random.default_rng(seed)
    draws = np.empty((B, 4))
    for b in range(B):
        s = agg[rng.integers(0, G, G)].sum(axis=0)
        rb, re_ = np.sqrt(s[0] / s[4]), np.sqrt(s[1] / s[4])
        mb, me = s[2] / s[4], s[3] / s[4]
        draws[b] = [rb - re_, (rb - re_) / rb, mb - me, (mb - me) / mb]
    lo, hi = np.percentile(draws, [2.5, 97.5], axis=0)
    return {"rmse_diff_ci": (lo[0], hi[0]), "rmse_rel_ci": (lo[1], hi[1]),
            "mae_diff_ci": (lo[2], hi[2]), "mae_rel_ci": (lo[3], hi[3]), "n_clusters": int(G)}


def loss_summary(y: np.ndarray, p_base: np.ndarray, p_exp: np.ndarray) -> dict:
    eb, ee = y - p_base, y - p_exp
    rb, re_ = float(np.sqrt(np.mean(eb ** 2))), float(np.sqrt(np.mean(ee ** 2)))
    mb, me = float(np.mean(np.abs(eb))), float(np.mean(np.abs(ee)))
    return dict(n=len(y), rmse_base=rb, rmse_exp=re_, rmse_diff=rb - re_, rmse_rel=(rb - re_) / rb,
                mae_base=mb, mae_exp=me, mae_diff=mb - me, mae_rel=(mb - me) / mb)


def classify_prediction(rel: float, lo: float, hi: float) -> str:
    """model_specification.md §7."""
    if rel >= 0.01 and lo > 0:
        return "material"
    if hi < 0.01:
        return "negligible"
    return "inconclusive"
