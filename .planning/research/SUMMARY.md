# Project Research Summary

**Project:** Korea Discount Study
**Domain:** Quantitative finance academic paper — cross-country equity valuation, corporate governance, natural experiment identification
**Researched:** 2026-04-14
**Confidence:** HIGH for econometric methodology and architecture; MEDIUM for data sourcing specifics and Korea/Japan differentiators

## Executive Summary

This project is a reproducible empirical finance paper, not a software product. The correct frame is: build a linear data pipeline that produces a single canonical panel, run three complementary econometric analyses on it, generate publication-quality figures and LaTeX tables as artifacts, and assemble those artifacts into a paper. The technology choices are stable and largely settled (Python, linearmodels, pysyncon, matplotlib, LaTeX), and the architectural pattern is well-established in the academic reproducibility literature. The hard problems are not technical — they are identification problems inherent to causal inference with a single treated country.

The recommended approach is a strictly layered pipeline: raw data (immutable) to cleaned interim files to one canonical processed panel to four parallel analysis modules to figures and table fragments to LaTeX paper. All parameters live in a single config.py. All stages are idempotent scripts, not notebooks. The paper is reproducible from scratch with two commands: python run_all.py then latexmk -pdf paper/main.tex. This architecture is not aspirational — it is the minimum viable approach for a paper that claims reproducibility.

The dominant risks are methodological, not implementation risks. Five critical pitfalls require explicit design decisions before any regressions are run: (1) staggered TWFE negative weighting across the three Japan reform events, (2) the untestability of parallel trends with a single treated unit, (3) synthetic control donor pool contamination from governance spillovers, (4) survivorship bias in historical index P/B data, and (5) look-ahead bias if event dates are selected post-hoc. The data sourcing phase is also high-risk: no single free API provides clean, point-in-time index-level P/B and P/E back to 2004 for all four markets. A manual download strategy from official exchange sources (KRX, JPX, MSCI factsheets) is the most reliable approach and must be planned for before coding begins.

---

## Key Findings

### Recommended Stack

The Python quant-finance academic stack is highly stable and well-suited to this project. The critical non-obvious choice is linearmodels.PanelOLS over statsmodels.OLS for all panel regressions — statsmodels does not natively support two-way fixed effects with correct within-transformation and clustered standard errors. For synthetic control, pysyncon is the recommended library; it implements the canonical Abadie-Diamond-Hainmueller algorithm with correct quadratic weight optimization and built-in placebo tests. Event studies should be implemented directly in statsmodels/pandas (~40 lines) rather than via a wrapper library — reviewers expect transparent, auditable estimation window choices.

Data sourcing is the highest-risk dimension. The recommended strategy is a layered approach: MSCI official factsheets (manual download) for apples-to-apples P/B and P/E across all four markets, supplemented by KRX and JPX official exchange statistics, with FRED/Shiller for S&P 500 CAPE. No single free API provides complete coverage. Expect to build a manual-download pipeline with documented provenance for each source file.

**Core technologies:**
- Python 3.11+: runtime — 3.11 is the stability sweet spot for the quant stack
- pandas 2.2.x: panel reshaping, time-series alignment — 2.x copy-on-write semantics eliminate silent mutation bugs
- linearmodels 6.x: panel OLS with two-way FE — the only correct tool for this in Python; statsmodels OLS is insufficient for panel FE
- pysyncon (verify version at pypi.org): synthetic control — implements ADH 2010 with correct weight constraints and placebo tests
- statsmodels 0.14.x: OLS market model for event study, HAC standard errors
- matplotlib 3.8.x + seaborn 0.13.x: publication-quality figures for LaTeX inclusion
- LaTeX (TeX Live): final document — the only acceptable format for journal submission
- parquet via pyarrow: processed data storage — preserves dtypes, prevents CSV encoding issues
- pip + requirements.txt: dependency pinning — more reviewer-friendly than conda/poetry

**What to avoid:**
- plotly/bokeh: interactive charts have no use in a static PDF paper
- statsmodels for panel FE: use linearmodels instead
- eventstudy library: too opaque; implement event study directly
- single pooled TWFE regression across all three reform events: causes negative weighting bias

### Expected Features

The paper has a well-defined scope derived from JF/JFE empirical finance conventions. All table-stakes sections are mandatory for any serious journal submission.

