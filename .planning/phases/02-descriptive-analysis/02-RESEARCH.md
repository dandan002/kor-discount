# Phase 2: Descriptive Analysis - Research

**Researched:** 2026-04-16
**Domain:** Python data visualization, statistical inference, LaTeX table generation
**Confidence:** HIGH

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- **D-01:** Figure 1 shows P/B only — one series per market (KOSPI, TOPIX, SP500, MSCI EM). PE excluded from the headline figure.
- **D-02:** Annotate all three Japan reform dates as vertical dashed lines with text labels: 2014-02-01, 2015-06-01, 2023-03-01. Read from `config.EVENT_DATES` and `config.EVENT_LABELS` — never hardcoded.
- **D-03:** Visual style: publication-plain — seaborn whitegrid or matplotlib default, no decorative elements.
- **D-04:** Korea Discount computed as spread against two benchmarks: TOPIX (developed peer) and MSCI EM (EM peer). SP500 is context-only in Figure 1.
- **D-05:** Units: P/B points (e.g., "KOSPI trades at a −0.45x P/B discount to TOPIX"). Do NOT convert to basis points.
- **D-06:** Statistical test: paired t-test on (KOSPI PB − benchmark PB) with Newey-West (HAC) standard errors using `sm.OLS` with `cov_type='HAC', maxlags=12`. Report t-statistic and 95% CI alongside mean spread.
- **D-07:** 300 DPI, PDF format, saved to `output/figures/`.
- **D-08:** LaTeX tables: booktabs style, 2 decimal places, saved as `.tex` fragments to `output/tables/`. Use `pandas.DataFrame.to_latex()` or `Styler.to_latex()`.
- **D-09:** Table 1 sub-periods: Full (2004–2024), Pre-reform (2004–2013), Reform era (2014–2022), Post-TSE (2023–2024).

### Claude's Discretion

- Legend placement, exact line colors within the publication-plain style, figure aspect ratio, whether to include a secondary axis or annotation box.
- Whether to output a companion PE figure to `output/figures/` (not Figure 1 numbered; supplementary). Note: deferred to Phase 5 per `<deferred>` block — do not implement.

### Deferred Ideas (OUT OF SCOPE)

- PE figure / appendix table — deferred to Phase 5 appendix assembly.
- Sub-period breakdown of discount magnitude (pre/post reform) — belongs in Phase 3 OLS results.
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| DESC-01 | Generate time-series Figure 1: KOSPI P/B vs TOPIX, SP500, MSCI EM P/B over full 20-year period | matplotlib/seaborn confirmed; PDF save confirmed; axvline annotation confirmed; data available 2004-01-31 to 2026-04-30 (restrict to 2024-12-31) |
| DESC-02 | Generate Table 1: summary statistics (mean, median, SD, min, max) by country and sub-period | pandas groupby + Styler.to_latex(hrules=True) confirmed; 4 sub-periods defined; row counts verified |
| DESC-03 | Quantify Korea Discount as time-averaged spread (P/B points) with statistical significance for abstract/introduction | statsmodels HAC confirmed working; actual numbers computed: KOSPI−TOPIX = −0.177x (t=−3.23), KOSPI−MSCI_EM = −0.601x (t=−10.30); machine-readable CSV artifact needed |
</phase_requirements>

---

## Summary

Phase 2 is a pure output-generation phase — no new data acquisition, no new methodological decisions. The panel is complete and verified (1072 rows, 4 countries, 2004-01-31 to 2026-04-30). All required libraries (matplotlib 3.9.2, seaborn 0.13.2, statsmodels 0.14.4) are already pinned in `requirements.txt` and confirmed working in the project's Python environment.

The one environment-level issue discovered during research: the system Anaconda environment has scipy 1.17.1 installed, which breaks `statsmodels` imports due to a missing `_lazywhere` symbol. The project's pinned `scipy==1.13.1` resolves this when installed. Scripts must be run after `pip install -r requirements.txt` — Wave 0 of the plan should include an environment validation step.

