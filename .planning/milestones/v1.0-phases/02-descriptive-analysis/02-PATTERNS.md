# Phase 2: Descriptive Analysis - Pattern Map

**Mapped:** 2026-04-16
**Files analyzed:** 4 new files (3 scripts + 1 test file)
**Analogs found:** 4 / 4

---

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `src/descriptive/figure1.py` | utility (output generator) | transform → file-I/O | `src/data/build_panel.py` | role-match (same skeleton; different output type) |
| `src/descriptive/table1.py` | utility (output generator) | transform → file-I/O | `src/data/build_panel.py` | role-match (same skeleton; aggregation + file write) |
| `src/descriptive/discount_stats.py` | utility (statistical inference) | transform → file-I/O | `src/data/verify_panel.py` | role-match (same skeleton; computes statistics, writes output) |
| `tests/test_descriptive.py` | test | batch | `src/data/verify_panel.py` | partial-match (verify_panel is effectively a test runner; provides check structure pattern) |

---

## Pattern Assignments

### `src/descriptive/figure1.py` (utility, transform → file-I/O)

**Analog:** `src/data/build_panel.py`

**Imports pattern** (build_panel.py lines 1-21):
```python
"""
figure1.py - Generate Figure 1: KOSPI P/B vs benchmark indices, 2004-2024.
"""
import logging
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # must come before pyplot import — headless execution
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import seaborn as sns

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import config

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
    stream=sys.stdout,
)
```

**Core pattern — data load + study period restriction** (build_panel.py lines 126-129, verify_panel.py lines 203-209):
```python
def main() -> None:
    df = pd.read_parquet(config.PROCESSED_DIR / "panel.parquet")
    df = df[df["date"] <= pd.Timestamp("2024-12-31")].copy()
```

**Core pattern — time series plot with reform date annotations** (RESEARCH.md Pattern 2):
```python
    sns.set_theme(style="whitegrid")
    fig, ax = plt.subplots(figsize=(10, 5))

    colors = {"KOSPI": "#1f77b4", "TOPIX": "#ff7f0e", "SP500": "#2ca02c", "MSCI_EM": "#d62728"}
    labels = {"KOSPI": "KOSPI", "TOPIX": "TOPIX", "SP500": "S&P 500", "MSCI_EM": "MSCI EM"}

    for country in config.COUNTRIES:
        sub = df[df["country"] == country].sort_values("date")
        ax.plot(sub["date"], sub["pb"], label=labels[country],
                color=colors[country], linewidth=1.5)

    # Add annotations AFTER all ax.plot() calls so ax.get_ylim() is stable
    for event_date, event_label in config.EVENT_LABELS.items():
        ax.axvline(pd.Timestamp(event_date), color="grey", linestyle="--",
                   linewidth=0.8, alpha=0.7)
        ax.text(pd.Timestamp(event_date), ax.get_ylim()[1] * 0.97,
                event_label, rotation=90, verticalalignment="top",
                fontsize=7, color="grey")

    ax.set_xlabel("Date")
    ax.set_ylabel("Price-to-Book Ratio (P/B)")
    ax.set_title("Figure 1: Index-Level P/B Ratios, 2004\u20132024", fontsize=11)
    ax.legend(loc="upper left", frameon=True)
    ax.xaxis.set_major_locator(mdates.YearLocator(4))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
```

**File save pattern** (RESEARCH.md Pattern 2, build_panel.py line 126):
```python
    output_path = config.OUTPUT_DIR / "figures" / "figure1_pb_comparison.pdf"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=300, bbox_inches="tight", format="pdf")
    plt.close(fig)
    logging.info("Saved Figure 1 to %s", output_path)
```

**Entry point pattern** (build_panel.py lines 142-147):
```python
if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
```

**Anti-patterns to avoid:**
- Never write `"2014-02-01"` as a string literal — always read from `config.EVENT_DATES` / `config.EVENT_LABELS`
- Never call `ax.get_ylim()` before all `ax.plot()` calls — y-limits are not stable until data is plotted
- Never filter the panel to 2024-12-31 only in Figure 1 and forget to do the same in table1.py and discount_stats.py

---

### `src/descriptive/table1.py` (utility, transform → file-I/O)

**Analog:** `src/data/build_panel.py`

**Imports pattern** (build_panel.py lines 1-27):
```python
"""
table1.py - Generate Table 1: P/B summary statistics by country and sub-period.
"""
import logging
import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import config

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
    stream=sys.stdout,
)
```

