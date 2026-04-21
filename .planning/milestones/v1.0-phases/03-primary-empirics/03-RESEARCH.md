# Phase 3: Primary Empirics - Research

**Researched:** 2026-04-17
**Domain:** Econometrics / Event Study / Panel OLS / Geopolitical Risk
**Confidence:** HIGH

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **D-01:** Pre-event estimation window: -36 months (3 years before each reform date)
- **D-02:** Event window shown in CAR figure: -12 to +24 months relative to event date
- **D-03:** "Abnormal" = KOSPI P/B minus TOPIX P/B spread; CAR = cumulative deviation of spread from pre-event trajectory
- **D-04:** Stacked design (Cengiz et al. 2019): stack three event-date cohorts, single regression with cohort × time-relative-to-event interactions; heteroskedasticity-robust SEs
- **D-05:** Estimator: `linearmodels.PanelOLS` (not `statsmodels.OLS`); two-way country + time fixed effects
- **D-06:** Reform dummies interacted with Japan indicator; coefficients in P/B points
- **D-07:** Wild-bootstrap clustered by country; 4 clusters means traditional cluster-SE unreliable; Rademacher or Mammen weights; 500–1000 iterations
- **D-08:** LaTeX regression table `output/tables/table2_ols.tex`; booktabs style, 2 decimal places; columns = baseline / + reform dummies / + reform × Japan interactions
- **D-09:** GPR data source: Caldara-Iacoviello GPR index, single downloadable XLS from matteoiacoviello.com; use GPRC_KOR series
- **D-10:** Escalation indicator: binary dummy = 1 if GPRC_KOR > 75th percentile of GPRC_KOR over 2004–2024; threshold stored as named constant
- **D-11:** OLS: `KOSPI P/B ~ GPR_escalation_dummy + time_FE + TOPIX P/B`; time FE absorb global macro; TOPIX P/B controls for developed-market sentiment
- **D-12:** Results written with partial-identification caveats
- **D-13:** One combined 3-panel CAR figure: `output/figures/figure2_event_study.pdf`
- **D-14:** Separate geopolitical figure: `output/figures/figure3_geo_risk.pdf`
- **D-15:** Each analysis module standalone; no cross-imports between analysis modules

### Claude's Discretion
- Wild-bootstrap iteration count (500 or 1000)
- Subplot layout for 3-panel event study figure (vertical stack vs. 1×3 horizontal)
- Whether geo regression table is standalone or folded into OLS table as additional column
- GPR data download filename and storage location within `data/raw/`
- Companion diagnostic figures (pre-trend tests, residual plots)

### Deferred Ideas (OUT OF SCOPE)
- Synthetic control (SYNTH-01 to SYNTH-03) — Phase 4
- Placebo / falsification tests (ROBUST-01 to ROBUST-04) — Phase 4
- Alternative metric (P/E) robustness — Phase 4
- Full channel decomposition (GEO-V2-01) — v2 requirements
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| EVNT-01 | Event study measuring cumulative abnormal valuation changes around each Japan reform date | Stacked regression design with cohort × event-time interactions; manual Python construction required — no mature library |
| EVNT-02 | Heteroskedastic-robust SEs; results presented separately per treatment date | `statsmodels` HC3 via `get_robustcov_results(cov_type="HC3")`; per-cohort subplots in figure |
| EVNT-03 | Stacked event study design (Cengiz et al. 2019 / Baker et al. 2022) | Build stacked dataset manually: three full-window cohorts, cohort × relative-time interactions, and explicit overlap annotations |
| EVNT-04 | CAR figures and coefficient tables output to `output/` | `matplotlib` 3-panel PDF; `pandas.to_latex()` or manual LaTeX string for coefficient table |
| OLS-01 | `linearmodels.PanelOLS` with two-way FE | `PanelOLS(..., entity_effects=True, time_effects=True)` — verified available at v6.1 |
| OLS-02 | Reform dummies × Japan indicator; interpret in P/B points | Interaction variable construction in pandas before passing to PanelOLS |
| OLS-03 | Wild-bootstrap clustered by country; LaTeX regression table | `wildboottest` 0.3.2 installed; requires FWL workaround (demean via PanelData.demean then pass to statsmodels OLS); `pandas.to_latex()` with booktabs |
| GEO-01 | NK escalation indicator from GPR index | GPRC_KOR series in `data_gpr_export.xls` — verified available, covers 1985–2026-03 |
| GEO-02 | Estimate KOSPI valuation response to escalation events | statsmodels OLS with time dummies + TOPIX P/B control |
| GEO-03 | Results with partial-identification caveats in paper | Script docstring + output `.tex` fragment with caveats |
</phase_requirements>