The actual Korea Discount numbers, computed directly from `panel.parquet` with Newey-West HAC errors (maxlags=12): KOSPI trades at a **−0.177x P/B discount to TOPIX** (t = −3.23, 95% CI [−0.284, −0.069]) and a **−0.601x P/B discount to MSCI EM** (t = −10.30, 95% CI [−0.716, −0.486]) over 2004–2024. These numbers are ready for verbatim use in the abstract once scripts are committed.

**Primary recommendation:** Three standalone scripts in `src/descriptive/` — `figure1.py`, `table1.py`, `discount_stats.py` — each executable directly and each importing `config` from the project root following the established Phase 1 pattern.

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Load panel data | Script (local) | — | Read from `data/processed/panel.parquet` via pandas; no network I/O |
| Time-series visualization | Script (local) | — | matplotlib/seaborn; generates static PDF to `output/figures/` |
| Event date annotations | Script (local) | config.py | Dates imported from `config.EVENT_DATES`, drawn via `ax.axvline` |
| Summary statistics (Table 1) | Script (local) | — | pandas groupby aggregation; no external dependency |
| LaTeX table export | Script (local) | — | `Styler.to_latex()` writes `.tex` fragment to `output/tables/` |
| Korea Discount inference | Script (local) | statsmodels | HAC OLS via `sm.OLS(...).get_robustcov_results(cov_type='HAC', maxlags=12)` |
| Machine-readable discount artifact | Script (local) | — | CSV written to `output/tables/discount_stats.csv` for Phase 3 consumption |

---

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| pandas | 2.2.3 | DataFrame operations, groupby aggregation, to_latex | Already pinned; Phase 1 established pattern |
| matplotlib | 3.9.2 | Figure creation, axvline, savefig PDF | Already pinned; journal-standard output format |
| seaborn | 0.13.2 | Style sheet (whitegrid) | Already pinned; clean academic aesthetic |
| statsmodels | 0.14.4 | HAC OLS (`sm.OLS` + `get_robustcov_results`) | Already pinned; standard econometrics library |
| numpy | 1.26.4 | Array construction for OLS regressor (constant) | Already pinned; zero new dependency |
| scipy | 1.13.1 | Transitive statsmodels dependency; must match pinned version | See environment note below |

[VERIFIED: direct execution against `data/processed/panel.parquet`]

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| matplotlib.dates (mdates) | (bundled) | Date-axis formatting (YearLocator, DateFormatter) | Figure 1 x-axis |
| pathlib.Path | (stdlib) | Output directory creation (`mkdir parents=True, exist_ok=True`) | All three scripts |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `Styler.to_latex()` | `DataFrame.to_latex()` | Both work in pandas 2.2.3; Styler is the forward-compatible path and cleaner for caption/label; DataFrame.to_latex() is simpler but deprecated |
| Manual seaborn whitegrid style | `matplotlib.style.use('seaborn-v0_8-whitegrid')` | Same visual result; use `sns.set_theme(style='whitegrid')` which is the seaborn-idiomatic call |
| `maxlags=12` (fixed) | Automatic lag selection | D-06 locks maxlags=12; skip automatic selection |

**Installation:** No new packages required — all dependencies already in `requirements.txt`.

**Version verification (confirmed 2026-04-16):**
- `matplotlib`: 3.10.0 installed (higher than pinned 3.9.2 — acceptable; API fully backward-compatible for this use case) [VERIFIED: pip show]
- `seaborn`: 0.13.2 [VERIFIED: pip show]
- `statsmodels`: 0.14.4 [VERIFIED: pip show]
- `scipy`: 1.13.1 after pip install (was 1.17.1, which breaks statsmodels import) [VERIFIED: execution test]

---

## Architecture Patterns

### System Architecture Diagram