**Must have (table stakes):**
- Data pipeline producing 20-year panel of KOSPI, TOPIX, S&P 500, MSCI EM (P/B, P/E) — all other sections depend on this
- Summary statistics table (Table 1) with mean, median, SD by country and period
- Descriptive discount time-series figure (Figure 1) — visual evidence precedes all formal tests
- Institutional background section covering chaebol mechanics and all three Japan reform dates
- Event study: cumulative abnormal valuation changes around 2014, 2015, and 2023 reform dates
- Panel OLS with country/time fixed effects and reform-interaction dummies
- Synthetic control for 2023 TSE reform as primary robustness check
- Placebo tests: apply reform treatment to non-reforming markets (Korea, Taiwan) to show null effects
- Limitations section: acknowledge single treated unit, untestable parallel trends, Abenomics confound
- Policy recommendations section with Korea-specific regulatory levers (FSC, KRX, stewardship code design)
- Literature review covering Korea Discount empirics, Japan governance reform event studies, governance-valuation literature, synthetic control methodology

**Should have (differentiators):**
- Stacked event study design (Cengiz et al. 2019) properly handling contamination across the three reform dates — reviewers at top venues will expect this given the staggered treatment
- Synthetic control with pre-treatment RMSPE reported and placebo inference — methodological frontier for single treated unit
- Formal robustness checks: alternative valuation metrics, alternative control groups, event date +/-3 and +/-6 month shifts
- Geopolitical risk sub-analysis using North Korea event indicators to estimate the geopolitical premium component
- Machine-readable replication package with make all entry point

**Defer to v2+:**
- Counterfactual projection for Korea ("if Korea adopted Japan's 2023 reform...") — requires additional modeling assumptions
- Comparison to other EM discounts (China A-share, India) — positioning enhancement, not core argument
- Full quantitative decomposition of discount by driver — very high complexity; add after core results are solid

**Anti-features (deliberately excluded):**
- Firm-level microstructure analysis — different identification strategy required; out of scope
- Real-time data pipeline — retrospective study
- FX confound as a primary section — handle in robustness (1-2 paragraphs)
- Trading strategy or alpha generation framing — penalized at policy journals

### Architecture Approach

The correct architecture is a strictly forward linear pipeline with immutable raw data and a single canonical long-format processed panel as the hub. All four analysis modules (descriptive, event study, panel OLS, synthetic control) read from the same data/processed/panel.parquet file and produce results objects passed to visualization modules. Visualization modules never import from analysis modules — they receive data as arguments. The paper/main.tex assembles all outputs via LaTeX \input{} and \includegraphics{}. Full reproduction requires exactly two commands.

**Major components:**
1. src/data/fetch.py and build_panel.py — acquires raw files and produces the canonical panel.parquet; this is the critical path; all other modules are blocked on it
2. src/analysis/ (four modules: descriptive, event_study, panel_ols, synthetic_control) — independent of each other, all reading from panel.parquet; can run in any order after data is ready
3. src/viz/figures.py and tables.py — rendering layer only; receives computed results as arguments; never does analysis
4. paper/main.tex — assembles prose with \input{} table fragments and \includegraphics{} figure PDFs
5. run_all.py — orchestrates all stages in dependency order; enables one-command reproduction
6. config.py — single source of truth for all event dates, sample bounds, country names, window widths

**Key patterns to follow:**
- One canonical panel, long format: (date, country, pb, pe) — no separate wide-format files per analysis
- Idempotent stage scripts: every script overwrites its outputs on re-run
- Configuration over hardcoded constants: all event dates and parameters in config.py
- Analysis functions return objects; file I/O only in __main__ blocks or run_all.py
- pathlib.Path relative to a project root constant — no hardcoded absolute paths

### Critical Pitfalls

1. **Staggered TWFE negative weighting (CRITICAL)** — Do not run a single pooled reform_intensity*post dummy across all three Japan reform events in one TWFE regression. Use separate regressions per event with clean pre-period windows, or the Cengiz et al. (2019) event-stacking design with event-by-cohort fixed effects. This is a paper-rejection-level error that referees catch immediately. Reference: Goodman-Bacon (2021), Callaway and Sant'Anna (2021).

2. **Survivorship bias in historical index P/B (CRITICAL)** — Free sources (Yahoo Finance, Macrotrends) often report P/B using current-day reconstituted constituents, not point-in-time weights. Prefer MSCI official factsheets, KRX official statistics, and JPX official statistics which use documented methodology. Verification check: the 2008-2009 GFC must show sharp P/B compression. If it does not, the series is survivorship-biased.

