"""Automated tests for the Phase 2 code (synthetic data only; no SCE data needed).

Run: python -m unittest discover -s tests -v
"""
import importlib.util
import sys
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

CODE = Path(__file__).resolve().parents[1] / "code"
sys.path.insert(0, str(CODE))
import phase2_lib as L  # noqa: E402


def load(name, fname):
    spec = importlib.util.spec_from_file_location(name, CODE / fname)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def panel(n_people=300, T=8, seed=0, noise=0.0):
    rng = np.random.default_rng(seed)
    rows = []
    for i in range(n_people):
        a = rng.normal(0, 5)
        start = rng.integers(0, 20)
        for t in range(rng.integers(2, T + 1)):
            m = start + t
            fd_true = rng.normal(5, 2) + 0.3 * a
            loss = rng.normal(2, 1)
            q30 = 10 + a + 0.8 * m % 3 + 1.5 * fd_true + 0.7 * loss + rng.normal(0, 2)
            rows.append(dict(userid=i, month=m, fd10=fd_true + rng.normal(0, noise) if noise else fd_true,
                             fd_true=fd_true, loss10=loss, q30new=q30, weight=rng.uniform(0.2, 3)))
    return pd.DataFrame(rows)


def dense(d, y, xs, w=None, fe=("userid", "month")):
    """Brute-force dummy-variable regression for comparison."""
    D = [pd.get_dummies(d[f], prefix=f, drop_first=(k > 0), dtype=float) for k, f in enumerate(fe)]
    X = np.column_stack([d[xs].to_numpy(float), *[x.to_numpy() for x in D]])
    w = np.ones(len(d)) if w is None else w
    b = np.linalg.lstsq(X * np.sqrt(w)[:, None], d[y].to_numpy(float) * np.sqrt(w), rcond=None)[0]
    return b[:len(xs)], X, d[y].to_numpy(float) - X @ b


class TestFixedEffects(unittest.TestCase):
    def test_absorb_matches_dummies_unweighted(self):
        d = L.drop_singletons(panel(), "userid")
        fit = L.ols_fe(d, "q30new", ["fd10", "loss10"], fe=("userid", "month"))
        b, _, _ = dense(d, "q30new", ["fd10", "loss10"])
        np.testing.assert_allclose(fit.coef, b, atol=1e-7)

    def test_absorb_matches_dummies_weighted(self):
        d = L.drop_singletons(panel(seed=1), "userid")
        fit = L.ols_fe(d, "q30new", ["fd10", "loss10"], fe=("userid", "month"), weights="weight")
        b, _, _ = dense(d, "q30new", ["fd10", "loss10"], w=d["weight"].to_numpy())
        np.testing.assert_allclose(fit.coef, b, atol=1e-7)

    def test_cluster_se_matches_dense_sandwich(self):
        # FWL: the slope block of the dense cluster-robust sandwich equals the absorbed one.
        d = L.drop_singletons(panel(seed=2), "userid").reset_index(drop=True)
        fit = L.ols_fe(d, "q30new", ["fd10", "loss10"], fe=("userid", "month"))
        _, X, e = dense(d, "q30new", ["fd10", "loss10"])
        bread = np.linalg.pinv(X.T @ X)
        cl = L.codes(d["userid"])
        meat, G = L._cluster_meat(X * e[:, None], cl)
        k_df = 2 + d["month"].nunique() - 1
        V = bread @ meat @ bread * G / (G - 1) * (len(d) - 1) / (len(d) - k_df)
        np.testing.assert_allclose(fit.vcov, V[:2, :2], rtol=1e-6)

    def test_true_slope_recovered(self):
        fit = L.ols_fe(panel(n_people=3000, seed=3), "q30new", ["fd10", "loss10"], fe=("userid", "month"))
        lo, hi = fit.table().loc[0, ["ci95_lo", "ci95_hi"]]
        self.assertTrue(lo < 1.5 < hi)

    def test_lincom(self):
        fit = L.ols_fe(panel(seed=4), "q30new", ["fd10", "loss10"], fe=("userid", "month"))
        est, se = fit.lincom({"fd10": 1, "loss10": 1})
        self.assertAlmostEqual(est, fit.coef.sum())
        self.assertAlmostEqual(se ** 2, fit.vcov.sum(), places=8)

    def test_iv_corrects_attenuation(self):
        # Persistent true belief + iid reporting error: OLS attenuates, lagged-belief IV does not.
        rng = np.random.default_rng(5)
        rows = []
        for i in range(4000):
            x = rng.normal(0, 1)
            for t in range(4):
                x = 0.9 * x + rng.normal(0, 0.5)
                rows.append(dict(userid=i, month=t, x_obs=x + rng.normal(0, 1), y=2 * x + rng.normal(0, 1)))
        d = pd.DataFrame(rows).sort_values(["userid", "month"])
        d["mnum"] = d["month"]
        d = L.add_neighbour(d, ["x_obs"], -1, "_lag")
        ols = L.ols_fe(d.dropna(), "y", ["x_obs"], fe=("month",))
        iv = L.iv_fe(d, "y", [], ["x_obs"], ["x_obs_lag"], fe=("month",))
        self.assertLess(ols.coef[0], 1.6)
        self.assertAlmostEqual(iv.coef[0], 2.0, delta=0.15)
        self.assertGreater(iv.extra["first_stage_F"]["x_obs"], 100)