---

## Summary

Phase 3 implements three econometric analyses — stacked event study, panel OLS, and geopolitical risk sub-analysis — all reading exclusively from `data/processed/panel.parquet` plus one new external file (Caldara-Iacoviello GPR index). The panel contains 268 monthly observations per country for KOSPI, TOPIX, SP500, and MSCI_EM covering 2004-01 through 2026-04, all P/B values confirmed present with no gaps in the four-country balanced panel.

The stacked event study must be constructed entirely from scratch in Python — no mature library implements the Cengiz et al. (2019) stacked design for valuation spreads. The key algorithmic steps are: (1) build a cohort dataframe for each of the three Japan reform dates by preserving the required [-36, +24] months window around the event, (2) flag rows whose calendar months also fall inside another reform event's window rather than dropping them, because dropping the 2014/2015 overlap would destroy the locked D-01/D-02 windows, (3) stack the three cohort dataframes with a cohort identifier, (4) regress the KOSPI-TOPIX spread on cohort × relative-time indicators using statsmodels OLS with HC3 standard errors, and (5) accumulate period coefficients into a CAR series.

The panel OLS uses `linearmodels.PanelOLS` (v6.1, already installed) for point estimation but wild-bootstrap standard errors for inference — a necessary correction with only four country clusters. The installed `wildboottest` 0.3.2 accepts statsmodels OLS objects only, so the implementation must use the Frisch-Waugh-Lovell (FWL) theorem: demean Y and X via `PanelData.demean(group="both")`, then fit a statsmodels OLS on the demeaned data, then pass that to `wildboottest`. The GPR data is a single Excel file (`data_gpr_export.xls`) downloadable from `matteoiacoviello.com/gpr_files/data_gpr_export.xls`; the `GPRC_KOR` column (index 48) is confirmed present covering 1985–2026-03 with monthly frequency.

**Primary recommendation:** Build three standalone scripts (`src/analysis/event_study.py`, `src/analysis/panel_ols.py`, `src/analysis/geo_risk.py`) following the `figure1.py` pattern; the stacked event study is the highest-complexity piece and should be waved first.

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Data loading and preprocessing | Script layer | — | All three scripts load `panel.parquet` independently; no shared data module |
| Stacked event study construction | Script layer (event_study.py) | — | Manual cohort stacking and regression; all logic self-contained |
| Panel OLS estimation | Script layer (panel_ols.py) | linearmodels API | Two-way FE demeaning delegated to PanelData; regression via statsmodels OLS for wildboottest compat |
| Wild-bootstrap inference | Script layer | wildboottest library | FWL workaround required; documented in script comments |
| GPR data acquisition | Data layer (data/raw/) | Script layer | XLS downloaded manually once; loaded by geo_risk.py |
| GPR escalation indicator | Script layer (geo_risk.py) | — | 75th-percentile threshold computed from data, stored as named constant |
| Output: figures | Script layer | matplotlib | PDF export via fig.savefig; publication-plain style matching Phase 2 |
| Output: LaTeX tables | Script layer | pandas.to_latex / manual | Booktabs style; \input{} by Phase 5 paper assembly |

---

## Standard Stack

### Core (all already pinned in requirements.txt)
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| pandas | 2.2.3 | Data wrangling, panel construction, LaTeX export | Project convention |
| numpy | 1.26.4 | Numerical arrays, FWL demeaning | Project convention |
| statsmodels | 0.14.4 | OLS for event study + FWL step for wild bootstrap | Project convention; wildboottest requires statsmodels OLS |
| linearmodels | 6.1 | PanelOLS with two-way FE for point estimates | Locked decision D-05; already installed [VERIFIED: pip show] |
| wildboottest | 0.3.2 | Wild cluster bootstrap p-values | Locked decision D-07; installed [VERIFIED: pip show, __version__=0.3.2] |
| matplotlib | 3.9.2 | Figure output (CAR plots, GPR overlay) | Project convention |
| seaborn | 0.13.2 | Figure styling (whitegrid theme) | Project convention |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| xlrd | 2.0.1 | Read .xls (old Excel binary format) | Loading `data_gpr_export.xls` — confirmed working [VERIFIED: local test] |
| pyarrow | 15.0.2 | Read panel.parquet | Already in use across project |

### No New Dependencies Required
All required libraries are already installed and pinned. Do not add any new packages to `requirements.txt` for this phase.

**Version verification:** [VERIFIED: pip show / python -c import] against installed environment — linearmodels 6.1, wildboottest 0.3.2, xlrd 2.0.1 all confirmed.

