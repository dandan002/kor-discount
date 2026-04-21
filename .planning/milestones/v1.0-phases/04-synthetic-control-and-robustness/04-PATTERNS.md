# Phase 4: Synthetic Control and Robustness — Pattern Map

**Mapped:** 2026-04-20
**Files analyzed:** 7 new/modified files
**Analogs found:** 6 / 7 (requirements.txt has no analog; it is a direct edit)

---

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `src/robustness/synthetic_control.py` | analysis script | transform + batch | `src/analysis/event_study.py` | role-match (same standalone script structure, figure-save pattern) |
| `src/robustness/robustness_pe.py` | analysis script | CRUD + transform | `src/analysis/panel_ols.py`, `src/analysis/event_study.py`, `src/analysis/geo_risk.py` | role-match (column-swap clone of Phase 3 trio) |
| `src/robustness/robustness_alt_control.py` | analysis script | CRUD + transform | `src/analysis/panel_ols.py` | role-match (same OLS structure, different control group) |
| `src/robustness/robustness_placebo.py` | analysis script | batch + transform | `src/analysis/event_study.py` | role-match (same stacked event-study design, different treated unit) |
| `src/robustness/__init__.py` | package init | — | `src/analysis/__init__.py` | exact (empty one-liner) |
| `tests/test_phase4.py` | test | request-response | `tests/test_phase3.py` | exact (same pytest structure, same project-root injection, same smoke-test pattern) |
| `requirements.txt` | config | — | `requirements.txt` (self) | direct edit — append one line |

---

## Pattern Assignments

### `src/robustness/synthetic_control.py` (analysis script, transform + batch)

**Primary analog:** `src/analysis/event_study.py`
**Secondary analog:** `src/analysis/geo_risk.py` (figure-save pattern)

#### Module docstring pattern (lines 1-7 of event_study.py):
```python
"""
synthetic_control.py - ADH (2010) synthetic control for the 2023 TSE P/B reform.

Estimates a synthetic Japan using pysyncon and the donor pool (STOXX600, FTSE100,
MSCI_HK, MSCI_TAIWAN, SP500). Runs in-time and in-space placebo tests (ROBUST-04).
Writes all outputs to output/robustness/ and output/figures/.
"""
```

#### Imports + PROJECT_ROOT pattern (lines 1-25 of event_study.py):
```python
import logging
import math
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # headless backend - must come before pyplot import
import matplotlib.pyplot as plt
import pandas as pd
from pysyncon import Dataprep, Synth

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import config
```
Note: `parents[2]` is correct for `src/robustness/synthetic_control.py` (two levels up: robustness → src → project root).

#### Logging setup pattern (lines 43-47 of event_study.py):
```python
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
    stream=sys.stdout,
)
```
Place at module level, after imports. Use `logging.info(...)` (not `logging.getLogger`) inside functions — consistent with all Phase 3 scripts.

#### Output directory creation pattern (lines 317-318 of event_study.py):
```python
tables_dir = config.OUTPUT_DIR / "tables"
tables_dir.mkdir(parents=True, exist_ok=True)
```
Adapt for robustness:
```python
ROBUSTNESS_DIR = config.OUTPUT_DIR / "robustness"
FIGURES_DIR = config.OUTPUT_DIR / "figures"

# Inside main():
ROBUSTNESS_DIR.mkdir(parents=True, exist_ok=True)
FIGURES_DIR.mkdir(parents=True, exist_ok=True)
```

#### Figure save pattern (lines 297-307 of event_study.py):
```python
output_path = config.OUTPUT_DIR / "figures" / "figure2_event_study.pdf"
output_path.parent.mkdir(parents=True, exist_ok=True)
fig.savefig(
    output_path,
    dpi=300,
    bbox_inches="tight",
    format="pdf",
    metadata={"CreationDate": None, "ModDate": None},
)
plt.close(fig)
logging.info("Saved %s", output_path)
```
Use `metadata={"CreationDate": None, "ModDate": None}` for reproducible PDF output. Always call `plt.close(fig)` immediately after `savefig`.

