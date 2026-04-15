# Technology Stack: Korea Discount Study

**Project:** Korea Discount — quantitative finance academic research paper
**Researched:** 2026-04-14
**Confidence note:** External search tools (WebSearch, WebFetch, Brave) were unavailable during this session. Findings draw on training knowledge through August 2025. The core Python quant-finance academic stack is highly stable; version numbers flagged LOW confidence where they may have drifted. Synthetic control library recommendations carry MEDIUM confidence and should be spot-checked at pypi.org before implementation.

---

## Recommended Stack

### Core Data & Wrangling

| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| Python | 3.11+ | Runtime | 3.11 is the stability sweet spot — 3.12 is production-ready but some quant libs lag; 3.11 maximizes compatibility |
| pandas | 2.2.x | Tabular data, panel reshaping, time-series alignment | The de facto standard; 2.x copy-on-write semantics eliminate a class of silent mutation bugs common in research code |
| numpy | 1.26.x / 2.0.x | Numerical arrays underlying all econometrics | 1.26 is maximum compatibility; 2.0 is stable but linearmodels and statsmodels may lag — pin 1.26 until dependencies confirm support |
| polars | 0.20.x | Optional: fast ETL on large raw data files | If ingesting multi-decade MSCI exports as large CSVs, polars read_csv is 10–50x faster than pandas; output to pandas for analysis |

### Data Acquisition

See the dedicated Data Sources section below — this is the highest-risk dimension of the project.

| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| yfinance | 0.2.x | Equity price history, some fundamental ratios | Free, no API key, 20+ year daily OHLCV; P/B ratio available for major indices via `.info`; coverage for KOSPI/^KS11 is partial — verify before depending on it |
| pandas-datareader | 0.10.x | FRED macro series, World Bank WDI | Best way to pull FRED series in Python; World Bank P/B/P/E data is sparse but present for some country panels |
| requests + openpyxl | standard | Manual downloads from MSCI, Shiller, KRX | Some authoritative sources (MSCI valuation sheets, KRX statistics) only publish as downloadable Excel/CSV; parse with openpyxl or pandas read_excel |
| wbgapi | 1.0.x | World Bank API | Cleaner than pandas-datareader for World Bank; programmatic access to WDI valuation series |

### Econometrics

| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| statsmodels | 0.14.x | OLS, WLS, GLS, HAC standard errors, event study abnormal return calculation | The standard Python econometrics library; good for time-series, rolling regressions, basic OLS with clustered SE via `HC3`/`cov_type='cluster'` |
| linearmodels | 6.x | Panel OLS with entity/time fixed effects, between estimator, first differences | THE correct tool for panel data with fixed effects in Python — statsmodels `OLS` does not natively support two-way FE with proper within-transformation; linearmodels is specifically built for this and follows Stata/R `felm` conventions closely |
| scipy | 1.12.x | Statistical tests, optimization routines used internally | Supporting library; Mann-Whitney, KS tests for pre/post reform comparison |
| pingouin | 0.5.x | Clean statistical tests with effect sizes | Optional but useful for reporting Cohen's d and confidence intervals on mean-difference tests |

**Why linearmodels over statsmodels for panel FE:**
`statsmodels.OLS` with dummies is technically correct but (1) computationally wasteful for large N×T panels due to dummy column explosion, (2) does not partial out FE via within-transformation, (3) standard errors need manual adjustment. `linearmodels.PanelOLS` handles entity/time absorption correctly and outputs standard errors compatible with academic reporting (clustered by entity, Driscoll-Kraay for cross-sectional dependence).

### Synthetic Control

| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| pysyncon | 1.4.x | Synthetic control method (Abadie, Diamond, Hainmueller 2010) | **RECOMMENDED.** Pure Python, actively maintained as of 2024, implements the canonical ADH synthetic control with the correct quadratic optimization for predictor weights and the standard in-time/in-space placebo tests. API is clean — takes a `Dataprep` object then `.fit()` then `.path_plot()`. |
| SparseSC | 0.2.x | Sparse synthetic control for high-dimensional donor pools | Alternative if donor pool is large (many countries); uses regularization. More complex API than pysyncon. For this project (small donor pool: US, Japan, EM) pysyncon is sufficient and simpler. |

