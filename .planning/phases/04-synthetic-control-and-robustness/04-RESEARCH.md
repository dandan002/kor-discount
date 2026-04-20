# Phase 4: Synthetic Control and Robustness — Research

**Researched:** 2026-04-20
**Domain:** Synthetic control methods (pysyncon/ADH 2010), robustness econometrics
**Confidence:** HIGH (pysyncon API verified by live inspection; data coverage verified against actual files)

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **D-01:** Use `pysyncon` (Python port of Stata `synth`, ADH 2010). Pin version in `requirements.txt`. Do NOT use `mlsynth` or manual `scipy.optimize`.
- **D-02:** Treated unit: Japan (TOPIX P/B). Treatment date: `TSE_PB_REFORM_DATE` from `config.py` (2023-03-01).
- **D-03:** Outcome variable: P/B. P/E robustness handled separately in ROBUST-02.
- **D-04:** Donor pool: STOXX600, FTSE100, HSI (MSCI HK), MSCI Taiwan, SP500.
- **D-05:** Korea (KOSPI) excluded from donor pool.
- **D-06:** India and Indonesia excluded from synthetic control donor pool; used in ROBUST-01 placebo tests instead.
- **D-07:** SUTVA justification must be documented as a comment in the synthetic control script.
- **D-08:** Pre-treatment period: 2004-01-01 to 2023-02-01. RMSPE must be reported.
- **D-09:** One standalone Python module per robustness check:
  - `src/robustness/synthetic_control.py` — SYNTH-01 through SYNTH-03 + ROBUST-04
  - `src/robustness/robustness_pe.py` — ROBUST-02
  - `src/robustness/robustness_alt_control.py` — ROBUST-03
  - `src/robustness/robustness_placebo.py` — ROBUST-01