#### CRITICAL: Gap plot workaround — do NOT call `synth.gaps_plot()`:
```python
# gaps_plot() calls plt.show() internally and cannot save to file.
# Use _gaps() to get the Series and build the figure manually.

all_period = pd.date_range(start="2004-01-01", end="2026-04-01", freq="MS")
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
ax.set_ylabel("P/B gap (Japan - Synthetic Japan)")
ax.set_title(f"Synthetic Control Gap — Pre-treatment RMSPE: {rmspe:.4f}")
ax.legend()
fig.savefig(FIGURES_DIR / "figure_synth_gap.pdf", dpi=300, bbox_inches="tight",
            format="pdf", metadata={"CreationDate": None, "ModDate": None})
plt.close(fig)
```

#### Weights + RMSPE extraction and CSV save:
```python
# RMSPE: pysyncon uses mspe() (mean squared), not rmspe(). Compute manually.
rmspe = math.sqrt(synth.mspe())        # float
weights = synth.weights(round=4)       # pd.Series: index=donor_name, values=weight

weights_df = weights.reset_index()
weights_df.columns = ["donor", "weight"]
weights_df["pre_rmspe"] = rmspe
weights_df.to_csv(ROBUSTNESS_DIR / "synthetic_control_weights.csv", index=False)
logging.info("Weights saved. RMSPE = %.4f", rmspe)
if rmspe > 0.15:
    logging.warning("RMSPE %.4f > 0.15 threshold — interpret with caution", rmspe)
```

#### SUTVA comment pattern (must appear as a block comment in the source):
```python
# SUTVA JUSTIFICATION (D-07):
# Donor pool: STOXX600, FTSE100, MSCI_HK, MSCI_TAIWAN, SP500.
# Korea (KOSPI) is excluded to avoid conflating the estimand with the primary
# comparison market (D-05). India and Indonesia are excluded due to high-growth
# P/B premium; they are used in ROBUST-01 placebo tests (D-06).
# STOXX600/FTSE100 governance reforms in this period did not involve TSE-style
# P/B mandates. HSI and MSCI Taiwan are Hong Kong and Taiwan markets with no
# equivalent reform event in 2023. The 19-year pre-treatment window (2004-2023)
# averages out global ESG/governance trends common to all markets.
```

#### Main + `if __name__ == "__main__"` guard pattern (lines 310-335 of event_study.py):
```python
def main() -> None:
    """Run synthetic control and write all Phase 4 outputs."""
    ROBUSTNESS_DIR.mkdir(parents=True, exist_ok=True)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    panel = load_donor_panel()
    synth, dataprep = run_synth(panel)
    # ... save weights, plot gap, run placebos ...

if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
```

#### Donor panel loading pattern (unique to Phase 4 — no direct analog):
```python
# Each donor CSV has columns: date, pb. Add unit label and concat.
DONORS = {
    "STOXX600":    "stoxx600_pb_2004_2026.csv",
    "FTSE100":     "ftse100_pb_2004_2026.csv",
    "MSCI_HK":     "msci_hk_pb_2004_2026.csv",
    "MSCI_TAIWAN": "msci_taiwan_pb_2004_2026.csv",
    "SP500":       "sp500_pb_2004_2026.csv",
}

def load_donor_panel() -> pd.DataFrame:
    rows = []
    df = pd.read_csv(config.RAW_DIR / "topix_pb_2004_2026.csv")
    df["unit"] = "TOPIX"
    rows.append(df)
    for unit_name, fname in DONORS.items():
        df = pd.read_csv(config.RAW_DIR / fname)
        df["unit"] = unit_name
        rows.append(df)
    panel = pd.concat(rows, ignore_index=True)
    panel["date"] = pd.to_datetime(panel["date"])
    return panel
```

#### In-space placebo loop pattern (ROBUST-04, no codebase analog):
```python
donors = list(DONORS.keys())
placebo_gaps = {}
for placebo_unit in donors:
    remaining = [d for d in donors if d != placebo_unit]
    dp_placebo = Dataprep(
        foo=panel_df,
        predictors=["pb"],
        predictors_op="mean",
        dependent="pb",
        unit_variable="unit",
        time_variable="date",
        treatment_identifier=placebo_unit,
        controls_identifier=["TOPIX"] + remaining,
        time_predictors_prior=pre_period,
        time_optimize_ssr=pre_period,
    )
    synth_p = Synth()
    synth_p.fit(dataprep=dp_placebo, optim_method="Nelder-Mead",
                optim_initial="equal", optim_options={"maxiter": 1000})
    Z0p, Z1p = dp_placebo.make_outcome_mats(time_period=all_period)
    placebo_gaps[placebo_unit] = synth_p._gaps(Z0=Z0p, Z1=Z1p)
```