3. **Synthetic control donor pool contamination (CRITICAL)** — Countries that experienced governance spillovers from Japan's reforms (Taiwan, Hong Kong-listed China) violate SUTVA and should be excluded from the primary donor pool. Justify each donor member explicitly in the paper and report robustness checks with restricted pools.

4. **Look-ahead bias in event date selection (CRITICAL)** — Event dates (2014, 2015, 2023) must be fixed to official FSA/TSE policy announcement records and prior academic literature (Miyajima et al., Becht et al.) before any regressions are run. Run robustness with +/-3 and +/-6 month date shifts.

5. **Parallel trends untestable with N=1 treated unit (CRITICAL)** — Formal pre-trend tests have near-zero power with Japan as the sole treated unit. State this explicitly in the identification section. Lean on synthetic control pre-treatment RMSPE and placebo tests on untreated countries as primary identification evidence. Do not overclaim causal identification.

**Additional moderate pitfalls requiring design attention:**
- Serial autocorrelation in monthly P/B (AR(1) typically 0.90-0.97): use Newey-West with maxlags=12 or Driscoll-Kraay SEs; test residuals with Durbin-Watson
- Small cluster problem (N=4 countries): use wild cluster bootstrap (wildboottest package) as primary inference; also report time-clustered SEs
- Abenomics macro confound (2013-2014): include BOJ balance sheet and JGB yield as controls in panel OLS; discuss in identification section
- MSCI EM composition drift (China weight 5% to 35% over sample period): note in data section; consider MSCI EM ex-China as robustness post-2017
- P/E instability near zero earnings (2008-2009 GFC): prefer P/B as primary metric; winsorize P/E at 1st/99th percentiles

---

## Implications for Roadmap

The research points to a six-phase structure that follows the strict pipeline dependency order. No phase can start until its upstream phase is complete, except within Phase 4 where the four analysis modules are fully independent of each other.

### Phase 1: Environment and Repository Setup
**Rationale:** config.py must lock event dates to official policy records before any data is loaded — this is the primary defense against look-ahead bias. No analysis is possible without the directory structure and working environment established.
**Delivers:** Reproducible Python environment, directory scaffold per the architecture, config.py with all event dates locked, requirements.txt pinned, run_all.py stub, Makefile.
**Addresses:** Look-ahead bias (Critical Pitfall 4), hard-coded paths (Minor Pitfall 12).
**Key action:** Commit event dates (2014-02-01, 2015-06-01, 2023-03-01) to config.py with citations to FSA/TSE announcements before writing any analysis code.

### Phase 2: Data Acquisition and Panel Construction
**Rationale:** This is the critical path. All four analysis modules are blocked on data/processed/panel.parquet. Data sourcing is the highest-risk phase: no single free API provides complete coverage, manual downloads are required, and survivorship bias must be verified source by source.
**Delivers:** data/raw/ populated with documented source files; data/processed/panel.parquet with schema (date, country, pb, pe) at monthly frequency for KOSPI, TOPIX, SP500, MSCI_EM, approximately 2003-2024.
**Uses:** pandas 2.2, pyarrow, openpyxl (MSCI/KRX Excel parsing), pandas-datareader (FRED/Shiller), wbgapi.
**Avoids:** Survivorship bias — verify point-in-time constituent methodology; check 2008-2009 shows P/B compression. Document accounting standard and currency convention for each source.
**Research flag:** NEEDS VALIDATION. Whether any free public source provides point-in-time KOSPI P/B back to 2004 is LOW confidence. KRX portal English-language export capabilities and historical depth must be confirmed. Bloomberg or Refinitiv institutional access may be necessary.

### Phase 3: Descriptive Analysis and Discount Documentation
**Rationale:** Establishes the phenomenon visually and quantitatively before any causal claims. Reviewers check Table 1 and Figure 1 before reading methods. This phase also validates the data pipeline output.
**Delivers:** Table 1 (summary statistics by country and period), Figure 1 (discount time-series), computed discount magnitude in basis points of P/B.
**Uses:** pandas descriptive stats, matplotlib, seaborn, pandas .to_latex().
**Note:** Institutional background and literature review sections of the paper can be drafted in parallel with this phase — they do not require empirical results.

