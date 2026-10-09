# G-P2 Phase 1 summary: reemployment beliefs and debt-payment distress

**Date:** 2026-10-09. **Scope:** feasibility only; no thesis analysis.

## What happened

* **Data verification could not be run.** `www.newyorkfed.org` (workbooks, questionnaire, FAQ)
  and the author and journal sites for the two key papers were **denied by this session's network
  egress policy** (proxy HTTP 403). The policy was changed during the session, but the change did
  not reach the running container. At the user's instruction the work is committed as
  **unverified**.
* **Built and smoke-tested:** a three-step reproducible pipeline, `code/01_download.py` →
  `02_build_panel.py` → `03_descriptives.py`. It downloads with SHA-256 manifests, builds the
  person-month panel, writes the full audit (keys, routing, missing and invalid answers,
  heaping, within-person variation, attrition, cross-release consistency), and produces
  descriptives. A preliminary model runs only when validation flags pass. It ran end-to-end on a
  **synthetic fixture**, which is not SCE data and was not reported.
* **Documented:** variable definitions, horizons and the prohibited product interpretation; data
  sources and licence handling; literature overlap with Mitra (2026) and Hartmann &
  Leth-Petersen (2024), with each claim's evidence basis marked.

No SCE numbers in this repository were computed in this session. The only counts quoted are the
adjudication report's and are labelled as such.

## Deliverables

| File | Status |
| - | - |
| `outputs/data_availability.md` | Complete (sources, licence); coverage **not replicated** |
| `outputs/variable_validation.md` | Checks specified and coded; all statuses ADJ, BK or PENDING |
| `outputs/sample_audit.csv` | Waterfall steps defined; counts **PENDING**; adjudication counts shown as prior values. Overwritten by `02_build_panel.py` with real counts |
| `outputs/preliminary_descriptives.md` | Table specification; **not run on SCE data** |
| `outputs/literature_overlap.md` | Complete with evidence tags; full texts must be re-read in Phase 2 |
| `outputs/phase1_feasibility.md` | Gate undetermined |
| `code/`, `tests/` | Reproducible pipeline and synthetic smoke test |

## Answers to the seven Phase 1 questions

**1. Are the three core variables usable?**
*Probably, but not verified here.* The adjudication report found `Q13new`, `Q22new` and
`Q30new` in the raw 2013–16 and latest files, with documented horizons: 12-month loss; 3-month
finding conditional on loss this month; 3-month inability to make a minimum debt payment. Two
issues must be settled before they are usable:
* the universe of `Q30new`: whether non-borrowers answer, and what a 0 means;
* the August-2013 change in `Q22` routing.

**2. How many eligible employed respondents and observations exist?**
*Not counted in this session.* The adjudication's **preliminary** filter covers 2013–16 only:
employee status plus bounded values of the three items. It gives **31,396 person-months from
5,327 people, 4,267 with ≥ 2 observations**. The latest file had 10,559 total rows from 2,159
IDs (2025-01 to 2025-10). The 2017–19 and 2020–24 files were never counted.

*Planning guess, not a count:* the adjudication's 2013–16 figures imply about 1,300 respondents
per month (56,444 / 43) and an eligibility share of about 56% (31,396 / 56,444). If both held
from 2013-06 to 2025-10 (149 months), the pooled eligible sample would be on the order of
100,000 person-months. `02_build_panel.py` replaces this with
the actual figure.

**3. Is within-person analysis feasible?**
*Structurally yes, substantively unknown.* Respondents stay up to about 12 months, and most
eligible 2013–16 respondents appear at least twice (adjudication). Whether `Q22new` and `Q30new`
actually change within person, beyond rounding and heaping noise, is the main open feasibility
question. `within_person.csv` and the first-difference table answer it directly.

**4. What survey-routing problems remain?**
All of them remain open, because the questionnaire could not be re-read:
* (a) the August-2013 `Q22` routing change and comparability of earlier months;
* (b) whether `Q13new` and `Q22new` are asked of the self-employed; main sample restricted to
  `Q12new = 1` pending this;
* (c) the universe of `Q30new` and the meaning of 0;
* (d) multi-ticked and "sick/other leave" employment statuses;
* (e) explicit missing codes vs blanks;
* (f) overlap between "latest" and 2020–24, and stability of variable names across the four
  releases.

Each has a coded check and a pass/fail rule.

**5. Can this project realistically produce a master's thesis?**
*Yes, conditionally.* The data are free, the core fields reportedly exist, and the design is
bounded: one association, one held-out prediction comparison, a few sensitivities. This holds
if Phase 2 confirms routing and within-person variation. It remains a completion-oriented backup
with a weak publication case, as the adjudication concluded.

**6. What is the most serious novelty obstacle?**
**Mitra (June 2026)** already uses SCE employed workers' job-loss *and* job-finding beliefs
and their interaction, and reports that the search response runs through job-loss fear rather
than finding beliefs. Combined with the common-pessimism critique, a referee can read G-P2 as
"the same beliefs with another pessimistic survey answer as the outcome." The only new element
is the debt-service outcome. It must show incremental, within-person, financially sized content
to count. Hartmann & Leth-Petersen (2024) already link labour-risk beliefs to household
self-insurance, with stronger administrative validation.

**7. What should be tested in Phase 2?**
1. Retrieve all four releases and the questionnaire. Run the pipeline. Replace every PENDING
   status. Record SHA-256 hashes and the actual last month.
2. Re-read the questionnaire verbatim for `Q10`, `Q12new`, `Q13new`, `Q22new`, `Q30new`.
   Resolve the `Q30new` universe and the Aug-2013 `Q22` change.
3. Manually trace 50 stratified person histories and set `manual_history_review_done`.
4. Within-person variation and heaping: decide whether the `Q22new` changes are signal.
5. Fix the magnitude of interest (2pp per 10pp, or a revised value) from descriptive scale,
   *before* looking at model output. Then run M0–M3 as preliminary associations.
6. Pre-specify the held-out prediction test: next-month `Q30new` from current `Q30new` +
   `Q13new`, with vs without `Q22new`, on later calendar months and on held-out persons.
7. Re-read the Mitra and Hartmann–Leth-Petersen full texts and confirm the overlap table. Run
   one SSRN/NBER search for SCE delinquency-expectation papers.
