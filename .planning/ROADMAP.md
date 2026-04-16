# Roadmap: Korea Discount Study

## Overview

Five phases that follow the strict pipeline dependency order of an empirical finance paper. Phase 1 builds the reproducible repo scaffold and produces the canonical panel dataset — the critical path that everything else depends on. Phase 2 validates the panel visually and quantitatively. Phase 3 runs the primary econometric analyses (event study, panel OLS, geopolitical sub-analysis). Phase 4 stress-tests those results with synthetic control and robustness checks. Phase 5 assembles all outputs into a submission-ready LaTeX paper with a clean replication package.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [x] **Phase 1: Repo Setup and Data Pipeline** - Build reproducible repo scaffold, lock event dates, acquire raw data, and produce `panel.parquet`
- [ ] **Phase 2: Descriptive Analysis** - Validate the panel and document the Korea Discount visually and statistically
- [ ] **Phase 3: Primary Empirics** - Run event study, panel OLS, and geopolitical risk sub-analysis
- [ ] **Phase 4: Synthetic Control and Robustness** - Synthetic control for 2023 TSE reform and full robustness test suite
- [ ] **Phase 5: Paper Assembly and Replication Package** - Write all paper sections, integrate outputs into LaTeX, deliver submission-ready PDF and replication package

## Phase Details

### Phase 1: Repo Setup and Data Pipeline
**Goal**: Researcher has a working reproducible environment, locked event dates in config.py, and a verified canonical `panel.parquet` file ready for all downstream analyses
**Depends on**: Nothing (first phase)
**Requirements**: DATA-01, DATA-02, DATA-03, DATA-04, DATA-05
**Success Criteria** (what must be TRUE):
  1. Running `pip install -r requirements.txt` in a fresh environment installs all pinned dependencies without error
  2. config.py exists with event dates locked to official policy records (2014-02-01, 2015-06-01, 2023-03-01) before any data is loaded
  3. `data/raw/` contains immutable source files with a manifest documenting source URL, vintage date, and download method for each series
  4. Running `python src/data/build_panel.py` produces `data/processed/panel.parquet` with schema (date, country, pb, pe) covering ~2004-2024 at monthly frequency for KOSPI, TOPIX, SP500, MSCI_EM with no undocumented missing observations
  5. The 2008-2009 global financial crisis period shows a sharp P/B compression for all markets in the panel, confirming absence of survivorship bias
**Plans**: 3 plans

Plans:
- [x] 01-PLAN-01.md — Repo scaffold: config.py (event dates firewall) + requirements.txt (pinned deps)
- [x] 01-PLAN-02.md — Data pipeline: build_panel.py produces data/processed/panel.parquet
- [x] 01-PLAN-03.md — Verification: verify_panel.py confirms schema, coverage, and GFC compression

### Phase 2: Descriptive Analysis
**Goal**: The Korea Discount is documented visually and quantitatively — Figure 1 and Table 1 exist and the discount magnitude is stated in basis points with statistical significance
**Depends on**: Phase 1
**Requirements**: DESC-01, DESC-02, DESC-03
**Success Criteria** (what must be TRUE):
  1. Figure 1 (KOSPI P/B vs TOPIX, S&P 500, MSCI EM over 20 years) is generated programmatically and saved as a publication-quality PDF in `output/figures/`
  2. Table 1 (summary statistics: mean, median, SD, min, max by country and sub-period) is generated programmatically and saved as a LaTeX fragment in `output/tables/`
  3. The Korea Discount magnitude is computed as a time-averaged P/B spread in basis points with a t-statistic or confidence interval, ready for use verbatim in the abstract and introduction
**Plans**: TBD

