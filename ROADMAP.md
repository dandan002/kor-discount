# ROADMAP.md
# Korea Discount: Value-Up Compliance Study
# Tools: Python · blpapi · LaTeX

---

## Project Structure

```
korea-discount/
├── ROADMAP.md                  ← this file
├── README.md
├── requirements.txt
├── .env                        ← Bloomberg connection config (host, port)
│
├── data/
│   ├── raw/
│   │   ├── bloomberg/          ← CSVs from blpapi pulls (never edited)
│   │   ├── krx/                ← Value-Up disclosure filings from KRX portal
│   │   ├── kftc/               ← Chaebol designation lists (KFTC PDFs/XLS)
│   │   └── dart/               ← Controlling shareholder ownership from DART
│   └── processed/
│       ├── sample.csv          ← Master firm list with all covariates
│       ├── compliance.csv      ← Coded compliance classifications
│       ├── events.csv          ← Event dates for event study
│       └── returns.csv         ← Daily return panel from Bloomberg
│
├── src/
│   ├── 00_build_universe.py
│   ├── 01_bloomberg_pull.py
│   ├── 02_build_compliance.py
│   ├── 03_merge_covariates.py
│   ├── 04_descriptive.py
│   ├── 05_logit_compliance.py
│   ├── 06_fundamentals_comparison.py
│   ├── 07_event_study.py
│   └── utils/
│       ├── bbg.py              ← blpapi wrapper (BDP, BDH, BDS helpers)
│       ├── stats.py            ← shared stats helpers
│       └── latex_tables.py     ← DataFrame → LaTeX table exporter
│
├── outputs/
│   ├── tables/                 ← .tex table fragments
│   ├── figures/                ← .pdf/.pgf figures (matplotlib)
│   └── logs/                   ← run logs per script
│
└── paper/
    ├── main.tex
    ├── sections/
    │   ├── 01_introduction.tex
    │   ├── 02_background.tex
    │   ├── 03_literature.tex
    │   ├── 04_data.tex
    │   ├── 05_who_complied.tex
    │   ├── 06_fundamentals.tex
    │   ├── 07_event_study.tex
    │   ├── 08_discussion.tex
    │   └── 09_conclusion.tex
    ├── tables/                 ← symlink or copy from outputs/tables/
    ├── figures/                ← symlink or copy from outputs/figures/
    ├── references.bib
    └── style/
        ├── paper.sty           ← custom style (fonts, margins, header)
        └── econometrics.sty    ← table/figure formatting conventions
```

---

## Phase 0 — Environment Setup

### 0.1 Python environment

```bash
python -m venv .venv
source .venv/bin/activate
pip install blpapi pandas numpy scipy statsmodels matplotlib seaborn stargazer pylatex tqdm python-dotenv
```

Key packages:
- `blpapi` — Bloomberg Python API (requires Bloomberg Terminal running locally or B-PIPE)
- `statsmodels` — logit, OLS, event study regressions
- `stargazer` — publication-quality regression tables (exports to LaTeX)
- `pylatex` — programmatic LaTeX generation if needed

### 0.2 Bloomberg connection

```python
# utils/bbg.py skeleton
import blpapi

SESSION_OPTIONS = blpapi.SessionOptions()
SESSION_OPTIONS.setServerHost("localhost")   # or B-PIPE host
SESSION_OPTIONS.setServerPort(8194)

def bdp(securities, fields, overrides=None):
    """Bloomberg Data Point — current/snapshot values."""
    ...

def bdh(security, fields, start_date, end_date, overrides=None):
    """Bloomberg Data History — time series."""
    ...

def bds(security, field):
    """Bloomberg Data Set — bulk reference data."""
    ...
```

Test connection before proceeding: `python src/utils/bbg.py --test`

### 0.3 LaTeX environment

Requires a full TeX distribution (TeX Live or MiKTeX). Confirm:
```bash
pdflatex --version
biber --version       # for bibliography
```

Compile command (add to Makefile):
```bash
cd paper && pdflatex main.tex && biber main && pdflatex main.tex && pdflatex main.tex
```

---

## Phase 1 — Build the Firm Universe

**Script:** `src/00_build_universe.py`  
**Output:** `data/raw/universe_raw.csv`

### Steps

1. Pull all KOSPI members via Bloomberg:
   ```
   BDS("KOSPI Index", "INDX_MEMBERS")
   ```
   Repeat for KOSDAQ if desired (optional — see sampling note below).

2. For each member, pull identifying fields via BDP:
   - `TICKER`, `NAME`, `GICS_SECTOR_NAME`, `GICS_INDUSTRY_NAME`, `CNTRY_ISSUE_ISO`