**Confidence note (MEDIUM):** pysyncon 1.4.x version number is from training data — verify current version at `pypi.org/project/pysyncon`. The library was actively developed through 2024. The alternative `SyntheticControlMethods` (by Pinilla et al.) also exists but has less active maintenance signal than pysyncon.

**What NOT to use for synthetic control:**
- `statsmodels` — no synthetic control implementation
- Manual scipy.optimize — reinventing the wheel; pysyncon wraps this correctly with the right weight constraints (sum to 1, non-negative)
- R's `Synth` package — out of scope per project constraints

### Event Study

| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| statsmodels | 0.14.x | OLS market model estimation for abnormal returns | Standard: estimate market model (CAPM or market-only) over estimation window, compute AR = actual - predicted, CAR = cumulative sum |
| eventstudy (optional) | 0.x | Wrapper automating event study pipeline | Small community library; its automation is convenient but the internals are thin wrappers around numpy/statsmodels; for an academic paper you want transparent, auditable code — implement the event study directly in statsmodels/pandas rather than relying on an opaque wrapper |

**Recommendation:** Implement the event study directly. The methodology is 40 lines of pandas/statsmodels code. For an academic paper, reviewers expect to see the estimation window, event window, and normalization choices explicit in your code, not hidden in a library.

### Visualization

| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| matplotlib | 3.8.x | Base plotting layer, all publication figures | Non-negotiable for academic work — gives pixel-level control over figure dimensions, font sizes, DPI for journal submission. All other plot libraries build on it. |
| seaborn | 0.13.x | Statistical plot types (heatmaps, regression plots, distribution comparisons) | Correct tool for correlation matrices, distribution overlays, and regression coefficient plots. Pin 0.13 — the API stabilized substantially in 0.12/0.13. |
| matplotlib-latex integration | via rcParams | LaTeX math in axis labels and titles | Set `plt.rcParams["text.usetex"] = True` (requires TeX Live) or use `mathtext` for inline math without full LaTeX installation. Essential for $P/B$, $\hat{\beta}$, etc. in figure labels. |

**What NOT to use:**
- `plotly` / `bokeh` — interactive web charts; useless for a static PDF paper and add complexity
- `altair` — grammar-of-graphics is excellent for exploration but poor for precise journal figure control
- `pandas.plot()` — convenient for EDA but not publication-quality; always go through matplotlib for final figures

### Reproducibility Infrastructure

| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| Jupyter Lab | 4.x | Interactive development and exploratory analysis | Standard for quant research; 4.x is stable and the current release |
| nbconvert | 7.x | Export notebooks to PDF/HTML for supplementary materials | Converts notebooks to clean outputs for appendices |
| papermill | 2.x | Parameterized notebook execution | Run notebooks with different parameters (e.g., different event windows) reproducibly |
| pip + requirements.txt | standard | Dependency pinning | For academic reproducibility, a flat `requirements.txt` with pinned versions (`==`) is more transparent than poetry/conda for reviewers who need to replicate |
| python-dotenv | 1.x | API key management | Keep any API keys out of notebooks/code |

**Why pip + requirements.txt over conda/poetry for academic reproducibility:**
Reviewers and journal replication teams are familiar with `pip install -r requirements.txt`. Poetry lock files and conda environments add friction. Use `pip freeze > requirements.txt` after confirming a working environment. Include a `Makefile` or `run_all.sh` that executes notebooks in order.

### Document Generation

| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| LaTeX (TeX Live 2024) | system install | Final paper document | The only acceptable format for economics/finance journal submission. Generates publication-quality PDF. |
| Jupyter nbconvert --to latex | via nbconvert | Export analysis notebooks as LaTeX fragments | Useful for appendices |
| Python `subprocess` + `os` | stdlib | Compile LaTeX from Python | Drive `pdflatex` or `latexmk` from a build script for one-command paper generation |
| pandas `.to_latex()` | pandas 2.2 | Generate LaTeX regression tables from DataFrames | Outputs `tabular` environments directly; use `float_format='{:.3f}'.format` and `na_rep=''` for clean tables |
| stargazer | 0.0.5 | Formatted regression output tables in LaTeX style | Generates multi-model comparison tables (like Stata's outreg2 / R's stargazer) — handles linearmodels and statsmodels results objects. Verify compatibility with linearmodels 6.x before committing. |