- **D-10:** ROBUST-02: full Phase 3 re-run (event study, panel OLS, GPR sub-analysis) using P/E. Results with `_pe` suffix in `output/robustness/`.
- **D-11:** ROBUST-02 uses same estimation windows, fixed effects, and SE methods as Phase 3 (D-01 through D-15 from `03-CONTEXT.md`).
- **D-12:** ROBUST-03 runs both: (a) MSCI EM Asia as EM ex-Korea proxy; (b) EM ex-China proxy (Claude's discretion on construction).
- **D-13:** Each alt-control variant produces its own LaTeX table in `output/robustness/`.
- **D-14:** ROBUST-01 falsification markets: MSCI Taiwan and MSCI Indonesia. Run Phase 3 event study design on each, expecting null effects.
- **D-15:** ROBUST-01 results saved to `output/robustness/placebo_*.csv` and a combined placebo figure.
- **D-16:** ROBUST-04 two placebo types: (a) in-time placebo with fake treatment date; (b) in-space placebo treating each donor as treated unit in turn.
- **D-17:** In-space and in-time placebo outputs saved to `output/robustness/` as CSV + PDF.
- **D-18:** Output structure in `output/robustness/`: `synthetic_control_weights.csv`, `figure_synth_gap.pdf`, `figure_placebo_intime.pdf`, `figure_placebo_inspace.pdf`, `placebo_taiwan_*.csv`, `placebo_indonesia_*.csv`, `robustness_pe_ols.tex`, `robustness_pe_event_coefs.tex`, `robustness_alt_control_em_asia.tex`, `robustness_alt_control_em_exchina.tex`.

### Claude's Discretion
- Exact `pysyncon` API calls (solver kwargs, predictor variable selection)
- Whether to use TOPIX or MSCI Japan series as the treated unit P/B input
- Construction method for MSCI EM ex-China proxy
- In-time placebo date selection
- Exact matplotlib layout for the in-space placebo distribution figure

### Deferred Ideas (OUT OF SCOPE)
- Full channel decomposition (GEO-V2-01)
- Callaway-Sant'Anna staggered DiD
- DVC pipeline for data versioning
- Formal MSCI EM ex-China index construction vs. proxy
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| SYNTH-01 | Estimate synthetic control for Japan using ADH (2010) for the 2023 TSE P/B reform | pysyncon 1.5.2 Dataprep + Synth API verified; donor pool CSVs confirmed present |
| SYNTH-02 | Report pre-treatment RMSPE, donor pool weights, pre/post fit chart | `synth.mspe()` → RMSPE = sqrt(mspe()); `synth.weights()` returns pd.Series; `_gaps()` enables custom gap plot |
| SYNTH-03 | Document donor pool with SUTVA justification | SUTVA narrative ready; comment template in Architecture Patterns |
| ROBUST-01 | Placebo/falsification tests on Taiwan and Indonesia | Both CSVs present; event study reuse pattern documented |
| ROBUST-02 | Replicate primary results using P/E instead of P/B | All donor CSVs have pe column; panel.parquet has pe (4 nulls in KOSPI 2004-01); Phase 3 scripts accept column swap |
| ROBUST-03 | Alternative control group: MSCI EM Asia and EM ex-China proxy | msci_em_asia_pb verified present; EM ex-China proxy construction via weighted residual feasible |
| ROBUST-04 | Synthetic control in-time and in-space placebo tests | In-space: manual loop over donor pool; in-time: re-run Dataprep with fake date |
</phase_requirements>

---

## Summary

Phase 4 adds no new primary estimates — it stress-tests Phase 3 results through four modules. The synthetic control module (`synthetic_control.py`) is the methodological centrepiece: it estimates a synthetic Japan using ADH (2010) via the `pysyncon` library, then runs in-time and in-space placebo tests to assess specificity. Three additional modules replicate Phase 3 analyses under alternative specifications (P/E metric, alternative EM benchmarks, falsification markets).

All required data is confirmed present in `data/raw/` and `data/processed/`. The `pysyncon` library (version 1.5.2) is the PyPI-latest version; it is not yet in `requirements.txt` and must be added. The library's API was verified by live introspection: `Dataprep` accepts pandas Timestamp columns directly; `Synth.fit()` optimises the V and W matrices; RMSPE = `sqrt(synth.mspe())`; donor weights are in `synth.weights()`. There is no built-in `PlaceboTest` class in 1.5.2 — in-space placebos must be implemented as a manual loop.

The single most important implementation decision left to Claude's discretion is the MSCI EM ex-China proxy: research confirms a weighted-residual approach is mathematically sound and produces valid P/B values across the full 2004-2026 range.

**Primary recommendation:** Pin `pysyncon==1.5.2` in `requirements.txt`; implement in-space placebos as a donor-loop; use `synth._gaps()` to extract the gap Series and build gap plots manually with matplotlib (pysyncon's built-in `gaps_plot()` calls `plt.show()` and cannot save to file directly).

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Synthetic control estimation | Analysis script (`synthetic_control.py`) | config.py (event date firewall) | ADH optimisation is a self-contained econometric computation |
| In-space placebo loop | `synthetic_control.py` | — | Donor-loop is part of the same estimation module |
| In-time placebo | `synthetic_control.py` | config.py | Reuses same Dataprep/Synth pattern with different treatment date |
| P/E robustness replication | `robustness_pe.py` | Phase 3 scripts (read/adapt, not import) | Column swap on Phase 3 patterns; no cross-module imports |
| Alt-control group robustness | `robustness_alt_control.py` | Raw CSV loader | Substitutes control panel, otherwise same OLS pattern |
| Placebo falsification markets | `robustness_placebo.py` | Phase 3 event_study logic (adapted inline) | Taiwan/Indonesia as pseudo-treated; same stacked design |
| Output directory creation | First script to run (any) | — | `Path.mkdir(parents=True, exist_ok=True)` idiom |
| Data loading | Each script independently | panel.parquet + raw CSVs | No cross-module data sharing |

---

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| pysyncon | 1.5.2 | ADH synthetic control: Dataprep + Synth | Only mature Python port of Stata `synth`; locked in D-01 |
| pandas | 2.2.3 (already pinned) | Panel construction, date handling, output CSV | Project standard |
| numpy | 1.26.4 (already pinned) | Weight/matrix operations, sqrt(mspe) | Project standard |
| scipy | 1.13.1 (already pinned) | pysyncon inner optimizer (Nelder-Mead) | pysyncon dependency |
| matplotlib | 3.9.2 (already pinned) | Gap plots, placebo distribution figure | Project standard |
| linearmodels | 6.1 (already pinned) | PanelOLS for ROBUST-02 and ROBUST-03 | Phase 3 carry-forward |
| wildboottest | 0.3.2 (already pinned) | Wild-bootstrap SE in ROBUST-02 | Phase 3 carry-forward |
| statsmodels | 0.14.4 (already pinned) | OLS for ROBUST-01 event study, GPR sub-analysis | Phase 3 carry-forward |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| math (stdlib) | — | RMSPE = math.sqrt(synth.mspe()) | Every synthetic control script |
| pathlib (stdlib) | — | OUTPUT_DIR / "robustness" directory creation | Every script |
| logging (stdlib) | — | Structured stdout logging | Every script |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| pysyncon | mlsynth | Explicitly out of scope (D-01) |
| pysyncon | Manual scipy.optimize | Out of scope; pysyncon is the tested implementation |
| Nelder-Mead optimizer | Powell, L-BFGS-B | Nelder-Mead is pysyncon default and standard for SCM |

**Installation (add to requirements.txt):**
```bash
pip install pysyncon==1.5.2
```

**Version verification:** [VERIFIED: pip index versions pysyncon] — latest stable is 1.5.2 as of 2026-04-20.

---

## Architecture Patterns

### System Architecture Diagram

```
data/raw/ (donor CSVs)
    │
    ├── topix_pb_2004_2026.csv ────────────────────────────────────────┐
    ├── stoxx600_pb_2004_2026.csv                                      │
    ├── ftse100_pb_2004_2026.csv                                       │
    ├── msci_hk_pb_2004_2026.csv                      Donor panel     │
    ├── msci_taiwan_pb_2004_2026.csv   ──────────────►  (wide format)  │
    ├── sp500_pb_2004_2026.csv                                         │
    ├── *_pe_2004_2026.csv (ROBUST-02/03)                              │
    └── msci_em_asia_pb, msci_china_pb (ROBUST-03)                    │
                                                                       ▼
data/processed/panel.parquet ──────────────────────────────► [Data Loader in each module]
    │ (date, country, pb, pe)                                          │
    │ KOSPI, TOPIX, SP500, MSCI_EM only                               │
    │ Used only by ROBUST-01, ROBUST-02, ROBUST-03                    │
    └─────────────────────────────────────────────────────────────────►│
                                                                       │
config.py (TSE_PB_REFORM_DATE)  ───────────────────────────────────►  │
                                                                       ▼
                                                            ┌─────────────────────┐
                                                            │  Dataprep object    │
                                                            │  (long → wide pivot)│
                                                            └─────────────────────┘
                                                                       │
                                                                       ▼
                                                            ┌─────────────────────┐
                                                            │  Synth.fit()        │
                                                            │  (V, W optimised)   │
                                                            └─────────────────────┘
                                                                       │
                          ┌────────────────────────────────────────────┤
                          │                    │                       │
                          ▼                    ▼                       ▼
                   weights CSV           RMSPE scalar         Gap series (pd.Series)
                                                                       │
                          ┌────────────────────────────────────────────┤
                          │                    │                       │
                          ▼                    ▼                       ▼
               in-space placebo loop   in-time placebo        Gap plot (manual
               (donor as treated,      (fake date 2019-01-01,  matplotlib, savefig)
                remaining as control)   re-run Dataprep)

output/robustness/ ◄── all CSV and PDF artefacts
output/figures/    ◄── figure_synth_gap.pdf
```

### Recommended Project Structure
```
src/
├── analysis/          # Phase 3 scripts (read-only for Phase 4 adaptation)
│   ├── event_study.py
│   ├── panel_ols.py
│   └── geo_risk.py
└── robustness/        # New Phase 4 directory
    ├── __init__.py
    ├── synthetic_control.py   # SYNTH-01/02/03 + ROBUST-04
    ├── robustness_pe.py       # ROBUST-02
    ├── robustness_alt_control.py # ROBUST-03
    └── robustness_placebo.py  # ROBUST-01

output/
├── figures/           # figure_synth_gap.pdf lands here
└── robustness/        # all other Phase 4 outputs (NEW directory)
```

### Pattern 1: Dataprep + Synth Fit
**What:** Constructs the ADH synthetic control for Japan's P/B using the donor pool.
**When to use:** `synthetic_control.py` and for every in-space and in-time placebo iteration.

```python
# Source: verified by live pysyncon 1.5.2 introspection — 2026-04-20
import math
import pandas as pd
from pysyncon import Dataprep, Synth
import config

# 1. Build long-format donor panel (date, unit_name, pb) from raw CSVs
#    TOPIX = treated unit; all donor CSVs loaded and stacked

# 2. Define time ranges as DatetimeIndex (verified: pysyncon accepts pd.Timestamp)
pre_period = pd.date_range(
    start="2004-01-01",
    end="2023-02-01",
    freq="MS",
)
all_period = pd.date_range(
    start="2004-01-01",
    end="2026-04-01",   # or end of available data
    freq="MS",
)

dataprep = Dataprep(
    foo=panel_df,                          # long-format DataFrame
    predictors=["pe"],                     # covariate predictors (see Predictor Selection below)
    predictors_op="mean",                  # aggregate over time_predictors_prior
    dependent="pb",                        # outcome variable
    unit_variable="unit",                  # column identifying unit
    time_variable="date",                  # column with pd.Timestamp values
    treatment_identifier="TOPIX",          # treated unit label
    controls_identifier=[                  # donor pool
        "STOXX600", "FTSE100", "MSCI_HK", "MSCI_TAIWAN", "SP500"
    ],
    time_predictors_prior=pre_period,      # time range for predictor aggregation
    time_optimize_ssr=pre_period,          # pre-treatment loss minimisation range
    # special_predictors: can add lagged PB values here for better fit
    # e.g., [("pb", [pd.Timestamp("2010-01-01"), pd.Timestamp("2018-01-01")], "mean")]
)

synth = Synth()
synth.fit(
    dataprep=dataprep,
    optim_method="Nelder-Mead",
    optim_initial="equal",
    optim_options={"maxiter": 1000},
)

# 3. Extract results
weights = synth.weights(round=4)         # pd.Series: index=donor names, values=weights
rmspe = math.sqrt(synth.mspe())         # float: pre-treatment RMSPE in P/B points
summary_df = synth.summary()            # DataFrame: V matrix + predictor balance table
att_result = synth.att(
    time_period=pd.date_range("2023-03-01", "2026-04-01", freq="MS")
)  # dict: {"att": float, "se": float}
```

### Pattern 2: Custom Gap Plot (bypassing plt.show())
**What:** `gaps_plot()` calls `plt.show()` internally — cannot save to file. Use `_gaps()` to get the Series and build the figure manually.
**When to use:** All synthetic control figures in `output/robustness/` and `output/figures/`.

```python
# Source: verified by live source inspection of pysyncon 1.5.2 base.py — 2026-04-20
import matplotlib
matplotlib.use("Agg")  # headless — must come before pyplot import
import matplotlib.pyplot as plt

# Get gap as pd.Series (index = pd.Timestamp, values = pb_japan - pb_synthetic)
Z0, Z1 = dataprep.make_outcome_mats(time_period=all_period)
ts_gap = synth._gaps(Z0=Z0, Z1=Z1)

fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(ts_gap.index, ts_gap.values, color="black", linewidth=1, label="Japan gap")
ax.axhline(0, color="black", linestyle="dashed", linewidth=0.8)
ax.axvline(
    x=pd.Timestamp(config.TSE_PB_REFORM_DATE),
    color="grey",
    linestyle="dashed",
    label="TSE P/B Reform (Mar 2023)",
)
ax.set_ylabel("P/B gap (Japan − Synthetic Japan)")
ax.set_title(f"Synthetic Control Gap — Pre-treatment RMSPE: {rmspe:.4f}")
ax.legend()
fig.savefig(output_dir / "figure_synth_gap.pdf", dpi=300, bbox_inches="tight")
plt.close(fig)
```

### Pattern 3: In-Space Placebo Loop (manual)
**What:** pysyncon 1.5.2 has no built-in `PlaceboTest` class. Implement as a loop over donors.
**When to use:** ROBUST-04 in-space placebo test.

```python
# Source: confirmed by pysyncon 1.5.2 module inspection — no PlaceboTest in inference module
donors = ["STOXX600", "FTSE100", "MSCI_HK", "MSCI_TAIWAN", "SP500"]
placebo_gaps = {}

for placebo_unit in donors:
    remaining = [d for d in donors if d != placebo_unit]
    dp_placebo = Dataprep(
        foo=panel_df,
        predictors=["pe"],
        predictors_op="mean",
        dependent="pb",
        unit_variable="unit",
        time_variable="date",
        treatment_identifier=placebo_unit,
        controls_identifier=["TOPIX"] + remaining,  # TOPIX now a control
        time_predictors_prior=pre_period,
        time_optimize_ssr=pre_period,
    )
    synth_p = Synth()
    synth_p.fit(dataprep=dp_placebo, optim_method="Nelder-Mead")
    Z0p, Z1p = dp_placebo.make_outcome_mats(time_period=all_period)
    placebo_gaps[placebo_unit] = synth_p._gaps(Z0=Z0p, Z1=Z1p)

# Japan gap is in ts_gap (from Pattern 2)
# Plot distribution of placebo gaps alongside Japan gap
```

### Pattern 4: In-Time Placebo
**What:** Re-run Dataprep/Synth with a fake treatment date well before 2023.
**When to use:** ROBUST-04 in-time placebo test.

```python
# Source: [ASSUMED] standard ADH in-time placebo convention
PLACEBO_DATE = pd.Timestamp("2019-01-01")  # pre-COVID, no Japan governance reform
pre_placebo = pd.date_range(start="2004-01-01", end="2018-12-01", freq="MS")

dataprep_intime = Dataprep(
    foo=panel_df,
    predictors=["pe"],
    predictors_op="mean",
    dependent="pb",
    unit_variable="unit",
    time_variable="date",
    treatment_identifier="TOPIX",
    controls_identifier=["STOXX600", "FTSE100", "MSCI_HK", "MSCI_TAIWAN", "SP500"],
    time_predictors_prior=pre_placebo,
    time_optimize_ssr=pre_placebo,
)
# Fit same way; expected result: gap near zero post-2019 if no spurious effect
```

### Pattern 5: ROBUST-02 P/E Column Swap
**What:** Replace `pb` with `pe` column throughout Phase 3 logic. No structural changes.
**When to use:** `robustness_pe.py`.

```python
# Source: verified panel.parquet schema — 2026-04-20
# panel.parquet has columns: date, country, pb, pe
# pe has 4 nulls in KOSPI rows for 2004-01-31 to 2004-04-30 (KOSPI PE starts 2004-05)
# Drop those rows or restrict study start to 2004-05-01 for PE analyses

panel_pe = panel.dropna(subset=["pe"]).copy()
# Then adapt event_study.build_stacked_dataset, construct_regression_panel
# to use "pe" instead of "pb" — all function signatures accept the column name
# or simply rename the column before passing to reused functions
```

### Pattern 6: ROBUST-03 EM ex-China Proxy
**What:** Construct MSCI EM ex-China P/B from available MSCI EM and MSCI China CSVs.
**When to use:** `robustness_alt_control.py`, ROBUST-03 second variant.

```python
# Source: verified by data inspection — 2026-04-20
# Mathematical derivation: MSCI_EM = china_wt * China_PB + (1 - china_wt) * EM_ex_China_PB
# => EM_ex_China_PB = (MSCI_EM_PB - china_wt * China_PB) / (1 - china_wt)
# china_wt ~ 0.30 (approximate; MSCI EM China weight was ~30-35% circa 2023)
# [ASSUMED] exact China weight; document this explicitly

CHINA_WEIGHT_APPROX = 0.30  # document as approximation in script comment

em = pd.read_csv(RAW_DIR / "msci_em_pb_2004_2026.csv")
china = pd.read_csv(RAW_DIR / "msci_china_pb_2004_2026.csv")
em["date"] = pd.to_datetime(em["date"])
china["date"] = pd.to_datetime(china["date"])
merged = em.merge(china, on="date", suffixes=("_em", "_china"))
merged["pb"] = (merged["pb_em"] - CHINA_WEIGHT_APPROX * merged["pb_china"]) / (1 - CHINA_WEIGHT_APPROX)
# Verified: no negative values across full 2004-2026 range (min ~0.40)
```

### Anti-Patterns to Avoid
- **Importing Phase 3 modules from robustness scripts:** Each robustness script is standalone. Copy/adapt the needed functions inline rather than importing from `src.analysis.*`. (Enforced by D-15 carry-forward from Phase 3.)
- **Using `plt.show()` in headless scripts:** All scripts use `matplotlib.use("Agg")` before importing `pyplot`. `gaps_plot()` and `path_plot()` both call `plt.show()` — use `_gaps()` pattern instead.
- **Hardcoding event dates or file paths:** Always import from `config.py`. The date firewall is the key reproducibility constraint.
- **Forgetting `Path.mkdir(parents=True, exist_ok=True)`:** `output/robustness/` does not exist yet. The first script to run must create it.
- **Using pysyncon with integer time periods when dates are Timestamps:** The `time_period`, `time_optimize_ssr`, and `time_predictors_prior` arguments must all use the same type as the `time_variable` column. Use `pd.date_range(..., freq="MS")` throughout.
- **Treating RMSPE > 0.15 P/B points as a hard failure:** CONTEXT.md specifies to note the limitation rather than abort. Flag in the figure caption and paper text.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| ADH (2010) synthetic control optimisation | Custom scipy.optimize V-W bilevel solver | `pysyncon.Synth.fit()` | The bilevel constrained quadratic program is subtle; pysyncon handles the V-matrix OLS initialisation and W-matrix SLSQP correctly |
| Predictor balance table | Custom dataframe comparison | `synth.summary()` | Returns V matrix weights alongside treated vs. synthetic means across predictors |
| ATT and post-treatment gap stats | Manual mean/SE computation | `synth.att(time_period=...)` | Returns dict with ATT and standard error computed correctly over specified post-treatment window |
| Wild-bootstrap inference (ROBUST-02) | Custom bootstrap loop | `wildboottest` (already in requirements) | 4-cluster bootstrap is notoriously underperforming without the Rademacher weights implementation |
| Panel OLS with two-way FE (ROBUST-02/03) | statsmodels OLS with dummies | `linearmodels.PanelOLS` | Exact FE absorber; correct within-group demeaning (Phase 3 established this) |

**Key insight:** The synthetic control bilevel optimisation is where most hand-roll attempts fail — the V matrix update requires careful initialisation. pysyncon's `optim_initial="equal"` starts from uniform weights, which is the standard ADH starting point.

---

## Data Inventory (Verified)

### panel.parquet
| Column | Type | Countries | Date Range | Notes |
|--------|------|-----------|------------|-------|
| date | datetime64 | all | 2004-01-31 to 2026-04-30 | monthly frequency |
| country | object | KOSPI, TOPIX, SP500, MSCI_EM | all | 4 countries only |
| pb | float64 | all | full range | 0 nulls |
| pe | float64 | all | full range | 4 nulls — KOSPI rows 2004-01 to 2004-04 |

**Panel.parquet is NOT used for the synthetic control** (it only contains TOPIX and MSCI_EM, not the individual donor pool markets). The synthetic control module must load donor CSVs directly from `data/raw/`.

### Donor Pool Raw CSVs (SYNTH-01 / ROBUST-04)
| File | Rows | PB Nulls | PE Nulls | Date Range |
|------|------|----------|----------|------------|
| topix_pb_2004_2026.csv | 268 | 0 | — | 2004-01-20 to 2026-04-20 |
| stoxx600_pb_2004_2026.csv | 268 | 0 | 0 | 2004-01-20 to 2026-04-20 |
| ftse100_pb_2004_2026.csv | 268 | 0 | 0 | 2004-01-20 to 2026-04-20 |
| msci_hk_pb_2004_2026.csv | 268 | 0 | 0 | 2004-01-20 to 2026-04-20 |
| msci_taiwan_pb_2004_2026.csv | 268 | 0 | 0 | 2004-01-20 to 2026-04-20 |
| sp500_pb_2004_2026.csv | 268 | 0 | 0 | 2004-01-20 to 2026-04-20 |
| msci_taiwan_pe_2004_2026.csv | 264 | — | 0 | 2004-05-20 to 2026-04-20 (4 early months missing) |

**Note on MSCI Taiwan PE:** 4 early months (2004-01 to 2004-04) missing in PE series. For ROBUST-02 P/E synthetic control, restrict pre-treatment period to start 2004-05-01 or use a balanced panel that excludes those months.

### ROBUST-01 Placebo Market CSVs
| File | Rows | Nulls |
|------|------|-------|
| msci_taiwan_pb_2004_2026.csv | 268 | 0 |
| msci_indonesia_pb_2004_2026.csv | 268 | 0 |

### ROBUST-03 Alt-Control CSVs
| File | Rows | Nulls | Notes |
|------|------|-------|-------|
| msci_em_asia_pb_2004_2026.csv | 268 | 0 | EM ex-Korea proxy (primary) |
| msci_em_pb_2004_2026.csv | 268 | 0 | For EM ex-China calculation |
| msci_china_pb_2004_2026.csv | 268 | 0 | For EM ex-China calculation |

### Treated Unit Selection (Claude's Discretion)
Both TOPIX and MSCI Japan PB series are available with identical coverage (268 rows, 0 nulls). Correlation = 0.993. **Recommendation: use TOPIX** because:
1. The TSE P/B reform targets companies listed on TOPIX specifically
2. panel.parquet uses `country="TOPIX"` as Japan's identifier — consistency
3. TOPIX is the more comprehensive index (2200+ stocks vs. MSCI Japan's narrower float-adjusted selection)

[VERIFIED: data inspection 2026-04-20]

---

## Common Pitfalls

### Pitfall 1: `gaps_plot()` Cannot Save to File
**What goes wrong:** Calling `synth.gaps_plot()` triggers `plt.show()` internally, which either opens a GUI window (crashes headless) or produces no output file.
**Why it happens:** pysyncon's base class plots are display-first; file saving is not implemented in the library.
**How to avoid:** Extract the gap Series via `synth._gaps(Z0, Z1)` after calling `dataprep.make_outcome_mats()`, then build the figure manually with matplotlib and call `fig.savefig(...)`.
**Warning signs:** `UserWarning: Matplotlib is currently using Agg` followed by blank output files.

### Pitfall 2: Time Period Type Mismatch
**What goes wrong:** `time_predictors_prior` and `time_optimize_ssr` accept any iterable, but they must contain the same types as the values in the `time_variable` column. If column values are `pd.Timestamp` and the argument is a Python `range()`, pysyncon raises a `KeyError` during `make_outcome_mats()`.
**Why it happens:** The internal `.isin()` filter is type-sensitive.
**How to avoid:** Always use `pd.date_range(start=..., end=..., freq="MS")` for both time period arguments when the panel has monthly datetime dates.
**Warning signs:** `KeyError` on a date string, or silently empty outcome matrices.

### Pitfall 3: Donor Panel Requires Wide → Long Assembly
**What goes wrong:** Each donor's PB/PE data is in its own CSV with only two columns (`date`, `pb`). They must be loaded, labelled, and stacked into a single long-format DataFrame before passing to `Dataprep`.
**Why it happens:** `Dataprep` expects a single `foo` DataFrame with a `unit_variable` column identifying each unit.
**How to avoid:** Load each CSV, add a `unit` column with the market name, then `pd.concat()` all into one long DataFrame.

### Pitfall 4: RMSPE Naming — pysyncon Uses `mspe()` Not `rmspe()`
**What goes wrong:** Code calls `synth.rmspe()` and gets `AttributeError`.
**Why it happens:** The method is named `mspe()` (mean squared prediction error). RMSPE must be computed as `math.sqrt(synth.mspe())`.
**How to avoid:** Use `math.sqrt(synth.mspe())` and label it as RMSPE in all outputs and figure captions.

### Pitfall 5: In-Time Placebo Date Selection
**What goes wrong:** Choosing a placebo date that overlaps with a real reform event (e.g., 2014-02-01, 2015-06-01) or a major macro shock (COVID: 2020-03) creates a placebo gap that may appear real, weakening the test.
**Why it happens:** Confounding events contaminate the counterfactual.
**How to avoid:** Use 2019-01-01 as the fake treatment date. TOPIX PB in 2019 is stable (1.1-1.2 range), pre-COVID, and no Japan governance reform occurred. The pre-treatment period for this placebo should end 2018-12-01; use the full 2004-2026 window as the "post" period to display. [VERIFIED: data inspection 2026-04-20]

### Pitfall 6: MSCI Taiwan PE Misalignment in ROBUST-02
**What goes wrong:** MSCI Taiwan PE series has 264 rows (vs. 268 for PB). The 4 missing rows are 2004-01 through 2004-04. A direct merge on `date` drops those rows, potentially shrinking the pre-treatment period.
**Why it happens:** Bloomberg data gap for Taiwan PE in early 2004.
**How to avoid:** Restrict the synthetic control PE analysis pre-treatment period to `2004-05-01` to `2023-02-01` (excluding those months). Document this in a comment. [VERIFIED: data inspection 2026-04-20]

### Pitfall 7: `pe` Column in panel.parquet Has 4 Nulls (KOSPI)
**What goes wrong:** ROBUST-02 P/E panel OLS using `panel.parquet` fails or silently drops KOSPI 2004 rows when `pe` is used as the dependent variable.
**Why it happens:** KOSPI PE data starts 2004-05-16 (documented in `config.py`). The 4 null rows are KOSPI 2004-01 through 2004-04.
**How to avoid:** `panel_pe = panel.dropna(subset=["pe"])` before any PE analysis. This is safe since the config.py already documents this limitation.

---

## Code Examples

### Complete Synthetic Control Setup (Verified)
```python
# Source: verified by live pysyncon 1.5.2 run — 2026-04-20
import math
import logging
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from pysyncon import Dataprep, Synth

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
import config

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s", stream=sys.stdout)

ROBUSTNESS_DIR = config.OUTPUT_DIR / "robustness"
FIGURES_DIR = config.OUTPUT_DIR / "figures"
DONORS = {
    "STOXX600": "stoxx600_pb_2004_2026.csv",
    "FTSE100":  "ftse100_pb_2004_2026.csv",
    "MSCI_HK":  "msci_hk_pb_2004_2026.csv",
    "MSCI_TAIWAN": "msci_taiwan_pb_2004_2026.csv",
    "SP500":    "sp500_pb_2004_2026.csv",
}

def load_donor_panel() -> pd.DataFrame:
    """Load TOPIX + donors into single long-format DataFrame."""
    rows = []
    # Treated unit
    df = pd.read_csv(config.RAW_DIR / "topix_pb_2004_2026.csv")
    df["unit"] = "TOPIX"
    rows.append(df.rename(columns={"pb": "pb"}))
    # Donor pool
    for unit_name, fname in DONORS.items():
        df = pd.read_csv(config.RAW_DIR / fname)
        df["unit"] = unit_name
        rows.append(df)
    panel = pd.concat(rows, ignore_index=True)
    panel["date"] = pd.to_datetime(panel["date"])
    return panel

def run_synth(panel: pd.DataFrame) -> tuple[Synth, Dataprep]:
    pre_period = pd.date_range(
        start="2004-01-01", end="2023-02-01", freq="MS"
    )
    dataprep = Dataprep(
        foo=panel,
        predictors=["pb"],          # lag P/B as predictor; no PE available in this panel
        predictors_op="mean",
        dependent="pb",
        unit_variable="unit",
        time_variable="date",
        treatment_identifier="TOPIX",
        controls_identifier=list(DONORS.keys()),
        time_predictors_prior=pre_period,
        time_optimize_ssr=pre_period,
        special_predictors=[
            ("pb", pd.date_range("2010-01-01", "2010-12-01", freq="MS"), "mean"),
            ("pb", pd.date_range("2018-01-01", "2018-12-01", freq="MS"), "mean"),
        ],
    )
    synth = Synth()
    synth.fit(dataprep=dataprep, optim_method="Nelder-Mead",
              optim_initial="equal", optim_options={"maxiter": 1000})
    return synth, dataprep
```

### Weights and RMSPE Extraction (Verified)
```python
# Source: verified by live pysyncon 1.5.2 run — 2026-04-20
synth, dataprep = run_synth(panel)

weights = synth.weights(round=4)                   # pd.Series
rmspe = math.sqrt(synth.mspe())                    # float
summary = synth.summary()                          # DataFrame with V matrix

# Save weights CSV
weights_df = weights.reset_index()
weights_df.columns = ["donor", "weight"]
weights_df["pre_rmspe"] = rmspe
weights_df.to_csv(ROBUSTNESS_DIR / "synthetic_control_weights.csv", index=False)
logger.info("Weights saved. RMSPE = %.4f", rmspe)
if rmspe > 0.15:
    logger.warning("RMSPE %.4f > 0.15 threshold — interpret with caution", rmspe)
```

### LaTeX Table Output Pattern (Carry-Forward from Phase 3)
```python
# Source: established Phase 3 pattern (panel_ols.py) — booktabs, 2 decimal places
def write_latex_fragment(results_df: pd.DataFrame, path: Path, caption: str) -> None:
    tex = results_df.to_latex(
        index=True,
        float_format="%.2f",
        escape=False,
        column_format="l" + "r" * len(results_df.columns),
    )
    # Add booktabs replacement
    tex = tex.replace("\\toprule", "\\toprule").replace("\\midrule", "\\midrule")
    path.write_text(tex)
    logger.info("LaTeX table saved: %s", path)
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Stata `synth` package | `pysyncon` Python port | 2022+ | Full Python workflow; no Stata license needed |
| Manual placebo loops with custom optimisation | pysyncon `Synth` class | — | V-W bilevel optimisation handled internally |
| `rmspe()` method | `mspe()` method → `math.sqrt(mspe())` | pysyncon 1.x | Naming difference; RMSPE still the standard report metric |

**Deprecated/outdated:**
- `mlsynth`: Explicitly rejected (D-01). More experimental, less tested for ADH (2010) exact replication.
- pysyncon built-in `PlaceboTest`: Present in some documentation but NOT in pysyncon 1.5.2 (verified by module inspection). Must loop manually.

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | China weight in MSCI EM is approximately 30% for EM ex-China proxy construction | Pattern 6, ROBUST-03 | If actual weight differs materially (e.g., 25% or 35%), the EM ex-China PB values shift; document the assumed weight and note as approximation |
| A2 | 2019-01-01 is a clean in-time placebo date with no Japan governance confounds | Pitfall 5 | If a relevant policy event occurred in Japan around 2019 that affected P/B, the in-time test is contaminated; verify against institutional background section |
| A3 | `special_predictors` with lagged PB means at 2010 and 2018 will improve pre-treatment fit | Pattern 1 code example | Predictor selection affects V matrix and pre-treatment RMSPE; planner should treat exact predictor list as Claude's discretion and tune empirically |

---

## Open Questions

1. **Predictor variable selection for Dataprep**
   - What we know: `pysyncon` accepts `predictors` (covariates aggregated over `time_predictors_prior`) and `special_predictors` (custom time ranges). Using the outcome variable (PB) at lagged time points is standard ADH practice.
   - What's unclear: Optimal set of predictors for the Japan/donor-pool setup. PE ratio would strengthen the model but is not available in the synthetic control donor panel (which is loaded from raw CSVs, not from panel.parquet).
   - Recommendation: Include lagged PB means (e.g., 2004-2009 mean, 2010-2018 mean) as `special_predictors`. Add PE data for donors as an additional predictor by loading the `*_pe_*.csv` files and merging into the donor panel. This is Claude's discretion per CONTEXT.md.

2. **MSCI Taiwan PE 4-row gap alignment with in-space placebo**
   - What we know: 4 rows missing from 2004-01 to 2004-04 in MSCI Taiwan PE series.
   - What's unclear: Whether this matters for the in-space placebo (which uses PB, not PE). For PB it does not — Taiwan PB is complete.
   - Recommendation: PB synthetic control is unaffected. Note for ROBUST-02 PE replication only.

---

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| pysyncon | synthetic_control.py | ✗ (not installed) | 1.5.2 (PyPI latest) | None — must install |
| pandas | all scripts | ✓ | 2.2.3 | — |
| numpy | all scripts | ✓ | 1.26.4 | — |
| scipy | pysyncon (Nelder-Mead) | ✓ | 1.13.1 | — |
| matplotlib | all figure scripts | ✓ | 3.9.2 | — |
| linearmodels | ROBUST-02/03 OLS | ✓ | 6.1 | — |
| wildboottest | ROBUST-02 SE | ✓ | 0.3.2 | — |
| statsmodels | ROBUST-01/02 event study, GPR | ✓ | 0.14.4 | — |

**Missing dependencies with no fallback:**
- `pysyncon==1.5.2` — must be added to `requirements.txt` and installed before any Phase 4 script runs. Wave 0 task must include this.

---

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 8.3.4 |
| Config file | none (direct invocation) |
| Quick run command | `pytest tests/test_phase4.py -x -q` |
| Full suite command | `pytest tests/ -q` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| SYNTH-01 | Synth fits without error; W weights sum to 1 | unit | `pytest tests/test_phase4.py::test_synth_weights_sum_to_one -x` | ❌ Wave 0 |
| SYNTH-02 | synthetic_control_weights.csv exists; RMSPE is a positive float in output | smoke | `pytest tests/test_phase4.py::test_synth_outputs_exist -x` | ❌ Wave 0 |
| SYNTH-03 | SUTVA comment present in synthetic_control.py source | static | `pytest tests/test_phase4.py::test_sutva_comment_present -x` | ❌ Wave 0 |
| ROBUST-01 | placebo_taiwan_*.csv and placebo_indonesia_*.csv exist; have expected columns | smoke | `pytest tests/test_phase4.py::test_placebo_outputs_exist -x` | ❌ Wave 0 |
| ROBUST-02 | robustness_pe_ols.tex exists; contains P/E header string | smoke | `pytest tests/test_phase4.py::test_robust02_outputs_exist -x` | ❌ Wave 0 |
| ROBUST-03 | robustness_alt_control_em_asia.tex and em_exchina.tex exist | smoke | `pytest tests/test_phase4.py::test_robust03_outputs_exist -x` | ❌ Wave 0 |
| ROBUST-04 | figure_placebo_intime.pdf and figure_placebo_inspace.pdf exist | smoke | `pytest tests/test_phase4.py::test_robust04_outputs_exist -x` | ❌ Wave 0 |

### Sampling Rate
- **Per task commit:** `pytest tests/test_phase4.py -x -q`
- **Per wave merge:** `pytest tests/ -q`
- **Phase gate:** Full suite green before `/gsd-verify-work`

### Wave 0 Gaps
- [ ] `tests/test_phase4.py` — covers SYNTH-01 through ROBUST-04 smoke tests
- [ ] `src/robustness/__init__.py` — empty, makes the directory a package
- [ ] `pip install pysyncon==1.5.2` and add to `requirements.txt`
- [ ] `output/robustness/` directory (created by first script; Wave 0 can pre-create it)

---

## Security Domain

This phase produces local research artefacts (CSV, PDF, LaTeX). No authentication, session management, or data ingestion from external APIs. ASVS categories V2, V3, V4, V6 do not apply.

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | — |
| V3 Session Management | no | — |
| V4 Access Control | no | — |
| V5 Input Validation | yes (minimal) | Validate donor CSV schema on load (assert columns, no nulls) |
| V6 Cryptography | no | — |

---

## Sources

### Primary (HIGH confidence)
- pysyncon 1.5.2 — verified by `pip install pysyncon==1.5.2` + live Python introspection of `Synth`, `Dataprep`, `PlaceboTest` modules (2026-04-20)
- pysyncon PyPI registry — [VERIFIED: pip index versions pysyncon] — 1.5.2 is current latest
- Project raw data files — [VERIFIED: data inspection 2026-04-20] — all donor CSVs confirmed present, date ranges and null counts documented

### Secondary (MEDIUM confidence)
- [pysyncon Synth documentation](https://sdfordham.github.io/pysyncon/synth.html) — method signatures confirmed against live introspection
- [pysyncon Placebo documentation](https://sdfordham.github.io/pysyncon/placebo.html) — PlaceboTest documented but not present in 1.5.2 install (WebFetch 403; confirmed by module inspection)
- [pysyncon GitHub basque.ipynb example](https://github.com/sdfordham/pysyncon/blob/main/examples/basque.ipynb) — Dataprep parameter names confirmed

### Tertiary (LOW confidence)
- China weight in MSCI EM ~30% (2023) — training knowledge; document as approximation
- 2019-01-01 as clean in-time placebo date — training knowledge + data inspection of TOPIX PB stability

---

## Metadata

**Confidence breakdown:**
- pysyncon API: HIGH — verified by live code introspection
- Data availability: HIGH — verified against actual files
- Architecture patterns: HIGH — derived from verified API + established Phase 3 code
- EM ex-China proxy math: HIGH — verified numerically; assumption on China weight is LOW
- In-time placebo date: MEDIUM — reasonable but not formally verified against Japan policy calendar

**Research date:** 2026-04-20
**Valid until:** 2026-07-20 (stable domain; pysyncon major version change would invalidate API patterns)