### Phase 4: Econometric Analysis (four independent modules)
**Rationale:** All four analyses are independent once the panel is ready. They address complementary aspects of the research question with designated roles: event study is the primary causal test, panel OLS provides long-run cross-sectional evidence, synthetic control is the primary robustness, and descriptive robustness checks validate all three.
**Delivers:**
- Event study results: CARs around 2014, 2015, 2023 with heteroskedasticity-robust SEs (Figure 2, Table 3)
- Panel OLS results: country/time FE regression table with reform interaction dummies and wild-bootstrap SEs (Table 2)
- Synthetic control: donor weights, gap plot for 2023 TSE reform, pre-treatment RMSPE (Figure 4)
- Robustness checks: placebo tests on untreated markets, alternative valuation metrics, date-shift sensitivity
**Uses:** statsmodels (event study, HAC SEs), linearmodels PanelOLS (panel FE), pysyncon (synthetic control), wildboottest (wild cluster bootstrap).
**Critical design decisions:**
- Separate regressions per reform event, not one pooled TWFE — avoids negative weighting
- Wild cluster bootstrap as primary inference method — N=4 clusters is too small for asymptotic cluster SEs
- Newey-West SEs with maxlags=12 for serial autocorrelation
- Donor pool: MSCI Europe, S&P 500, MSCI World ex-Japan — exclude Asia-Pacific; test as robustness
- Pre-treatment fit period for synthetic control: full available pre-2023 window (2004-2022)
- BOJ balance sheet and JGB yield as controls in panel OLS for Abenomics confound
**Research flag:** NEEDS VALIDATION. Stacked event study implementation in Python (Cengiz et al. 2019 design) requires manual construction — no mature library exists. This is the most technically novel implementation step and merits a focused research pass before coding.

### Phase 5: Paper Writing and Output Assembly
**Rationale:** All empirical results exist; the paper assembles them with prose. Writing can be partially parallelized: institutional background and literature review have no dependency on empirical results.
**Delivers:** Complete draft LaTeX paper (~35-50 pages) with all sections, figures, and tables; paper/main.pdf compiling cleanly from run_all.py + latexmk.
**Uses:** LaTeX (TeX Live), pandas .to_latex() or stargazer for regression tables, nbconvert for appendix notebooks.
**Note:** Verify stargazer compatibility with linearmodels before relying on it. pandas .to_latex() with manual formatting is the safe fallback.

### Phase 6: Robustness, Replication Package, and Submission Prep
**Rationale:** Additional robustness checks and final polish. Clean end-to-end reproduction, Bonferroni corrections applied across three event tests, documented replication package.
**Delivers:** Robustness appendix tables, full replication package with make all entry point, submission-ready PDF.
**Addresses:** Multiple testing inflation (Bonferroni correction, alpha/3 = 0.017), replication package as differentiator.

### Phase Ordering Rationale

- Phase 1 before everything: config.py must lock event dates before any data is loaded — this is the look-ahead bias firewall
- Phase 2 is the strict bottleneck: all four analysis modules in Phase 4 are entirely blocked on the panel
- Phase 3 before Phase 4: descriptive results validate the panel before investing in complex econometrics; also surfaces data quality issues early
- Phase 4 modules are fully independent: event study, panel OLS, synthetic control, and robustness checks can be built in any order or in parallel
- Paper writing (Phase 5) has a parallel track: institutional background, literature review, and data section can be drafted during Phases 2-4
- Phase 6 is last: robustness polish and replication packaging require stable final results

### Research Flags

Phases needing a deeper research step during planning:
- **Phase 2 (data sourcing):** LOW confidence on KOSPI point-in-time P/B availability from free public sources. Before implementation, confirm KRX portal export capabilities and historical depth. This single question may force a strategy pivot to institutional data access.
- **Phase 4 (stacked event study):** Cengiz et al. (2019) event-stacking design in Python requires manual construction. The dataset construction and event-by-cohort fixed effects setup merit a focused pre-implementation research step.
- **Phase 4 (wildboottest):** Verify package availability and linearmodels 6.x compatibility before committing to this inference approach.

Phases with standard, well-documented patterns:
- **Phase 1 (environment setup):** Standard pip workflow; directory structure follows Cookiecutter Data Science conventions.
- **Phase 3 (descriptive analysis):** Standard pandas descriptive stats and matplotlib time-series plotting.
- **Synthetic control (Phase 4 module):** pysyncon API is documented; Abadie et al. 2010 methodology is well-established.
- **Phase 5 (LaTeX assembly):** Standard LaTeX \input{} and \includegraphics{} workflow.