class TestPrediction(unittest.TestCase):
    def setUp(self):
        self.all = pd.DataFrame(dict(userid=[1, 1, 1, 2, 2, 3], mnum=[10, 11, 13, 10, 12, 5],
                                     q30new=[5, 6, 7, 1, 2, np.nan]))

    def test_exact_next_calendar_month_only(self):
        a = self.all.iloc[[0, 1, 3, 5]]
        p = L.next_month_pairs(a, self.all)
        got = dict(zip(zip(p["userid"], p["mnum"]), p["q30_next"]))
        self.assertEqual(got[(1, 10)], 6)            # 10 -> 11 consecutive
        self.assertTrue(np.isnan(got[(1, 11)]))      # 11 -> 13 is a gap: no target
        self.assertTrue(np.isnan(got[(2, 10)]))      # 10 -> 12 is a gap: no target
        self.assertTrue(np.isnan(got[(3, 5)]))       # no later response

    def test_neighbour_lag_requires_exact_gap(self):
        d = self.all.assign(x=[1, 2, 3, 4, 5, 6])
        out = L.add_neighbour(d, ["x"], -1, "_lag")
        self.assertEqual(out.loc[(out.userid == 1) & (out.mnum == 11), "x_lag"].item(), 1)
        self.assertTrue(np.isnan(out.loc[(out.userid == 1) & (out.mnum == 13), "x_lag"].item()))

    def test_person_folds_disjoint(self):
        ids = pd.Series(np.repeat(np.arange(500), 3))
        f = L.person_folds(ids, 5, 1)
        self.assertTrue((pd.DataFrame({"id": ids, "f": f}).groupby("id")["f"].nunique() == 1).all())
        self.assertEqual(set(f.unique()), set(range(5)))

    def test_bootstrap_zero_when_identical(self):
        y = np.arange(100.0)
        r = L.loss_diff_bootstrap(y, y, np.repeat(np.arange(20), 5), 50, 0)
        self.assertEqual(r["rmse_diff_ci"], (0.0, 0.0))

    def test_classification_rules(self):
        self.assertEqual(L.classify(2.5, 0.5, 4.5), "economically meaningful")
        self.assertEqual(L.classify(0.1, -0.2, 0.4), "precisely small")
        self.assertEqual(L.classify(1.0, -0.5, 2.5), "inconclusive")
        self.assertEqual(L.classify_prediction(0.02, 0.005, 0.03), "material")
        self.assertEqual(L.classify_prediction(0.001, -0.001, 0.004), "negligible")


class TestValidationRouting(unittest.TestCase):
    def setUp(self):
        self.v = load("vp", "04_validation_package.py")

    def row(self, **kw):
        base = {f"q10_{i}": 0 for i in range(1, 11)}
        base.update(dict(q10_1=1, q11=1, q12new=1, employed=True, month=pd.Period("2015-03", "M"),
                         q13new=10.0, q22new=60.0, q30new=5.0, q13new_raw=10.0, q22new_raw=60.0,
                         q30new_raw=5.0))
        base.update(kw)
        return base

    def test_eligible(self):
        self.assertTrue(self.v.routing(self.row())[0].startswith("ELIGIBLE"))

    def test_pre_aug2013_q12_missing(self):
        dec, why = self.v.routing(self.row(q12new=np.nan, month=pd.Period("2013-06", "M")))
        self.assertIn("S4", dec)
        self.assertIn("not fielded before 2013-08", why)

    def test_self_employed_not_asked(self):
        r = self.row(q12new=2, q13new=np.nan, q22new=np.nan)
        self.assertIn("self-employed", self.v.routing(r)[0])
        self.assertEqual(self.v.expected_routing(r), "Q13/Q22 not asked (self-employed)")

    def test_q11_zero_routed_out(self):
        r = self.row(q11=0, q12new=np.nan)
        self.assertIn("Q11 = 0", self.v.routing(r)[1])

    def test_transformation_text(self):
        self.assertIn("100 - 60 = 40", self.v.explain(self.row()))


if __name__ == "__main__":
    unittest.main()