---

## Architecture Patterns

### System Architecture Diagram

```
data/processed/panel.parquet  ──┬──► event_study.py ──► figure2_event_study.pdf
                                │                    ──► table_event_study_coefs.tex
                                │
                                ├──► panel_ols.py ──► table2_ols.tex
                                │
                                └──► geo_risk.py ──► figure3_geo_risk.pdf
                                                 ──► (optional) table3_geo.tex

data/raw/data_gpr_export.xls ──────────────────────► geo_risk.py

config.py (EVENT_DATES) ──────── imported by event_study.py
```

Each script is an independent entry point. No script imports from another script. `config.py` is the only shared import.

### Recommended Project Structure

```
src/
├── analysis/             # NEW: Phase 3 analysis scripts
│   ├── event_study.py    # Stacked event study + CAR figure (EVNT-01..04)
│   ├── panel_ols.py      # Two-way FE OLS + wild-bootstrap table (OLS-01..03)
│   └── geo_risk.py       # GPR escalation indicator + KOSPI response (GEO-01..03)
├── data/
│   └── build_panel.py    # Phase 1 (no changes)
└── descriptive/
    ├── figure1.py        # Phase 2 (no changes)
    └── discount_stats.py # Phase 2 (no changes)
data/
└── raw/
    └── data_gpr_export.xls   # NEW: download from matteoiacoviello.com/gpr_files/
output/
├── figures/
│   ├── figure2_event_study.pdf   # NEW
│   └── figure3_geo_risk.pdf      # NEW
└── tables/
    ├── table2_ols.tex             # NEW
    └── table_event_study_coefs.tex  # NEW (coefficient table for EVNT-04)
```

### Pattern 1: Script Entry-Point (Established Project Convention)

Every analysis script follows the `figure1.py` / `discount_stats.py` pattern:

```python
# Source: src/descriptive/figure1.py (project-established pattern)
import logging, sys
from pathlib import Path
import matplotlib
matplotlib.use("Agg")

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import config

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s", stream=sys.stdout)

def main() -> None:
    df = pd.read_parquet(config.PROCESSED_DIR / "panel.parquet")
    # ... analysis ...
    output_path = config.OUTPUT_DIR / "figures" / "figure2_event_study.pdf"
    output_path.parent.mkdir(parents=True, exist_ok=True)

if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
```

### Pattern 2: Stacked Event Study Construction (Cengiz et al. 2019)

No Python library implements this design. Manual construction required.

```python
# Source: [ASSUMED] — standard implementation of Cengiz et al. 2019 stacked design
# Reference: Cengiz et al. (2019), "The Effect of Minimum Wages on Low-Wage Jobs"
# The stacked design creates one cohort per event date and preserves
# project-locked windows while flagging overlapping reform exposure.

import pandas as pd
import numpy as np
import statsmodels.api as sm
import config

def build_stacked_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """
    Stack three event-date cohorts.
    For each event date:
      - Restrict to [-36, +24] months relative window
      - Preserve the full [-36, +24] window even if months overlap another
        reform event window; add overlap flags and document the limitation.
      - Add columns: cohort_id, event_rel_time (months since event)
    """
    spread = (
        df.pivot(index="date", columns="country", values="pb")
        .assign(spread=lambda x: x["KOSPI"] - x["TOPIX"])
        [["spread"]]
    )
    cohorts = []
    for event_date in config.EVENT_DATES:
        # Relative time in months
        cohort = spread.copy()
        cohort["event_rel_time"] = (
            (cohort.index.year - event_date.year) * 12
            + (cohort.index.month - event_date.month)
        )
        cohort = cohort[
            (cohort["event_rel_time"] >= -36) &
            (cohort["event_rel_time"] <= 24)
        ]
        # Cengiz et al. (2019) stacked cohorts; preserve locked D-01/D-02
        # windows and flag, rather than drop, overlapping reform exposure.
        cohort["overlaps_other_event_window"] = False
        for other_date in config.EVENT_DATES:
            if other_date == event_date:
                continue
            other_rel = (
                (cohort.index.year - other_date.year) * 12
                + (cohort.index.month - other_date.month)
            )
            cohort["overlaps_other_event_window"] |= (
                (other_rel >= -36) & (other_rel <= 24)
            )
        cohort["cohort"] = event_date.strftime("%Y-%m")
        cohorts.append(cohort.reset_index())
    return pd.concat(cohorts, ignore_index=True)


def estimate_car(stacked: pd.DataFrame) -> pd.DataFrame:
    """
    Regress spread on cohort × event_rel_time dummies with HC3 SEs.
    Extract CAR per cohort as cumulative sum of relative-time coefficients.
    """
    stacked = stacked.copy()
    # Create relative-time dummies (omit t=-1 as base period)
    stacked["cohort_x_time"] = stacked["cohort"] + "_t" + stacked["event_rel_time"].astype(str)
    dummies = pd.get_dummies(stacked["cohort_x_time"], drop_first=False)
    # Drop base period (t=-1) columns for identification
    base_cols = [c for c in dummies.columns if c.endswith("_t-1")]
    dummies = dummies.drop(columns=base_cols)
    X = sm.add_constant(dummies.astype(float))
    model = sm.OLS(stacked["spread"].values, X).fit()
    hc3 = model.get_robustcov_results(cov_type="HC3")
    return hc3
```