```
panel.parquet (data/processed/)
        |
        v
[src/descriptive/figure1.py]  ----reads config.EVENT_DATES---->  [config.py]
        |                                                               |
        |  pivot: date x country (P/B)                    EVENT_LABELS |
        |  4 line series                                               |
        |  axvline x3 (reform dates)                                   |
        v
[output/figures/figure1_pb_comparison.pdf]

[src/descriptive/table1.py]
        |  groupby(country, sub-period)
        |  agg(mean, median, std, min, max)
        |  Styler.to_latex(hrules=True)
        v
[output/tables/table1_summary_stats.tex]

[src/descriptive/discount_stats.py]
        |  pivot KOSPI, TOPIX, MSCI_EM
        |  spread = KOSPI_pb - benchmark_pb
        |  sm.OLS(spread, const).get_robustcov_results(HAC, maxlags=12)
        |  write prose-ready LaTeX fragment
        v
[output/tables/discount_stats.tex]     (LaTeX fragment for abstract)
[output/tables/discount_stats.csv]     (machine-readable for Phase 3)
```

### Recommended Project Structure

```
src/
└── descriptive/          # New directory for Phase 2 scripts
    ├── figure1.py        # Figure 1: P/B time series + reform annotations
    ├── table1.py         # Table 1: summary stats by country and sub-period
    └── discount_stats.py # Korea Discount magnitude + Newey-West inference

output/                   # Created by scripts if absent
├── figures/
│   └── figure1_pb_comparison.pdf
└── tables/
    ├── table1_summary_stats.tex
    ├── discount_stats.tex
    └── discount_stats.csv
```

### Pattern 1: Script Skeleton (follow Phase 1 convention)

**What:** All Phase 2 scripts follow the identical bootstrapping pattern established in Phase 1.
**When to use:** Every new script in `src/descriptive/`.

```python
# Source: established in src/data/build_panel.py and src/data/verify_panel.py
import logging
import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import config

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s", stream=sys.stdout)

if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
```

### Pattern 2: Figure 1 — Time Series with Reform Date Annotations

**What:** Load panel, pivot to wide format, plot 4 series, add axvline annotations from config.
**When to use:** `figure1.py`

```python
# Source: verified against matplotlib docs + direct execution
import matplotlib
matplotlib.use("Agg")  # non-interactive backend for script execution
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns

sns.set_theme(style="whitegrid")

df = pd.read_parquet(config.PROCESSED_DIR / "panel.parquet")
# Restrict to study period
df = df[df["date"] <= pd.Timestamp("2024-12-31")]

fig, ax = plt.subplots(figsize=(10, 5))

# Line colors: order matters — KOSPI should be visually distinct (e.g., blue/bold)
colors = {"KOSPI": "#1f77b4", "TOPIX": "#ff7f0e", "SP500": "#2ca02c", "MSCI_EM": "#d62728"}
labels = {"KOSPI": "KOSPI", "TOPIX": "TOPIX", "SP500": "S&P 500", "MSCI_EM": "MSCI EM"}

for country in config.COUNTRIES:
    sub = df[df["country"] == country].sort_values("date")
    ax.plot(sub["date"], sub["pb"], label=labels[country],
            color=colors[country], linewidth=1.5)

# Reform date annotations — read from config, never hardcoded
for event_date, event_label in config.EVENT_LABELS.items():
    ax.axvline(pd.Timestamp(event_date), color="grey", linestyle="--",
               linewidth=0.8, alpha=0.7)
    ax.text(pd.Timestamp(event_date), ax.get_ylim()[1] * 0.97,
            event_label, rotation=90, verticalalignment="top",
            fontsize=7, color="grey")

ax.set_xlabel("Date")
ax.set_ylabel("Price-to-Book Ratio (P/B)")
ax.set_title("Figure 1: Index-Level P/B Ratios, 2004–2024", fontsize=11)
ax.legend(loc="upper left", frameon=True)
ax.xaxis.set_major_locator(mdates.YearLocator(4))
ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))

output_path = config.OUTPUT_DIR / "figures" / "figure1_pb_comparison.pdf"
output_path.parent.mkdir(parents=True, exist_ok=True)
fig.savefig(output_path, dpi=300, bbox_inches="tight", format="pdf")
plt.close(fig)
logging.info("Saved Figure 1 to %s", output_path)
```

