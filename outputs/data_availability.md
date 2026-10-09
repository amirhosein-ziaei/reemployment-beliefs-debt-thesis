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

## Retrieval status

| Item | Status |
| - | - |
| Microdata workbooks (4) | **RETRIEVED** 2026-10-09 ~10:41 UTC, HTTP 200 for each file. SHA-256 per file in `outputs/generated/download_manifest.csv`. The server sent no `Last-Modified` header for the workbooks, so hash plus retrieval date identify the vintage |
| Core questionnaire PDF | **RETRIEVED** (HTTP 200; `Last-Modified` 2024-02-09; © 2013-2024) |
| Data Bank page, FAQ | **RETRIEVED** (HTTP 200). All four workbook file names above are linked from the Data Bank page as retrieved |
| Earlier attempts | 2026-10-09 ~09:53–10:28 UTC were denied by the session's egress policy (proxy HTTP 403); resolved after the environment's network access was changed |

## Coverage (RAW-P1: computed from the retrieved files; `outputs/generated/file_schema.csv`)

| File | Rows | User IDs | Months | First | Last | Columns |
| - | - | - | - | - | - | - |
| 2013–2016 | 56,444 | 8,735 | 43 | 2013-06 | 2016-12 | 220 |
| 2017–2019 | 47,681 | 7,379 | 36 | 2017-01 | 2019-12 | 220 |
| 2020–2024 | 71,976 | 9,751 | 60 | 2020-01 | 2024-12 | 229 |
| latest | 10,559 | 2,159 | 10 | 2025-01 | 2025-10 | 229 |
| **Pooled** | **186,660** | **24,592** | **149** | 2013-06 | 2025-10 | |

* The 2013–2016 and latest counts **match the adjudication report exactly**.
* The four files tile the calendar with **no gaps and no overlapping userid×month keys**
  (`cross_file_overlap.csv` is empty). Some `userid`s appear in two adjacent files: a respondent
  who straddles a year boundary keeps the same ID, so IDs are stable across releases.
* The usable end month is **2025-10**. That is consistent with the FAQ as retrieved: "For the
  SCE core survey and SCE Credit Access module, microdata are posted with a nine-month lag."
* Each workbook has one sheet (`Data`) with a one-row attribution preamble above the header.
* The 2020–2024 and latest files add 9 columns (`q1a`, `q1apart2` and seven `q9new2_*`
  5-year inflation-density fields). None are used here. All variables the project uses are
  present in all four files.
* The core file has **no debt-holding indicator**: `Q30new` is the only debt item.

## Licence and redistribution

* Each workbook carries this attribution line (RAW-P1, verbatim): "Source: Survey of Consumer
  Expectations, © 2013-26 Federal Reserve Bank of New York (FRBNY). The SCE data are available
  without charge at www.newyorkfed.org and may be used subject to license terms posted there.
  FRBNY disclaims any responsibility or legal liability for this analysis and interpretation of
  Survey of Consumer Expectations data." That is the 2020–24 and latest preamble; the 2013–16 and
  2017–19 files read "© 2013-20" and "© 2013-21". The full licence is in the questionnaire PDF. The pipeline stores each preamble in
  `file_schema.csv`.
* **Raw workbooks and person-level derived files are not committed.** `.gitignore` excludes
  `data/`, `*.xlsx` and `*.csv.gz`. Only code and aggregate tables are committed. Do not rehost the
  microdata.
* Cite with the workbook attribution line above, which takes precedence over any shorter form.

## What the core file does not contain

* No realised delinquency, default or credit-bureau link, and no debt-holding filter (RAW-P1: column list).
* No liquid-wealth measure in the core module (ADJ; not re-checked).
* Supplementary SCE modules (Credit Access; Household Spending; Labor Market) have separate
  release lags (FAQ: up to 18 months). They should only be linked after checking common IDs,
  timing and sample loss. They are **not used in Phase 1**.

## Access from the student's location

Raw access from any cloud host does not certify access from the student's normal network
connection in Iran (adjudication point). Keep dated local copies once retrieved.
