"""Step 1: retrieve the official SCE core public microdata and documentation.

Files go to data/raw/<retrieval-date>/ (gitignored). A manifest with URL,
HTTP status, size, SHA-256 and Last-Modified header is written both next to the
raw files and to outputs/generated/download_manifest.csv (committed), so that a
reviewer can tell exactly which vintage of the mutable "latest" file was used.

Usage:  python code/01_download.py [--only latest] [--date YYYY-MM-DD]
"""
from __future__ import annotations

import argparse
import datetime as dt
import sys

import pandas as pd
import requests

from sce_common import BASE, DOC_URLS, GEN_DIR, MICRODATA_FILES, RAW_DIR, sha256, write_json

UA = {"User-Agent": "Mozilla/5.0 (academic research; SCE microdata audit)"}


def fetch(url: str, dest) -> dict:
    rec = {"url": url, "file": dest.name, "retrieved_utc": dt.datetime.now(dt.timezone.utc).isoformat()}
    try:
        with requests.get(url, headers=UA, stream=True, timeout=120) as r:
            rec["http_status"] = r.status_code
            rec["last_modified"] = r.headers.get("Last-Modified")
            rec["content_type"] = r.headers.get("Content-Type")
            if r.status_code != 200:
                return rec
            with open(dest, "wb") as f:
                for chunk in r.iter_content(1 << 20):
                    f.write(chunk)
        rec["bytes"] = dest.stat().st_size
        rec["sha256"] = sha256(dest)
    except requests.RequestException as e:  # network policy, DNS, timeouts
        rec["error"] = f"{type(e).__name__}: {e}"[:300]
    return rec


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", nargs="*", help="subset of release keys", default=None)
    ap.add_argument("--date", default=dt.date.today().isoformat())
    args = ap.parse_args()

    outdir = RAW_DIR / args.date
    outdir.mkdir(parents=True, exist_ok=True)
    records = []
    for key, fname in MICRODATA_FILES.items():
        if args.only and key not in args.only:
            continue
        rec = fetch(BASE + fname, outdir / fname)
        rec["release"] = key
        records.append(rec)
        print(key, rec.get("http_status"), rec.get("bytes"), rec.get("error", ""))
    for fname, url in DOC_URLS.items():
        rec = fetch(url, outdir / fname)
        rec["release"] = "documentation"
        records.append(rec)
        print(fname, rec.get("http_status"), rec.get("bytes"), rec.get("error", ""))

    write_json(records, outdir / "MANIFEST.json")
    GEN_DIR.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(records).to_csv(GEN_DIR / "download_manifest.csv", index=False)
    ok = [r for r in records if r.get("release") != "documentation" and r.get("sha256")]
    if not ok:
        print("No microdata retrieved; see download_manifest.csv", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