3. **Drop financials** (GICS sector = "Financials", codes 4010xx) — standard practice; bank/insurance PBR is structurally different.

4. Drop firms with IPO date after 2023-01-01 (insufficient pre-program history).

5. Save universe: ~600–700 KOSPI non-financial firms expected.

### Sampling note
Start with KOSPI only. KOSDAQ firms are smaller and more illiquid — their daily return noise will degrade your event study. If you want a robustness check, rerun the event study on KOSDAQ separately and report in an appendix.

---

## Phase 2 — Bloomberg Data Pull

**Script:** `src/01_bloomberg_pull.py`  
**Outputs:** `data/raw/bloomberg/snapshot_2023.csv`, `data/raw/bloomberg/returns_panel.csv`

### 2.1 Cross-sectional snapshot (as of 2023-12-31)

Pull via `BDP` for each ticker, reference date `2023-12-31`:

| Variable | Bloomberg Field | Notes |
|---|---|---|
| Price-to-Book Ratio | `PX_TO_BOOK_RATIO` | Core Korea discount measure |
| P/E Ratio | `PE_RATIO` | Alternative valuation |
| Return on Equity | `RETURN_COM_EQY` | Profitability |
| Return on Assets | `RETURN_ON_ASSET` | Alternative profitability |
| Foreign Ownership % | `EQY_FLOAT_PCT` | Governance pressure proxy |
| Market Cap (KRW bn) | `CUR_MKT_CAP` | Size control |
| Dividend Yield | `EQY_DVD_YLD_IND` | Shareholder return proxy |
| Debt-to-Equity | `TOT_DEBT_TO_TOT_EQY` | Financial risk |
| Total Assets (KRW bn) | `BS_TOT_ASSET` | Size alternative |
| Revenue Growth YoY | `SALES_GROWTH` | Growth proxy |
| Cash & Equivalents | `CASH_AND_NEAR_CASH_ITEM` | Capital hoarding proxy |

**Override required** for historical date:
```python
overrides = {"FUNDAMENTAL_DATABASE_DATE": "20231231"}
```

### 2.2 ROE time series (2019–2023)

Pull via `BDH` for each ticker:
- Field: `RETURN_COM_EQY`, annual frequency
- Purpose: assess whether compliant firms were already-improving or stagnant (Part B of analysis)

### 2.3 Daily returns panel (2022-01-01 to 2025-06-30)

Pull via `BDH` for each ticker:
- Field: `PX_LAST` (closing price)
- Compute daily log returns in script
- Also pull `KOSPI Index` as market benchmark

**Rate limiting:** blpapi handles ~100 securities per request comfortably. Batch your universe into chunks of 100; add a small sleep between batches to avoid throttling.

---

## Phase 3 — Build Compliance Dataset

**Script:** `src/02_build_compliance.py`  
**Output:** `data/processed/compliance.csv`

### 3.1 Source: KRX Value-Up Disclosure Portal

URL: `http://disclosure.krx.co.kr` → 기업가치 제고 계획 공시  
Download the full disclosure list (firm name, ticker, date submitted).

Alternatively, the FSC published summary compliance data — cross-reference both.

### 3.2 Compliance classification (three-way)

Manually review each submitted disclosure and classify:

| Code | Label | Criteria |
|---|---|---|
| 0 | Non-compliant | No disclosure submitted |
| 1 | Compliant / Vague | Submitted but no quantitative targets (e.g., "will strive to improve shareholder value") |
| 2 | Compliant / Quantitative | Submitted with specific numerical targets (e.g., target PBR, ROE, payout ratio, timeline) |

**Record in:** `data/raw/krx/compliance_coded.csv` with columns:
`ticker, firm_name, disclosure_date, compliance_code, coder_notes`

**Inter-rater check:** Have a second reader independently code a random 20% subsample. Compute Cohen's Kappa. Report in the paper's data section. Target κ > 0.75.

### 3.3 Extract event dates

From the compliance dataset, extract disclosure dates for compliant firms (codes 1 and 2). Save to `data/processed/events.csv`:
`ticker, event_date, compliance_code`

---

## Phase 4 — Merge External Data

**Script:** `src/03_merge_covariates.py`  
**Output:** `data/processed/sample.csv` (master file)

### 4.1 Chaebol affiliation (KFTC)

Source: KFTC 공시 → 대규모기업집단 지정현황 (2023 designation)  
URL: `https://www.ftc.go.kr`  
Download the 2023 large business group list. Code dummy: `chaebol = 1` if firm appears in any designated group.