### Phase 3: Primary Empirics
**Goal**: Event study, panel OLS, and geopolitical risk sub-analysis are fully estimated — results tables and figures exist and are ready for inclusion in the paper
**Depends on**: Phase 2
**Requirements**: EVNT-01, EVNT-02, EVNT-03, EVNT-04, OLS-01, OLS-02, OLS-03, GEO-01, GEO-02, GEO-03
**Success Criteria** (what must be TRUE):
  1. The stacked event study (Cengiz et al. 2019 design) estimates cumulative abnormal valuation changes separately for each of the three Japan reform dates with heteroskedasticity-robust standard errors; CAR figures and coefficient tables are saved to `output/`
  2. Panel OLS with two-way country + time fixed effects (`linearmodels.PanelOLS`) estimates reform-interaction dummies; regression table is LaTeX-formatted with wild-bootstrap standard errors clustered by country
  3. A North Korea escalation event indicator series is constructed from GDELT or the Caldara-Iacoviello GPR index; KOSPI valuation response to escalation events is estimated and results are written up with explicit partial-identification caveats
  4. All three analyses read exclusively from `data/processed/panel.parquet`; no analysis module imports from another analysis module
**Plans**: TBD

### Phase 4: Synthetic Control and Robustness
**Goal**: The synthetic control for the 2023 TSE reform is estimated and all planned robustness checks pass — the primary result is confirmed robust to alternative specifications
**Depends on**: Phase 3
**Requirements**: SYNTH-01, SYNTH-02, SYNTH-03, ROBUST-01, ROBUST-02, ROBUST-03, ROBUST-04
**Success Criteria** (what must be TRUE):
  1. Synthetic control for Japan using ADH (2010) estimates for the 2023 TSE P/B reform event; output includes pre-treatment RMSPE, donor pool weights, and a pre/post gap plot saved to `output/figures/`
  2. Donor pool composition is documented with explicit SUTVA justification; in-space and in-time placebo tests are run and their results are saved alongside the primary synthetic control output
  3. Placebo falsification tests run on non-reform markets (e.g., Taiwan, Indonesia) over the same event windows, showing null or negligible effects
  4. Primary event study and OLS results are replicated using P/E instead of P/B, and with an alternative control group (MSCI EM ex-China or substituted EM benchmark), with results saved to `output/robustness/`
**Plans**: TBD

### Phase 5: Paper Assembly and Replication Package
**Goal**: A complete, compiling LaTeX paper exists as a PDF integrating all programmatically generated figures and tables, and running `python run_all.py` followed by `latexmk -pdf paper/main.tex` reproduces the full paper from raw data
**Depends on**: Phase 4
**Requirements**: PAPER-01, PAPER-02, PAPER-03, PAPER-04, PAPER-05, PAPER-06, PAPER-07, PAPER-08, PAPER-09, PAPER-10, POLICY-01, POLICY-02, OUTPUT-01, OUTPUT-02, OUTPUT-03
**Success Criteria** (what must be TRUE):
  1. `paper/main.tex` compiles to a clean PDF (~35-50 pages) containing all ten required sections (abstract, introduction, institutional background, literature review, data, causal mechanisms, empirical strategy, discussion/limitations, conclusion, appendices)
  2. Every figure and table in the PDF is included via `\includegraphics{}` or `\input{}` pointing to a file in `output/` — no manually created charts or hand-typed numbers
  3. Policy section provides specific near-term recommendations tied to FSC, KRX, and stewardship code levers; counterfactual projection for Korea is clearly labeled as illustrative
  4. Running `python run_all.py` from a clean checkout (with raw data present) regenerates all figures and tables without error; `requirements.txt` pins all dependencies and a README documents the two-command reproduction workflow
**Plans**: TBD

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3 → 4 → 5

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Repo Setup and Data Pipeline | 3/3 | Complete | 2026-04-16 |
| 2. Descriptive Analysis | 0/TBD | Not started | - |
| 3. Primary Empirics | 0/TBD | Not started | - |
| 4. Synthetic Control and Robustness | 0/TBD | Not started | - |
| 5. Paper Assembly and Replication Package | 0/TBD | Not started | - |