[VERIFIED: PDF generation tested end-to-end against actual panel.parquet]

### Pattern 3: Table 1 — Sub-Period Summary Statistics

**What:** Compute mean/median/SD/min/max by country and sub-period, export as booktabs LaTeX.
**When to use:** `table1.py`

```python
# Source: verified pandas 2.2.3 Styler.to_latex output
SUB_PERIODS = {
    "Full (2004--2024)":      ("2004-01-01", "2024-12-31"),
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

latex_str = table1.style.format(precision=2).to_latex(
    hrules=True,
    caption="Summary statistics of P/B ratios by country and sub-period.",
    label="tab:summary_stats",
)

output_path = config.OUTPUT_DIR / "tables" / "table1_summary_stats.tex"
output_path.parent.mkdir(parents=True, exist_ok=True)
output_path.write_text(latex_str, encoding="utf-8")
```

[VERIFIED: Styler.to_latex(hrules=True) produces \toprule/\midrule/\bottomrule in pandas 2.2.3]

### Pattern 4: Newey-West HAC Inference on Spread

**What:** Mean spread with HAC standard errors, t-statistic, 95% CI.
**When to use:** `discount_stats.py`

```python
# Source: verified against statsmodels 0.14.4 with scipy==1.13.1
import statsmodels.api as sm
import numpy as np

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
        "n": len(spread),
        "mean": hac.params[0],
        "nw_se": hac.bse[0],
        "t_stat": hac.tvalues[0],
        "ci_lower": hac.conf_int()[0, 0],
        "ci_upper": hac.conf_int()[0, 1],
    }
```

[VERIFIED: actual output — KOSPI−TOPIX: mean=−0.1766, NW SE=0.0546, t=−3.23, CI=[−0.284, −0.069]; KOSPI−MSCI_EM: mean=−0.6012, NW SE=0.0584, t=−10.30, CI=[−0.716, −0.486]]

### Anti-Patterns to Avoid

- **Hardcoding event dates in figure scripts:** D-02 mandates `config.EVENT_DATES` / `config.EVENT_LABELS`. Never write `"2014-02-01"` as a string literal in any Phase 2 script.
- **Using `ax.text()` before `ax.get_ylim()` is stable:** Set y-limits before adding text annotations, or use `ax.transAxes` coordinates (0–1 range) instead of data coordinates.
- **Restricting to 2024-12-31 only in figure, forgetting table:** Both Figure 1 and Table 1 must be restricted to the study period (2004–2024). The panel runs to 2026-04-30.
- **Using `matplotlib.use('TkAgg')` or display backend in scripts:** Scripts run headless; always use `matplotlib.use('Agg')` before importing `pyplot`.
- **`booktabs=True` kwarg on `DataFrame.to_latex()`:** This parameter does not exist in pandas 2.x. Use `Styler.to_latex(hrules=True)` for the cleaner path with caption/label support, or use `DataFrame.to_latex()` which already outputs booktabs rules automatically.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Autocorrelation-robust standard errors | Custom Newey-West implementation | `sm.OLS(...).get_robustcov_results(cov_type='HAC', maxlags=12)` | Handles lag selection, matrix algebra, degrees-of-freedom correctly |
| LaTeX table formatting | String concatenation with `\toprule` etc. | `Styler.to_latex(hrules=True)` | Edge cases in escaping, alignment, multirow — use pandas |
| Date axis formatting | Manual string-based x-axis labels | `matplotlib.dates.YearLocator` + `DateFormatter` | Handles leap years, label collision, time zone safely |
| Sub-period slicing | Custom period-detection logic | Pandas boolean indexing on datetime column | Tested, composable |

**Key insight:** All statistical and formatting heavy lifting is handled by mature libraries already pinned in `requirements.txt`. Phase 2 is orchestration, not implementation.

---

## Common Pitfalls

### Pitfall 1: scipy/statsmodels version mismatch