**Core pattern — sub-period aggregation** (RESEARCH.md Pattern 3):
```python
SUB_PERIODS = {
    "Full (2004--2024)":       ("2004-01-01", "2024-12-31"),
    "Pre-reform (2004--2013)": ("2004-01-01", "2013-12-31"),
    "Reform era (2014--2022)": ("2014-01-01", "2022-12-31"),
    "Post-TSE (2023--2024)":   ("2023-01-01", "2024-12-31"),
}

frames = []
for period_name, (start, end) in SUB_PERIODS.items():
    subset = df[(df["date"] >= start) & (df["date"] <= end)]
    stats = subset.groupby("country")["pb"].agg(
        mean="mean", median="median", std="std", min="min", max="max"
    ).round(3)
    stats.insert(0, "Period", period_name)
    frames.append(stats)

table1 = pd.concat(frames)
```

**LaTeX export pattern** (RESEARCH.md Pattern 3):
```python
latex_str = table1.style.format(precision=2).to_latex(
    hrules=True,            # produces \toprule, \midrule, \bottomrule (booktabs-compatible)
    caption="Summary statistics of P/B ratios by country and sub-period.",
    label="tab:summary_stats",
)

output_path = config.OUTPUT_DIR / "tables" / "table1_summary_stats.tex"
output_path.parent.mkdir(parents=True, exist_ok=True)
output_path.write_text(latex_str, encoding="utf-8")
logging.info("Saved Table 1 to %s", output_path)
```

**Anti-patterns to avoid:**
- Do NOT use `DataFrame.to_latex(booktabs=True)` — the `booktabs` kwarg does not exist in pandas 2.x; use `Styler.to_latex(hrules=True)` instead
- Filter `df = df[df["date"] <= pd.Timestamp("2024-12-31")].copy()` at the top of `main()` — the panel runs to 2026-04-30

**Entry point pattern** (build_panel.py lines 142-147 — identical for all scripts):
```python
if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
```

---

### `src/descriptive/discount_stats.py` (utility, statistical inference → file-I/O)

**Analog:** `src/data/verify_panel.py`

**Imports pattern** (verify_panel.py lines 1-21 + statsmodels addition):
```python
"""
discount_stats.py - Quantify the Korea Discount with Newey-West HAC inference.

Outputs:
  output/tables/discount_stats.tex  — LaTeX \newcommand fragment for abstract
  output/tables/discount_stats.csv  — machine-readable artifact for Phase 3
"""
import logging
import sys
from pathlib import Path

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
```

**Core pattern — HAC inference on spread** (RESEARCH.md Pattern 4):
```python
df_2024 = df[df["date"] <= pd.Timestamp("2024-12-31")]
kospi = df_2024[df_2024["country"] == "KOSPI"].set_index("date")["pb"].sort_index()
topix = df_2024[df_2024["country"] == "TOPIX"].set_index("date")["pb"].sort_index()
msci  = df_2024[df_2024["country"] == "MSCI_EM"].set_index("date")["pb"].sort_index()

results = {}
for name, benchmark in [("TOPIX", topix), ("MSCI_EM", msci)]:
    spread = (kospi - benchmark).dropna().values
    model = sm.OLS(spread, np.ones(len(spread))).fit()
    hac = model.get_robustcov_results(cov_type="HAC", maxlags=12)
    results[name] = {
        "benchmark":  name,
        "n":          len(spread),
        "mean":       hac.params[0],
        "nw_se":      hac.bse[0],
        "t_stat":     hac.tvalues[0],
        "ci_lower":   hac.conf_int()[0, 0],
        "ci_upper":   hac.conf_int()[0, 1],
    }
```

**Dual output pattern — CSV + LaTeX fragment** (integration point from CONTEXT.md):
```python
    # Machine-readable CSV for Phase 3 consumption
    csv_path = config.OUTPUT_DIR / "tables" / "discount_stats.csv"
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(results.values()).to_csv(csv_path, index=False)
    logging.info("Saved discount_stats.csv to %s", csv_path)

    # Prose-ready LaTeX \newcommand fragment for abstract
    tex_lines = [
        "% Korea Discount magnitude — auto-generated by discount_stats.py\n",
    ]
    for name, r in results.items():
        safe = name.replace("_", "")
        tex_lines.append(
            f"\\newcommand{{\\korDiscount{safe}}}{{{r['mean']:.3f}x}}\n"
        )
        tex_lines.append(
            f"\\newcommand{{\\korDiscount{safe}TStat}}{{{r['t_stat']:.2f}}}\n"
        )
    tex_path = config.OUTPUT_DIR / "tables" / "discount_stats.tex"
    tex_path.write_text("".join(tex_lines), encoding="utf-8")
    logging.info("Saved discount_stats.tex to %s", tex_path)
```

**Anti-patterns to avoid:**
- Do NOT use `scipy==1.17.1` — statsmodels 0.14.4 requires `scipy<=1.13.x`; run `pip install -r requirements.txt` first
- Do NOT write only the `.tex` file and omit `discount_stats.csv` — Phase 3 requires the CSV artifact
- Do NOT use `maxlags` other than 12 — D-06 locks this convention for monthly data

---

