# Roadmap: Korea Discount — Value-Up Compliance Study

## Overview

Four horizontal layers stack a complete, reproducible empirical pipeline. Phase 1 lays the project skeleton and mock-data machinery so every downstream script can run offline. Phase 2 builds the compliance and master datasets that all analysis depends on. Phase 3 implements all three analytical sections of the paper (descriptive, logit, fundamentals, event study). Phase 4 wraps the LaTeX paper scaffold around the outputs and validates the full pipeline end-to-end.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [ ] **Phase 1: Foundation** - Project infrastructure, utility modules, and Bloomberg acquisition scripts with mock mode
- [ ] **Phase 2: Data Pipeline** - Compliance classification dataset and master covariate merge
- [ ] **Phase 3: Analysis** - Descriptive stats, logit regression, fundamentals comparison, and event study
- [ ] **Phase 4: Paper + Validation** - LaTeX paper scaffold and end-to-end mock pipeline validation

## Phase Details

### Phase 1: Foundation
**Goal**: The project can run its full mock pipeline offline — directory layout exists, all utilities are importable, and both acquisition scripts produce correct-schema CSVs with --mock
**Depends on**: Nothing (first phase)
**Requirements**: INFR-01, INFR-02, INFR-03, INFR-04, INFR-05, UTIL-01, UTIL-02, UTIL-03, UTIL-04, DATA-01, DATA-02, DATA-03, DATA-04, DATA-05
**Success Criteria** (what must be TRUE):
  1. `python src/00_build_universe.py --mock` produces `data/raw/universe_raw.csv` with 650 rows and correct columns (ticker, name, sector, industry, country_iso)
  2. `python src/01_bloomberg_pull.py --mock` produces snapshot_2023.csv, roe_panel.csv, and returns_panel.csv under data/raw/bloomberg/
  3. `python src/utils/bbg.py --test` runs without crashing when blpapi is not installed; running either acquisition script without --mock and without blpapi prints an informative error and exits non-zero
  4. `from utils.stats import winsorize` and `from utils.latex_tables import df_to_latex` import successfully and are callable
  5. `make mock` target exists in Makefile and completes without errors
**Plans**: TBD

### Phase 2: Data Pipeline
**Goal**: The master analysis file sample.csv exists and all downstream analysis scripts can load it — compliance classifications coded, event dates extracted, and all covariates joined and winsorized
**Depends on**: Phase 1
**Requirements**: COMP-01, COMP-02, COMP-03, MSTR-01, MSTR-02, MSTR-03
**Success Criteria** (what must be TRUE):
  1. `python src/02_build_compliance.py` produces `data/processed/compliance.csv` with a three-way compliance_code column (0/1/2) and `data/processed/events.csv` with disclosure dates for codes 1 and 2
  2. Running the script without compliance_coded.csv present exits with an informative error message (not a Python traceback)
  3. `python src/03_merge_covariates.py` produces `data/processed/sample.csv` containing all columns specified in ROADMAP Phase 4.3 (ticker through disclosure_date)
  4. sample.csv missingness report prints to stdout; all continuous variables are winsorized at 1st/99th percentiles
**Plans**: TBD

### Phase 3: Analysis
**Goal**: All four analysis scripts run against mock data and produce the correct output files — four .tex tables and four .pdf figures exist under outputs/
**Depends on**: Phase 2
**Requirements**: DESC-01, DESC-02, DESC-03, DESC-04, LOGI-01, LOGI-02, LOGI-03, LOGI-04, FUND-01, FUND-02, FUND-03, FUND-04, EVNT-01, EVNT-02, EVNT-03, EVNT-04, EVNT-05, EVNT-06, EVNT-07
**Success Criteria** (what must be TRUE):
  1. `outputs/tables/table1_summary.tex` exists and contains a three-group (0/1/2) summary statistics table with means, medians, and SDs; `outputs/figures/fig1_pbr_dist.pdf` and `outputs/figures/fig2_compliance_breakdown.pdf` both exist
  2. `outputs/tables/table2_logit.tex` exists with three side-by-side logit specifications; average marginal effects are reported; an appendix robustness table with sector FE is produced
  3. `outputs/tables/table3_fundamentals.tex` exists; `outputs/figures/fig3_roe_trends.pdf` shows ROE trajectories 2019–2023 by compliance group; cash ratio t-test result is printed to stdout
  4. `outputs/tables/table4_cars.tex` exists with Patell and BMP test statistics; power analysis minimum-detectable CAR is printed to stdout; `outputs/figures/fig4_car_plot.pdf` exists with SE bands by group; cross-sectional CAR regression is included
**Plans**: TBD

### Phase 4: Paper + Validation
**Goal**: The LaTeX paper compiles to a PDF without errors and the full mock pipeline passes end-to-end — a single `make all` from a clean state produces paper.pdf with all tables and figures resolved
**Depends on**: Phase 3
**Requirements**: LTEX-01, LTEX-02, LTEX-03, LTEX-04, LTEX-05, E2E-01, E2E-02, E2E-03
**Success Criteria** (what must be TRUE):
  1. `paper/main.tex` compiles with `pdflatex + biber + pdflatex + pdflatex` without errors and produces a PDF; all nine section \input{} references resolve
  2. All 9 section files exist with placeholder content; paper.sty and econometrics.sty define fonts, margins, booktabs table conventions, and figure conventions
  3. `paper/references.bib` contains BibTeX entries for all key references listed in the technical ROADMAP.md
  4. `make mock && make analysis && make paper` completes without errors and all 4 tables + 4 figures appear in outputs/; \input{} table and figure references in the compiled PDF resolve without undefined-reference warnings
**Plans**: TBD

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3 → 4

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Foundation | 0/TBD | Not started | - |
| 2. Data Pipeline | 0/TBD | Not started | - |
| 3. Analysis | 0/TBD | Not started | - |
| 4. Paper + Validation | 0/TBD | Not started | - |
