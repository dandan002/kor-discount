# Architecture Patterns

**Domain:** Reproducible academic quantitative finance research codebase (Python)
**Project:** Korea Discount Study
**Researched:** 2026-04-14
**Confidence:** HIGH — directory conventions and data flow patterns for academic Python research are stable and well-established across Cookiecutter Data Science, academic reproducibility literature, and observed norms in econometrics/finance research repos.

---

## Recommended Architecture

A linear pipeline architecture: raw data flows forward through deterministic, idempotent stages. Each stage writes outputs that the next stage reads. No stage reaches backward. The paper assembles all upstream outputs.

```
raw/                   (immutable source data — never modified)
  └── fetched files
       └──────────────────────────────────────────────────────>
                                                              data/
                                                            interim/   (cleaned, merged)
                                                           processed/  (analysis-ready panel)
                                                                └────────────────────────>
                                                                                      outputs/
                                                                                      figures/
                                                                                       tables/
                                                                                           └──>
                                                                                            paper/
```

---

## Recommended Directory Structure

```
KoreaDiscountStudy/
│
├── data/
│   ├── raw/                    # Downloaded source files. NEVER edited by hand.
│   │   ├── kospi_pb_pe.csv     # One file per source/index/metric
│   │   ├── topix_pb_pe.csv
│   │   ├── sp500_pb_pe.csv
│   │   ├── msci_em_pb_pe.csv
│   │   └── ...
│   ├── interim/                # After cleaning/normalizing, before joining
│   │   ├── kospi_clean.parquet
│   │   ├── topix_clean.parquet
│   │   ├── sp500_clean.parquet
│   │   └── msci_em_clean.parquet
│   └── processed/              # Analysis-ready joined panel
│       └── panel.parquet       # One canonical panel: (date, country, metric, value)
│
├── src/
│   ├── data/
│   │   ├── fetch.py            # Downloads raw data from APIs/FRED/Yahoo
│   │   └── build_panel.py      # Cleans, normalizes, merges -> processed/panel.parquet
│   │
│   ├── analysis/
│   │   ├── descriptive.py      # Summary stats, discount magnitude over time
│   │   ├── event_study.py      # Staggered event study: CAR around 2014/2015/2023
│   │   ├── panel_ols.py        # Fixed effects OLS + reform interaction dummies
│   │   └── synthetic_control.py# Synthetic control for 2023 TSE reform
│   │
│   └── viz/
│       ├── figures.py          # All figure generation (called by run_all or notebooks)
│       └── tables.py           # All LaTeX table generation
│
├── outputs/
│   ├── figures/                # .pdf and .png figures (committed or .gitignored, project preference)
│   │   ├── fig1_discount_timeseries.pdf
│   │   ├── fig2_event_study_car.pdf
│   │   ├── fig3_panel_coefs.pdf
│   │   └── fig4_synthetic_control.pdf
│   └── tables/                 # .tex table fragments included by paper
│       ├── tab1_descriptive_stats.tex
│       ├── tab2_panel_ols.tex
│       └── tab3_event_study.tex
│
├── notebooks/                  # Exploration and narrative — NOT the canonical run path
│   ├── 01_data_exploration.ipynb
│   ├── 02_descriptive_analysis.ipynb
│   ├── 03_event_study.ipynb
│   ├── 04_panel_ols.ipynb
│   └── 05_synthetic_control.ipynb
│
├── paper/
│   ├── main.tex                # Master LaTeX document
│   ├── sections/
│   │   ├── introduction.tex
│   │   ├── data.tex
│   │   ├── methods.tex
│   │   ├── results.tex
│   │   └── conclusion.tex
│   ├── references.bib
│   └── figures/                # Symlinks or copies from outputs/figures/
│
├── tests/
│   ├── test_build_panel.py     # Assert panel shape, no nulls in required cols, date coverage
│   ├── test_event_study.py     # Assert output shapes, CAR column exists, dates match
│   └── test_panel_ols.py       # Assert coefficient table keys, no NaN coefs
│
├── run_all.py                  # Top-level orchestration script: runs all stages in order
├── Makefile                    # Optional: `make data`, `make analysis`, `make paper`
├── requirements.txt            # Pinned dependencies
├── environment.yml             # Conda environment (preferred for scientific stack)
└── README.md
```

