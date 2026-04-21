# Phase 5: Paper Assembly and Replication Package - Pattern Map

**Mapped:** 2026-04-20
**Files analyzed:** 5 new/modified files
**Analogs found:** 5 / 5

---

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `run_all.py` | utility (orchestrator) | request-response (subprocess fan-out) | `src/robustness/synthetic_control.py` (script structure) | role-match |
| `src/policy/counterfactual_projection.py` | utility (analysis script) | transform (read parquet + CSV → write PDF) | `src/descriptive/figure1.py` | exact |
| `src/policy/__init__.py` | config | — | `src/descriptive/__init__.py` | exact |
| `paper/main.tex` | config (LaTeX document) | batch (figure/table integration) | `output/tables/table2_ols.tex` (booktabs style) | partial |
| `paper/references.bib` | config (bibliography) | — | `papers/REFERENCES.md` (seed content) | partial |

---

## Pattern Assignments

### `run_all.py` (utility, subprocess fan-out)

**Analog:** `src/analysis/panel_ols.py` and `src/robustness/synthetic_control.py` — for `if __name__ == "__main__"` guard with `sys.exit(1)` on exception; and `src/descriptive/figure1.py` for `PROJECT_ROOT` resolution.

**Module-level constants pattern** (`src/descriptive/figure1.py` lines 19-21, `src/robustness/synthetic_control.py` lines 20-21):
```python
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
```
Note: `run_all.py` lives at repo root so use `.resolve().parent` (not `.parents[2]`).

**Fail-fast guard pattern** (`src/descriptive/figure1.py` lines 102-107, same across all scripts):
```python
if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
```

**Core subprocess fan-out pattern** (from RESEARCH.md Pattern 1 — derived from all existing scripts using `sys.exit(1)` on non-zero exit):
```python
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent

SCRIPTS = [
    ("descriptive analysis — Figure 1", "src/descriptive/figure1.py"),
    ("descriptive analysis — Table 1", "src/descriptive/table1.py"),
    ("discount statistics", "src/descriptive/discount_stats.py"),
    ("event study", "src/analysis/event_study.py"),
    ("panel OLS", "src/analysis/panel_ols.py"),
    ("geopolitical risk", "src/analysis/geo_risk.py"),
    ("synthetic control", "src/robustness/synthetic_control.py"),
    ("placebo falsification", "src/robustness/robustness_placebo.py"),
    ("P/E robustness", "src/robustness/robustness_pe.py"),
    ("alternative control robustness", "src/robustness/robustness_alt_control.py"),
    ("counterfactual projection", "src/policy/counterfactual_projection.py"),
]

def main():
    n = len(SCRIPTS)
    for i, (label, script_rel) in enumerate(SCRIPTS, 1):
        script_path = PROJECT_ROOT / script_rel
        print(f"\n=== [{i}/{n}] Running {label} ===")
        subprocess.run([sys.executable, str(script_path)], check=True)

    print("\nAll outputs regenerated successfully.")
```

**Critical constraints:**
- Use `sys.executable` not `"python"` (D-08, anti-pattern in RESEARCH.md)
- Use `check=True` on every `subprocess.run` call (D-08)
- Do NOT include `build_panel.py` in SCRIPTS (D-07)

---

### `src/policy/counterfactual_projection.py` (utility, transform)

**Analog:** `src/descriptive/figure1.py` — exact match: reads `panel.parquet`, produces PDF figure with identical save pattern. Also references `src/robustness/synthetic_control.py` for gap-series CSV reading.

**Imports pattern** (`src/descriptive/figure1.py` lines 1-23):
```python
"""
counterfactual_projection.py - Japan-calibrated illustrative KOSPI P/B projection.
...
"""
import logging
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # headless backend - must come before pyplot import
import matplotlib.pyplot as plt
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

**Data reading pattern** (`src/descriptive/figure1.py` lines 34-35 and `src/robustness/synthetic_control.py` lines 62-67):
```python
# Read canonical panel for KOSPI historical series
panel = pd.read_parquet(config.PROCESSED_DIR / "panel.parquet")
kospi = panel[panel["country"] == "KOSPI"].sort_values("date")

