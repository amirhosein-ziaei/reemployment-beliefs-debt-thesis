# Data availability: NY Fed Survey of Consumer Expectations, core public microdata

## Provider and access route

* **Provider:** Federal Reserve Bank of New York, Center for Microeconomic Data (CMD).
* **Product:** Survey of Consumer Expectations (SCE), **core module**, public microdata.
* **Landing page:** CMD Data Bank, <https://www.newyorkfed.org/microeconomics/databank.html>
* **FAQ (release lags):** <https://www.newyorkfed.org/microeconomics/sce/sce-faq>
* **Questionnaire:** <https://www.newyorkfed.org/medialibrary/interactives/sce/sce/downloads/data/frbny-sce-survey-core-module-public-questionnaire.pdf>

## Exact source files

| Release key | URL |
| - | - |
| 2013–2016 | <https://www.newyorkfed.org/medialibrary/interactives/sce/sce/downloads/data/frbny-sce-public-microdata-complete-13-16.xlsx> |
| 2017–2019 | <https://www.newyorkfed.org/medialibrary/interactives/sce/sce/downloads/data/frbny-sce-public-microdata-complete-17-19.xlsx> |
| 2020–2024 | <https://www.newyorkfed.org/medialibrary/interactives/sce/sce/downloads/data/frbny-sce-public-microdata-20-24.xlsx> |
| latest | <https://www.newyorkfed.org/medialibrary/interactives/sce/sce/downloads/data/frbny-sce-public-microdata-latest.xlsx> |

`code/01_download.py` retrieves all four files plus the documentation into
`data/raw/<YYYY-MM-DD>/` and writes a manifest. The manifest records URL, HTTP status, bytes,
SHA-256 and the `Last-Modified` header, and goes to `outputs/generated/download_manifest.csv`.
The "latest" file is overwritten in place by the provider, so the SHA-256 plus the retrieval
date identify the vintage actually used.

## Retrieval status in this session

| Item | Status |
| - | - |
| Microdata workbooks (4) | **NOT RETRIEVED.** `www.newyorkfed.org` denied by the session's egress policy (HTTP 403 at the proxy) |
| Questionnaire PDF, Data Bank page, FAQ | **NOT RETRIEVED** (same host) |
| Date of attempts | 2026-10-09 (UTC), repeated ~09:53–10:28; final scripted attempt logged in `outputs/generated/download_manifest.csv` |

To retrieve, allow `www.newyorkfed.org` in the environment's network settings, start a session
in which the change is active, then run `python code/01_download.py`.

## Coverage: what is known and what is not

Coverage below is **reported by the October 2026 adjudication report** (it downloaded two of the
four files) and was **not replicated here**:

| File | Rows | User IDs | Months | First | Last |
| - | - | - | - | - | - |
| 2013–2016 | 56,444 | 8,735 | 43 | 2013-06 | 2016-12 |
| latest (as downloaded for the adjudication) | 10,559 | 2,159 | 10 | 2025-01 | 2025-10 |
| 2017–2019 | not downloaded | | | | |
| 2020–2024 | not downloaded | | | | |

* **Do not assume data through October 2026.** The SCE FAQ (per adjudication) states a
  **nine-month release lag** for core microdata. Monthly releases of aggregate statistics run to
  late 2026, but public microdata trail them. The usable end date is the maximum `date` in the
  file actually retrieved, which `file_schema.csv` records (`last_month`).
* Whether 2017–2019 and 2020–2024 begin and end exactly at calendar-year boundaries, and whether
  "latest" overlaps "2020–2024", is **unknown** until download. The overlap check handles both
  cases.
* The 2013–2016 file starts in June 2013, not January 2013.

## Licence and redistribution

* The workbooks carry the New York Fed's licence and attribution terms (ADJ). The pipeline stores
  the workbook preamble text in `file_schema.csv` (`preamble`), so the exact terms are archived
  with each retrieval. Keep the downloaded licence with the cached data.
* **Raw workbooks and person-level derived files are not committed.** `.gitignore` excludes
  `data/`, `*.xlsx` and `*.csv.gz`. Only code and aggregate tables are committed. Do not rehost the
  microdata.
* Cite as: Federal Reserve Bank of New York, *Survey of Consumer Expectations*, © 2013–2026
  Federal Reserve Bank of New York. Use the exact citation text in the workbook preamble, which
  takes precedence.

## What the core file does not contain (ADJ; not re-checked)

* No realised delinquency, default or credit-bureau link.
* No liquid-wealth measure in the core module.
* Supplementary SCE modules (Credit Access; Household Spending; Labor Market) have separate
  release lags (FAQ: up to 18 months). They should only be linked after checking common IDs,
  timing and sample loss. They are **not used in Phase 1**.

## Access from the student's location

Raw access from any cloud host does not certify access from the student's normal network
connection in Iran (adjudication point). Keep dated local copies once retrieved.