---

## Component Boundaries

| Component | Responsibility | Reads From | Writes To |
|-----------|---------------|------------|-----------|
| `src/data/fetch.py` | Download raw source files | External APIs, FRED, Yahoo | `data/raw/` |
| `src/data/build_panel.py` | Clean, normalize, merge all sources into one panel | `data/raw/` | `data/interim/`, `data/processed/panel.parquet` |
| `src/analysis/descriptive.py` | Compute discount magnitude, summary stats | `data/processed/panel.parquet` | `outputs/tables/tab1_*.tex`, in-memory DataFrames passed to viz |
| `src/analysis/event_study.py` | CAR computation around 2014/2015/2023 dates | `data/processed/panel.parquet` | In-memory results, `outputs/tables/tab3_*.tex` |
| `src/analysis/panel_ols.py` | Fixed effects regression + interaction terms | `data/processed/panel.parquet` | `outputs/tables/tab2_*.tex`, coefficient objects |
| `src/analysis/synthetic_control.py` | Donor pool construction, weights, gap plot for 2023 | `data/processed/panel.parquet` | `outputs/figures/fig4_*.pdf`, robustness table |
| `src/viz/figures.py` | Render all paper figures to file | Analysis outputs (DataFrames/dicts passed in) | `outputs/figures/` |
| `src/viz/tables.py` | Render LaTeX table strings to .tex | Analysis outputs | `outputs/tables/` |
| `paper/main.tex` | Assemble prose + `\input{}` figure and table files | `outputs/figures/`, `outputs/tables/` | `paper/main.pdf` |
| `run_all.py` | Execute all stages end-to-end in dependency order | Nothing (orchestrator) | Triggers all above |

**Rule:** Analysis modules NEVER import from `viz`. Viz modules NEVER import from `analysis`. Both receive data as arguments or read from `processed/`. This keeps figure code testable independently.

---

## Data Flow

```
[External Sources]
  FRED, Yahoo Finance, Bloomberg export, OECD
        |
        | fetch.py (HTTP requests, file download)
        v
[data/raw/]  <-- Immutable. If a source changes, re-fetch but do not edit in place.
        |
        | build_panel.py
        |   - Parse each source into consistent schema: (date, country, metric, value)
        |   - Handle missing periods, forward-fill where appropriate (document decisions)
        |   - Normalize index names to: KOSPI, TOPIX, SP500, MSCI_EM
        |   - Write per-source cleaned files to interim/
        |   - Merge on (date, country) -> panel.parquet
        v
[data/processed/panel.parquet]
  Columns: date (monthly, datetime), country (str), pb (float), pe (float), [ev_ebitda (float)]
  Rows: ~20 years * 12 months * 4 countries = ~960 rows (plus any sub-monthly if daily)
        |
        |----> descriptive.py  -----> summary stats + discount timeseries
        |----> event_study.py  -----> event windows [-12, +12] months around 3 dates
        |----> panel_ols.py    -----> regression table: country FE + time FE + interactions
        |----> synthetic_control.py --> donor weights + counterfactual gap
        |
        v
[Analysis objects: DataFrames, dicts, statsmodels RegressionResults]
        |
        | figures.py + tables.py (receive analysis objects as arguments)
        v
[outputs/figures/*.pdf]   [outputs/tables/*.tex]
        |                         |
        +-------------------------+
                    |
                    | \input{} and \includegraphics{} in paper/main.tex
                    v
              [paper/main.pdf]
```

---

## Suggested Build Order (with dependencies)

Build order is strictly forward — each stage depends only on what was already built.

