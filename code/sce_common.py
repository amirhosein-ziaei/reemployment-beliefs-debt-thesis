"""Shared constants and helpers for the G-P2 Phase 1 SCE audit.

Everything that encodes a *substantive* assumption about the survey (variable
names, eligibility rules, valid ranges) lives here so that it can be reviewed in
one place and changed once the official questionnaire has been re-read.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[1]
RAW_DIR = REPO / "data" / "raw"          # gitignored: provider workbooks + docs
DERIVED_DIR = REPO / "data" / "derived"  # gitignored: person-month panel (microdata)
OUT_DIR = REPO / "outputs"
GEN_DIR = OUT_DIR / "generated"          # machine-written tables (aggregates only)

BASE = "https://www.newyorkfed.org/medialibrary/interactives/sce/sce/downloads/data/"

# Official SCE core public microdata releases (CMD Data Bank). File names are
# those listed in the October 2026 adjudication report; re-check the Data Bank
# page on each retrieval because the "latest" file is overwritten in place.
MICRODATA_FILES = {
    "2013_2016": "frbny-sce-public-microdata-complete-13-16.xlsx",
    "2017_2019": "frbny-sce-public-microdata-complete-17-19.xlsx",
    "2020_2024": "frbny-sce-public-microdata-20-24.xlsx",
    "latest": "frbny-sce-public-microdata-latest.xlsx",
}
DOC_URLS = {
    "core_questionnaire.pdf": BASE + "frbny-sce-survey-core-module-public-questionnaire.pdf",
    "databank.html": "https://www.newyorkfed.org/microeconomics/databank.html",
    "sce_faq.html": "https://www.newyorkfed.org/microeconomics/sce/sce-faq",
}

# --- Variables ---------------------------------------------------------------
KEY_VARS = ["userid", "date"]
DESIGN_VARS = ["weight", "tenure"]
# Q10_1..Q10_10: "check all that apply" employment situation (wording to verify).
EMP_STATUS_VARS = [f"q10_{i}" for i in range(1, 11)]
EMP_DETAIL_VARS = ["q11", "q12new"]
CORE_VARS = {
    "q13new": "P(lose main job within 12 months), percent chance",
    "q22new": "P(find acceptable job within 3 months | lose main job this month), percent chance",
    "q30new": "P(unable to make minimum debt payment within 3 months), percent chance",
}
# Candidate 'general pessimism' controls; used only if present in every file.
SENTIMENT_VARS = {
    "q4new": "P(US unemployment rate higher in 12 months)",
    "q1": "Household financial situation vs 12 months ago (categorical)",
    "q2": "Expected household financial situation in 12 months (categorical)",
    "q6new": "P(US stock prices higher in 12 months)",
}
DEMOG_VARS = ["q32", "q33", "q36", "q47", "_state", "_age_cat", "_edu_cat",
              "_hh_inc_cat", "_region_cat"]

PROB_MIN, PROB_MAX = 0.0, 100.0

# --- Eligibility (Phase 1 working definition; see variable_validation.md) ----
# Employed = ticked "working full-time" (Q10_1) or "working part-time" (Q10_2).
# Main sample additionally requires Q12new == 1 ("work for someone else"),
# because a job-loss probability for the self-employed is a different object.
EMPLOYED_CODES = ["q10_1", "q10_2"]
SICK_LEAVE_CODE = "q10_5"   # sensitivity only
EMPLOYEE_CODE = 1           # Q12new value for "work for someone else" (TO VERIFY)

HEAP_POINTS = [0, 50, 100]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def find_header_row(raw: pd.DataFrame, token: str = "userid", max_rows: int = 30) -> int | None:
    """Return the index of the first row whose cells contain `token`."""
    for i in range(min(max_rows, len(raw))):
        cells = raw.iloc[i].astype(str).str.strip().str.lower()
        if (cells == token).any():
            return i
    return None


def to_prob(s: pd.Series) -> tuple[pd.Series, pd.Series]:
    """Coerce to numeric percent chance. Returns (clean, invalid_flag).

    Non-numeric strings and values outside [0, 100] are set to NaN and flagged;
    genuine blanks are *not* flagged as invalid (they are item non-response or
    routing skips, audited separately).
    """
    num = pd.to_numeric(s, errors="coerce")
    nonblank = s.notna() & (s.astype(str).str.strip() != "")
    invalid = (nonblank & num.isna()) | (num < PROB_MIN) | (num > PROB_MAX)
    return num.where(~invalid), invalid


def parse_date(s: pd.Series) -> pd.Series:
    """SCE `date` is expected as YYYYMM (int). Fall back to generic parsing."""
    txt = s.astype(str).str.replace(r"\.0$", "", regex=True).str.strip()
    out = pd.to_datetime(txt, format="%Y%m", errors="coerce")
    miss = out.isna() & s.notna()
    if miss.any():
        out.loc[miss] = pd.to_datetime(s[miss], errors="coerce")
    return out.dt.to_period("M")


def write_json(obj, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, default=str))


def md_table(df: pd.DataFrame, floatfmt: str = "{:.2f}") -> str:
    """Minimal markdown table writer (avoids a `tabulate` dependency)."""
    def fmt(v):
        if isinstance(v, (float, np.floating)):
            return "" if np.isnan(v) else floatfmt.format(v)
        return str(v)
    cols = [str(c) for c in df.columns]
    lines = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    for row in df.itertuples(index=False):
        lines.append("| " + " | ".join(fmt(v) for v in row) + " |")
    return "\n".join(lines)
