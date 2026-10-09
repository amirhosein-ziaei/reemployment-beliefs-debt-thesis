# reemployment-beliefs-debt-thesis

Candidate **G-P2** (backup master's thesis): among employed respondents in the NY Fed Survey of
Consumer Expectations, does perceived difficulty finding another job (`Q22new`) predict
subjective debt-payment distress (`Q30new`) beyond perceived job-loss risk (`Q13new`) and
general pessimism? Association only: no causal claims, no realised delinquency.

## Phase 1 (feasibility)

Start with `outputs/phase1_summary.md`. Other deliverables are in `outputs/`. Phase 1 was run on the
official SCE files retrieved 2026-10-09 (2013-06..2025-10); the association model is gated and has not been run.

```bash
pip install -r requirements.txt
python code/01_download.py        # needs network access to www.newyorkfed.org
python code/02_build_panel.py     # panel, routing and sample audit -> outputs/
python code/03_descriptives.py    # descriptives; model runs only if validation flags pass

# Smoke test on SYNTHETIC data (not SCE data; outputs go to a scratch directory)
python tests/make_synthetic_fixture.py /tmp/sce_fixture/raw
cd code && python 02_build_panel.py --raw /tmp/sce_fixture/raw --out /tmp/sce_fixture/out --derived /tmp/sce_fixture/derived \
        && python 03_descriptives.py --out /tmp/sce_fixture/out --derived /tmp/sce_fixture/derived --force
```

## Phase 2 (initial econometric evidence; exploratory)

Start with `outputs/phase2_summary.md`. The specification (`outputs/model_specification.md`) was
committed before any model was run. All estimates are **exploratory, pending independent human
validation** (`outputs/human_validation_guide.md`), and live in `outputs/exploratory/`.

```bash
python code/04_validation_package.py      # private review package -> data/review/ (gitignored)
python code/05_phase2_models.py           # Models A-C, inference variants, sensitivity list
python code/06_prediction.py              # next-month prediction comparison
python -m unittest discover -s tests -v   # automated tests (synthetic data)
```

## Data licence

The SCE microdata are © Federal Reserve Bank of New York and carry the provider's licence and
attribution terms. Raw workbooks and person-level derived files live in `data/`, which is
gitignored and never committed. Only code and aggregate tables are committed.
