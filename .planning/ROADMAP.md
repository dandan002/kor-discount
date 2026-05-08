# Roadmap: Korea Discount — Value-Up Compliance Study

## Overview

Four horizontal layers stack a complete, reproducible empirical pipeline. Phase 1 builds the project skeleton, utility modules, and both Bloomberg acquisition scripts — ready to run at a terminal. After Phase 1 the user runs the scripts at a Bloomberg terminal and the raw CSVs land in `data/raw/bloomberg/`. Phase 2 builds the compliance and master datasets from those real CSVs. Phase 3 implements all three analytical sections of the paper (descriptive, logit, fundamentals, event study). Phase 4 wraps the LaTeX paper scaffold around the outputs and validates the full pipeline end-to-end.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [ ] **Phase 1: Foundation** - Project infrastructure, utility modules, and Bloomberg acquisition scripts (ready to run at terminal)
- [ ] **Phase 2: Data Pipeline** - Compliance classification dataset and master covariate merge
- [ ] **Phase 3: Analysis** - Descriptive stats, logit regression, fundamentals comparison, and event study
- [ ] **Phase 4: Paper + Validation** - LaTeX paper scaffold and end-to-end pipeline validation on real data

## Phase Details

### Phase 1: Foundation
**Goal**: All project infrastructure is in place and both Bloomberg acquisition scripts are complete and ready to run at a Bloomberg terminal — directory layout exists, utilities are importable, and the scripts contain correct BDS/BDP/BDH field calls
**Depends on**: Nothing (first phase)
**Requirements**: INFR-01, INFR-02, INFR-03, INFR-04, INFR-05, UTIL-01, UTIL-02, UTIL-03, UTIL-04, DATA-01, DATA-03, DATA-05
**Success Criteria** (what must be TRUE):
  1. `src/00_build_universe.py` exists with correct BDS("KOSPI Index", "INDX_MEMBERS") and BDP calls for all required fields; script is runnable at a Bloomberg terminal
  2. `src/01_bloomberg_pull.py` exists with correct BDP snapshot pull (all 12 fields), BDH ROE panel, and BDH returns panel; script is runnable at a Bloomberg terminal
  3. Running either acquisition script without blpapi installed prints an informative error and exits non-zero (does not traceback)
  4. `from utils.stats import winsorize` and `from utils.latex_tables import df_to_latex` import successfully and are callable
  5. `make acquire` target exists in Makefile; `make analysis` and `make paper` targets exist for later phases
**Plans**: 5 plans

Plans:
- [x] 01-01-PLAN.md — Cleanup + infrastructure scaffold (gitignore, prior-project data move, utils/ package, requirements.txt, .env.example, README.md)
- [ ] 01-02-PLAN.md — Utils package implementation (bbg.py, stats.py, latex_tables.py)
- [ ] 01-03-PLAN.md — src/00_build_universe.py (KOSPI universe pull)
- [ ] 01-04-PLAN.md — src/01_bloomberg_pull.py (snapshot, ROE panel, returns panel)
- [ ] 01-05-PLAN.md — Makefile (acquire guard + analysis + paper + all targets)

> **Bloomberg Terminal Checkpoint**
> After Phase 1 completes, go to a Bloomberg terminal and run:
> ```bash
> pip install blpapi
> python utils/bbg.py --test               # verify connection (D-03: utils/ at project root)
> python src/00_build_universe.py          # → data/raw/universe_raw.csv
> python src/01_bloomberg_pull.py          # → data/raw/bloomberg/*.csv
> ls -lh data/raw/bloomberg/              # confirm three non-empty CSVs
> ```
> Once `data/raw/bloomberg/` contains snapshot_2023.csv, roe_panel.csv, and returns_panel.csv, proceed to Phase 2.

### Phase 2: Data Pipeline
**Goal**: The master analysis file sample.csv exists and all downstream analysis scripts can load it — compliance classifications coded, event dates extracted, and all covariates joined and winsorized from real Bloomberg data
**Depends on**: Phase 1 + Bloomberg terminal run (data/raw/bloomberg/*.csv must exist)
**Requirements**: COMP-01, COMP-02, COMP-03, MSTR-01, MSTR-02, MSTR-03
**Success Criteria** (what must be TRUE):
  1. `python src/02_build_compliance.py` produces `data/processed/compliance.csv` with a three-way compliance_code column (0/1/2) and `data/processed/events.csv` with disclosure dates for codes 1 and 2
  2. Running the script without compliance_coded.csv present exits with an informative error message (not a Python traceback)
  3. `python src/03_merge_covariates.py` produces `data/processed/sample.csv` containing all columns specified in ROADMAP Phase 4.3 (ticker through disclosure_date)
  4. sample.csv missingness report prints to stdout; all continuous variables are winsorized at 1st/99th percentiles
**Plans**: TBD

### Phase 3: Analysis
**Goal**: All four analysis scripts run against real data and produce the correct output files — four .tex tables and four .pdf figures exist under outputs/
**Depends on**: Phase 2
**Requirements**: DESC-01, DESC-02, DESC-03, DESC-04, LOGI-01, LOGI-02, LOGI-03, LOGI-04, FUND-01, FUND-02, FUND-03, FUND-04, EVNT-01, EVNT-02, EVNT-03, EVNT-04, EVNT-05, EVNT-06, EVNT-07
**Success Criteria** (what must be TRUE):
  1. `outputs/tables/table1_summary.tex` exists and contains a three-group (0/1/2) summary statistics table with means, medians, and SDs; `outputs/figures/fig1_pbr_dist.pdf` and `outputs/figures/fig2_compliance_breakdown.pdf` both exist
  2. `outputs/tables/table2_logit.tex` exists with three side-by-side logit specifications; average marginal effects are reported; an appendix robustness table with sector FE is produced
  3. `outputs/tables/table3_fundamentals.tex` exists; `outputs/figures/fig3_roe_trends.pdf` shows ROE trajectories 2019–2023 by compliance group; cash ratio t-test result is printed to stdout
  4. `outputs/tables/table4_cars.tex` exists with Patell and BMP test statistics; power analysis minimum-detectable CAR is printed to stdout; `outputs/figures/fig4_car_plot.pdf` exists with SE bands by group; cross-sectional CAR regression is included
**Plans**: TBD

### Phase 4: Paper + Validation
**Goal**: The LaTeX paper compiles to a PDF without errors and the full pipeline passes end-to-end from real data — `make analysis && make paper` produces paper.pdf with all tables and figures resolved
**Depends on**: Phase 3
**Requirements**: LTEX-01, LTEX-02, LTEX-03, LTEX-04, LTEX-05, E2E-01, E2E-02, E2E-03
**Success Criteria** (what must be TRUE):
  1. `paper/main.tex` compiles with `pdflatex + biber + pdflatex + pdflatex` without errors and produces a PDF; all nine section \input{} references resolve
  2. All 9 section files exist with placeholder content; paper.sty and econometrics.sty define fonts, margins, booktabs table conventions, and figure conventions
  3. `paper/references.bib` contains BibTeX entries for all key references listed in the technical ROADMAP.md
  4. `make analysis && make paper` completes without errors and all 4 tables + 4 figures appear in outputs/; \input{} table and figure references in the compiled PDF resolve without undefined-reference warnings
**Plans**: TBD

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3 → 4

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Foundation | 0/5 | Not started | - |
| 2. Data Pipeline | 0/TBD | Not started | - |
| 3. Analysis | 0/TBD | Not started | - |
| 4. Paper + Validation | 0/TBD | Not started | - |