### Pattern 3: PanelOLS + FWL Wild-Bootstrap Workaround

`wildboottest` 0.3.2 accepts only `statsmodels.regression.linear_model.OLS` — NOT `linearmodels.PanelOLS`. Use the FWL theorem to demean data first.

```python
# Source: [VERIFIED: linearmodels PanelData.demean() API, wildboottest signature]
# FWL workaround: demean Y and X via linearmodels, then run wildboottest on
# the demeaned statsmodels OLS.

import pandas as pd
import numpy as np
import statsmodels.api as sm
from linearmodels import PanelOLS
from linearmodels.panel.data import PanelData
from wildboottest.wildboottest import wildboottest

def fit_panel_with_wildbootstrap(
    panel_df: pd.DataFrame,  # Must have MultiIndex (country, date)
    y_col: str,
    x_cols: list[str],
    B: int = 999,
    seed: int = 42,
):
    """
    Step 1: Fit PanelOLS for point estimates.
    Step 2: Demean Y and X via FWL theorem for wildboottest compatibility.
    Step 3: Run wildboottest on demeaned statsmodels OLS.
    Returns: PanelOLS result (point estimates), wildboottest DataFrame (p-values).
    """
    # Step 1: PanelOLS for point estimates
    mod = PanelOLS(panel_df[y_col], panel_df[x_cols],
                   entity_effects=True, time_effects=True)
    res_panel = mod.fit(cov_type="robust")

    # Step 2: FWL demeaning (both entity and time)
    pd_y = PanelData(panel_df[[y_col]])
    pd_x = PanelData(panel_df[x_cols])
    y_dm = pd_y.demean(group="both", return_panel=False).squeeze()
    x_dm = pd_x.demean(group="both", return_panel=False)

    # Step 3: statsmodels OLS on demeaned data (no constant — already absorbed)
    sm_mod = sm.OLS(y_dm, x_dm)
    cluster_series = panel_df.index.get_level_values("country")

    # wildboottest: Rademacher weights, 11-bootstrap
    wb_results = wildboottest(
        sm_mod, B=B,
        cluster=pd.Series(cluster_series, name="country"),
        weights_type="rademacher",
        bootstrap_type="11",
        seed=str(seed),
        show=False,
    )
    return res_panel, wb_results
```

### Pattern 4: linearmodels PanelData Setup (MultiIndex)

```python
# Source: [VERIFIED: linearmodels 6.1 PanelOLS documentation]
# linearmodels requires a (entity, time) MultiIndex on the DataFrame.

df = pd.read_parquet(config.PROCESSED_DIR / "panel.parquet")
panel = df.set_index(["country", "date"])  # entity=country, time=date
# Then: PanelOLS(panel["pb"], panel[["japan_dummy", "reform_x_japan"]], ...)
```

### Pattern 5: GPR Data Loading

```python
# Source: [VERIFIED: local test — pd.read_excel on data_gpr_export.xls]
# pandas auto-parses the Excel date serial in the 'month' column to datetime64.

import pandas as pd
import config

def load_gpr_korea(study_start: str = "2004-01-01",
                   study_end: str = "2024-12-31") -> pd.DataFrame:
    gpr_path = config.RAW_DIR / "data_gpr_export.xls"
    gpr = pd.read_excel(gpr_path, usecols=["month", "GPRC_KOR"])
    gpr = gpr.dropna(subset=["GPRC_KOR"]).rename(columns={"month": "date"})
    gpr["date"] = pd.to_datetime(gpr["date"])
    # Restrict to study period for threshold computation
    study = gpr[(gpr["date"] >= study_start) & (gpr["date"] <= study_end)].copy()
    # 75th-percentile threshold — stored as named constant (D-10)
    GPR_KOREA_ESCALATION_THRESHOLD = study["GPRC_KOR"].quantile(0.75)
    study["gpr_escalation"] = (study["GPRC_KOR"] > GPR_KOREA_ESCALATION_THRESHOLD).astype(int)
    return study, GPR_KOREA_ESCALATION_THRESHOLD
```

