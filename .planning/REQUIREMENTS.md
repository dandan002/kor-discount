# Requirements: Korea Discount — Value-Up Compliance Study

**Defined:** 2026-05-08
**Core Value:** A complete, reproducible analysis pipeline that produces all tables and figures from raw Bloomberg/KRX data — so the paper can be compiled and re-run with one command.

## v1 Requirements

### Infrastructure

- [x] **INFR-01**: Project directory layout matches ROADMAP spec (data/, src/, outputs/, paper/, utils/)
- [x] **INFR-02**: requirements.txt lists all Python dependencies with pinned versions
- [x] **INFR-03**: Makefile provides `make acquire`, `make analysis`, `make paper`, and `make all` targets
- [x] **INFR-04**: .env pattern configured for Bloomberg host/port; template .env.example committed
- [x] **INFR-05**: Virtual environment setup documented in README

### Utilities

- [x] **UTIL-01**: utils/bbg.py implements BDP, BDH, BDS wrappers with graceful ImportError fallback when blpapi not installed
- [x] **UTIL-02**: utils/bbg.py passes connection test when run as `python src/utils/bbg.py --test`
- [x] **UTIL-03**: utils/stats.py provides shared helpers for winsorization, robust SE computation, and Cohen's Kappa
- [x] **UTIL-04**: utils/latex_tables.py exports a DataFrame to a standalone .tex table fragment with booktabs formatting, caption, label, and optional footnote

### Data Acquisition

- [x] **DATA-01**: src/00_build_universe.py pulls live KOSPI universe from Bloomberg (BDS + BDP) and saves universe_raw.csv
- [x] **DATA-03**: src/01_bloomberg_pull.py pulls snapshot_2023.csv, roe_panel.csv, and returns_panel.csv from Bloomberg
- [x] **DATA-05**: All Bloomberg scripts fail gracefully with an informative error when blpapi is not installed

### Compliance Dataset

- [ ] **COMP-01**: src/02_build_compliance.py reads compliance_coded.csv and produces compliance.csv with three-way classification (0/1/2)
- [ ] **COMP-02**: src/02_build_compliance.py produces events.csv with disclosure dates for compliant firms (codes 1 and 2)
- [ ] **COMP-03**: Script validates input schema and reports missingness; exits with informative error if compliance_coded.csv not found

### Master Dataset

- [ ] **MSTR-01**: src/03_merge_covariates.py joins Bloomberg snapshot + compliance + chaebol + controlling shareholder % on ticker
- [ ] **MSTR-02**: Output sample.csv contains all columns specified in ROADMAP Phase 4.3
- [ ] **MSTR-03**: Script winsorizes all continuous variables at 1st/99th percentiles and reports missingness by variable

### Descriptive Statistics

- [ ] **DESC-01**: src/04_descriptive.py produces Table 1 (summary stats split by compliance group) as outputs/tables/table1_summary.tex
- [ ] **DESC-02**: src/04_descriptive.py produces Figure 1 (PBR distribution by compliance group) as outputs/figures/fig1_pbr_dist.pdf
- [ ] **DESC-03**: src/04_descriptive.py produces Figure 2 (compliance breakdown by sector and chaebol) as outputs/figures/fig2_compliance_breakdown.pdf
- [ ] **DESC-04**: Script reports t-test / Mann-Whitney U comparisons across compliance groups for each continuous covariate

### Part A — Logit Regression

- [ ] **LOGI-01**: src/05_logit_compliance.py runs three logit specifications (binary complied, binary quantitative, ordered logit) with HC3 robust SEs
- [ ] **LOGI-02**: Script reports average marginal effects (AME) via statsmodels .get_margeff()
- [ ] **LOGI-03**: Script exports side-by-side regression table as outputs/tables/table2_logit.tex
- [ ] **LOGI-04**: Robustness checks with sector FE and excluding top-10 chaebols reported in appendix table

### Part B — Fundamentals Comparison

- [ ] **FUND-01**: src/06_fundamentals_comparison.py computes mean ROE per compliance group per year (2019–2023) and plots line chart as Figure 3
- [ ] **FUND-02**: Script compares dividend growth rates across compliance groups (DPS 2019–2023)
- [ ] **FUND-03**: Script tests whether non-compliant firms have higher cash ratios (t-test / regression)
- [ ] **FUND-04**: Script exports Table 3 (fundamentals comparison) as outputs/tables/table3_fundamentals.tex