### 4.2 Controlling shareholder ownership (DART)

Source: DART 전자공시 → 대량보유상황보고서 / 사업보고서 (2023 annual reports)  
URL: `https://dart.fss.or.kr`  

Pull the "최대주주 및 특수관계인 지분율" (largest shareholder + related parties %) from each firm's 2023 annual report. This is the controlling shareholder ownership variable. Can be scraped using DART Open API (OpenDART) with Python's `requests`:

```python
import requests
BASE = "https://opendart.fss.or.kr/api/"
# Endpoint: majorstock.json
# Parameters: corp_code, bsns_year, reprt_code
```

Register for a free OpenDART API key at dart.fss.or.kr.

### 4.3 Master merge

Join on ticker:
- Bloomberg snapshot (Phase 2.1)
- Compliance classification (Phase 3)
- Chaebol dummy (Phase 4.1)
- Controlling shareholder % (Phase 4.2)

Final columns in `sample.csv`:

```
ticker, name, sector, market_cap, pbr, per, roe, roa,
foreign_own_pct, div_yield, leverage, cash_ratio, rev_growth,
chaebol, controlling_shareholder_pct,
compliance_code, disclosure_date
```

Run diagnostics: check missingness by variable, winsorize continuous variables at 1st/99th percentiles.

---

## Phase 5 — Descriptive Statistics

**Script:** `src/04_descriptive.py`  
**Outputs:** `outputs/tables/table1_summary.tex`, `outputs/figures/fig1_pbr_dist.pdf`, `outputs/figures/fig2_compliance_breakdown.pdf`

### 5.1 Table 1 — Summary statistics

Full sample, then split by compliance code (0 / 1 / 2). Report mean, median, SD for all continuous variables. Report N and % for chaebol dummy.

Use `stargazer` or write custom LaTeX table via `utils/latex_tables.py`.

### 5.2 Figure 1 — PBR distribution by compliance group

Overlapping KDE or violin plot: non-compliant vs. vague vs. quantitative. Use `matplotlib` / `seaborn`. Save as `.pdf` for clean LaTeX embedding.

### 5.3 Figure 2 — Compliance breakdown by sector and chaebol status

Stacked bar chart: compliance rate by GICS sector. Separate panel for chaebol vs. non-chaebol.

### 5.4 t-tests / Mann-Whitney U

Compare means across compliance groups for each covariate. Flag statistically significant differences (these preview your logit results).

---

## Phase 6 — Part A: Determinants of Compliance (Logistic Regression)

**Script:** `src/05_logit_compliance.py`  
**Outputs:** `outputs/tables/table2_logit.tex`

### 6.1 Models to run

Run three specifications, report side-by-side:

| Model | Dependent Variable | Notes |
|---|---|---|
| (1) | Binary: complied (1/2) vs. not (0) | Baseline logit |
| (2) | Binary: quantitative (2) vs. vague/none (0/1) | Quality of compliance |
| (3) | Ordinal: 0 / 1 / 2 | Ordered logit via `statsmodels` |

```python
import statsmodels.formula.api as smf

# Binary logit
model1 = smf.logit(
    "complied ~ pbr + roe + foreign_own_pct + chaebol + "
    "controlling_shareholder_pct + np.log(market_cap) + "
    "div_yield + leverage",
    data=sample
).fit(cov_type="HC3")  # heteroskedasticity-robust SEs
```

### 6.2 Hypotheses to test

| Hypothesis | Variable | Expected sign |
|---|---|---|
| H1: Low-PBR firms more likely to comply (more to gain) | `pbr` | − |
| H2: High foreign ownership → more compliance (external pressure) | `foreign_own_pct` | + |
| H3: Chaebol firms less likely to comply / comply vaguely | `chaebol` | − |
| H4: High controlling shareholder stake → less compliance | `controlling_shareholder_pct` | − |

### 6.3 Marginal effects

Report average marginal effects (AME), not raw logit coefficients, for interpretability. `statsmodels` provides `.get_margeff()`.

### 6.4 Robustness

- Add sector fixed effects (GICS sector dummies)
- Rerun excluding the top 10 chaebols by market cap (Samsung, SK, Hyundai, etc.) to check if results are driven by mega-groups
- Report in appendix

---

## Phase 7 — Part B: Is Compliance Substantive?

**Script:** `src/06_fundamentals_comparison.py`  
**Outputs:** `outputs/tables/table3_fundamentals.tex`, `outputs/figures/fig3_roe_trends.pdf`

### 7.1 ROE trajectory comparison (2019–2023)