```
Stage 1: Environment
  Install requirements.txt / environment.yml
  No code dependencies.

Stage 2: Data acquisition
  Run: src/data/fetch.py
  Depends on: Stage 1, network access
  Output: data/raw/

Stage 3: Panel construction
  Run: src/data/build_panel.py
  Depends on: Stage 2 (data/raw/ populated)
  Output: data/processed/panel.parquet
  CRITICAL PATH: Everything downstream blocks on this.

Stage 4a: Descriptive analysis
  Run: src/analysis/descriptive.py
  Depends on: Stage 3

Stage 4b: Event study
  Run: src/analysis/event_study.py
  Depends on: Stage 3

Stage 4c: Panel OLS
  Run: src/analysis/panel_ols.py
  Depends on: Stage 3

Stage 4d: Synthetic control
  Run: src/analysis/synthetic_control.py
  Depends on: Stage 3
  NOTE: 4a–4d are independent of each other and can run in any order.

Stage 5: Outputs
  Run: src/viz/figures.py + src/viz/tables.py
  Depends on: Stages 4a–4d (all analysis complete)
  Output: outputs/figures/, outputs/tables/

Stage 6: Paper compilation
  Run: pdflatex paper/main.tex (or latexmk)
  Depends on: Stage 5 (figures and tables present)
  Output: paper/main.pdf
```

`run_all.py` encodes this order. A `Makefile` with targets `make data`, `make analysis`, `make paper` is a worthwhile addition for granular re-running.

---

## File Format Conventions

### Parquet over CSV for processed data

Use `.parquet` for `interim/` and `processed/`. Rationale:
- Preserves dtypes (especially datetime and float precision) across read/write cycles without configuration
- ~5-10x faster read than CSV for 1000-row panels (negligible here but instills good habit)
- Compressed by default; no accidental whitespace/encoding issues
- `pd.read_parquet()` / `df.to_parquet()` require only `pyarrow` (already a pandas dependency)

Use `.csv` ONLY for `data/raw/` files that arrive as CSV from sources (e.g., FRED exports). Do not re-save raw files in any other format — keep them exactly as downloaded.

### Scripts over Notebooks as the canonical run path

Use `.py` scripts in `src/` as the authoritative execution path. Rationale:
- Scripts are diffable in git — you can see exactly what changed between runs
- Scripts can be imported, tested, and called from `run_all.py` without kernel state concerns
- Notebooks carry hidden state: cell execution order bugs are invisible in version control
- Academic reviewers and replication auditors can run `python run_all.py` without Jupyter

Use notebooks in `notebooks/` for exploration, narrative, and "show your work" documentation only. They should import from `src/` rather than re-implementing logic. A clean repo has notebooks that are readable but not required for reproduction.

### Figure format: PDF for paper, PNG for quick review

Save figures as `.pdf` for inclusion in LaTeX (vector, no resolution loss). Also save `.png` at 150dpi for README display and quick visual QC. `matplotlib.figure.savefig()` accepts both in one pass.

### Table format: .tex fragments

Save tables as `.tex` files containing only the `tabular` environment (no surrounding `\begin{table}` boilerplate). The paper's `.tex` files wrap them with `\begin{table}[h]\caption{...}\input{outputs/tables/tab1.tex}\end{table}`. This keeps table formatting decisions in the paper layer, not the analysis layer.

---

## Patterns to Follow

### Pattern 1: One canonical panel, long format

Build a single long-format panel file: `(date, country, metric, value)` or equivalently `(date, country, pb, pe)`. All analysis reads from this one file. Do not maintain separate wide-format files for different analyses — they diverge silently.

```python
# processed/panel.parquet schema
# date: datetime64[ns], monthly frequency
# country: str in {"KOSPI", "TOPIX", "SP500", "MSCI_EM"}
# pb: float64 (price-to-book)
# pe: float64 (price-to-earnings)
# ev_ebitda: float64 (nullable — not all sources provide this)
```

### Pattern 2: Idempotent stage scripts

Every `src/` script can be re-run safely. It overwrites its outputs rather than appending. This means:
- `build_panel.py` deletes and rewrites `panel.parquet` on each run
- Figure scripts overwrite existing PDFs

This prevents stale output confusion during iterative development.

### Pattern 3: Configuration over hardcoded constants

Store event dates, country lists, window widths, and figure dimensions in a single `config.py` or `config.yaml`. All scripts import from it. When a reviewer asks "what window did you use for the event study?" the answer is in one place.