---

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | Core Python quant-finance stack is stable and well-tested. linearmodels version (6.x) and pysyncon version are MEDIUM — verify at pypi.org. stargazer linearmodels compatibility is LOW — use pandas.to_latex() as fallback. |
| Features | HIGH | Table-stakes paper structure is well-established and stable across JF/JFE/RFS conventions. Differentiators are MEDIUM — a 2024-2025 SSRN scan would confirm which ideas are already published. |
| Architecture | HIGH | Linear pipeline, immutable raw data, one canonical panel, scripts over notebooks — conventions are stable, well-documented in Gentzkow-Shapiro and Cookiecutter Data Science, and correct for this project. |
| Pitfalls | HIGH for methodology; MEDIUM for data specifics | Econometric pitfalls are grounded in foundational literature (Goodman-Bacon 2021, Callaway-Sant'Anna 2021, Abadie et al. 2010). Data-specific pitfalls are directionally correct but exact details need source verification. |

**Overall confidence:** HIGH for methodology and architecture; MEDIUM for data availability and Korea/Japan-specific empirical literature currency.

### Gaps to Address

- **KOSPI point-in-time P/B data (2004-2024):** The most critical unresolved question. Before Phase 2 implementation, confirm whether KRX official statistics portal provides historical monthly P/B with point-in-time constituents, or whether Bloomberg/Refinitiv institutional access is required. This may determine the entire data strategy.

- **2024-2025 Korea Discount working papers:** Run a live SSRN search for "Korea Discount," "KOSPI valuation discount," and "Japanese governance reform synthetic control" before Phase 5 writing. Identifies competing papers and confirms the three-event staggered design has not been scooped.

- **pysyncon vs. mlsynth current state:** PITFALLS.md mentions mlsynth; STACK.md recommends pysyncon. Resolve before Phase 4 implementation. Verify both libraries exist, compare APIs, and commit to one.

- **Japan fiscal year alignment for P/B:** Japan's March fiscal year-end means annual P/B reported as "2015" may use March 2016 book values. Document how KRX/MSCI handle this in their published statistics. For monthly data this is less severe but must be noted in the data section.

- **Abenomics macro controls availability:** Panel OLS requires BOJ balance sheet size and 10-year JGB yield as time-varying controls. Verify FRED series codes for these before Phase 4 panel OLS implementation.

---

## Sources

### Primary (HIGH confidence)
- Abadie, Diamond & Hainmueller (2010, JASA) — synthetic control methodology; SUTVA donor pool requirements
- Goodman-Bacon (2021, QJE) — staggered DiD negative weighting formalization
- Callaway & Sant'Anna (2021, JoE) — heterogeneous treatment effects in staggered DiD
- Sun & Abraham (2021, JoE) — staggered DiD estimator
- Cameron, Gelbach & Miller (2008, REStat) — wild cluster bootstrap for small N clusters
- Newey & West (1987, Econometrica) — HAC standard errors
- Gentzkow & Shapiro (2014) "Code and Data for the Social Sciences" — reproducible pipeline conventions
- Cookiecutter Data Science (drivendata.org) — directory structure conventions
- linearmodels documentation (bashtage.github.io/linearmodels) — PanelOLS API
- statsmodels documentation (statsmodels.org) — event study estimation, HAC SEs
- MSCI valuation data (msci.com) — official index-level P/B and P/E source
- KRX data portal (data.krx.co.kr) — official KOSPI statistics
- JPX statistics (jpx.co.jp/markets/statistics-equities/) — official TOPIX statistics
- FRED (fred.stlouisfed.org) — S&P 500 CAPE, macro controls
- Shiller data (econ.yale.edu/~shiller/data.htm) — S&P 500 historical P/E

### Secondary (MEDIUM confidence)
- Miyajima et al. — Japan governance reform event studies (training data; confirm publication details before citing)
- Becht et al. — Japan governance reform dates (training data)
- Black, Jang & Kim (2006) — Korea corporate governance empirics
- Cengiz et al. (2019) — stacked event study design
- Gompers, Ishii & Metrick (2003) — governance index and valuation
- La Porta et al. (1998, 2000) — investor protection and valuation
- pysyncon library (github.com/sdfordham/pysyncon) — verify current version at pypi.org

### Tertiary (LOW confidence, needs validation)
- MSCI EM China weight trajectory (~5% to ~35%, 2004-2020) — verify against MSCI published factsheets
- wildboottest Python package and linearmodels 6.x compatibility — verify at pypi.org before implementing
- stargazer Python library linearmodels compatibility — verify before using; pandas.to_latex() is the fallback
- KOSPI historical point-in-time P/B availability from free public sources — must be directly verified during data sourcing phase

---
*Research completed: 2026-04-14*
*Ready for roadmap: yes*