# Read synthetic control gap CSV (written by synthetic_control.py)
gap_df = pd.read_csv(config.OUTPUT_DIR / "robustness" / "synthetic_control_gap.csv")
gap_df["date"] = pd.to_datetime(gap_df["date"])
```

**Event date import pattern** (`src/robustness/synthetic_control.py` line 125):
```python
reform_date = pd.Timestamp(config.TSE_PB_REFORM_DATE)
```
Never hardcode `"2023-03-01"` — always import from `config`.

**Figure save pattern** (`src/descriptive/figure1.py` lines 89-98 and `src/robustness/synthetic_control.py` lines 132-140 — identical across ALL scripts):
```python
output_path = config.OUTPUT_DIR / "figures" / "figure4_counterfactual_projection.pdf"
output_path.parent.mkdir(parents=True, exist_ok=True)
fig.savefig(
    output_path,
    dpi=300,
    bbox_inches="tight",
    format="pdf",
    metadata={"CreationDate": None, "ModDate": None},
)
plt.close(fig)
logging.info("Saved figure4 to %s", output_path)
```

**Figure style constraints** (verified in `src/descriptive/figure1.py` and `src/robustness/synthetic_control.py`):
- Figure size: `fig, ax = plt.subplots(figsize=(10, 5))`
- Primary series: `color="black"` or index-specific color from `colors` dict
- Dashed projection line: `linestyle="--"` (matches event-line style `linestyle="dashed"`)
- Shaded band: `ax.fill_between(..., alpha=0.15)` — consistent with existing placebo shading
- No `seaborn.set_theme()` in this script (only `figure1.py` uses it; `synthetic_control.py` does NOT)
- Event date vline: `color="grey"`, `linestyle="dashed"`, `linewidth=0.8`

**Core projection logic** (from RESEARCH.md Pattern 3):
```python
# Post-reform gap: months 1-18 after TSE_PB_REFORM_DATE
post_reform_gap = gap_df[
    (gap_df["date"] >= reform_date) &
    (gap_df["date"] <= reform_date + pd.DateOffset(months=18))
]["gap"]
monthly_lift = post_reform_gap.diff().mean()  # avg monthly P/B change

# Project forward 60 months from last KOSPI 2024 observation
kospi_2024 = kospi[kospi["date"] <= pd.Timestamp("2024-12-31")]
base_level = kospi_2024["pb"].iloc[-1]
base_date = kospi_2024["date"].iloc[-1]
proj_dates = pd.date_range(start=base_date, periods=61, freq="MS")[1:]
proj_values = base_level + monthly_lift * range(1, 61)
uncertainty = 0.2893  # RMSPE from synthetic_control_weights.csv
```

**Fail-fast guard** (identical across all scripts — `src/descriptive/figure1.py` lines 102-107):
```python
if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
```

---

### `src/policy/__init__.py` (config, package init)

**Analog:** `src/descriptive/__init__.py` (1 line, verified) and `src/robustness/__init__.py` (1 line: `# robustness package`).

**Pattern** (copy exactly from `src/robustness/__init__.py` line 1):
```python
# policy package
```

---

### `paper/main.tex` (LaTeX document, batch integration)

**Analog:** `output/tables/table2_ols.tex` — booktabs table style. All pre-generated `.tex` fragments already contain complete `\begin{table}...\end{table}` environments; use bare `\input{}` only.

**LaTeX preamble pattern** (from RESEARCH.md + `output/tables/table2_ols.tex` booktabs verification):
```latex
\documentclass[12pt]{article}

% Page geometry — NBER style
\usepackage[margin=1in]{geometry}

% Font: Times New Roman
\usepackage{newtxtext,newtxmath}

% Double spacing
\usepackage{setspace}
\doublespacing

% Bibliography — author-year
\usepackage[authoryear,round]{natbib}
\bibliographystyle{apalike}

% Tables
\usepackage{booktabs}
\usepackage{longtable}

% Figures
\usepackage{graphicx}

% Math
\usepackage{amsmath}

% Appendices
\usepackage[titletoc]{appendix}

% Captions
\usepackage{caption}

% Hyperlinks (load last)
\usepackage[hidelinks]{hyperref}
```

**Figure inclusion pattern** (relative path from `paper/` — verified via RESEARCH.md Pattern 2):
```latex
\begin{figure}[htbp]
  \centering
  \includegraphics[width=\textwidth]{../output/figures/figure1_pb_comparison.pdf}
  \caption{Index-Level P/B Ratios, 2004--2024.}
  \label{fig:figure1}
\end{figure}
```

**Table inclusion pattern** — bare `\input{}`, no wrapping `\begin{table}` (verified from `output/tables/table2_ols.tex` which starts with `\begin{table}` on line 1):
```latex
% CORRECT — fragments already contain \begin{table}...\end{table}
\input{../output/tables/table1_summary_stats.tex}
\input{../output/tables/table2_ols.tex}
\input{../output/tables/table3_geo_risk.tex}
\input{../output/tables/table_event_study_coefs.tex}

% WRONG — do NOT wrap in another \begin{table}
% \begin{table}[htbp]
%   \input{../output/tables/table2_ols.tex}
% \end{table}
```