```python
# config.py
EVENT_DATES = {
    "stewardship_code": "2014-02-01",
    "corporate_governance_code": "2015-06-01",
    "tse_pb_reform": "2023-03-01",
}
COUNTRIES = ["KOSPI", "TOPIX", "SP500", "MSCI_EM"]
EVENT_WINDOW_MONTHS = (-12, 12)
FIGURE_DPI = 150
```

### Pattern 4: Analysis functions return objects, side effects in runner

Analysis scripts expose functions that return DataFrames or result objects. The `if __name__ == "__main__"` block (or `run_all.py`) handles writing to disk. This makes functions testable without writing files during tests.

```python
# src/analysis/event_study.py
def compute_car(panel: pd.DataFrame, event_dates: dict, window: tuple) -> pd.DataFrame:
    ...
    return car_df  # no file I/O

if __name__ == "__main__":
    panel = pd.read_parquet("data/processed/panel.parquet")
    car = compute_car(panel, EVENT_DATES, EVENT_WINDOW_MONTHS)
    car.to_parquet("outputs/event_study_results.parquet")
```

---

## Anti-Patterns to Avoid

### Anti-Pattern 1: Notebooks as the canonical pipeline

If `run_all.py` calls `jupyter nbconvert --execute notebook.ipynb`, the pipeline is fragile (kernel state, hidden cell order, output bloat in git). Keep notebooks for exploration. Scripts for reproduction.

### Anti-Pattern 2: Mutable raw data

Never write to `data/raw/`. If cleaning requires judgment calls (e.g., dropping a data point), make that decision in `build_panel.py` with a comment, not by editing the source file. Reviewers must be able to verify the transformation chain.

### Anti-Pattern 3: Analysis logic in figure scripts

Figure scripts should receive already-computed results and only handle rendering. If `figures.py` is doing regression or computing CARs, the logic is untestable and non-reusable.

### Anti-Pattern 4: Wide-format intermediate files per analysis

Do not create `kospi_event_study.csv`, `topix_event_study.csv` separately. One panel, filtered in code. Separate files diverge when the cleaning logic changes.

### Anti-Pattern 5: Hardcoded paths

Use `pathlib.Path` relative to a project root constant. Never hardcode `/Users/dandan/...`.

```python
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]  # from src/analysis/ up to project root
PANEL_PATH = ROOT / "data" / "processed" / "panel.parquet"
```

---

## Scalability Considerations

This is a ~960-row monthly panel. Scalability is not a concern. All operations fit in memory with trivial margin. The architecture is designed for reproducibility and auditability, not scale.

| Concern | At current scale (~1K rows) | Note |
|---------|----------------------------|------|
| Memory | Trivially fits in RAM | Parquet is still preferred for dtype safety |
| Runtime | Full pipeline runs in < 2 minutes | No caching or parallelism needed |
| Storage | < 10 MB for all data and outputs | Commit outputs to git is feasible |

---

## Paper Integration

LaTeX is the correct choice for academic submission. The integration pattern:

1. `paper/main.tex` uses `\input{../outputs/tables/tab1_descriptive_stats.tex}` for tables
2. `paper/main.tex` uses `\includegraphics{../outputs/figures/fig1_discount_timeseries.pdf}` for figures
3. Tables are generated as bare `tabular` environments so caption/label/positioning is controlled in LaTeX
4. `latexmk -pdf paper/main.tex` compiles the full document in one command

This means a full reproduction is:
```bash
python run_all.py        # data -> analysis -> figures -> tables
latexmk -pdf paper/main.tex  # figures + tables -> PDF
```

Two commands, reproducible from scratch.

---

## Sources

- Cookiecutter Data Science project structure (drivendata.org): well-established convention for this directory layout
- Academic reproducibility standards: Gentzkow & Shapiro (2014) "Code and Data for the Social Sciences" — scripts over notebooks, immutable raw data, idempotent pipelines
- Python packaging conventions: `src/` layout preferred over flat layout for importability and test isolation
- Confidence: HIGH — these are structural conventions that have been stable for 5+ years and are not library-version-dependent