For each compliance group, compute mean ROE per year. Plot as a line chart — are quantitative disclosers genuinely on an upward profitability trajectory, or are they indistinguishable from non-compliers?

### 7.2 Dividend growth comparison

Pull dividend per share (DPS) 2019–2023 from Bloomberg (`DVD_SH_12M`, annual). Compare growth rates across groups.

### 7.3 Capital allocation: cash hoarding

Test whether non-compliant firms have higher cash ratios (cash & equivalents / total assets). This speaks to the "hoarding" argument — controlling shareholders retaining cash rather than returning it.

### 7.4 Governance quality (if available)

KCGS (한국기업지배구조원) publishes annual governance scores for KOSPI firms. If accessible, merge and compare governance scores across compliance groups. This is optional but strengthens Part B considerably.

### 7.5 Key question to answer in the paper

> Are compliant firms firms that *need* reform, or firms that were already doing well and face low cost to disclosing?

If you find compliant firms had *already-higher* ROE and *lower* controlling shareholder stakes going into 2024, this is adverse selection — the program attracted the easy cases and left the problem firms untouched.

---

## Phase 8 — Part C: Event Study

**Script:** `src/07_event_study.py`  
**Outputs:** `outputs/tables/table4_cars.tex`, `outputs/figures/fig4_car_plot.pdf`

### 8.1 Market model estimation

For each firm *i* with a disclosure event:

**Estimation window:** t = −120 to t = −21 (100 trading days before event)

```python
# OLS: R_i,t = alpha_i + beta_i * R_m,t + epsilon_i,t
import statsmodels.api as sm

for ticker, event_date in events.iterrows():
    est_window = returns[
        (returns.date >= event_date - 120_trading_days) &
        (returns.date <= event_date - 21_trading_days)
    ]
    X = sm.add_constant(est_window["kospi_return"])
    model = sm.OLS(est_window[ticker], X).fit()
    alpha[ticker] = model.params["const"]
    beta[ticker] = model.params["kospi_return"]
```

### 8.2 Abnormal returns

**Event window:** t = −1 to t = +5 (primary), t = −1 to t = +20 (secondary)

```
AR_i,t = R_i,t - (alpha_i + beta_i * R_m,t)
CAR_i = sum(AR_i,t) over event window
```

### 8.3 Statistical tests

- **Patell (standardized) t-test** on mean CAR across firms — accounts for variance differences across firms
- **Boehmer et al. (1991) test** — robust to event-induced variance changes (important here since disclosure is news)
- Report N, mean CAR, t-stat, and % positive for each subgroup

### 8.4 Cross-sectional CAR regression

To understand *what predicts* a stronger market response:

```
CAR_i = γ₀ + γ₁(QuantitativeDummy_i) + γ₂(ForeignOwnership_i) +
        γ₃(ChaeholDummy_i) + γ₄(PBR_i) + γ₅(log(MarketCap_i)) + ε_i
```

This is your most important regression for the market response section. H: quantitative disclosures and high foreign ownership → larger positive CAR; chaebol affiliation → smaller/insignificant CAR.

### 8.5 Figure 4 — CAR plot

Cumulative average abnormal returns by group (quantitative / vague / split by chaebol) plotted over t = −5 to t = +20. Standard error bands. This is the most visually compelling output in the paper.

### 8.6 Interpretation guidance

- If overall CARs are small and insignificant → market didn't believe the program
- If CARs are positive only for quantitative/non-chaebol disclosures → credibility is conditional on firm type
- Either result is a meaningful finding for your societal argument

---

## Phase 9 — LaTeX Paper

### 9.1 main.tex skeleton

```latex
\documentclass[12pt]{article}
\usepackage{style/paper}
\usepackage{style/econometrics}
\usepackage{booktabs}       % professional tables
\usepackage{graphicx}
\usepackage{hyperref}
\usepackage[backend=biber, style=apa]{biblatex}
\addbibresource{references.bib}

\title{Voluntary Reform and Adverse Selection:\\
       Evidence from Korea's Corporate Value-Up Program}
\author{[Your Name]}
\date{[Date]}

\begin{document}
\maketitle
\begin{abstract}
  [~200 words: puzzle, method, main findings, implication]
\end{abstract}

\input{sections/01_introduction}
\input{sections/02_background}
\input{sections/03_literature}
\input{sections/04_data}
\input{sections/05_who_complied}
\input{sections/06_fundamentals}
\input{sections/07_event_study}
\input{sections/08_discussion}
\input{sections/09_conclusion}

\printbibliography
\end{document}
```

### 9.2 Table conventions (`style/econometrics.sty`)