**Alternative to stargazer:** The `modelsummary` approach from R has no direct Python equivalent with equal polish. For publication tables, generating them with `pandas.to_latex()` with manual formatting is often cleaner and more controllable than stargazer for Python. Budget time to format tables manually.

---

## Data Sources: 20-Year Valuation Panel (Critical Path)

This is the highest-risk dimension. Index-level P/B, P/E, and EV/EBITDA over 20 years for KOSPI, TOPIX, S&P 500, and MSCI EM is not trivially available from a single free API. The strategy below uses a layered approach.

### Layer 1: Free / Programmatic Sources

| Source | Data Available | Coverage | Access Method | Confidence |
|--------|---------------|----------|---------------|------------|
| **FRED (Federal Reserve)** | S&P 500 P/E (Shiller CAPE via `MULTPL`), some equity market ratios | US-focused; limited Asia | `pandas-datareader.DataReader('CAPE', 'fred')` or direct FRED API | HIGH |
| **Robert Shiller data** | S&P 500 CAPE, P/E back to 1871 | US only | CSV download from `econ.yale.edu/~shiller/data.htm` | HIGH |
| **World Bank WDI** | "Price to book ratio" (FS.AST.PRVT.GD.ZS adjacent series) and market cap/GDP | Country-level, annual, patchy for Korea/Japan P/B specifically | `wbgapi` or `pandas-datareader` World Bank reader | MEDIUM — verify series codes |
| **MSCI Market Valuation Data** | P/B, P/E, P/CF for MSCI Korea, MSCI Japan, MSCI EM, MSCI World indices | Monthly, back to ~2000 | **Manual download** from `msci.com/our-solutions/indexes/gimi/all-country-world-index` — MSCI publishes monthly factsheets and historical characteristic sheets as free PDFs/Excel. No programmatic API. | HIGH (data quality) / LOW (automation) |
| **Nikkei / TSE statistical data** | TOPIX P/B, P/E (official exchange statistics) | Japan, monthly | Manual download from `jpx.co.jp/markets/statistics-equities/` | HIGH (official) |
| **KRX (Korea Exchange) statistics** | KOSPI P/B, P/E, EPS, dividend yield | Korea, monthly/annual | Manual download from `data.krx.co.kr` — English interface limited; data available in Korean-language portal | HIGH (official) |
| **Stooq.com** | Historical price data, some fundamental ratios | Global indices | `pandas-datareader.DataReader('^KOSPI', 'stooq')` | MEDIUM — ratio coverage inconsistent |
| **Yahoo Finance (yfinance)** | Price, market cap; P/B via `.info` for some tickers | Index-level P/B inconsistent; company-level reliable | `yfinance.Ticker('^GSPC').info` | LOW for index-level ratios — verify manually |

### Layer 2: Paid / Institutional Sources (if free sources have gaps)

| Source | Data | Cost | Note |
|--------|------|------|------|
| **Bloomberg Terminal export** | Full KOSPI/TOPIX/MSCI history, all valuation multiples | Institutional subscription | If university library access exists, export 20-year monthly CSV; no Python API needed |
| **Refinitiv Eikon / LSEG** | Same coverage as Bloomberg | Institutional | Similar; `eikon` Python library if API access available |
| **OECD Stat** | Some equity market statistics by country | Free | `pandas-datareader` OECD reader; coverage for P/B is limited |
| **Quandl / Nasdaq Data Link** | Historical market statistics | Freemium | Some MSCI data available via Quandl `MSCI/` namespace; verify current availability |

### Recommended Data Pipeline Strategy

Given the patchwork nature of free index valuation data, the recommended approach is:

1. **MSCI official factsheets** (manual download, parse with openpyxl): P/B and P/E for MSCI Korea, MSCI Japan, MSCI EM, MSCI World — this is the cleanest single source for apples-to-apples comparison since all series use identical MSCI methodology.

2. **KRX official statistics** (manual download): KOSPI P/B, P/E — official exchange data, Korean-language portal but data exportable.

3. **JPX/TSE official statistics** (manual download): TOPIX P/B, P/E — Tokyo Exchange publishes these directly.

4. **FRED / Shiller**: S&P 500 CAPE and P/E — programmatic, high quality.

