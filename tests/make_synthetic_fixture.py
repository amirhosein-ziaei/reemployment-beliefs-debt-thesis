"""SYNTHETIC test fixture — NOT SCE data.

Writes two small workbooks shaped like the SCE public files (a licence preamble
row above the header, YYYYMM dates, Q10_* tick boxes, overlapping keys across
files) so the pipeline can be smoke-tested without network access. Numbers in
these files are random and must never be reported as results.

Usage: python tests/make_synthetic_fixture.py <outdir>
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

rng = np.random.default_rng(0)


def person_months(n_people, start, months, id0):
    rows = []
    for i in range(n_people):
        uid = id0 + i
        t0 = rng.integers(0, months)
        n = int(rng.integers(1, 13))
        status = rng.choice(["ft", "pt", "self", "unemp", "retired"], p=[.5, .1, .08, .07, .25])
        base_loss, base_find, base_debt = rng.uniform(0, 40), rng.uniform(20, 90), rng.uniform(0, 30)
        for k in range(n):
            m = (pd.Period(start, "M") + int(t0) + k)
            r = {"userid": uid, "date": int(m.strftime("%Y%m")), "weight": rng.uniform(.3, 3),
                 "tenure": k + 1}
            for j in range(1, 11):
                r[f"Q10_{j}"] = np.nan
            if status in ("ft", "self"):
                r["Q10_1"] = 1
            elif status == "pt":
                r["Q10_2"] = 1
            elif status == "unemp":
                r["Q10_3"] = 1
            else:
                r["Q10_7"] = 1
            working = status in ("ft", "pt", "self")
            r["Q11"] = 1 if working else np.nan
            r["Q12new"] = (2 if status == "self" else 1) if working else np.nan
            r["Q13new"] = round(np.clip(base_loss + rng.normal(0, 8), 0, 100)) if status in ("ft", "pt") else np.nan
            r["Q22new"] = round(np.clip(base_find + rng.normal(0, 10), 0, 100)) if working else np.nan
            r["Q30new"] = round(np.clip(base_debt + .1 * (100 - (r["Q22new"] if working else 50))
                                        + rng.normal(0, 6), 0, 100))
            r["Q4new"] = round(rng.uniform(0, 100))
            rows.append(r)
    return pd.DataFrame(rows)


def write(df, path):
    with pd.ExcelWriter(path) as xw:
        pd.DataFrame([["SYNTHETIC FIXTURE - not Federal Reserve Bank of New York data"]]).to_excel(
            xw, sheet_name="Data", header=False, index=False, startrow=0)
        df.to_excel(xw, sheet_name="Data", index=False, startrow=1)


def main():
    out = Path(sys.argv[1])
    out.mkdir(parents=True, exist_ok=True)
    a = person_months(300, "2013-06", 30, 70000)
    b = person_months(200, "2025-01", 8, 90000)
    b = pd.concat([b, a.tail(5)])                       # cross-file overlapping keys
    a.loc[a.index[3], "Q30new"] = 150                    # invalid out-of-range value
    a["Q22new"] = a["Q22new"].astype(object)
    a.loc[a.index[4], "Q22new"] = "refused"             # non-numeric value
    write(a, out / "frbny-sce-public-microdata-complete-13-16.xlsx")
    write(b, out / "frbny-sce-public-microdata-latest.xlsx")


if __name__ == "__main__":
    main()