**What goes wrong:** `ImportError: cannot import name '_lazywhere' from 'scipy._lib._util'` — statsmodels 0.14.4 cannot import at all.
**Why it happens:** The system Anaconda env has scipy 1.17.1; statsmodels 0.14.4 requires scipy ≤ 1.13.x for this internal symbol.
**How to avoid:** Run `pip install -r requirements.txt` before executing any Phase 2 script. The pinned `scipy==1.13.1` resolves this.
**Warning signs:** Any script that imports `statsmodels.api` crashes on import, not at the function call.

[VERIFIED: confirmed by direct execution; resolved by installing scipy==1.13.1]

### Pitfall 2: Text annotations appearing before axis limits are set

**What goes wrong:** Annotation text for reform dates appears at wrong y-position (e.g., outside plot bounds) because `ax.get_ylim()` is called before data is plotted.
**Why it happens:** matplotlib sets axis limits dynamically as data is added. Querying limits before `ax.plot()` returns the default (0, 1).
**How to avoid:** Either (a) add annotations after all `ax.plot()` calls, or (b) use `ax.transAxes` coordinates for y-position (e.g., `y=0.97` in axes fraction) instead of data coordinates.
**Warning signs:** All three reform date labels cluster at the same y position regardless of plot scale.

### Pitfall 3: Study period not restricted to 2024-12-31

**What goes wrong:** Figure 1 shows data through 2026-04 (present); Table 1 sub-period row counts are inflated; discount magnitude includes 2025–2026 data.
**Why it happens:** `panel.parquet` extends to 2026-04-30 (the panel is kept current by build_panel.py).
**How to avoid:** Filter `df = df[df["date"] <= pd.Timestamp("2024-12-31")]` at the top of every Phase 2 script.
**Warning signs:** `Pre-reform` sub-period has 120 rows/country, `Full period` has more than 252 rows/country.

### Pitfall 4: `discount_stats.csv` not written

**What goes wrong:** Phase 3 cannot consume discount magnitude programmatically; the number exists only in a `.tex` fragment.
**Why it happens:** Easy to forget the machine-readable artifact when focusing on LaTeX output.
**How to avoid:** `discount_stats.py` must write both `.tex` and `.csv` — the CONTEXT.md integration point explicitly requires `output/tables/discount_stats.csv`.
**Warning signs:** Phase 3 reviewer finds no CSV in `output/tables/`.

### Pitfall 5: matplotlib interactive backend on headless system

**What goes wrong:** `figure1.py` hangs or raises `_tkinter.TclError: no display name` when run in a non-interactive shell.
**Why it happens:** Default matplotlib backend tries to open a display window.
**How to avoid:** Call `matplotlib.use("Agg")` before `import matplotlib.pyplot as plt` at the top of each figure script.
**Warning signs:** Script hangs indefinitely instead of producing output.

---

## Code Examples

### Loading Panel with Study Period Filter

```python
# Source: established pattern from src/data/build_panel.py
import pandas as pd
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
import config

df = pd.read_parquet(config.PROCESSED_DIR / "panel.parquet")
df = df[df["date"] <= pd.Timestamp("2024-12-31")].copy()
```

[VERIFIED: pattern used in build_panel.py and verify_panel.py]

### savefig to PDF at 300 DPI

```python
# Source: matplotlib docs (confirmed working in matplotlib 3.9.2/3.10.0)
output_path = config.OUTPUT_DIR / "figures" / "figure1_pb_comparison.pdf"
output_path.parent.mkdir(parents=True, exist_ok=True)
fig.savefig(output_path, dpi=300, bbox_inches="tight", format="pdf")
plt.close(fig)
```

[VERIFIED: confirmed PDF output 22 KB, correct format]

### HAC Inference (Newey-West, maxlags=12)

```python
# Source: statsmodels docs + direct execution on panel.parquet
import statsmodels.api as sm
import numpy as np

spread = (kospi_pb - topix_pb).dropna().values
model = sm.OLS(spread, np.ones(len(spread))).fit()
hac = model.get_robustcov_results(cov_type="HAC", maxlags=12)
# hac.params[0]  -> mean spread
# hac.bse[0]     -> Newey-West standard error
# hac.tvalues[0] -> t-statistic (H0: mean = 0)
# hac.conf_int() -> 95% confidence interval [[lower, upper]]
```