### Pattern 6: LaTeX Table Output (Booktabs, 2 decimal places)

```python
# Source: [VERIFIED: pandas 2.2.3 to_latex() API; project convention from Phase 2]
# pandas.to_latex() with buf parameter writes directly to file.

df_results.to_latex(
    buf=output_path,
    float_format="%.2f",
    escape=False,           # allow LaTeX commands in column headers
    column_format="lcccc",
    hrules=True,            # booktabs \toprule / \midrule / \bottomrule
    label="tab:ols",
    caption="Panel OLS Results: Korea Discount and Japan Reform Events",
)
```

### Anti-Patterns to Avoid

- **Importing panel.parquet in multiple scripts via a shared helper:** Each script must load `panel.parquet` independently (D-15 — no cross-module imports).
- **Hardcoding event dates:** Always import `config.EVENT_DATES` — never write `datetime.date(2014, 2, 1)` in analysis scripts.
- **Hardcoding the GPR 75th-percentile threshold as a number:** Compute from data and assign to a named constant (e.g., `GPR_KOREA_ESCALATION_THRESHOLD = study["GPRC_KOR"].quantile(0.75)`).
- **Running wildboottest directly on linearmodels PanelOLS output:** Not supported. Must use FWL workaround (demean first, then statsmodels OLS).
- **Using traditional cluster-robust SEs for OLS with 4 clusters:** With N=4 country clusters, conventional cluster SEs are severely undersized. Wild bootstrap is the correct correction (D-07).
- **Silently pooling overlapping event-date cohorts:** The 2014 and 2015 reform windows overlap. Do not drop overlapping months if doing so would violate the locked -36 pre-period and -12..+24 plotted window; preserve the required windows, add overlap flags, and document overlap/contamination as a limitation in the event-study output and paper text.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Two-way FE demeaning | Custom group-mean subtraction loops | `PanelData.demean(group="both")` from linearmodels | Handles unbalanced panels, edge cases; already tested |
| HC3 heteroskedastic SEs | Manual sandwich estimator | `sm.OLS.fit().get_robustcov_results(cov_type="HC3")` | Verified API in statsmodels 0.14 |
| Wild cluster bootstrap | Manual Rademacher weight loop | `wildboottest.wildboottest.wildboottest()` | Library handles small-sample corrections, parallelization |
| LaTeX table formatting | String interpolation | `pandas.to_latex(hrules=True, float_format="%.2f")` | Booktabs output with one call; project convention |
| Excel date parsing | Manual serial-number conversion | `pd.read_excel()` | Confirmed: pandas auto-converts GPR XLS date serials to datetime64 |

**Key insight:** The stacked event study regression itself has no mature Python library — that genuinely must be hand-rolled. Everything else (FE demeaning, robust SEs, bootstrap, LaTeX output) has a production-quality library implementation.

---

## Common Pitfalls

### Pitfall 1: Contaminated Event-Study Cohorts
**What goes wrong:** The three reform dates (2014-02, 2015-06, 2023-03) have overlapping estimation windows. The 2015 event falls within the [-36, +24] window of the 2014 event (15 months post-event). Stacking without exclusion contaminates the 2014 cohort with the 2015 treatment.
**Why it happens:** Naively filtering by `event_rel_time` without checking the other event dates.
**How to avoid:** For this project, preserve the full D-01/D-02 windows, add an `overlaps_other_event_window` flag and `overlap_event_labels` annotation, and document the 2014/2015 overlap as a limitation. Do not use a clean-cohort exclusion that removes required pre-period or plotted-window rows.
**Warning signs:** Any cohort has fewer than 36 pre-event rows for t=-36..-1, or `event_study_car.csv` lacks all plotted relative months -12..+24 for every cohort.

### Pitfall 2: wildboottest Incompatibility with linearmodels Output
**What goes wrong:** Passing a `linearmodels.PanelEffectsResults` object to `wildboottest()` raises a TypeError — the function signature expects `statsmodels.regression.linear_model.OLS`, not a linearmodels result.
**Why it happens:** `wildboottest` 0.3.2 was written for statsmodels and has no linearmodels integration.
**How to avoid:** Use the FWL workaround: `PanelData.demean(group="both")` → statsmodels OLS on demeaned arrays → `wildboottest()`.
**Warning signs:** `AttributeError: 'PanelEffectsResults' object has no attribute 'model'` or similar.

