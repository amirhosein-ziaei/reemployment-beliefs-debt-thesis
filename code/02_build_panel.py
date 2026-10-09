"""Step 2: load every SCE core workbook, harmonise, build the eligible
employed person-month panel and write the sample audit.

Outputs (aggregates only; committed):
  outputs/sample_audit.csv                 exclusion waterfall, overall/by year/by file
  outputs/generated/file_schema.csv        per-file coverage and variable presence
  outputs/generated/routing_by_group.csv   item response rates by employment group
  outputs/generated/q22_routing_by_month.csv
  outputs/generated/invalid_and_missing.csv
  outputs/generated/heaping.csv
  outputs/generated/within_person.csv
  outputs/generated/panel_length.csv
  outputs/generated/cross_file_consistency.csv
  outputs/generated/cross_file_overlap.csv
  outputs/generated/validation_flags.json
Microdata (gitignored): data/derived/panel_all.csv.gz, panel_analysis.csv.gz,
  person_histories_for_manual_review.csv

Usage: python code/02_build_panel.py [--raw data/raw/YYYY-MM-DD]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from sce_common import (CORE_VARS, DEMOG_VARS, DERIVED_DIR, DESIGN_VARS, EMP_DETAIL_VARS,
                        EMP_STATUS_VARS, EMPLOYED_CODES, EMPLOYEE_CODE, GEN_DIR, HEAP_POINTS,
                        KEY_VARS, MICRODATA_FILES, OUT_DIR, RAW_DIR, SENTIMENT_VARS,
                        SICK_LEAVE_CODE, find_header_row, parse_date, to_prob, write_json)

CORE = list(CORE_VARS)
KEEP = (KEY_VARS + DESIGN_VARS + EMP_STATUS_VARS + EMP_DETAIL_VARS + CORE
        + list(SENTIMENT_VARS) + DEMOG_VARS)


# ----------------------------------------------------------------------------- load
def load_workbook(path: Path, cache_dir: Path) -> tuple[pd.DataFrame, dict]:
    """Read the sheet containing `userid`; keep the preamble (licence text)."""
    cache = cache_dir / (path.stem + ".csv.gz")
    meta = {"file": path.name}
    xl = pd.ExcelFile(path)
    meta["sheets"] = xl.sheet_names
    for sheet in xl.sheet_names:
        head = pd.read_excel(xl, sheet_name=sheet, header=None, nrows=30, dtype=str)
        hdr = find_header_row(head)
        if hdr is None:
            continue
        meta.update(sheet=sheet, header_row=hdr,
                    preamble=" | ".join(head.iloc[:hdr].fillna("").astype(str)
                                        .agg(" ".join, axis=1).str.strip()))
        if cache.exists():
            df = pd.read_csv(cache, low_memory=False)
        else:
            df = pd.read_excel(xl, sheet_name=sheet, header=hdr)
            df.to_csv(cache, index=False)
        df.columns = [str(c).strip().lower() for c in df.columns]
        meta["n_columns"] = df.shape[1]
        return df, meta
    raise ValueError(f"{path.name}: no sheet with a 'userid' header found")


def release_key(fname: str) -> str:
    for k, v in MICRODATA_FILES.items():
        if v == fname:
            return k
    return fname


# ------------------------------------------------------------------------ construct
def construct(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    out = df.copy()
    out["month"] = parse_date(out["date"])
    out["year"] = out["month"].dt.year
    inv = {}
    for v in CORE + [s for s in SENTIMENT_VARS if s.endswith("new")]:
        if v in out:
            out[v + "_raw"] = out[v]
            out[v], inv[v] = to_prob(out[v])
    invalid = pd.DataFrame(inv)

    ticked = lambda c: (pd.to_numeric(out[c], errors="coerce") == 1) if c in out else False
    out["q10_any"] = out[[c for c in EMP_STATUS_VARS if c in out]].notna().any(axis=1)
    out["employed"] = ticked(EMPLOYED_CODES[0]) | ticked(EMPLOYED_CODES[1])
    out["sick_leave_only"] = ticked(SICK_LEAVE_CODE) & ~out["employed"]
    q12 = pd.to_numeric(out.get("q12new"), errors="coerce")
    out["employee"] = out["employed"] & (q12 == EMPLOYEE_CODE)
    out["self_employed"] = out["employed"] & q12.notna() & (q12 != EMPLOYEE_CODE)
    out["multi_status"] = out[[c for c in EMP_STATUS_VARS if c in out]].apply(
        pd.to_numeric, errors="coerce").eq(1).sum(axis=1) > 1

    # Mutually exclusive groups for the routing table (priority order).
    grp = np.select(
        [out["employee"], out["self_employed"], out["employed"] & q12.isna(),
         out["sick_leave_only"], ticked("q10_4"), ticked("q10_3"), ticked("q10_7"),
         ~out["q10_any"]],
        ["employed: works for someone else", "employed: self-employed",
         "employed: Q12new missing", "sick/other leave only", "temporarily laid off",
         "not working, would like to work", "retired", "Q10 all missing"],
        default="other not employed")
    out["emp_group"] = grp
    return out, invalid


# ---------------------------------------------------------------------------- audit
def waterfall(d: pd.DataFrame, scope: str) -> list[dict]:
    steps = [
        ("S0", "All respondent-month rows", None, ""),
        ("S1", "Valid userid and YYYYMM date", d["key_ok"], "missing/unparseable userid or date"),
        ("S2", "First occurrence of userid-month key", d["key_first"],
         "duplicate userid-month (cross-file overlap or within-file duplicate)"),
        ("S3", "Employed: Q10_1 full-time or Q10_2 part-time ticked", d["employed"],
         "not working / not reporting work in Q10"),
        ("S4", "Works for someone else (Q12new = 1)", d["employee"],
         "self-employed or Q12new missing; Q13new job-loss item not comparable"),
        ("S5", "Q13new valid 0-100", d["q13new"].notna(), "Q13new missing or invalid"),
        ("S6", "Q22new valid 0-100", d["q22new"].notna(), "Q22new missing or invalid"),
        ("S7", "Q30new valid 0-100", d["q30new"].notna(), "Q30new missing or invalid"),
    ]
    rows, mask = [], pd.Series(True, index=d.index)
    prev_n = len(d)
    for code, label, cond, reason in steps:
        if cond is not None:
            mask &= cond
        n = int(mask.sum())
        rows.append(dict(scope=scope, step=code, step_label=label, n_rows=n,
                         n_persons=int(d.loc[mask, "userid"].nunique()),
                         rows_excluded=prev_n - n, exclusion_reason=reason))
        prev_n = n
    # S8: persons with >= 2 analysis months (within-person sample)
    cnt = d.loc[mask].groupby("userid")["userid"].transform("size")
    m2 = mask.copy()
    m2.loc[mask] = cnt >= 2
    n = int(m2.sum())
    rows.append(dict(scope=scope, step="S8", step_label="Analysis rows of persons with >= 2 analysis months",
                     n_rows=n, n_persons=int(d.loc[m2, "userid"].nunique()),
                     rows_excluded=prev_n - n, exclusion_reason="singleton person in analysis sample"))
    return rows


def heaping(d: pd.DataFrame, by: str) -> pd.DataFrame:
    rows = []
    for g, sub in d.groupby(by):
        for v in CORE:
            x = sub[v].dropna()
            if x.empty:
                continue
            r = dict(group=g, variable=v, n=len(x))
            for p in HEAP_POINTS:
                r[f"share_eq_{p}"] = (x == p).mean()
            r["share_mult_10"] = (x % 10 == 0).mean()
            r["share_mult_5"] = (x % 5 == 0).mean()
            r["share_non_integer"] = (x % 1 != 0).mean()
            rows.append(r)
    return pd.DataFrame(rows)


def within_person(a: pd.DataFrame) -> pd.DataFrame:
    a = a[a.groupby("userid")["userid"].transform("size") >= 2].sort_values(["userid", "month"])
    rows = []
    for v in CORE:
        g = a.groupby("userid")[v]
        pm = g.transform("mean")
        within = a[v] - pm
        tot_var = a[v].var()
        lag = g.shift(1)
        consec = (a["month"] - a.groupby("userid")["month"].shift(1)).apply(
            lambda x: getattr(x, "n", np.nan)) == 1
        dlt = (a[v] - lag)[consec]
        rows.append(dict(
            variable=v, n_rows=len(a), n_persons=a["userid"].nunique(),
            share_persons_any_change=(g.nunique() > 1).mean(),
            sd_total=a[v].std(), sd_within=within.std(), sd_between=g.mean().std(),
            share_variance_within=within.var() / tot_var if tot_var else np.nan,
            n_consecutive_pairs=int(consec.sum()),
            share_pairs_changed=(dlt != 0).mean(),
            mean_abs_change_consecutive=dlt.abs().mean(),
            share_pairs_abs_change_ge_10=(dlt.abs() >= 10).mean(),
        ))
    ch = a.groupby("userid").agg(**{f"ch_{v}": (v, lambda s: s.nunique() > 1) for v in CORE})
    rows.append(dict(variable="q22new & q30new both vary", n_persons=len(ch),
                     share_persons_any_change=(ch["ch_q22new"] & ch["ch_q30new"]).mean()))
    rows.append(dict(variable="q13new & q22new & q30new all vary", n_persons=len(ch),
                     share_persons_any_change=ch.all(axis=1).mean()))
    return pd.DataFrame(rows)


def panel_length(d: pd.DataFrame, a: pd.DataFrame) -> pd.DataFrame:
    rows = []
    n_all = d.groupby("userid").size()
    n_ana = a.groupby("userid").size()
    for name, s in [("months in survey (all rows)", n_all), ("months in analysis sample", n_ana)]:
        vc = s.clip(upper=13).value_counts().sort_index()
        for k, c in vc.items():
            rows.append(dict(measure=name, n_months=("13+" if k == 13 else int(k)),
                             n_persons=int(c), share=c / len(s)))
    # Exit from eligibility among those observed again next calendar month
    d = d.sort_values(["userid", "month"])
    nxt_m = d.groupby("userid")["month"].shift(-1)
    nxt_emp = d.groupby("userid")["employee"].shift(-1)
    gap1 = (nxt_m - d["month"]).apply(lambda x: getattr(x, "n", np.nan)) == 1
    base = d["employee"] & gap1
    rows.append(dict(measure="employee -> not employee next month (share of consecutive pairs)",
                     n_months="", n_persons=int(base.sum()),
                     share=float((nxt_emp[base] == False).mean()) if base.any() else np.nan))  # noqa: E712
    last = d.groupby("userid")["month"].transform("max") == d["month"]
    rows.append(dict(measure="share of employee rows that are the person's last survey month",
                     n_months="", n_persons=int(d["employee"].sum()),
                     share=float(last[d["employee"]].mean())))
    if "tenure" in d:
        t = pd.to_numeric(d.loc[d["employee"], "tenure"], errors="coerce")
        for q in [0.1, 0.5, 0.9]:
            rows.append(dict(measure=f"tenure quantile {q} (employee rows)", n_months="",
                             n_persons=int(t.notna().sum()), share=t.quantile(q)))
    return pd.DataFrame(rows)


def history_sample(d: pd.DataFrame, n: int = 50, seed: int = 20261009) -> pd.DataFrame:
    """Stratified person histories for manual tracing (microdata; not committed)."""
    rng = np.random.default_rng(seed)
    p = d.groupby("userid").agg(
        src=("source_release", lambda s: s.iloc[0]),
        trans=("employee", lambda s: s.nunique() > 1),
        miss=("q22new", lambda s: s.isna().any()),
        endpt=("q30new", lambda s: s.isin(HEAP_POINTS).any()))
    p["stratum"] = (p["src"].astype(str) + "|t" + p["trans"].astype(int).astype(str)
                    + "|m" + p["miss"].astype(int).astype(str) + "|e" + p["endpt"].astype(int).astype(str))
    picks = []
    strata = p["stratum"].unique()
    per = max(1, n // max(1, len(strata)))
    for s in strata:
        ids = p.index[p["stratum"] == s].to_numpy()
        picks += list(rng.choice(ids, size=min(per, len(ids)), replace=False))
    cols = [c for c in ["userid", "month", "source_release", "tenure", "emp_group", *EMP_STATUS_VARS,
                        "q12new", "q13new_raw", "q22new_raw", "q30new_raw", "q13new", "q22new",
                        "q30new", "analysis"] if c in d]
    return d[d["userid"].isin(picks[:n])].sort_values(["userid", "month"])[cols]


# ----------------------------------------------------------------------------- main
def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", default=None, help="directory with the provider workbooks")
    ap.add_argument("--out", default=str(OUT_DIR))
    ap.add_argument("--derived", default=str(DERIVED_DIR))
    args = ap.parse_args()
    out_dir, derived = Path(args.out), Path(args.derived)
    gen = out_dir / "generated"
    gen.mkdir(parents=True, exist_ok=True)
    derived.mkdir(parents=True, exist_ok=True)

    raw = Path(args.raw) if args.raw else max((p for p in RAW_DIR.glob("*") if p.is_dir()), default=None)
    if raw is None or not list(raw.glob("*.xlsx")):
        print(f"No workbooks found in {raw}; run code/01_download.py first.", file=sys.stderr)
        return 1

    frames, schema = [], []
    for path in sorted(raw.glob("*.xlsx")):
        df, meta = load_workbook(path, derived)
        rel = release_key(path.name)
        m = parse_date(df["date"]) if "date" in df else pd.Series(dtype="period[M]")
        meta.update(release=rel, n_rows=len(df), n_userids=df["userid"].nunique(),
                    first_month=str(m.min()), last_month=str(m.max()), n_months=m.nunique())
        for v in KEEP:
            meta[f"has_{v}"] = v in df.columns
            if v in df.columns:
                meta[f"nonmissing_{v}"] = round(float(df[v].notna().mean()), 4)
        schema.append(meta)
        df = df[[c for c in KEEP if c in df.columns]].copy()
        df["source_release"] = rel
        frames.append(df)
        print(f"{path.name}: {len(df):,} rows, {meta['n_userids']:,} ids, {meta['first_month']}..{meta['last_month']}")
    pd.DataFrame(schema).to_csv(gen / "file_schema.csv", index=False)

    d = pd.concat(frames, ignore_index=True)
    d, invalid = construct(d)

    # Keys: validity, cross-file overlap, duplicates.
    d["key_ok"] = d["userid"].notna() & d["month"].notna()
    order = {k: i for i, k in enumerate(MICRODATA_FILES)}
    d["_ord"] = d["source_release"].map(order).fillna(99)
    d = d.sort_values(["userid", "month", "_ord"]).reset_index(drop=True)
    invalid = invalid.reindex(d.index)
    dup = d.duplicated(["userid", "month"], keep=False) & d["key_ok"]
    ov = d[dup].groupby(["userid", "month"]).agg(
        n=("source_release", "size"), releases=("source_release", lambda s: "+".join(sorted(set(s)))),
        **{f"agree_{v}": (v, lambda s: s.nunique(dropna=False) == 1) for v in CORE})
    (ov.groupby("releases").agg(n_keys=("n", "size"),
                                **{f"share_agree_{v}": (f"agree_{v}", "mean") for v in CORE})
       .reset_index().to_csv(gen / "cross_file_overlap.csv", index=False))
    # Prefer the historical "complete" file over "latest" on overlap (documented choice).
    d["key_first"] = ~d.duplicated(["userid", "month"], keep="first")

    # Routing table (all valid, de-duplicated rows).
    base = d[d["key_ok"] & d["key_first"]].copy()
    resp_vars = [v for v in ["q11", "q12new", *CORE, "q4new"] if v in base]
    rt = base.groupby("emp_group").agg(n_rows=("userid", "size"),
                                       **{f"answered_{v}": (v, lambda s: s.notna().mean()) for v in resp_vars})
    rt.reset_index().to_csv(gen / "routing_by_group.csv", index=False)
    (base[base["employee"]].groupby("month")
         .agg(n_rows=("userid", "size"),
              **{f"answered_{v}": (v, lambda s: s.notna().mean()) for v in CORE})
         .reset_index().to_csv(gen / "q22_routing_by_month.csv", index=False))

    # Invalid / missing by variable among employees.
    emp = base["employee"]
    im = []
    for v in CORE + [s for s in SENTIMENT_VARS if s in base]:
        im.append(dict(variable=v, n_employee_rows=int(emp.sum()),
                       share_missing=float(base.loc[emp, v].isna().mean()),
                       n_invalid_nonnumeric_or_out_of_range=int(invalid.loc[base.index[emp], v].sum())
                       if v in invalid else np.nan))
    pd.DataFrame(im).to_csv(gen / "invalid_and_missing.csv", index=False)

    # Waterfall: overall, by year, by release.
    rows = waterfall(d, "all")
    for y, sub in d.groupby("year"):
        rows += waterfall(sub, f"year={int(y)}")
    for r, sub in d.groupby("source_release"):
        rows += waterfall(sub, f"release={r}")
    audit = pd.DataFrame(rows)
    audit["status"] = "computed"
    audit.to_csv(out_dir / "sample_audit.csv", index=False)

    d["analysis"] = (d["key_ok"] & d["key_first"] & d["employee"]
                     & d[CORE].notna().all(axis=1))
    a = d[d["analysis"]].copy()
    heaping(a, "source_release").to_csv(gen / "heaping.csv", index=False)
    within_person(a).to_csv(gen / "within_person.csv", index=False)
    panel_length(base, a).to_csv(gen / "panel_length.csv", index=False)

    cons = a.groupby("source_release").agg(
        n_rows=("userid", "size"), n_persons=("userid", "nunique"),
        **{f"mean_{v}": (v, "mean") for v in CORE},
        **{f"median_{v}": (v, "median") for v in CORE})
    cons.reset_index().to_csv(gen / "cross_file_consistency.csv", index=False)

    # Validation gate for running any association model in step 3.
    def rate(g, v):
        return float(rt.loc[g, f"answered_{v}"]) if g in rt.index else np.nan
    flags = {
        "all_required_vars_in_every_file": bool(all(
            all(s.get(f"has_{v}") for v in KEY_VARS + CORE + ["q10_1", "q10_2", "q12new"]) for s in schema)),
        "keys_unique_after_dedup": bool(not d.loc[d["key_first"] & d["key_ok"]]
                                        .duplicated(["userid", "month"]).any()),
        "q13_answered_by_employees": rate("employed: works for someone else", "q13new"),
        "q22_answered_by_employees": rate("employed: works for someone else", "q22new"),
        "q30_answered_by_employees": rate("employed: works for someone else", "q30new"),
        "q13_answered_by_not_working": rate("not working, would like to work", "q13new"),
        "q22_answered_by_not_working": rate("not working, would like to work", "q22new"),
        "n_analysis_rows": int(len(a)), "n_analysis_persons": int(a["userid"].nunique()),
    }
    flags["routing_consistent"] = bool(
        flags["q13_answered_by_employees"] > 0.9 and flags["q22_answered_by_employees"] > 0.9
        and flags["q30_answered_by_employees"] > 0.9
        and not (flags["q13_answered_by_not_working"] > 0.05)
        and not (flags["q22_answered_by_not_working"] > 0.05))
    flags["validated_for_preliminary_model"] = bool(
        flags["all_required_vars_in_every_file"] and flags["keys_unique_after_dedup"]
        and flags["routing_consistent"])
    flags["manual_history_review_done"] = False  # set by hand after tracing histories
    write_json(flags, gen / "validation_flags.json")

    d.drop(columns=["_ord"]).to_csv(derived / "panel_all.csv.gz", index=False)
    a.to_csv(derived / "panel_analysis.csv.gz", index=False)
    history_sample(d).to_csv(derived / "person_histories_for_manual_review.csv", index=False)
    print(f"Analysis sample: {len(a):,} rows, {a['userid'].nunique():,} persons")
    print("Validation flags:", flags)
    return 0


if __name__ == "__main__":
    sys.exit(main())