---

### `src/robustness/robustness_pe.py` (analysis script, CRUD + transform)

**Primary analogs:** `src/analysis/panel_ols.py`, `src/analysis/event_study.py`, `src/analysis/geo_risk.py`

This script is a metric-swap clone of all three Phase 3 scripts. Do NOT import from `src.analysis.*` — adapt inline (anti-pattern documented in RESEARCH.md).

#### Imports pattern (panel_ols.py lines 1-23):
```python
import logging
import math
import sys
import warnings
from pathlib import Path

import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from linearmodels import PanelOLS
from linearmodels.panel.data import PanelData
from wildboottest.wildboottest import wildboottest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import config

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
    stream=sys.stdout,
)

ROBUSTNESS_DIR = config.OUTPUT_DIR / "robustness"
```

#### P/E column swap pattern (RESEARCH.md Pattern 5):
```python
# panel.parquet has 4 nulls in KOSPI pe for 2004-01 through 2004-04.
# Always drop before any PE analysis.
panel = pd.read_parquet(config.PROCESSED_DIR / "panel.parquet")
panel_pe = panel.dropna(subset=["pe"]).copy()
# Use "pe" wherever Phase 3 code uses "pb":
#   construct_regression_panel: change required_columns and dependent variable
#   _fit_panel_ols: change reg_panel["pb"] → reg_panel["pe"]
#   write_latex_table: update caption, label, output filename with _pe suffix
```

#### Output filename convention (all outputs get `_pe` suffix, D-10):
```python
# CSV
ROBUSTNESS_DIR / "robustness_pe_ols.csv"
# LaTeX
ROBUSTNESS_DIR / "robustness_pe_ols.tex"
ROBUSTNESS_DIR / "robustness_pe_event_coefs.tex"
```

#### Panel OLS fit pattern (panel_ols.py lines 86-105):
```python
def _fit_panel_ols(reg_panel: pd.DataFrame, terms: list[str]):
    exog = pd.DataFrame({"constant": 1.0}, index=reg_panel.index)
    for term in terms:
        exog[term] = reg_panel[term]
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        model = PanelOLS(
            reg_panel["pe"],          # <-- pe, not pb
            exog,
            entity_effects=True,
            time_effects=True,
            drop_absorbed=True,
            check_rank=False,
        )
        return model.fit(cov_type="robust")
```

#### Wild-bootstrap pattern (panel_ols.py lines 158-198):
Copy `_wild_bootstrap_pvalues()` verbatim; only change the dependent variable column in `PanelData(reg_panel[["pe"]])`.

#### GPR sub-analysis column swap (geo_risk.py lines 71-94):
```python
# In build_geo_regression_data: rename KOSPI column to kospi_pe
pb = (
    panel_study.pivot(index="date", columns="country", values="pe")  # pe not pb
    .reset_index()
    .rename(columns={"KOSPI": "kospi_pe", "TOPIX": "topix_pe"})
)
# model formula: "kospi_pe ~ gpr_escalation_dummy + topix_pe + C(year)"
```

---

### `src/robustness/robustness_alt_control.py` (analysis script, CRUD + transform)

**Primary analog:** `src/analysis/panel_ols.py`

#### Imports + header pattern: same as panel_ols.py — copy exactly, then replace OUTPUT target:
```python
ROBUSTNESS_DIR = config.OUTPUT_DIR / "robustness"
```

#### MSCI EM Asia as EM ex-Korea proxy (variant a, ROBUST-03):
```python
# msci_em_asia_pb_2004_2026.csv is the closest available proxy for EM ex-Korea.
# Load it from RAW_DIR and substitute for the MSCI_EM column in the panel.
em_asia = pd.read_csv(config.RAW_DIR / "msci_em_asia_pb_2004_2026.csv")
em_asia["date"] = pd.to_datetime(em_asia["date"])
em_asia["country"] = "MSCI_EM_ASIA"
# Replace MSCI_EM rows in panel, then run construct_regression_panel as normal.
# Document this substitution in a comment and in the LaTeX table caption.
```