5. **All manual downloads wrapped in a `data/raw/` directory** with a documented `data/README.md` explaining provenance, download date, and URL for each file. A `scripts/01_build_panel.py` script reads all raw files and outputs a single `data/processed/panel.parquet`.

**Why parquet for the processed panel:** parquet preserves dtypes (including DatetimeTZDtype), compresses well, loads in milliseconds, and is language-agnostic for future replication. Use `pandas.read_parquet()` / `DataFrame.to_parquet()`.

---

## Alternatives Considered

| Category | Recommended | Alternative | Why Not |
|----------|-------------|-------------|---------|
| Panel FE | linearmodels PanelOLS | statsmodels OLS + dummies | Dummy explosion, no within-transformation, manual SE adjustment required |
| Panel FE | linearmodels PanelOLS | pyfixest | pyfixest is excellent and faster for large panels, but is newer (less battle-tested citation trail); linearmodels has more academic usage as of 2025 |
| Synthetic control | pysyncon | manual scipy.optimize | Reinventing; pysyncon implements weight constraints and placebo tests correctly |
| Synthetic control | pysyncon | SparseSC | SparseSC suits large donor pools; for a 4-5 country panel pysyncon is simpler |
| Visualization | matplotlib + seaborn | plotly | Static PDF paper; interactive charts add no value and complicate LaTeX integration |
| Tables | pandas.to_latex() + stargazer | Manually typed LaTeX | Reproducibility — all tables must generate from code |
| Data storage | parquet | CSV | CSV loses dtypes on reload, slower, larger; parquet is correct for research pipelines |
| Environment | pip + requirements.txt | conda / poetry | Reviewer friction; pip is universal |
| Document | LaTeX | Quarto / R Markdown | LaTeX is journal-submission standard; Quarto requires Pandoc chain that can break |

---

## Full Installation

```bash
# Core analysis
pip install pandas==2.2.* numpy==1.26.* scipy==1.12.* statsmodels==0.14.*

# Panel econometrics (critical)
pip install linearmodels==6.*

# Synthetic control (critical — verify version at pypi.org/project/pysyncon)
pip install pysyncon

# Data acquisition
pip install yfinance pandas-datareader wbgapi openpyxl requests

# Visualization
pip install matplotlib==3.8.* seaborn==0.13.*

# Reproducibility
pip install jupyterlab papermill nbconvert python-dotenv

# Tables
pip install stargazer

# Storage
pip install pyarrow  # enables pandas parquet read/write

# Dev
pip install black isort pytest
```

---

## Version Confidence Notes

| Package | Version Cited | Confidence | Note |
|---------|--------------|------------|------|
| pandas | 2.2.x | HIGH | Released early 2024; 2.x branch is current |
| numpy | 1.26.x | HIGH | 1.26 is 2023/2024 stable; 2.0 released June 2024 |
| statsmodels | 0.14.x | HIGH | 0.14 released 2023; current as of Aug 2025 |
| linearmodels | 6.x | MEDIUM | 5.x was current through 2023; check pypi for 6.x confirmation |
| pysyncon | 1.4.x | MEDIUM | Training data shows active development; verify pypi |
| matplotlib | 3.8.x | HIGH | 3.8 released 2023; 3.9 may be current by 2026 |
| seaborn | 0.13.x | HIGH | 0.13 released 2023 with API stabilization |
| stargazer | 0.0.5 | LOW | Small library; verify linearmodels compatibility |

---

## Sources

- linearmodels documentation: `https://bashtage.github.io/linearmodels/` (Kevin Sheppard, UCL) — MEDIUM confidence (training data)
- pysyncon: `https://github.com/sdfordham/pysyncon` — MEDIUM confidence (training data)
- statsmodels: `https://www.statsmodels.org/stable/` — HIGH confidence (established library)
- MSCI valuation data: `https://www.msci.com/our-solutions/indexes/gimi` — HIGH confidence (official source)
- KRX data portal: `https://data.krx.co.kr` — HIGH confidence (official exchange)
- JPX statistics: `https://www.jpx.co.jp/markets/statistics-equities/` — HIGH confidence (official exchange)
- FRED: `https://fred.stlouisfed.org` — HIGH confidence (official)
- Shiller data: `http://www.econ.yale.edu/~shiller/data.htm` — HIGH confidence (primary source)
