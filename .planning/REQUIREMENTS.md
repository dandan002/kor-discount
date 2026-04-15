# Requirements: Korea Discount Study

**Defined:** 2026-04-14
**Core Value:** A rigorous, reproducible empirical argument that the Korea Discount is structural and addressable — with credible causal evidence from Japan that reform works.

---

## v1 Requirements

### Data Pipeline

- [ ] **DATA-01**: Researcher can acquire and load 20-year monthly/annual index-level P/B and P/E data for KOSPI, TOPIX, S&P 500, and MSCI EM from documented sources (KRX, JPX, MSCI factsheets, FRED/Shiller)
- [ ] **DATA-02**: Researcher can run a single script that produces a clean, long-format `panel.parquet` file with columns: (date, country, pb, pe) and no missing observations without documented explanation
- [ ] **DATA-03**: Researcher can verify data provenance via a documented manifest listing source, vintage date, and download method for each series
- [ ] **DATA-04**: Data pipeline includes survivorship bias assessment and documents any known limitations of the chosen sources
- [ ] **DATA-05**: All raw data files are version-controlled in `data/raw/` with no transformations applied; all cleaning logic lives in reproducible scripts

### Descriptive Analysis

- [ ] **DESC-01**: Researcher can generate a time-series figure (Figure 1) showing KOSPI P/B vs TOPIX, S&P 500, and MSCI EM P/B over the full 20-year period
- [ ] **DESC-02**: Researcher can generate Table 1: summary statistics (mean, median, SD, min, max) of core valuation metrics by country and sub-period
- [ ] **DESC-03**: Researcher can quantify the Korea Discount as a time-averaged spread (bps or ratio) with statistical significance for use in the introduction and abstract

### Paper Sections

- [ ] **PAPER-01**: Paper includes an abstract (150–200 words) stating the research question, methods, and main finding with discount magnitude
- [ ] **PAPER-02**: Paper includes an introduction (3–5 pages) with motivation, contribution-to-literature paragraph, preview of key numbers, and paper structure
- [ ] **PAPER-03**: Paper includes an institutional background section (3–5 pages) covering: chaebol cross-shareholding mechanics, FSC/KRX regulatory history, Japan's three reform dates (2014/2015/2023), and North Korea risk history
- [ ] **PAPER-04**: Paper includes a literature review (3–6 pages) covering Korea Discount prior empirics, Japan governance reform event studies, governance–valuation literature, and natural experiment methodology
- [ ] **PAPER-05**: Paper includes a data section (2–4 pages) describing sources, coverage, variable construction, survivorship bias discussion, and missing data treatment
- [ ] **PAPER-06**: Paper includes a causal mechanism section (2–4 pages) articulating three channels: chaebol opacity, minority-shareholder recourse deficit, and geopolitical risk premium
- [ ] **PAPER-07**: Paper includes an empirical strategy section (1–2 pages) with estimating equations and notation for event study, panel OLS, and synthetic control
- [ ] **PAPER-08**: Paper includes a discussion/limitations section (1–2 pages) explicitly addressing the single treated unit problem, Abenomics confound, and generalizability of Japan→Korea inference
- [ ] **PAPER-09**: Paper includes a conclusion (1–2 pages) summarizing findings, contributions, and future work
- [ ] **PAPER-10**: Paper includes appendices for variable definitions and overflow robustness tables

### Event Study

- [ ] **EVNT-01**: Researcher can run an event study measuring cumulative abnormal valuation changes (P/B or P/E) around each of the three Japan reform dates (Stewardship Code 2014, CGC 2015, TSE P/B reform 2023)
- [ ] **EVNT-02**: Event study uses heteroskedasticity-robust standard errors; results presented separately for each treatment date
- [ ] **EVNT-03**: Stacked event study design implemented across all three treatment dates (citing Cengiz et al. 2019 / Baker et al. 2022 methodology) rather than a single pooled regression
- [ ] **EVNT-04**: Event study outputs cumulative abnormal return / valuation change figures and coefficient tables for inclusion in the paper

### Panel OLS

- [ ] **OLS-01**: Researcher can estimate panel OLS with two-way country + time fixed effects using `linearmodels.PanelOLS` (not `statsmodels.OLS`)
- [ ] **OLS-02**: Panel OLS specification includes reform dummy variables interacted with the Japan indicator; coefficients interpreted in economic terms (bps of P/B)
- [ ] **OLS-03**: Standard errors are clustered by country; results presented in a regression table (LaTeX-formatted via `pandas.to_latex` or equivalent)

### Synthetic Control

- [ ] **SYNTH-01**: Researcher can estimate a synthetic control for Japan using the Abadie-Diamond-Hainmueller (2010) method for the 2023 TSE P/B reform event
- [ ] **SYNTH-02**: Synthetic control reports pre-treatment RMSPE, donor pool weights, and a pre/post fit chart
- [ ] **SYNTH-03**: Synthetic control donor pool selection is documented with explicit justification; SUTVA concerns (regional governance contagion) addressed in text

### Geopolitical Risk Sub-Analysis

- [ ] **GEO-01**: Researcher can construct a North Korea escalation event indicator series using GDELT or the Caldara-Iacoviello Geopolitical Risk (GPR) index for the study period
- [ ] **GEO-02**: Analysis estimates KOSPI valuation response to North Korea escalation events as a sub-sample test to partially quantify the geopolitical premium channel
- [ ] **GEO-03**: Geopolitical risk results integrated into the causal mechanism section with appropriate caveats about partial identification

### Robustness & Validation