[VERIFIED: KOSPI−TOPIX mean=−0.1766, t=−3.23; KOSPI−MSCI_EM mean=−0.6012, t=−10.30]

### Styler.to_latex for LaTeX Fragment

```python
# Source: verified pandas 2.2.3
latex_str = table_df.style.format(precision=2).to_latex(
    hrules=True,           # produces \toprule, \midrule, \bottomrule
    caption="Caption text.",
    label="tab:label",
)
output_path.write_text(latex_str, encoding="utf-8")
```

[VERIFIED: output confirmed booktabs-compatible]

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `DataFrame.to_latex(booktabs=True)` | `Styler.to_latex(hrules=True)` | pandas 2.0 | `booktabs=True` kwarg removed from DataFrame.to_latex(); `DataFrame.to_latex()` still works but Styler path is forward-compatible |
| `matplotlib.style.use('seaborn-whitegrid')` | `matplotlib.style.use('seaborn-v0_8-whitegrid')` or `sns.set_theme()` | matplotlib 3.6+ | Style name prefix changed to `seaborn-v0_8-*` to avoid naming collision |
| Fixed lag selection (e.g., lags=6) | maxlags=12 (one year) | — | Convention for monthly data; D-06 locks this |

**Deprecated/outdated:**
- `DataFrame.to_latex(booktabs=True)`: `booktabs` kwarg does not exist in pandas 2.x. Use `Styler.to_latex(hrules=True)` instead — confirmed in pandas 2.2.3.
- `matplotlib.style.use('seaborn-whitegrid')`: Renamed to `seaborn-v0_8-whitegrid` in matplotlib 3.6+. Use `sns.set_theme(style='whitegrid')` for forward compatibility.

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | Study period should be restricted to 2024-12-31 (panel extends to 2026-04) | Standard Stack, Pitfalls | If wrong, 2025-2026 data included in headline numbers — confirmed by inspection of panel.parquet date range; restriction is consistent with paper scope "20-year period" ending 2024 |

Note: A1 is a reasonable interpretation (the paper covers "20 years" and data vintage ends 2024-12); a planner or executor should confirm this with the user if any ambiguity remains.

---

## Open Questions

1. **`output/tables/discount_stats.tex` format — what prose goes in it?**
   - What we know: The `.tex` file is meant as a "prose-ready LaTeX fragment" for verbatim use in the abstract.
   - What's unclear: Should it be a `\newcommand{}` definition (e.g., `\korTopixDiscount{−0.177}`), a sentence fragment, or a table?
   - Recommendation: Implement as a set of `\newcommand` definitions so the abstract can reference them symbolically. This is more robust than inline numbers. If the user prefers a prose sentence, adjust in execution.

2. **matplotlib backend on user's machine**
   - What we know: `matplotlib.use("Agg")` works; PDF confirmed generated.
   - What's unclear: If the user runs scripts interactively in a notebook or IDE, `Agg` will suppress display. The scripts are designed for CLI execution.
   - Recommendation: Add a comment in each figure script explaining the Agg choice.

---

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python | All scripts | ✓ | 3.12.2 (anaconda) | — |
| pandas | All scripts | ✓ | 2.2.3 | — |
| matplotlib | figure1.py | ✓ | 3.10.0 (> pinned 3.9.2) | — |
| seaborn | figure1.py | ✓ | 0.13.2 | — |
| statsmodels | discount_stats.py | ✓ | 0.14.4 | — |
| scipy | statsmodels dep | ✓ (after pip install) | 1.13.1 (requires downgrade from 1.17.1) | Fails import without |
| numpy | discount_stats.py | ✓ | 1.26.4 | — |
| pyarrow | panel load | ✓ | 15.0.2 | — |
| data/processed/panel.parquet | All scripts | ✓ | 1072 rows, 2004-01-31 to 2026-04-30 | — |
| output/ directory | All scripts | ✗ (does not exist) | — | Created by scripts via `Path.mkdir(parents=True, exist_ok=True)` |