**Bibliography pattern** — `\bibliographystyle` must precede `\bibliography`:
```latex
\bibliographystyle{apalike}
\bibliography{references}
```

**Required section order** (D-06):
1. `\begin{abstract}` (150–200 words)
2. `\section{Introduction}`
3. `\section{Institutional Background}`
4. `\section{Literature Review}`
5. `\section{Data}`
6. `\section{Causal Mechanisms}`
7. `\section{Empirical Strategy}`
8. `\section{Results}`
9. `\section{Discussion and Limitations}`
10. `\section{Conclusion}`
11. `\section{Policy Recommendations}`
12. `\begin{appendices}` ... `\end{appendices}`

---

### `paper/references.bib` (bibliography, batch)

**Analog:** `papers/REFERENCES.md` — seed content list. No direct code analog; use standard BibTeX entry types.

**BibTeX entry type pattern** — verified standard economics/finance entry types:
```bibtex
@article{baek2004,
  author  = {Baek, Jae-Seung and Kang, Jun-Koo and Park, Kyung Suh},
  title   = {Corporate governance and firm value},
  journal = {Journal of Financial Economics},
  year    = {2004},
  volume  = {71},
  number  = {2},
  pages   = {265--313},
}

@article{abadie2010,
  author  = {Abadie, Alberto and Diamond, Alexis and Hainmueller, Jens},
  title   = {Synthetic Control Methods for Comparative Case Studies},
  journal = {Journal of the American Statistical Association},
  year    = {2010},
  volume  = {105},
  number  = {490},
  pages   = {493--505},
}

@article{cengiz2019,
  author  = {Cengiz, Doruk and Dube, Arindrajit and Lindner, Attila and Zipperer, Ben},
  title   = {The Effect of Minimum Wages on Low-Wage Jobs},
  journal = {Quarterly Journal of Economics},
  year    = {2019},
  volume  = {134},
  number  = {3},
  pages   = {1405--1454},
}

@techreport{kcmi2023,
  author      = {{Korea Capital Market Institute}},
  title       = {Causes behind the Korea Discount and Policy Implications},
  institution = {Korea Capital Market Institute},
  year        = {2023},
}
```