- All regression tables: `booktabs` format (`\toprule`, `\midrule`, `\bottomrule`)
- Standard errors in parentheses below coefficients
- Significance stars: * p<0.10, ** p<0.05, *** p<0.01 (note at bottom of each table)
- Table notes in `\footnotesize` with `\raggedright`

### 9.3 Figure conventions

Generate all figures in Python with:
```python
import matplotlib
matplotlib.use("pdf")        # vector output for LaTeX
matplotlib.rcParams.update({
    "font.family": "serif",
    "font.size": 11,
    "axes.spines.top": False,
    "axes.spines.right": False,
})
plt.savefig("outputs/figures/figN_name.pdf", bbox_inches="tight")
```

Include in LaTeX:
```latex
\begin{figure}[htbp]
  \centering
  \includegraphics[width=0.85\textwidth]{figures/fig4_car_plot.pdf}
  \caption{Cumulative Average Abnormal Returns by Compliance Type}
  \label{fig:car}
\end{figure}
```

### 9.4 Auto-exporting tables from Python

```python
# utils/latex_tables.py
def df_to_latex(df, path, caption, label, note=None):
    """Export a DataFrame to a standalone .tex table fragment."""
    ...
    # Use df.to_latex(booktabs=True, escape=False) as base
    # Wrap in table + caption + label + footnote
```

Each analysis script calls this at the end to drop a `.tex` file into `outputs/tables/`. The paper `\input{}`s them directly — no manual copy-paste between Python and LaTeX.

---

## Phase 10 — Execution Order & Checklist

Run scripts in order. Each script reads from `data/` and writes to `data/processed/` or `outputs/`. Nothing modifies raw data.

```
[ ] Phase 0: Environment confirmed, Bloomberg connection tested
[ ] Phase 1: 00_build_universe.py → universe_raw.csv
[ ] Phase 2: 01_bloomberg_pull.py → snapshot_2023.csv, returns_panel.csv
[ ] Phase 3: Manual KRX compliance coding → compliance_coded.csv
            02_build_compliance.py → compliance.csv, events.csv
[ ] Phase 4: Manual KFTC/DART data collection
            03_merge_covariates.py → sample.csv
[ ] Phase 5: 04_descriptive.py → Table 1, Figures 1–2
[ ] Phase 6: 05_logit_compliance.py → Table 2
[ ] Phase 7: 06_fundamentals_comparison.py → Table 3, Figure 3
[ ] Phase 8: 07_event_study.py → Table 4, Figure 4
[ ] Phase 9: Write paper sections, compile LaTeX
[ ] Phase 10: Robustness checks (appendix), final compile, proofread
```

---

## Known Risks & Mitigations

| Risk | Mitigation |
|---|---|
| Low N of compliant firms (~100–150) reduces event study power | Report economic magnitude alongside p-values; frame as directional evidence; add a power analysis note |
| blpapi field availability varies by Terminal license | Test all fields in Phase 2 first; fall back to Bloomberg Excel Add-in for missing fields |
| Controlling shareholder % missing for some firms | Use DART OpenAPI; supplement manually for large firms; report missingness in Table 1 |
| Compliance coding is subjective | Inter-rater kappa check; provide coding guide in appendix |
| Endogeneity in logit (firms planning reform self-select) | Acknowledge explicitly in Section 5; frame as correlational; do not over-claim causality |
| KRX disclosure portal data incomplete | Cross-reference with FSC press releases and DART 기업가치 제고 계획 filings |

---

## Key References to Cite

From your Abstracts_Collection.md — all already in hand:
- **Paper 3** (Lee, Jin-hyo, 2025) — Value-Up program overview and Japan comparison
- **Paper 4** (Njoku et al., 2026) — governance mechanisms under concentrated ownership
- **Paper 13** (Kang & Kim, 2026) — Commercial Act amendment event study (your main comparator)
- **Paper 1** (Kim, Seok et al., 2025) — shareholder return policies and Korea discount
- **Paper 2** (Lee, Jeong, 2025) — PBR determinants and capital allocation

Additional to acquire:
- Bae, Kang & Kim (2002) — tunneling via chaebol acquisitions (*Journal of Finance*)
- Black, Jang & Kim (2015) — governance reform and tunneling channel (*Journal of Banking & Finance*)
- Voluntary disclosure theory: Verrecchia (1983, *Journal of Accounting and Economics*)
- Adverse selection in voluntary governance: Hermalin & Weisbach (2012, *Journal of Finance*)

---

*Last updated: [date]. All Bloomberg pulls should be re-run if paper submission date is more than 3 months after initial data collection.*