### `tests/test_descriptive.py` (test, batch)

**Analog:** `src/data/verify_panel.py` (closest functional match — structured check runner)

**No direct test file analog exists in the codebase.** The project has no `tests/` directory yet. Use `verify_panel.py` as the structural template: define discrete named check functions, collect pass/fail results, assert. The RESEARCH.md Validation Architecture section specifies the exact test map.

**Test file structure pattern** (modeled on verify_panel.py check structure, lines 53-96):
```python
"""
tests/test_descriptive.py - Smoke and unit tests for Phase 2 descriptive outputs.

Run: pytest tests/test_descriptive.py -x -q
"""
import sys
from pathlib import Path

import pandas as pd
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import config

OUTPUT_FIGURES = config.OUTPUT_DIR / "figures"
OUTPUT_TABLES  = config.OUTPUT_DIR / "tables"


# DESC-01 checks
def test_figure1_pdf_exists():
    assert (OUTPUT_FIGURES / "figure1_pb_comparison.pdf").exists()

def test_figure1_pdf_nonempty():
    path = OUTPUT_FIGURES / "figure1_pb_comparison.pdf"
    assert path.stat().st_size > 0

# DESC-02 checks
def test_table1_tex_exists():
    assert (OUTPUT_TABLES / "table1_summary_stats.tex").exists()

def test_table1_booktabs():
    content = (OUTPUT_TABLES / "table1_summary_stats.tex").read_text()
    assert "\\toprule" in content

# DESC-03 checks
def test_discount_csv_exists():
    path = OUTPUT_TABLES / "discount_stats.csv"
    assert path.exists()
    df = pd.read_csv(path)
    assert "TOPIX" in df["benchmark"].values
    assert "MSCI_EM" in df["benchmark"].values

def test_discount_topix_negative():
    df = pd.read_csv(OUTPUT_TABLES / "discount_stats.csv")
    topix_mean = df[df["benchmark"] == "TOPIX"]["mean"].iloc[0]
    assert topix_mean < 0

def test_discount_tstat_significant():
    df = pd.read_csv(OUTPUT_TABLES / "discount_stats.csv")
    for _, row in df.iterrows():
        assert abs(row["t_stat"]) > 2.0, (
            f"t-stat for {row['benchmark']} = {row['t_stat']:.2f}, expected |t| > 2.0"
        )
```

**Companion file needed** (no analog exists):
```python
# tests/__init__.py — empty file required for pytest module discovery
```

---

## Shared Patterns

### Script Bootstrap (PROJECT_ROOT + sys.path + config import)
**Source:** `src/data/build_panel.py` lines 17-27 and `src/data/verify_panel.py` lines 16-21
**Apply to:** All three scripts in `src/descriptive/`
```python
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import config

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
    stream=sys.stdout,
)
```
Note: `parents[2]` is correct for `src/descriptive/*.py` (two levels up from file to project root). `build_panel.py` at `src/data/` also uses `parents[2]`.

### Study Period Restriction
**Source:** Verified against `panel.parquet` in RESEARCH.md
**Apply to:** All three scripts — must be applied at the top of each `main()` before any computation
```python
df = pd.read_parquet(config.PROCESSED_DIR / "panel.parquet")
df = df[df["date"] <= pd.Timestamp("2024-12-31")].copy()
```

### Output Directory Creation
**Source:** `src/data/build_panel.py` line 126
**Apply to:** All three scripts, at point of first write
```python
output_path.parent.mkdir(parents=True, exist_ok=True)
```

### Main Entry Point Guard
**Source:** `src/data/build_panel.py` lines 142-147 (identical pattern in all Phase 1 scripts)
**Apply to:** All three scripts
```python
if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
```

### Event Date Access
**Source:** `config.py` lines 27-37
**Apply to:** `figure1.py` only (the only script using event dates for visualization)
```python
# config.EVENT_DATES is a list[datetime.date]
# config.EVENT_LABELS is a dict[datetime.date, str]
# Always iterate config.EVENT_LABELS.items() — never hardcode "2014-02-01"
for event_date, event_label in config.EVENT_LABELS.items():
    ax.axvline(pd.Timestamp(event_date), ...)
```

---

## No Analog Found

| File | Role | Data Flow | Reason |
|------|------|-----------|--------|
| `tests/__init__.py` | config | — | No test infrastructure exists yet; empty file, no pattern needed |

---

## Metadata

**Analog search scope:** `/Users/dandan/Desktop/Projects/kor-discount/src/` (all `.py` files), `/Users/dandan/Desktop/Projects/kor-discount/config.py`
**Files scanned:** 4 Python source files (`build_panel.py`, `verify_panel.py`, `pull_bloomberg.py`, `config.py`)
**Tests directory:** Does not exist — `tests/` must be created in Wave 0
**Pattern extraction date:** 2026-04-16