### Pitfall 3: Panel MultiIndex Ordering for linearmodels
**What goes wrong:** `PanelOLS` requires a DataFrame with a `(entity, time)` MultiIndex where entity is the OUTER level and time is the INNER level. Swapping the order raises a `PanelError`.
**Why it happens:** `df.set_index(["date", "country"])` creates (time, entity) ordering — the wrong way.
**How to avoid:** Always `df.set_index(["country", "date"])` — entity first, time second.
**Warning signs:** `linearmodels.panel.data.PanelError: Inputs must have a MultiIndex...`

### Pitfall 4: Base Period Selection in Event-Study Dummies
**What goes wrong:** Omitting t=0 (event month itself) instead of t=-1 as the base period. Alternatively, including a constant alongside a full set of time dummies creates perfect multicollinearity.
**Why it happens:** Default `pd.get_dummies(drop_first=True)` drops the lexicographically first category, not the economically correct base period.
**How to avoid:** Manually drop the t=-1 dummy columns after creating the full dummy matrix; omit any constant (the omitted dummy serves as the intercept group).
**Warning signs:** `PerfectSeparationWarning` or NaN coefficients for some time periods.

### Pitfall 5: GPR Threshold Computed on Wrong Date Range
**What goes wrong:** Computing the 75th percentile on the full GPR series (1985–2026) instead of the study period (2004–2024) inflates the threshold (Cold War-era NK escalations in the 1990s push up the distribution), reducing the number of escalation months flagged.
**Why it happens:** Loading the full GPR file and computing `quantile(0.75)` before date-filtering.
**How to avoid:** Always filter to the study period first; D-10 specifies "75th percentile of GPR-Korea over the full study period (2004–2024)."
**Warning signs:** Fewer than ~60 months flagged as escalation (roughly 25% of 240 months expected).

### Pitfall 6: xlrd Cannot Read .xlsx; openpyxl Cannot Read .xls
**What goes wrong:** `pd.read_excel("data_gpr_export.xls")` fails with `XLRDError: Excel xlsx file; not supported` if pandas defaults to openpyxl for `.xls` files.
**Why it happens:** xlrd 2.0+ dropped `.xlsx` support; openpyxl does not support old binary `.xls` format.
**How to avoid:** Explicitly pass `engine="xlrd"` to `pd.read_excel()` for `.xls` files.
**Warning signs:** `ValueError: Excel file format cannot be determined` or `XLRDError`.

---

## Code Examples

### Verified: linearmodels PanelOLS fit with clustered SE

```python
# Source: [VERIFIED: linearmodels 6.1 PanelOLS.fit() docstring — confirmed locally]
from linearmodels import PanelOLS

panel = df.set_index(["country", "date"])
mod = PanelOLS(panel["pb"], panel[["reform_x_japan", "japan"]],
               entity_effects=True, time_effects=True)
# For point estimates: clustered by entity
res = mod.fit(cov_type="clustered", cluster_entity=True)
print(res.summary)
```

### Verified: GPR Data Loading

```python
# Source: [VERIFIED: local test against data_gpr_export.xls downloaded 2026-04-17]
# File: matteoiacoviello.com/gpr_files/data_gpr_export.xls
# Columns confirmed: 'month' (datetime64 after pd.read_excel), 'GPRC_KOR' (float64)
# Date range: 1985-01 to 2026-03 (495 non-null rows for GPRC_KOR)

gpr = pd.read_excel(config.RAW_DIR / "data_gpr_export.xls",
                    usecols=["month", "GPRC_KOR"],
                    engine="xlrd")
gpr = gpr.dropna(subset=["GPRC_KOR"]).rename(columns={"month": "date"})
gpr["date"] = pd.to_datetime(gpr["date"])
```

### Verified: wildboottest function signature