#### MSCI EM ex-China proxy construction (variant b, ROBUST-03, RESEARCH.md Pattern 6):
```python
# Mathematical derivation:
# MSCI_EM = china_wt * China_PB + (1 - china_wt) * EM_ex_China_PB
# => EM_ex_China_PB = (MSCI_EM_PB - china_wt * China_PB) / (1 - china_wt)
# [ASSUMED] china_wt ~ 0.30 — document as approximation.
CHINA_WEIGHT_APPROX = 0.30

em = pd.read_csv(config.RAW_DIR / "msci_em_pb_2004_2026.csv")
china = pd.read_csv(config.RAW_DIR / "msci_china_pb_2004_2026.csv")
em["date"] = pd.to_datetime(em["date"])
china["date"] = pd.to_datetime(china["date"])
merged = em.merge(china, on="date", suffixes=("_em", "_china"))
merged["pb"] = (
    (merged["pb_em"] - CHINA_WEIGHT_APPROX * merged["pb_china"])
    / (1 - CHINA_WEIGHT_APPROX)
)
merged["country"] = "MSCI_EM_EX_CHINA"
```

#### LaTeX output pattern for each variant (panel_ols.py write_latex_table, lines 259-293):
```python
# Use table.style.to_latex(hrules=True, caption=..., label=...) pattern.
# Save each variant to its own file:
ROBUSTNESS_DIR / "robustness_alt_control_em_asia.tex"
ROBUSTNESS_DIR / "robustness_alt_control_em_exchina.tex"
```

---

### `src/robustness/robustness_placebo.py` (analysis script, batch + transform)

**Primary analog:** `src/analysis/event_study.py`

#### Imports pattern: identical to event_study.py lines 1-47 — copy wholesale:
```python
import logging
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.api as sm

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import config

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
    stream=sys.stdout,
)

ROBUSTNESS_DIR = config.OUTPUT_DIR / "robustness"
```

#### Placebo treated-unit swap pattern (adapt build_stacked_dataset from event_study.py):
The Phase 3 `build_stacked_dataset()` hardcodes the spread as `KOSPI - TOPIX`. For placebo markets, the treated unit changes:
```python
# For Taiwan placebo: treat MSCI_TAIWAN as pseudo-treated vs. existing panel
# Load msci_taiwan_pb_2004_2026.csv and msci_indonesia_pb_2004_2026.csv from RAW_DIR.
# Build a spread: placebo_market - TOPIX (same Japan baseline as primary analysis).
# Apply the same event_rel_time construction around config.TSE_PB_REFORM_DATE.
# Expected result: null or negligible CAR near zero post-reform.

PLACEBO_MARKETS = {
    "taiwan":    ("msci_taiwan_pb_2004_2026.csv",    "MSCI_TAIWAN"),
    "indonesia": ("msci_indonesia_pb_2004_2026.csv", "MSCI_INDONESIA"),
}
```

#### Output convention (D-15):
```python
ROBUSTNESS_DIR / "placebo_taiwan_car.csv"        # CAR estimates for Taiwan
ROBUSTNESS_DIR / "placebo_indonesia_car.csv"     # CAR estimates for Indonesia
ROBUSTNESS_DIR / "figure_placebo_falsification.pdf"  # combined figure
```

#### Combined placebo figure pattern (adapt plot_event_study from event_study.py lines 273-307):
```python
# Three-panel layout (or two-panel for two placebo markets):
# Each subplot: CAR over event_rel_time for one placebo market.
# Add dashed lines at x=0, y=0 using ax.axvline / ax.axhline.
# Save pattern: identical to event_study.py plot_event_study() savefig block.
fig.savefig(
    ROBUSTNESS_DIR / "figure_placebo_falsification.pdf",
    dpi=300,
    bbox_inches="tight",
    format="pdf",
    metadata={"CreationDate": None, "ModDate": None},
)
plt.close(fig)
```

---

### `src/robustness/__init__.py` (package init)

**Analog:** `src/analysis/__init__.py`

The analog file is a single blank line (1-line file, contents empty). Copy exactly:
```python
# robustness package
```
Or leave entirely empty — either is acceptable. The file exists solely to make `src/robustness/` a Python package.

---

### `tests/test_phase4.py` (test, request-response)

**Analog:** `tests/test_phase3.py`

#### Module header + project root injection (test_phase3.py lines 1-21):
```python
"""
tests/test_phase4.py - Smoke and unit tests for Phase 4 robustness outputs.

Run: pytest tests/test_phase4.py -x -q
"""
import ast
import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import config

ROBUSTNESS_DIR = config.OUTPUT_DIR / "robustness"
FIGURES_DIR = config.OUTPUT_DIR / "figures"
PANEL_PATH = config.PROCESSED_DIR / "panel.parquet"
```