- [ ] **ROBUST-01**: Placebo / falsification tests: run event study on non-reform markets (e.g., Taiwan, Indonesia) over the same event windows to show effects are reform-specific
- [ ] **ROBUST-02**: Alternative valuation metric robustness: replicate primary results using P/E instead of P/B
- [ ] **ROBUST-03**: Alternative control group robustness: vary the MSCI EM composition or substitute an alternative EM benchmark
- [ ] **ROBUST-04**: Synthetic control in-time and in-space placebo tests (run synthetic control on pre-treatment periods and on donor pool countries) to assess specificity of the Japan treatment effect

### Policy Recommendations

- [ ] **POLICY-01**: Policy section (2–3 pages) provides specific near-term recommendations tied to Korean institutional levers: FSC disclosure requirements, KRX listing rules, stewardship code design
- [ ] **POLICY-02**: Counterfactual projection: based on Japan's observed valuation response, construct an illustrative projection of discount closure magnitude/timeline if Korea implemented a P/B reform — clearly labeled as illustrative

### Output & Reproducibility

- [ ] **OUTPUT-01**: All paper figures and tables are generated programmatically from `panel.parquet` and analysis outputs; no manual chart creation
- [ ] **OUTPUT-02**: Paper compiled as a PDF via LaTeX (pdflatex/XeLaTeX); all figure/table includes point to generated output files
- [ ] **OUTPUT-03**: Replication package: running `python run_all.py` regenerates all figures and tables from raw data; accompanied by `requirements.txt` and a documented README

---

## v2 Requirements

### Geopolitical Risk (Extended)

- **GEO-V2-01**: Full decomposition of the Korea Discount into quantitative attribution for each of the three channels (chaebol, regulatory, geopolitical) using structural identification
- **GEO-V2-02**: CDS spread correlation with equity discount as a descriptive aside for the geopolitical channel

### Comparative EM Analysis

- **EM-V2-01**: Brief comparative section positioning Korea alongside other "discounted" EM markets (China A-share discount, India discount) — 1–2 pages of context

### Extended Replication

- **REP-V2-01**: Full DVC (Data Version Control) pipeline for end-to-end data versioning
- **REP-V2-02**: CI/CD integration to verify reproducibility on a clean environment

---

## Out of Scope

| Feature | Reason |
|---------|--------|
| Formal theoretical model (game theory / asset pricing) | Months of additional work; not needed for policy-adjacent journals; cite existing frameworks instead |
| Firm-level / individual chaebol microstructure analysis | Requires different identification strategy, separate data pipeline, dramatically larger scope |
| Real-time or live data pipeline | Retrospective study; static versioned snapshots are sufficient and more reproducible |
| Full DID parallel-trends pre-test section | For N=4 countries, formal pre-trends testing has near-zero power; synthetic control pre-fit is the appropriate substitute |
| Survey or qualitative interview data | Methodological incoherence with quantitative design; cite qualitative literature instead |
| Non-equity asset classes (bonds, FX, CDS) as primary analysis | Separate data pipelines; tangential to equity valuation argument |
| Trading strategy / alpha generation framing | Repositions paper as practitioner piece; penalized by academic governance reviewers |
| Staggered DiD with Callaway-Sant'Anna correction | Requires multiple treated units; Japan is N=1 treated country; wrong estimator for this design |

---

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| DATA-01 | Phase 1 | Pending |
| DATA-02 | Phase 1 | Pending |
| DATA-03 | Phase 1 | Pending |
| DATA-04 | Phase 1 | Pending |
| DATA-05 | Phase 1 | Pending |
| DESC-01 | Phase 2 | Pending |
| DESC-02 | Phase 2 | Pending |
| DESC-03 | Phase 2 | Pending |
| EVNT-01 | Phase 3 | Pending |
| EVNT-02 | Phase 3 | Pending |
| EVNT-03 | Phase 3 | Pending |
| EVNT-04 | Phase 3 | Pending |
| OLS-01 | Phase 3 | Pending |
| OLS-02 | Phase 3 | Pending |
| OLS-03 | Phase 3 | Pending |
| GEO-01 | Phase 3 | Pending |
| GEO-02 | Phase 3 | Pending |
| GEO-03 | Phase 3 | Pending |
| SYNTH-01 | Phase 4 | Pending |
| SYNTH-02 | Phase 4 | Pending |
| SYNTH-03 | Phase 4 | Pending |
| ROBUST-01 | Phase 4 | Pending |
| ROBUST-02 | Phase 4 | Pending |
| ROBUST-03 | Phase 4 | Pending |
| ROBUST-04 | Phase 4 | Pending |
| PAPER-01 | Phase 5 | Pending |
| PAPER-02 | Phase 5 | Pending |
| PAPER-03 | Phase 5 | Pending |
| PAPER-04 | Phase 5 | Pending |
| PAPER-05 | Phase 5 | Pending |
| PAPER-06 | Phase 5 | Pending |
| PAPER-07 | Phase 5 | Pending |
| PAPER-08 | Phase 5 | Pending |
| PAPER-09 | Phase 5 | Pending |
| PAPER-10 | Phase 5 | Pending |
| POLICY-01 | Phase 5 | Pending |
| POLICY-02 | Phase 5 | Pending |
| OUTPUT-01 | Phase 5 | Pending |
| OUTPUT-02 | Phase 5 | Pending |
| OUTPUT-03 | Phase 5 | Pending |

**Coverage:**
- v1 requirements: 40 total
- Mapped to phases: 40/40 ✓
- Unmapped: 0

---
*Requirements defined: 2026-04-14*
*Last updated: 2026-04-14 after roadmap creation*