```python
# Source: [VERIFIED: wildboottest 0.3.2 installed, inspect.signature confirmed locally]
# Takes: statsmodels OLS object (NOT linearmodels result)
# Returns: pd.DataFrame with bootstrap p-values per parameter

from wildboottest.wildboottest import wildboottest
wb_df = wildboottest(
    sm_model,           # statsmodels.regression.linear_model.OLS (fitted or unfitted)
    B=999,              # bootstrap iterations
    cluster=cluster_series,   # pd.Series of cluster labels
    param=None,         # None = test all params
    weights_type="rademacher",  # or "mammen"
    bootstrap_type="11",
    seed="42",
    show=False,
)
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Single pooled pre-post regression | Stacked cohort design (Cengiz 2019) | ~2019–2022 | Separates event-time paths by cohort; this project additionally flags overlapping 2014/2015 exposure because full-window coverage is locked |
| `statsmodels.OLS` for panel FE | `linearmodels.PanelOLS` | ~2017 | Proper two-way FE with degree-of-freedom adjustments |
| Conventional cluster SEs (G=4) | Wild cluster bootstrap (Cameron-Gelbach-Miller 2008) | ~2008 | Corrects severe underrejection with few clusters |
| Manual booktabs LaTeX | `pandas.to_latex(hrules=True)` | pandas 1.3+ | One-call booktabs output |

**Deprecated/outdated:**
- `statsmodels.OLS` for panel FE: produces biased SEs without explicit FE dummies; use `linearmodels.PanelOLS` for point estimates.
- xlrd 2.0+ for `.xlsx`: xlrd dropped xlsx support; use openpyxl for xlsx, xlrd for xls. The GPR file is `.xls` so xlrd is correct here.

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | Base period t=-1 is the correct omitted category for event-study identification | Architecture Patterns / Pattern 2 | Wrong base normalizes CAR to wrong reference point; standard convention but should verify against Cengiz et al. paper |
| A2 | FWL demeaning via `PanelData.demean(group="both")` produces numerically equivalent demeaned residuals to within-estimator FE removal | Architecture Patterns / Pattern 3 | If not equivalent, wildboottest operates on wrong residuals; FWL theorem guarantees equivalence but linearmodels internal implementation should be spot-checked |
| A3 | 999 bootstrap iterations is the publication-ready default for 4-cluster wild bootstrap | Discretion / Open Questions (RESOLVED) | Higher runtime than 500 draws, but avoids noisier p-values and matches the resolved Phase 3 plan |

---

## Open Questions (RESOLVED)

1. **2014 and 2015 event cohort overlap**
   - What we know: 2015-06 is approximately +16 months after 2014-02. The 2014 cohort extends to +24, so the 2015 event falls inside the 2014 cohort's event window.
   - RESOLVED: Do not apply a clean-cohort exclusion that drops rows inside another event's [-36, +24] window. That exclusion would remove required D-01 pre-trend rows for the 2015 cohort and required D-02 plotted rows for the 2014 cohort. Instead, preserve all three cohorts' -36..+24 windows, add row-level overlap annotations, and document the 2014/2015 overlap as a contamination limitation in the script/table notes and Phase 5 paper text.

2. **Bootstrap iteration count (discretion)**
   - What we know: 500 is fast; 999 is standard for publication; 1000 is also acceptable. With 4 clusters, even 500 converges well.
   - RESOLVED: Use 999 Rademacher wild-bootstrap draws, with `BOOTSTRAP_ITERATIONS = 999` and `BOOTSTRAP_SEED = 42`, because 999 is the standard publication convention and avoids tie-breaking in p-value computation.

3. **Standalone geo regression table vs. additional OLS column (discretion)**
   - What we know: D-08 specifies `table2_ols.tex` with columns = baseline / + reform dummies / + reform × Japan. Adding geo as a fourth column would make the table wider.
   - RESOLVED: Keep geo results as a standalone LaTeX fragment (`table3_geo_risk.tex`) — the geo regression has a different LHS (KOSPI-only, not panel) and folding it into the OLS table conflates two distinct estimands.

---

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python | All scripts | Yes | 3.12 | — |
| pandas | All scripts | Yes | 2.2.3 | — |
| linearmodels | panel_ols.py | Yes | 6.1 | — |
| wildboottest | panel_ols.py | Yes | 0.3.2 | — |
| statsmodels | event_study.py, geo_risk.py | Yes | 0.14.4 | — |
| matplotlib | event_study.py, geo_risk.py | Yes | 3.9.2 | — |
| xlrd | geo_risk.py | Yes | 2.0.1 | — |
| data/processed/panel.parquet | All scripts | Yes | 268 rows × 4 countries | — |
| data/raw/data_gpr_export.xls | geo_risk.py | No (not yet downloaded) | — | Must be downloaded before geo_risk.py can run |

**Missing dependencies with no fallback:**
- `data/raw/data_gpr_export.xls` — must be downloaded from `https://www.matteoiacoviello.com/gpr_files/data_gpr_export.xls` and placed in `data/raw/`. Wave 0 of geo_risk plan should include this download step and a MANIFEST.md entry.