### Part C — Event Study

- [ ] **EVNT-01**: src/07_event_study.py estimates market model for each disclosure event using −120 to −21 estimation window
- [ ] **EVNT-02**: Script computes abnormal returns and CAR for −1 to +5 (primary) and −1 to +20 (secondary) event windows
- [ ] **EVNT-03**: Script runs power analysis (Brown & Warner 1985) and reports minimum detectable CAR given actual N
- [ ] **EVNT-04**: Script reports Patell standardized t-test and Boehmer-Musumeci-Poulsen (1991) test statistics
- [ ] **EVNT-05**: Script runs cross-sectional CAR regression (quantitative dummy, foreign ownership, chaebol, PBR, log market cap)
- [ ] **EVNT-06**: Script exports Table 4 (CAR results) as outputs/tables/table4_cars.tex
- [ ] **EVNT-07**: Script exports Figure 4 (CAR plot by group with SE bands) as outputs/figures/fig4_car_plot.pdf

### LaTeX Paper

- [ ] **LTEX-01**: paper/main.tex compiles end-to-end with pdflatex + biber without errors
- [ ] **LTEX-02**: All 9 section files exist (01_introduction through 09_conclusion) with placeholder content and \input{} wired into main.tex
- [ ] **LTEX-03**: paper/style/paper.sty and paper/style/econometrics.sty define fonts, margins, and table/figure conventions
- [ ] **LTEX-04**: paper/references.bib contains BibTeX entries for all key references listed in ROADMAP
- [ ] **LTEX-05**: Makefile paper target compiles LaTeX with biber and produces outputs/paper.pdf

### End-to-End Validation

- [ ] **E2E-01**: Full real-data pipeline runs without errors: `make analysis && make paper`
- [ ] **E2E-02**: All outputs/ files (4 tables, 4 figures) are produced from real data in data/processed/sample.csv
- [ ] **E2E-03**: Paper compiles with \input{} table and figure references resolving correctly against real outputs

## v2 Requirements

### Robustness & Extensions

- **ROBU-01**: KOSDAQ firms analyzed separately as appendix robustness check
- **ROBU-02**: KCGS governance scores merged and compared across compliance groups (if accessible)
- **ROBU-03**: Propensity score matching for fundamentals comparison (Part B)
- **ROBU-04**: Additional event windows (−5 to +10, −1 to +40) as appendix

### Automation

- **AUTO-01**: DART OpenAPI Python client for automated controlling shareholder % retrieval
- **AUTO-02**: Automated KRX disclosure list download script

## Out of Scope

| Feature | Reason |
|---------|--------|
| KOSDAQ analysis in v1 | Illiquid; degrades event study; deferred to appendix robustness |
| KCGS governance scores in v1 | Optional; not required for core three-part analysis |
| Causal identification (IV, DiD) | Explicitly correlational study; selection acknowledged in text |
| Web scraping for KRX/DART | Manual data collection is planned approach for compliance coding |
| Real-time or automated Bloomberg re-runs | One-time pull at library terminal; static CSVs thereafter |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| INFR-01 through INFR-05 | Phase 1 | Pending |
| UTIL-01 through UTIL-04 | Phase 1 | Pending |
| DATA-01, DATA-03, DATA-05 | Phase 1 | Pending |
| COMP-01 through COMP-03 | Phase 2 | Pending |
| MSTR-01 through MSTR-03 | Phase 2 | Pending |
| DESC-01 through DESC-04 | Phase 3 | Pending |
| LOGI-01 through LOGI-04 | Phase 3 | Pending |
| FUND-01 through FUND-04 | Phase 3 | Pending |
| EVNT-01 through EVNT-07 | Phase 3 | Pending |
| LTEX-01 through LTEX-05 | Phase 4 | Pending |
| E2E-01 through E2E-03 | Phase 4 | Pending |

**Coverage:**
- v1 requirements: 41 total
- Mapped to phases: 41
- Unmapped: 0 ✓

---
*Requirements defined: 2026-05-08*
*Last updated: 2026-05-08 after restructuring — mock mode removed entirely; Phase 1 goal is terminal-ready acquisition scripts*