#### Output existence smoke-test pattern (test_phase3.py test_figure2_exists, lines 55-58):
```python
def test_synth_outputs_exist():
    """SYNTH-02: synthetic_control_weights.csv must exist with positive RMSPE."""
    path = ROBUSTNESS_DIR / "synthetic_control_weights.csv"
    assert path.exists(), f"Missing: {path}"
    assert path.stat().st_size > 0
    df = pd.read_csv(path)
    assert "donor" in df.columns
    assert "weight" in df.columns
    assert "pre_rmspe" in df.columns
    assert (df["pre_rmspe"] > 0).all()
```

#### Source inspection / static test pattern (test_phase3.py test_panel_ols_results_csv_contract, lines 102-141):
```python
def test_sutva_comment_present():
    """SYNTH-03: SUTVA justification comment must appear in synthetic_control.py."""
    source = PROJECT_ROOT / "src" / "robustness" / "synthetic_control.py"
    content = source.read_text()
    assert "SUTVA" in content, "SUTVA justification comment missing from synthetic_control.py"
    assert "STOXX600" in content
    assert "KOSPI" in content
```

#### Weights sum-to-one unit test pattern:
```python
def test_synth_weights_sum_to_one():
    """SYNTH-01: Donor weights must sum to 1.0 (convexity constraint)."""
    path = ROBUSTNESS_DIR / "synthetic_control_weights.csv"
    assert path.exists(), f"Run synthetic_control.py first: {path}"
    df = pd.read_csv(path)
    total = df["weight"].sum()
    assert abs(total - 1.0) < 1e-3, f"Weights sum to {total:.6f}, expected 1.0"
```

#### Cross-module isolation test (test_phase3.py lines 207-232):
```python
def test_robustness_modules_do_not_import_each_other():
    """Robustness scripts must be standalone — no cross-imports within src/robustness/."""
    robustness_modules = {"synthetic_control", "robustness_pe",
                          "robustness_alt_control", "robustness_placebo"}
    for module_name in robustness_modules:
        path = PROJECT_ROOT / "src" / "robustness" / f"{module_name}.py"
        if not path.exists():
            continue
        tree = ast.parse(path.read_text(), filename=str(path))
        for node in ast.walk(tree):
            if not isinstance(node, ast.ImportFrom) or node.module is None:
                continue
            module = node.module
            if module.startswith(("src.robustness.", "robustness.")):
                imported = module.rsplit(".", maxsplit=1)[-1]
                assert imported not in robustness_modules - {module_name}, (
                    f"{path} imports another robustness module: {module}"
                )
```

#### File-exists pattern for each ROBUST- requirement:
```python
def test_placebo_outputs_exist():
    """ROBUST-01: placebo CSV files must exist with expected columns."""
    for market in ("taiwan", "indonesia"):
        path = ROBUSTNESS_DIR / f"placebo_{market}_car.csv"
        assert path.exists(), f"Missing: {path}"
        df = pd.read_csv(path)
        assert "event_rel_time" in df.columns
        assert "car" in df.columns

def test_robust02_outputs_exist():
    """ROBUST-02: P/E robustness LaTeX files must exist and contain P/E header."""
    for fname in ("robustness_pe_ols.tex", "robustness_pe_event_coefs.tex"):
        path = ROBUSTNESS_DIR / fname
        assert path.exists(), f"Missing: {path}"
        assert path.stat().st_size > 0
        content = path.read_text()
        assert any(token in content.lower() for token in ("p/e", "price-to-earnings", "pe"))

def test_robust03_outputs_exist():
    """ROBUST-03: alt-control LaTeX files must exist."""
    for fname in ("robustness_alt_control_em_asia.tex",
                  "robustness_alt_control_em_exchina.tex"):
        path = ROBUSTNESS_DIR / fname
        assert path.exists(), f"Missing: {path}"
        assert path.stat().st_size > 0

def test_robust04_outputs_exist():
    """ROBUST-04: in-time and in-space placebo figures must exist."""
    for fname in ("figure_placebo_intime.pdf", "figure_placebo_inspace.pdf"):
        path = ROBUSTNESS_DIR / fname
        assert path.exists(), f"Missing: {path}"
        assert path.stat().st_size > 0
```