---

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 8.3.4 |
| Config file | none (implicit discovery) |
| Quick run command | `pytest tests/test_phase3.py -x -q` |
| Full suite command | `pytest tests/ -x -q` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|--------------|
| EVNT-01 | `output/figures/figure2_event_study.pdf` exists and is non-empty | smoke | `pytest tests/test_phase3.py::test_figure2_exists -x` | Wave 0 |
| EVNT-02 | CAR coefficient table exists; HC3 SEs present (non-zero) | smoke | `pytest tests/test_phase3.py::test_event_study_coefs -x` | Wave 0 |
| EVNT-03 | Stacked dataset has 3 distinct cohort identifiers, 36 pre-event observations per cohort, and overlap annotations for 2014/2015 windows | unit | `pytest tests/test_phase3.py::test_three_cohorts -x` | Wave 0 |
| EVNT-04 | CAR output covers every plotted month -12..+24 for all three cohorts before Figure 2 is drawn | smoke | `pytest tests/test_phase3.py::test_figure2_panels -x` | Wave 0 |
| OLS-01 | `output/tables/table2_ols.tex` exists | smoke | `pytest tests/test_phase3.py::test_table2_exists -x` | Wave 0 |
| OLS-02 | table2_ols.tex contains reform interaction coefficients | content | `pytest tests/test_phase3.py::test_table2_reform_dummies -x` | Wave 0 |
| OLS-03 | table2_ols.tex contains `\toprule` (booktabs) | content | `pytest tests/test_phase3.py::test_table2_booktabs -x` | Wave 0 |
| GEO-01 | GPR escalation indicator has ~25% months flagged (study period) | unit | `pytest tests/test_phase3.py::test_gpr_threshold -x` | Wave 0 |
| GEO-02 | `output/figures/figure3_geo_risk.pdf` exists and is non-empty | smoke | `pytest tests/test_phase3.py::test_figure3_exists -x` | Wave 0 |
| GEO-03 | GPR results file contains "partial identification" or "caveat" text | content | `pytest tests/test_phase3.py::test_geo_caveats -x` | Wave 0 |

### Sampling Rate
- **Per task commit:** `pytest tests/test_phase3.py -x -q`
- **Per wave merge:** `pytest tests/ -x -q`
- **Phase gate:** Full suite green before `/gsd-verify-work`

### Wave 0 Gaps
- [ ] `tests/test_phase3.py` — covers EVNT-01 through GEO-03
- [ ] `src/analysis/__init__.py` — empty init for the new package
- [ ] Download `data/raw/data_gpr_export.xls` from `https://www.matteoiacoviello.com/gpr_files/data_gpr_export.xls`
- [ ] Add MANIFEST.md entry for `data_gpr_export.xls`

---

## Sources

### Primary (HIGH confidence)
- `linearmodels.PanelOLS` — verified via `python -c "from linearmodels import PanelOLS; import inspect; inspect.getsource(PanelOLS.fit)"` on v6.1 installed in project environment
- `wildboottest.wildboottest.wildboottest` — verified function signature via `inspect.signature`; confirmed takes statsmodels OLS, returns pd.DataFrame
- `PanelData.demean()` — verified API via `inspect.getsource(PanelData.demean)` on linearmodels 6.1
- `data_gpr_export.xls` — verified download from `https://www.matteoiacoviello.com/gpr_files/data_gpr_export.xls`; confirmed `GPRC_KOR` column at index 48, monthly dates parsed by `pd.read_excel`, date range 1985-01 to 2026-03
- `data/processed/panel.parquet` — verified schema (date, country, pb, pe); 268 rows × 4 countries, no gaps

### Secondary (MEDIUM confidence)
- Cengiz et al. (2019) stacked event study design — described in CONTEXT.md D-04 and REQUIREMENTS.md EVNT-03; implementation pattern [ASSUMED] based on published methodology
- Cameron-Gelbach-Miller (2008) wild cluster bootstrap for few clusters — [ASSUMED] standard econometrics reference; wildboottest library implementation verified

### Tertiary (LOW confidence)
- None — all critical implementation claims verified against live codebase and installed libraries

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — all packages verified via pip/import against installed environment
- GPR data: HIGH — file downloaded, column structure confirmed, date range confirmed
- Architecture: HIGH — established project patterns verified from figure1.py, discount_stats.py
- wildboottest/FWL workaround: HIGH — function signature verified; FWL equivalence is a theorem
- Stacked event study construction: MEDIUM — no library to verify against; implementation pattern based on published methodology (Cengiz et al. 2019)
- Pitfalls: HIGH — contamination pitfall verified by counting months; xlrd/openpyxl pitfall verified by testing

**Research date:** 2026-04-17
**Valid until:** 2026-07-17 (stable libraries; GPR data updates monthly but study period is fixed)