**Citation key convention** (Claude's discretion — use `authorYYYY` lowercase): `baek2004`, `abadie2010`, `cengiz2019`, `caldara2022`, `kcmi2023`, `imf2021`, `gs2022`, `jensen1976`, `black2006`, `claessens2000`.

---

### `src/robustness/synthetic_control.py` (MODIFICATION — add gap CSV write)

**Analog:** itself (existing file, lines 115-142 — `plot_gap` function).

**Addition to `plot_gap` function** (insert after `ts_gap` is computed, before `fig, ax = plt.subplots(...)` at line 121 — from RESEARCH.md Pattern gap-CSV):
```python
# Write gap series for counterfactual_projection.py dependency
gap_df = ts_gap.reset_index()
gap_df.columns = ["date", "gap"]
gap_df.to_csv(ROBUSTNESS_DIR / "synthetic_control_gap.csv", index=False)
logging.info("Saved synthetic_control_gap.csv")
```

---

### `tests/test_phase5.py` (test, smoke)

**Analog:** `tests/test_phase4.py` — exact match for test structure, imports, PROJECT_ROOT pattern.

**Imports and PROJECT_ROOT pattern** (`tests/test_phase4.py` lines 1-19):
```python
"""
tests/test_phase5.py - Smoke and unit tests for Phase 5 paper assembly outputs.

Run: pytest tests/test_phase5.py -x -q
"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import config

FIGURES_DIR = config.OUTPUT_DIR / "figures"
TABLES_DIR = config.OUTPUT_DIR / "tables"
ROBUSTNESS_DIR = config.OUTPUT_DIR / "robustness"
PAPER_DIR = PROJECT_ROOT / "paper"
```

**Output existence test pattern** (`tests/test_phase4.py` lines 32-42):
```python
def test_counterfactual_figure_exists():
    """POLICY-02: figure4_counterfactual_projection.pdf must exist and be non-empty."""
    path = FIGURES_DIR / "figure4_counterfactual_projection.pdf"
    assert path.exists(), f"Missing: {path}"
    assert path.stat().st_size > 0

def test_all_figures_exist():
    """OUTPUT-01: All expected figures must exist."""
    expected = [
        "figure1_pb_comparison.pdf",
        "figure2_event_study.pdf",
        "figure3_geo_risk.pdf",
        "figure_synth_gap.pdf",
        "figure4_counterfactual_projection.pdf",
    ]
    for fname in expected:
        p = FIGURES_DIR / fname
        assert p.exists(), f"Missing figure: {p}"
```

**Section presence test pattern** (structural check for required sections):
```python
def test_required_sections_present():
    """PAPER-01–10: Required section headings must appear in main.tex."""
    tex = (PAPER_DIR / "main.tex").read_text()
    required = [
        r"\section{Introduction}",
        r"\section{Institutional Background}",
        r"\section{Literature Review}",
        r"\section{Data}",
        r"\section{Causal Mechanisms}",
        r"\section{Empirical Strategy}",
        r"\section{Results}",
        r"\section{Discussion",
        r"\section{Conclusion}",
        r"\section{Policy Recommendations}",
    ]
    for heading in required:
        assert heading in tex, f"Missing section: {heading}"
```

---

## Shared Patterns

### Script structure (apply to `counterfactual_projection.py`)

**Source:** Every existing script — `src/descriptive/figure1.py`, `src/descriptive/table1.py`, `src/analysis/panel_ols.py`, `src/robustness/synthetic_control.py`

**Apply to:** `src/policy/counterfactual_projection.py`

Canonical 3-part structure present in all scripts:
1. Module docstring stating outputs
2. `logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s", stream=sys.stdout)` (lines 25-29 of `figure1.py`)
3. `if __name__ == "__main__": try: main() except Exception as exc: print(f"ERROR: {exc}", file=sys.stderr); sys.exit(1)` (lines 102-107 of `figure1.py`)

### Config import firewall (apply to all new Python files)

**Source:** `config.py` lines 1-15 (docstring) + every existing script

**Apply to:** `run_all.py`, `src/policy/counterfactual_projection.py`

```python
# FIREWALL: always import event dates from config, never hardcode
import config
reform_date = pd.Timestamp(config.TSE_PB_REFORM_DATE)  # correct
# reform_date = pd.Timestamp("2023-03-01")  # WRONG — violates firewall
```

### Output directory creation (apply to `counterfactual_projection.py`)

**Source:** `src/descriptive/figure1.py` line 90, `src/descriptive/table1.py` line 69, `src/robustness/synthetic_control.py` lines 284-285

```python
output_path.parent.mkdir(parents=True, exist_ok=True)
```
Always called immediately before writing any output file.

### PDF save metadata (apply to `counterfactual_projection.py`)

**Source:** `src/descriptive/figure1.py` lines 91-97 — identical in ALL figure scripts

```python
fig.savefig(
    output_path,
    dpi=300,
    bbox_inches="tight",
    format="pdf",
    metadata={"CreationDate": None, "ModDate": None},
)
plt.close(fig)
```
The `metadata` dict suppresses timestamps for reproducible PDF output. `plt.close(fig)` is mandatory to avoid memory leaks across scripts.

---

## No Analog Found

All files have analogs in the codebase. No entries in this section.

---

## Key Numbers for Prose Authoring (verified from output files)

| Statistic | Value | Source file |
|---|---|---|
| Korea Discount vs TOPIX | −0.177x (t=−3.23, 95% CI: [−0.284x, −0.069x]) | `output/tables/discount_stats.csv` |
| Korea Discount vs MSCI EM | −0.601x (t=−10.30, 95% CI: [−0.716x, −0.486x]) | `output/tables/discount_stats.csv` |
| Stewardship Code × Japan | +0.09 [p=0.750] | `output/tables/table2_ols.tex` line 12 |
| CGC × Japan | −0.32 [p=0.375] | `output/tables/table2_ols.tex` line 13 |
| TSE P/B reform × Japan | −0.24 [p=0.500] | `output/tables/table2_ols.tex` line 14 |
| Synthetic control RMSPE | 0.2893 (single donor: MSCI_HK weight=1.0) | `output/robustness/synthetic_control_weights.csv` |
| GPR escalation coefficient | −0.02 (t=−0.84, p=0.40) | `output/tables/table3_geo_risk.tex` |
| Panel observations | 1,072 | `data/processed/panel.parquet` shape |
| KOSPI P/B mean Post-TSE | 0.93x | `output/tables/table1_summary_stats.tex` |
| TOPIX P/B mean Post-TSE | 1.36x | `output/tables/table1_summary_stats.tex` |

---

## Metadata

**Analog search scope:** `src/descriptive/`, `src/analysis/`, `src/robustness/`, `output/tables/`, `tests/`
**Files scanned:** 10 source files + 3 test files + 2 output table files
**Pattern extraction date:** 2026-04-20