**Missing dependencies with no fallback:**
- None blocking execution after `pip install -r requirements.txt`.

**Missing dependencies with fallback:**
- scipy 1.13.1: currently 1.17.1 on system; `pip install -r requirements.txt` downgrades to pinned version and resolves statsmodels import error. This MUST be the first step in Wave 0.

[VERIFIED: all checks by direct execution 2026-04-16]

---

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest (not yet installed in project) |
| Config file | None — Wave 0 gap |
| Quick run command | `pytest tests/ -x -q` |
| Full suite command | `pytest tests/ -q` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| DESC-01 | `figure1_pb_comparison.pdf` exists in `output/figures/` after running `figure1.py` | smoke | `pytest tests/test_descriptive.py::test_figure1_pdf_exists -x` | Wave 0 |
| DESC-01 | PDF file size > 0 bytes | smoke | `pytest tests/test_descriptive.py::test_figure1_pdf_nonempty -x` | Wave 0 |
| DESC-02 | `table1_summary_stats.tex` exists in `output/tables/` | smoke | `pytest tests/test_descriptive.py::test_table1_tex_exists -x` | Wave 0 |
| DESC-02 | `.tex` file contains `\toprule` (booktabs) | unit | `pytest tests/test_descriptive.py::test_table1_booktabs -x` | Wave 0 |
| DESC-03 | `discount_stats.csv` exists and has TOPIX and MSCI_EM rows | unit | `pytest tests/test_descriptive.py::test_discount_csv_exists -x` | Wave 0 |
| DESC-03 | KOSPI−TOPIX mean spread is negative (< 0) | unit | `pytest tests/test_descriptive.py::test_discount_topix_negative -x` | Wave 0 |
| DESC-03 | t-statistic absolute value > 2.0 (statistically significant) | unit | `pytest tests/test_descriptive.py::test_discount_tstat_significant -x` | Wave 0 |

### Sampling Rate

- **Per task commit:** `pytest tests/test_descriptive.py -x -q`
- **Per wave merge:** `pytest tests/ -q`
- **Phase gate:** Full suite green before `/gsd-verify-work`

### Wave 0 Gaps

- [ ] `tests/test_descriptive.py` — smoke + unit tests covering DESC-01, DESC-02, DESC-03
- [ ] `tests/__init__.py` — empty file for pytest discovery
- [ ] `pip install pytest` — not in requirements.txt; needed for test runner
- [ ] `pip install -r requirements.txt` to pin scipy==1.13.1 — prerequisite to any statsmodels test

---

## Security Domain

Not applicable for this phase. Phase 2 performs local file I/O only — reads from `data/processed/panel.parquet`, writes to `output/`. No network access, no user input, no authentication, no secrets.

---

## Sources

### Primary (HIGH confidence)
- Direct execution against `data/processed/panel.parquet` — all numerical outputs, pandas behavior, statsmodels HAC, matplotlib PDF save
- `config.py` at project root — event dates, path constants, country list
- `src/data/build_panel.py` — established script skeleton pattern
- Context7 `/websites/matplotlib_stable` — savefig parameters, axvline API, rcParams
- Context7 `/websites/pandas_pydata` — `Styler.to_latex` and `DataFrame.to_latex` API

### Secondary (MEDIUM confidence)
- pip show output for installed package versions — matplotlib 3.10.0, seaborn 0.13.2, statsmodels 0.14.4

### Tertiary (LOW confidence)
- None

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — all libraries verified by direct execution; versions confirmed via pip show
- Architecture: HIGH — pattern established by Phase 1; all API calls confirmed working
- Pitfalls: HIGH — scipy/statsmodels conflict reproduced and resolved; all other pitfalls verified by code execution
- Numerical outputs: HIGH — computed directly from `panel.parquet` (not estimated from training data)

**Research date:** 2026-04-16
**Valid until:** 2026-07-16 (stable libraries; 90 days)