---

### `requirements.txt` (config, direct edit)

**No analog needed — single line append.**

Add after the `wildboottest` line:
```
# Synthetic control (Phase 4)
pysyncon==1.5.2
```

---

## Shared Patterns

These patterns apply to all four robustness scripts.

### PROJECT_ROOT resolution
**Source:** `src/analysis/event_study.py` lines 21-23
**Apply to:** All `src/robustness/*.py` scripts
```python
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
```
`parents[2]` navigates: `synthetic_control.py` → `robustness/` → `src/` → `PROJECT_ROOT`.

### Logging setup
**Source:** `src/analysis/event_study.py` lines 43-47
**Apply to:** All `src/robustness/*.py` scripts
```python
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
    stream=sys.stdout,
)
```

### Output directory creation
**Source:** `src/analysis/event_study.py` lines 317-318 and `src/analysis/geo_risk.py` line 127
**Apply to:** All scripts — inside `main()` before any file I/O
```python
ROBUSTNESS_DIR = config.OUTPUT_DIR / "robustness"
FIGURES_DIR = config.OUTPUT_DIR / "figures"

# In main():
ROBUSTNESS_DIR.mkdir(parents=True, exist_ok=True)
FIGURES_DIR.mkdir(parents=True, exist_ok=True)
```

### Figure save
**Source:** `src/analysis/event_study.py` lines 297-307 and `src/analysis/geo_risk.py` lines 238-248
**Apply to:** All scripts that produce PDF figures
```python
fig.savefig(
    output_path,
    dpi=300,
    bbox_inches="tight",
    format="pdf",
    metadata={"CreationDate": None, "ModDate": None},
)
plt.close(fig)
logging.info("Saved %s", output_path)
```

### LaTeX table output (booktabs style)
**Source:** `src/analysis/panel_ols.py` lines 259-293 and `src/analysis/event_study.py` lines 244-271
**Apply to:** `robustness_pe.py`, `robustness_alt_control.py`

Two patterns in use:
1. `table.style.to_latex(hrules=True, caption=..., label=...)` — panel_ols.py style (preferred for multi-column regression tables)
2. `table.to_latex(index=False, escape=False, float_format="%.2f", na_rep="--", caption=..., label=...)` — event_study.py style (for coefficient tables)

Both produce booktabs `\toprule`, `\midrule`, `\bottomrule`. Float format is always `%.2f`.

### `if __name__ == "__main__"` guard
**Source:** `src/analysis/event_study.py` lines 330-335
**Apply to:** All `src/robustness/*.py` scripts
```python
if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
```

### Matplotlib Agg backend
**Source:** `src/analysis/event_study.py` line 14
**Apply to:** All scripts that import matplotlib.pyplot
```python
import matplotlib
matplotlib.use("Agg")  # headless backend - must come before pyplot import
import matplotlib.pyplot as plt
```

### Config import (date firewall)
**Source:** `src/analysis/panel_ols.py` lines 63-73 and `config.py` lines 23-25
**Apply to:** All `src/robustness/*.py` scripts
```python
import config
# Use config.TSE_PB_REFORM_DATE, config.RAW_DIR, config.PROCESSED_DIR, config.OUTPUT_DIR
# NEVER hardcode event dates or file paths.
```

---

## No Analog Found

| File | Role | Data Flow | Reason |
|---|---|---|---|
| `src/robustness/synthetic_control.py` (Dataprep/Synth API calls) | analysis | transform | No ADH synthetic control exists in codebase; RESEARCH.md code examples are the primary reference |
| In-space placebo loop | pattern | batch | No placebo loop exists anywhere in codebase; construct from RESEARCH.md Pattern 3 |
| In-time placebo | pattern | transform | No time-placebo exists in codebase; construct from RESEARCH.md Pattern 4 |
| Donor panel CSV loader | utility | file-I/O | All Phase 3 scripts use panel.parquet; Phase 4 requires wide-to-long CSV stacking not previously implemented |

---

## Metadata

**Analog search scope:** `src/analysis/`, `src/descriptive/`, `tests/`, `config.py`, `requirements.txt`
**Files read:** 8 (event_study.py, panel_ols.py, geo_risk.py, figure1.py, test_phase3.py, requirements.txt, config.py, src/analysis/__init__.py)
**Pattern extraction date:** 2026-04-20
