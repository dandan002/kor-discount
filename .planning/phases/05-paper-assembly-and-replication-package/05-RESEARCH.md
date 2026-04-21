# Phase 5: Paper Assembly and Replication Package - Research

**Researched:** 2026-04-20
**Domain:** LaTeX document authoring, Python replication orchestration, counterfactual projection
**Confidence:** HIGH

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- **D-01:** Claude writes full, publication-quality prose for every section — abstract, introduction, institutional background, literature review, data, causal mechanisms, empirical strategy, discussion/limitations, conclusion, appendices. No placeholders.
- **D-02:** Numbers embedded directly from actual output files (`output/tables/`, `output/robustness/`). No `\newcommand` macro infrastructure. Key numbers: Korea Discount −0.177x vs TOPIX (t=−3.23, 95% CI: −0.284x to −0.069x), −0.601x vs MSCI EM (t=−10.30); Panel OLS: stewardship +0.09 [p=0.750], CGC −0.32 [p=0.375], TSE P/B reform −0.24 [p=0.500] (wild-bootstrap p-values); Synthetic control pre-treatment RMSPE: 0.2893; all CAR figures reference `output/tables/event_study_car.csv`.
- **D-03:** `\documentclass[12pt]{article}` with NBER-style geometry — 1-inch margins, Times New Roman font, double-spaced, A4 or letter.
- **D-04:** Paper lives in `paper/` directory (does not exist yet). Main file: `paper/main.tex`. Figures/tables included via `\includegraphics{../output/figures/}` and `\input{../output/tables/}` (relative paths from `paper/`).
- **D-05:** BibTeX: `paper/references.bib` created from scratch. All citations for Korea Discount priors, Japan governance reform studies, Cengiz et al. 2019, ADH 2010, Caldara-Iacoviello GPR index, governance-valuation literature (~30–50 entries). Citation style: `\bibliographystyle{apa}` or similar author-year.
- **D-06:** Required sections in `main.tex`: Abstract (150–200 words), Introduction (3–5 pp), Institutional Background (3–5 pp), Literature Review (3–6 pp), Data (2–4 pp), Causal Mechanisms (2–4 pp), Empirical Strategy (1–2 pp), Results, Discussion/Limitations (1–2 pp), Conclusion (1–2 pp), Policy Recommendations (2–3 pp), Appendices.
- **D-07:** `run_all.py` at repo root regenerates all figures and tables from `data/processed/panel.parquet` (and `data/raw/` for GPR series). Does NOT re-run `build_panel.py`. Two-command workflow: `pip install -r requirements.txt` then `python run_all.py`.
- **D-08:** Fail fast — any script that exits non-zero stops `run_all.py` immediately with a clear error naming the failed script. No continue-on-error.
- **D-09:** Execution order: descriptive → event study → panel OLS → geo risk → synthetic control → robustness (placebo, P/E, alt-control) → counterfactual projection. Each is `subprocess.run([sys.executable, "src/..."], check=True)`.
- **D-10:** `run_all.py` prints step banner before each script (`\n=== [1/N] Running descriptive analysis ===`) and `All outputs regenerated successfully.` on completion.
- **D-11:** Counterfactual method: apply Japan's observed post-2023 TSE reform P/B lift to Korea. Measure average monthly TOPIX P/B change in 12–18 months post-reform from synthetic control gap, then project KOSPI P/B on same trajectory starting from 2024 level. Clearly labeled "Illustrative projection."
- **D-12:** Counterfactual output: `output/figures/figure4_counterfactual_projection.pdf` — KOSPI P/B historical solid line through 2024, dashed projection ~5 years forward, shaded uncertainty band. PDF, consistent with Figures 1–3 style.
- **D-13:** Script: `src/policy/counterfactual_projection.py` — reads `data/processed/panel.parquet` + `output/robustness/synthetic_control_weights.csv`, computes projection, writes figure. Included in `run_all.py` execution order.

### Claude's Discretion

- Exact section lengths and subsection structure within the prose constraints above
- BibTeX citation key naming convention
- Exact citation-count target for the literature review
- Whether the Results section is a standalone section or folds into the empirical strategy section
- Shaded uncertainty band width for the counterfactual projection figure (e.g., ±1 RMSPE or ±1 SD of post-reform gap)
- Exact LaTeX packages (geometry, fontenc, natbib, booktabs, graphicx, hyperref, etc.)

### Deferred Ideas (OUT OF SCOPE)

- LaTeX `\newcommand` macro infrastructure
- DVC pipeline for end-to-end data versioning (v2 requirement REP-V2-01)
- CI/CD reproducibility verification (v2 requirement REP-V2-02)
- Full end-to-end `run_all.py` including `build_panel.py`
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| PAPER-01 | Abstract (150–200 words) with research question, methods, and key discount magnitude | Exact numbers verified in `output/tables/discount_stats.csv`; −0.177x vs TOPIX (t=−3.23), −0.601x vs MSCI EM (t=−10.30) |
| PAPER-02 | Introduction (3–5 pages) with motivation, contribution, key numbers, paper structure | Numbers table fully populated from existing outputs; all available from LaTeX/CSV fragments |
| PAPER-03 | Institutional background (3–5 pages): chaebol mechanics, FSC/KRX history, Japan three reform dates, NK risk | Reform dates locked in `config.py`; context in `papers/LITERATURE_REVIEW.md` |
| PAPER-04 | Literature review (3–6 pages): Korea Discount, Japan governance event studies, governance-valuation, natural experiments | Seed references in `papers/REFERENCES.md` and `papers/LITERATURE_REVIEW.md`; BibTeX to be constructed |
| PAPER-05 | Data section (2–4 pages): sources, coverage, variable construction, survivorship bias, missing data | `data/raw/MANIFEST.md` documents provenance; `panel.parquet` schema (date, country, pb, pe), 1,072 observations, 4 countries, 2004–2024 |
| PAPER-06 | Causal mechanisms (2–4 pages): chaebol opacity, minority-shareholder recourse deficit, geopolitical risk premium | GPR coefficient from `output/tables/table3_geo_risk.tex`: −0.02 (t=−0.84, p=0.40); literature supports three-channel framing |
| PAPER-07 | Empirical strategy (1–2 pages): estimating equations for event study, panel OLS, synthetic control | Equations derived from `panel_ols.py`, `event_study.py`, `synthetic_control.py` |
| PAPER-08 | Discussion/limitations (1–2 pages): single treated unit, Abenomics confound, Japan→Korea generalizability | Single-donor caveat (MSCI_HK weight=1.0, RMSPE=0.2893) documented; wild-bootstrap p-values all >0.35 for N=4 cluster |
| PAPER-09 | Conclusion (1–2 pages): findings, contributions, future work | All key results available |
| PAPER-10 | Appendices: variable definitions and overflow robustness tables | 6 robustness `.tex` fragments available in `output/robustness/` |
| POLICY-01 | Policy section (2–3 pages): FSC, KRX, stewardship code levers | Context in `papers/LITERATURE_REVIEW.md` (Korea Value-Up program, Commercial Act 2025) |
| POLICY-02 | Counterfactual projection: Japan-calibrated illustrative projection for Korea | New script `src/policy/counterfactual_projection.py`; reads `panel.parquet` + `synthetic_control_weights.csv` |
| OUTPUT-01 | All figures and tables generated programmatically | Verified: all 4 figures + 4 tables + 6 robustness files already in `output/` |
| OUTPUT-02 | Paper compiled as PDF via LaTeX | `latexmk` 4.83 and `pdflatex` (TeX Live 2024) confirmed available on machine |
| OUTPUT-03 | Replication package: `run_all.py` regenerates all figures and tables from raw data | New file; 9 scripts to orchestrate in dependency order |
</phase_requirements>

---

## Summary

Phase 5 is an assembly and authoring phase with no new econometric analyses. All empirical outputs — four figures, four tables, six robustness fragments — already exist in `output/`. The work divides into four concrete deliverables: (1) `paper/` directory with a compiling `main.tex` (LaTeX prose + figure/table integration), (2) `paper/references.bib` (~30–50 entries), (3) `src/policy/counterfactual_projection.py` producing `output/figures/figure4_counterfactual_projection.pdf`, and (4) `run_all.py` at repo root orchestrating all nine existing analysis scripts in dependency order.

The LaTeX toolchain is fully available on the machine: `latexmk` 4.83, `pdflatex` (TeX Live 2024), `xelatex` (TeX Live 2024). All analysis outputs have been verified to exist and contain the expected data. The counterfactual projection script is the only new Python code required. The synthetic control gap series provides the Japan P/B lift estimate needed for the projection: post-March-2023 gap values from the `_gaps()` output show TOPIX lifting above synthetic Japan. That lift, averaged over months 1–18 post-reform, is applied to KOSPI's 2024 P/B level (~0.93x per `table1_summary_stats.tex`).

The primary planning risk is prose completeness: the paper has 10+ required sections spanning approximately 35–50 pages. Plans must allocate dedicated tasks per section cluster rather than attempting the full paper in one pass. The BibTeX file is a distinct sub-deliverable that should be drafted early since `\cite{}` calls will be woven through all prose sections.

**Primary recommendation:** Structure plans as section clusters (scaffold → BibTeX → section prose batches → counterfactual script → run_all.py → compilation verification), not as a single "write the paper" task.

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| LaTeX prose authoring | File system (paper/) | — | Static document generation; no runtime service |
| Figure/table integration | LaTeX (paper/main.tex) | Output files (output/) | Figures are pre-generated PDFs; `\includegraphics` / `\input` references |
| Counterfactual projection | Python script (src/policy/) | output/figures/ | Follows existing fan-out pattern; reads parquet, writes PDF |
| Replication orchestration | run_all.py (repo root) | src/* scripts | Single entry point invoking all analysis scripts via subprocess |
| Bibliography | paper/references.bib | main.tex | BibTeX; compiled by pdflatex/bibtex/latexmk |
| PDF compilation | latexmk / pdflatex | paper/ | CLI tool invocation; TeX Live 2024 available |

---

## Standard Stack

### Core

| Library/Tool | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| `latexmk` | 4.83 (TeX Live 2024) | Automated LaTeX compilation (handles bibtex, reruns) | De facto standard for economics papers; handles multi-pass compilation automatically |
| `pdflatex` | TeX Live 2024 | PDF typesetting engine | Required by `\documentclass[12pt]{article}`; Times font and geometry work cleanly with pdflatex |
| `matplotlib` | 3.9.2 (pinned) | Counterfactual projection figure | Already used by all existing figure scripts; must match style |
| `pandas` | 2.2.3 (pinned) | Read parquet + CSVs for counterfactual script | Already in requirements.txt |
| `pyarrow` | 15.0.2 (pinned) | Parquet reading backend | Already in requirements.txt |
| `subprocess` (stdlib) | Python 3.12 | Script orchestration in run_all.py | Standard library; no extra dependency |

[VERIFIED: Bash — `latexmk --version`, `pdflatex --version`, `python3 --version`]

### LaTeX Packages (for main.tex preamble)

| Package | Purpose | Notes |
|---------|---------|-------|
| `geometry` | 1-inch margins, page size | Standard NBER style |
| `newtxtext` / `newtxmath` | Times New Roman body + matching math | Better than `times` alone; provides consistent math font [ASSUMED] |
| `setspace` | Double spacing | `\doublespacing` |
| `natbib` | Author-year citations (`\citep`, `\citet`) | Preferred for economics; works with `\bibliographystyle{apalike}` or `apa` |
| `booktabs` | Publication-quality tables | Already used in `table2_ols.tex` [VERIFIED: grep of table2_ols.tex] |
| `graphicx` | `\includegraphics` | Required for PDF figure inclusion |
| `hyperref` | PDF bookmarks and links | Load last in preamble |
| `amsmath` | Estimating equations | Aligned environments |
| `caption` | Caption formatting | Subfigure and table caption control |
| `appendix` | Appendix environment | `\begin{appendices}` |

### Supporting

| Library | Purpose | When to Use |
|---------|---------|-------------|
| `xelatex` | Alternative engine if font issues arise | Fallback if `newtxtext` causes issues; `xelatex` handles system fonts natively |
| `bibtex` | Bibliography processing | Called automatically by `latexmk`; no manual invocation needed |

**Installation:**
```bash
# TeX Live 2024 already installed — no installation needed
# Python deps already pinned in requirements.txt — no additions needed
```

**Version verification:** [VERIFIED: Bash — all tools confirmed present at versions listed above]

---

## Architecture Patterns

### System Architecture Diagram

```
data/raw/ + data/processed/panel.parquet
          |
          v
run_all.py (repo root)
    |--- subprocess: src/descriptive/figure1.py      --> output/figures/figure1_pb_comparison.pdf
    |                src/descriptive/table1.py        --> output/tables/table1_summary_stats.tex
    |                src/descriptive/discount_stats.py --> output/tables/discount_stats.*
    |--- subprocess: src/analysis/event_study.py      --> output/figures/figure2_event_study.pdf
    |                                                  --> output/tables/event_study_car.csv
    |                                                  --> output/tables/table_event_study_coefs.tex
    |--- subprocess: src/analysis/panel_ols.py        --> output/tables/table2_ols.tex
    |--- subprocess: src/analysis/geo_risk.py         --> output/figures/figure3_geo_risk.pdf
    |                                                  --> output/tables/table3_geo_risk.tex
    |--- subprocess: src/robustness/synthetic_control.py --> output/figures/figure_synth_gap.pdf
    |                                                     --> output/robustness/synthetic_control_weights.csv
    |--- subprocess: src/robustness/robustness_placebo.py   --> output/robustness/figure_placebo_*.pdf
    |--- subprocess: src/robustness/robustness_pe.py        --> output/robustness/robustness_pe_*.tex
    |--- subprocess: src/robustness/robustness_alt_control.py --> output/robustness/robustness_alt_*.tex
    |--- subprocess: src/policy/counterfactual_projection.py --> output/figures/figure4_counterfactual_projection.pdf
          |
          v
       [all outputs in output/]
          |
          v
latexmk -pdf paper/main.tex
    paper/main.tex
        \input{../output/tables/table1_summary_stats.tex}
        \input{../output/tables/table2_ols.tex}
        \input{../output/tables/table3_geo_risk.tex}
        \input{../output/tables/table_event_study_coefs.tex}
        \input{../output/robustness/*.tex}
        \includegraphics{../output/figures/figure1_pb_comparison.pdf}
        \includegraphics{../output/figures/figure2_event_study.pdf}
        \includegraphics{../output/figures/figure3_geo_risk.pdf}
        \includegraphics{../output/figures/figure_synth_gap.pdf}
        \includegraphics{../output/figures/figure4_counterfactual_projection.pdf}
    paper/references.bib  <-- bibliography database
          |
          v
     paper/main.pdf  (final output)
```

### Recommended Project Structure

```
paper/                      # New directory (does not exist yet)
├── main.tex                # Master LaTeX file; all \input{} and \includegraphics{} here
└── references.bib          # BibTeX database (~30-50 entries)

src/
└── policy/                 # New package (does not exist yet)
    ├── __init__.py
    └── counterfactual_projection.py

run_all.py                  # New file at repo root
```

### Pattern 1: run_all.py Subprocess Fan-Out

**What:** Orchestrate all analysis scripts via `subprocess.run([sys.executable, path], check=True)`. Fail fast on first non-zero exit. Print step banner before each call.

**When to use:** Replication entry points where each script is self-contained; avoids Python module import side effects across scripts with different logging configurations.

```python
# Established pattern from existing scripts: all use sys.exit(1) on exception
import subprocess
import sys

SCRIPTS = [
    ("descriptive analysis", "src/descriptive/figure1.py"),
    ("descriptive analysis", "src/descriptive/table1.py"),
    ("discount statistics", "src/descriptive/discount_stats.py"),
    ("event study", "src/analysis/event_study.py"),
    ("panel OLS", "src/analysis/panel_ols.py"),
    ("geopolitical risk", "src/analysis/geo_risk.py"),
    ("synthetic control", "src/robustness/synthetic_control.py"),
    ("placebo falsification", "src/robustness/robustness_placebo.py"),
    ("P/E robustness", "src/robustness/robustness_pe.py"),
    ("alt control robustness", "src/robustness/robustness_alt_control.py"),
    ("counterfactual projection", "src/policy/counterfactual_projection.py"),
]

for i, (label, script) in enumerate(SCRIPTS, 1):
    print(f"\n=== [{i}/{len(SCRIPTS)}] Running {label} ===")
    result = subprocess.run([sys.executable, script], check=True)

print("\nAll outputs regenerated successfully.")
```

### Pattern 2: LaTeX Figure/Table Integration

**What:** `\includegraphics{}` for PDF figures; `\input{}` for pre-formatted `.tex` table fragments. Paths relative from `paper/` directory.

```latex
% Figures (pre-generated PDFs)
\begin{figure}[htbp]
  \centering
  \includegraphics[width=\textwidth]{../output/figures/figure1_pb_comparison.pdf}
  \caption{Index-Level P/B Ratios, 2004--2024.}
  \label{fig:figure1}
\end{figure}

% Tables (pre-formatted LaTeX fragments with \begin{table}...\end{table} already included)
\input{../output/tables/table1_summary_stats.tex}
```

**Important:** Existing `.tex` fragments (`table1_summary_stats.tex`, `table2_ols.tex`, `table3_geo_risk.tex`) already include `\begin{table}`, `\caption{}`, `\label{}`, and `\end{table}`. Use `\input{}` directly — do not wrap in another `\begin{table}` environment.

[VERIFIED: Inspection of `output/tables/table1_summary_stats.tex`, `table2_ols.tex`, `table3_geo_risk.tex`]

### Pattern 3: Counterfactual Projection Script

**What:** Read synthetic control gap series post-March-2023 to measure TOPIX's average monthly P/B lift above synthetic Japan. Apply that lift rate to KOSPI's 2024 P/B level (~0.93x) projected 5 years forward. Shaded band using ±1 RMSPE (=0.2893) as uncertainty.

```python
# src/policy/counterfactual_projection.py skeleton
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))
import config

# Read panel for KOSPI historical series
panel = pd.read_parquet(config.PROCESSED_DIR / "panel.parquet")
kospi = panel[panel["country"] == "KOSPI"].sort_values("date")

# Read synthetic control gap
# Re-derive post-reform gap from synthetic_control_weights.csv is not sufficient;
# the script must either re-run synth OR read from a saved gap CSV.
# DECISION REQUIRED: Save gap series as output/robustness/synthetic_control_gap.csv
# in run_all.py execution (synthetic_control.py must be updated to write this CSV),
# OR counterfactual_projection.py re-derives via pysyncon directly.
# Recommended: save gap CSV in synthetic_control.py (minimal change).

# Average monthly P/B lift in months 1-18 post-reform
# Apply to KOSPI 2024 level, project forward 60 months
# Write PDF to output/figures/figure4_counterfactual_projection.pdf
```

**Integration dependency (CRITICAL):** The counterfactual projection script needs the post-reform P/B gap series from the synthetic control. Two options:

1. **Option A (recommended):** Modify `src/robustness/synthetic_control.py` to also write `output/robustness/synthetic_control_gap.csv` (gap series with date and gap columns). Counterfactual script reads this CSV.
2. **Option B:** Counterfactual script re-runs the synthetic control optimization internally (slow, ~minutes, introduces pysyncon dependency in policy package).

Option A is preferred: minimal change to existing script, no performance penalty.

### Pattern 4: Existing Figure Style (for Figure 4 consistency)

All existing figures use:
- `matplotlib.use("Agg")` (headless backend)
- `fig.savefig(..., dpi=300, bbox_inches="tight", format="pdf", metadata={"CreationDate": None, "ModDate": None})`
- No `seaborn.set_theme()` in analysis scripts (only `figure1.py` uses seaborn whitegrid)
- Color palette: black for primary series, grey for event lines, lightgrey for placebo series
- Figure size typically `(10, 5)`

[VERIFIED: Inspection of `src/descriptive/figure1.py`, `src/robustness/synthetic_control.py`]

### Anti-Patterns to Avoid

- **Wrapping pre-formatted table fragments:** The existing `.tex` files already contain complete `\begin{table}...\end{table}` environments. Using `\input{}` inside another `\begin{table}` block causes double-environment errors.
- **Hardcoding event dates in counterfactual script:** Must import from `config.py` per the event dates firewall (`config.TSE_PB_REFORM_DATE`).
- **`subprocess.run` without `check=True`:** Silent failures would defeat the fail-fast requirement (D-08).
- **`sys.executable` omission:** Using `"python"` instead of `sys.executable` will invoke the wrong Python in environments with multiple Python installations.
- **`\bibliographystyle{}` placed after `\bibliography{}`:** Must precede `\bibliography{references}` for bibtex to apply correctly.
- **Relative path breakage in LaTeX:** `../output/figures/` works only when `latexmk` is run from the `paper/` directory OR with `-cd` flag. Standard invocation `latexmk -pdf paper/main.tex` from repo root requires using `paper/main.tex` — latexmk changes to the file's directory before processing. [VERIFIED: latexmk documentation behavior; [ASSUMED] -cd flag behavior in latexmk 4.83]

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Multi-pass LaTeX compilation (bibtex reruns, aux file management) | Custom shell script with pdflatex + bibtex + pdflatex + pdflatex | `latexmk -pdf` | latexmk handles all reruns automatically; hand-rolled multi-pass scripts frequently miss edge cases |
| BibTeX formatting | Manual `.bib` creation without checking format | Standard BibTeX entry types (`@article`, `@book`, `@techreport`, `@unpublished`) | Malformed BibTeX is silent until compilation; use established entry types |
| Subprocess error propagation | `try/except` catching every script | `subprocess.run(..., check=True)` | `check=True` raises `CalledProcessError` on non-zero exit; the error message names the failed script automatically |

**Key insight:** The LaTeX compilation toolchain (`latexmk`) and Python subprocess pattern already handle the hard parts. This phase is primarily a content-authoring problem, not an engineering problem.

---

## Runtime State Inventory

This is an assembly phase, not a rename/refactor phase. No runtime state inventory required.

---

## Common Pitfalls

### Pitfall 1: Table Fragment Double-Wrapping

**What goes wrong:** Writer wraps `\input{../output/tables/table2_ols.tex}` inside `\begin{table}[htbp]...\end{table}`, causing LaTeX error "something's wrong, perhaps a missing \item" or the table float appearing twice.

**Why it happens:** The `.tex` fragments were generated by pandas `to_latex()` with a `\begin{table}` wrapper already included. A second float environment doubles it.

**How to avoid:** Use bare `\input{../output/tables/X.tex}` for all pre-formatted fragments. Only bare `\includegraphics{}` calls need their own `\begin{figure}...\end{figure}` wrapper.

**Warning signs:** LaTeX log warnings about mismatched environments or float errors on `\input` lines.

### Pitfall 2: Synthetic Control Gap Not Persisted

**What goes wrong:** `counterfactual_projection.py` cannot access the post-reform gap series without re-running the full `pysyncon` optimization (which takes 1–3 minutes and requires the donor CSV files in `data/raw/`).

**Why it happens:** `synthetic_control.py` writes `synthetic_control_weights.csv` (donor weights) but does not write the gap time series as a CSV.

**How to avoid:** Add a `synthetic_control_gap.csv` write step to `synthetic_control.py` before the `run_all.py` plan is written. The gap series is already computed as `ts_gap` in `plot_gap()`.

**Warning signs:** `counterfactual_projection.py` has an import of `pysyncon.Dataprep` — this signals it is re-running the optimization rather than reading a cached result.

### Pitfall 3: Wild-Bootstrap p-values Mischaracterized

**What goes wrong:** Paper text says "standard errors are clustered by country with wild bootstrap" but Table 2 shows bracketed values (p-values) not standard errors. Conflation of inference type creates reviewer confusion.

**Why it happens:** The wild-bootstrap provides p-values for the reform×Japan interaction terms, not standard errors. The `table2_ols.tex` footnote is correct but prose may restate it imprecisely.

**How to avoid:** Prose must explicitly state: "bracketed values in Table 2 are wild-bootstrap p-values (999 Rademacher draws, clustered by country), not standard errors."

**Warning signs:** Any sentence that says "standard errors in brackets" for the interaction specification column.

### Pitfall 4: Event Study CAR Sign Interpretation for 2023 Cohort

**What goes wrong:** The 2023 TSE reform cohort shows strongly negative CARs for KOSPI in `event_study_car.csv` (CAR at t=24: −6.48x). This is counter-intuitive given the reform was a positive Japan event. The sign reflects KOSPI abnormal returns relative to the stacked control — KOSPI continued falling while reform benchmarks rose.

**Why it happens:** The stacked event study design measures CAR for the reform country (Japan/TOPIX) relative to the non-reform pool. The 2023 cohort data in the CSV covers KOSPI in the stacked design, not Japan directly. [ASSUMED — needs verification against event_study.py implementation]

**How to avoid:** Review `src/analysis/event_study.py` logic before writing the Results section prose. Confirm whether the CSV's 2023 cohort rows represent Japan's CAR or KOSPI's reaction.

**Warning signs:** A large negative CAR series for the 2023 cohort in a paper that argues reform was positive for Japan.

### Pitfall 5: latexmk Working Directory

**What goes wrong:** Running `latexmk -pdf paper/main.tex` from the repo root may fail to resolve `../output/figures/` paths because `../` resolves relative to the working directory, not the `.tex` file location.

**Why it happens:** `latexmk` by default changes to the directory of the input file before running pdflatex. So `../output/figures/` from `paper/main.tex` correctly resolves to `output/figures/` at the repo root. This is correct behavior. The pitfall is running `latexmk` without this understanding and assuming relative paths break.

**How to avoid:** Confirm the two-command workflow in the README: `cd paper && latexmk -pdf main.tex` OR `latexmk -pdf paper/main.tex` from repo root (both work due to latexmk's `-cd` default behavior). [ASSUMED — verify by compilation test]

**Warning signs:** "File not found" errors during compilation for `../output/figures/` paths.

### Pitfall 6: Single-Donor Caveat Must Be Prominent

**What goes wrong:** Relegating the MSCI_HK weight=1.0 / RMSPE=0.2893 caveat to a footnote or a single sentence makes it easy for reviewers to flag as a major limitation that was buried.

**Why it happens:** Authors minimize discomfiting results.

**How to avoid:** The Discussion/Limitations section must explicitly state: synthetic control assigns all weight to MSCI Hong Kong (weight=1.0, all other donors=0.0); RMSPE of 0.2893 exceeds the typical acceptance threshold of 0.15; the design is treated as corroborating evidence for the 2023 TSE reform, not primary causal identification. The primary identification strategy is the stacked event study + panel OLS.

---

## Code Examples

### run_all.py Complete Template

```python
#!/usr/bin/env python3
"""
run_all.py - Replication entry point for the Korea Discount study.

Regenerates all figures and tables from data/processed/panel.parquet
(and data/raw/ for GPR series). Does NOT regenerate panel.parquet itself.

Usage:
    pip install -r requirements.txt
    python run_all.py

Requirements:
    data/processed/panel.parquet must exist (run src/data/build_panel.py once)
    All data/raw/ CSV files must be present
"""

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

if __name__ == "__main__":
    main()
```

### Counterfactual Projection — Gap CSV Dependency Resolution

```python
# Addition to synthetic_control.py plot_gap() function
# After computing ts_gap, write it as CSV for counterfactual_projection.py

gap_df = ts_gap.reset_index()
gap_df.columns = ["date", "gap"]
gap_df.to_csv(ROBUSTNESS_DIR / "synthetic_control_gap.csv", index=False)
logging.info("Saved synthetic_control_gap.csv")
```

```python
# In counterfactual_projection.py — reading the gap
gap_df = pd.read_csv(config.OUTPUT_DIR / "robustness" / "synthetic_control_gap.csv")
gap_df["date"] = pd.to_datetime(gap_df["date"])
reform_date = pd.Timestamp(config.TSE_PB_REFORM_DATE)
post_reform_gap = gap_df[
    (gap_df["date"] >= reform_date) &
    (gap_df["date"] <= reform_date + pd.DateOffset(months=18))
]["gap"]
monthly_lift = post_reform_gap.diff().mean()  # average monthly P/B change
```

### LaTeX Preamble (main.tex)

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

% Hyperlinks (load last)
\usepackage[hidelinks]{hyperref}

\title{Corporate Governance Reform and the Korea Discount:\\
Evidence from Japan's Natural Experiment}
\author{[Author]}
\date{\today}

\begin{document}
\maketitle
\begin{abstract}
% 150–200 words
\end{abstract}
\newpage
\tableofcontents
\newpage

% Sections...

\bibliography{references}
\end{appendices}
\end{document}
```

---

## Existing Output Inventory (all verified present)

| File | Path | Content | Status |
|------|------|---------|--------|
| figure1_pb_comparison.pdf | output/figures/ | 20-year KOSPI P/B vs peers | [VERIFIED] |
| figure2_event_study.pdf | output/figures/ | Stacked event study CARs (3-panel) | [VERIFIED] |
| figure3_geo_risk.pdf | output/figures/ | GPR overlay + KOSPI response | [VERIFIED] |
| figure_synth_gap.pdf | output/figures/ | Synthetic control gap plot | [VERIFIED] |
| table1_summary_stats.tex | output/tables/ | Summary stats by country/sub-period | [VERIFIED] |
| table2_ols.tex | output/tables/ | Panel OLS with wild-bootstrap p-values | [VERIFIED] |
| table3_geo_risk.tex | output/tables/ | GPR regression table | [VERIFIED] |
| table_event_study_coefs.tex | output/tables/ | Event study coefficient table | [VERIFIED] |
| discount_stats.tex | output/tables/ | Korea Discount macros (key numbers source) | [VERIFIED] |
| discount_stats.csv | output/tables/ | Raw discount numbers (benchmark, n, mean, nw_se, t_stat, ci) | [VERIFIED] |
| event_study_car.csv | output/tables/ | Full CAR series by cohort | [VERIFIED] |
| robustness_alt_control_em_asia.tex | output/robustness/ | Alt control (EM Asia) | [VERIFIED] |
| robustness_alt_control_em_exchina.tex | output/robustness/ | Alt control (EM ex-China) | [VERIFIED] |
| robustness_pe_ols.tex | output/robustness/ | P/E OLS robustness | [VERIFIED] |
| robustness_pe_event_coefs.tex | output/robustness/ | P/E event study robustness | [VERIFIED] |
| synthetic_control_weights.csv | output/robustness/ | Donor weights + RMSPE=0.2893 | [VERIFIED] |
| figure_placebo_falsification.pdf | output/robustness/ | Placebo falsification figure | [VERIFIED] |
| figure_placebo_inspace.pdf | output/robustness/ | In-space placebo figure | [VERIFIED] |
| figure_placebo_intime.pdf | output/robustness/ | In-time placebo figure | [VERIFIED] |

**Missing (must be created in this phase):**
- `output/figures/figure4_counterfactual_projection.pdf` — produced by `src/policy/counterfactual_projection.py`
- `output/robustness/synthetic_control_gap.csv` — produced by updated `src/robustness/synthetic_control.py`

---

## Key Numbers Reference (for prose authoring)

All numbers below are [VERIFIED] from output files:

| Statistic | Value | Source |
|-----------|-------|--------|
| Korea Discount vs TOPIX (mean P/B spread) | −0.177x | `output/tables/discount_stats.csv` |
| Korea Discount vs TOPIX (t-statistic) | −3.23 | `output/tables/discount_stats.csv` |
| Korea Discount vs TOPIX (95% CI) | [−0.284x, −0.069x] | `output/tables/discount_stats.csv` |
| Korea Discount vs MSCI EM (mean spread) | −0.601x | `output/tables/discount_stats.csv` |
| Korea Discount vs MSCI EM (t-statistic) | −10.30 | `output/tables/discount_stats.csv` |
| Korea Discount vs MSCI EM (95% CI) | [−0.716x, −0.486x] | `output/tables/discount_stats.csv` |
| Stewardship Code × Japan interaction | +0.09 [p=0.750] | `output/tables/table2_ols.tex` |
| CGC × Japan interaction | −0.32 [p=0.375] | `output/tables/table2_ols.tex` |
| TSE P/B reform × Japan interaction | −0.24 [p=0.500] | `output/tables/table2_ols.tex` |
| Synthetic control RMSPE | 0.2893 | `output/robustness/synthetic_control_weights.csv` |
| Synthetic Japan donor: MSCI_HK weight | 1.0 (all others 0.0) | `output/robustness/synthetic_control_weights.csv` |
| GPR escalation coefficient | −0.02 (t=−0.84, p=0.40) | `output/tables/table3_geo_risk.tex` |
| TOPIX P/B coefficient in GPR model | +0.63 (t=5.40) | `output/tables/table3_geo_risk.tex` |
| Panel observations | 1,072 | Verified: `panel.parquet` shape (1072, 4) |
| Countries | KOSPI, TOPIX, SP500, MSCI_EM | Verified: `panel.parquet` unique countries |
| KOSPI P/B mean (Post-TSE 2023–2024) | 0.93x | `output/tables/table1_summary_stats.tex` |
| TOPIX P/B mean (Post-TSE 2023–2024) | 1.36x | `output/tables/table1_summary_stats.tex` |

---

## BibTeX Seed References

From `papers/REFERENCES.md` and `papers/LITERATURE_REVIEW.md`:

| BibTeX Key | Entry | Notes |
|------------|-------|-------|
| `baek2004` | Baek, Kang & Park (2004) JFE | Chaebol governance and firm value |
| `eberhart2012` | Eberhart (2012) Stanford | Japan corporate governance natural experiment |
| `miyajima2023` | Miyajima & Saito (2023) RIETI | Japan cross-shareholding reform impact |
| `bereskin2015` | Bereskin, Kim & Oh (2015) | Korea credit rating and governance |
| `kcmi2023` | KCMI (2023) | Causes behind the Korea Discount (definitive report) |
| `imf2021` | IMF WP 21/251 | Geopolitical risk and KOSPI; GPRNK Index |
| `gs2022` | Goldman Sachs (2022) | Korea MSCI DM reclassification analysis |
| `abadie2010` | Abadie, Diamond & Hainmueller (2010) | Synthetic control methodology (JASA) |
| `cengiz2019` | Cengiz et al. (2019) QJE | Stacked event study / bunching estimator |
| `caldara2022` | Caldara & Iacoviello (2022) AER | Geopolitical Risk (GPR) index |

Additional needed (to be authored during BibTeX creation):
- Korea Value-Up Program (FSC 2024–2025) — policy document
- Commercial Act Amendments (2025) — legislative source
- Baker, Larcker & Wang (2022) — stacked DiD reference (cited in Roadmap)
- Claessens et al. (2000 or 2002) — chaebol control/ownership pyramid literature
- Black et al. (2006) — Korean corporate governance and firm value
- Jensen & Meckling (1976) — agency cost foundational theory

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Single DiD with one treatment date | Stacked event study (Cengiz 2019) across all three reform dates | Post-2019 | Avoids treatment contamination across reform dates |
| Generic heteroskedasticity-robust SE with N=4 clusters | Wild bootstrap (Rademacher, 999 draws) for small-cluster inference | ~2012–2016 | Correct size control when cluster count < 10 |
| Standard synthetic control with multiple donors | Accept single-donor result with explicit RMSPE caveat | Phase 4 decision | Honest reporting; donors (STOXX600, FTSE100, SP500, MSCI_TAIWAN) receive zero weight |

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | `newtxtext`/`newtxmath` preferred over `times` package alone | Standard Stack | Minor: may need to substitute `mathptmx` or `times` if newtxtext not in TeX Live 2024 install; cosmetic only |
| A2 | `latexmk -pdf paper/main.tex` from repo root correctly resolves `../output/figures/` relative paths | Common Pitfalls | Medium: compilation fails if path resolution differs; workaround is `cd paper && latexmk -pdf main.tex` |
| A3 | 2023 cohort CAR series in `event_study_car.csv` represents KOSPI stacked-cohort abnormal returns (not Japan's) | Code Examples | High: if wrong, the negative CARs in 2023 cohort need different interpretation in Results prose |
| A4 | `synthetic_control.py` can be extended with a `to_csv()` call for the gap series without breaking existing output | Code Examples | Low: adding a write call is additive; no existing test checks for absence of this CSV |

---

## Open Questions

1. **CAR sign interpretation for 2023 cohort**
   - What we know: `event_study_car.csv` shows large negative CARs for the 2023 cohort (reaching −6.48x at t=24)
   - What's unclear: Does this represent KOSPI's abnormal performance within the stacked design, or Japan's CAR? The stacked design treats Japan as the treated unit. If the CSV includes all countries' cohort-level CARs, the negative 2023 values may reflect KOSPI's counter-reform trajectory.
   - Recommendation: Planner should assign a task to read `src/analysis/event_study.py` carefully before drafting the Results prose for the event study section.

2. **gap CSV dependency resolution timing**
   - What we know: `synthetic_control.py` does not currently write a gap CSV; `counterfactual_projection.py` needs the gap series
   - What's unclear: Whether to update `synthetic_control.py` (minimal change) or have `counterfactual_projection.py` re-run pysyncon
   - Recommendation: Update `synthetic_control.py` to write `output/robustness/synthetic_control_gap.csv`. This is a one-line addition and the right architectural choice.

---

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| `latexmk` | PDF compilation | ✓ | 4.83 (TeX Live 2024) | `pdflatex` direct (manual reruns) |
| `pdflatex` | PDF typesetting | ✓ | TeX Live 2024 | `xelatex` (also available) |
| `xelatex` | Font fallback | ✓ | TeX Live 2024 | — |
| `python3` | All Python scripts | ✓ | 3.12.2 | — |
| `data/processed/panel.parquet` | All analysis scripts + counterfactual | ✓ (1072 × 4) | — | Must be present; `run_all.py` does not regenerate it |
| `data/raw/` CSV files | Analysis scripts (GPR, synthetic control donors) | Not verified individually | — | Must be present for full replication |
| `output/` existing files | Paper integration | ✓ (all 19 files listed) | — | Re-run respective Phase 2–4 scripts |

**Missing dependencies with no fallback:** None — all required tools are present.

**Missing dependencies with fallback:**
- `data/raw/` individual CSVs: not individually probed, but Phase 1–4 completion and prior successful output generation implies they exist.

[VERIFIED: Bash — all CLI tools confirmed present]

---

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest 8.3.4 |
| Config file | none (project root discovery) |
| Quick run command | `pytest tests/ -x -q` |
| Full suite command | `pytest tests/ -v` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| OUTPUT-01 | All figures and tables generated programmatically | smoke | `pytest tests/test_phase5.py::test_all_figures_exist -x` | ❌ Wave 0 |
| OUTPUT-02 | paper/main.tex compiles to PDF | smoke | `pytest tests/test_phase5.py::test_latex_compiles -x` | ❌ Wave 0 |
| OUTPUT-03 | run_all.py exits 0 without error | smoke | `pytest tests/test_phase5.py::test_run_all_executes -x` | ❌ Wave 0 |
| POLICY-02 | figure4_counterfactual_projection.pdf exists and is non-empty | smoke | `pytest tests/test_phase5.py::test_counterfactual_figure_exists -x` | ❌ Wave 0 |
| PAPER-01–10 | Prose completeness (sections present in main.tex) | smoke | `pytest tests/test_phase5.py::test_required_sections_present -x` | ❌ Wave 0 |

**Note:** PAPER-01 through PAPER-10 (prose content quality) are manual-only in their qualitative dimension. Automated tests verify structural presence (section headings exist, word count targets met) but not prose quality.

### Sampling Rate

- **Per task commit:** `pytest tests/test_phase5.py -x -q`
- **Per wave merge:** `pytest tests/ -v`
- **Phase gate:** Full suite green before `/gsd-verify-work`

### Wave 0 Gaps

- [ ] `tests/test_phase5.py` — covers OUTPUT-01, OUTPUT-02, OUTPUT-03, POLICY-02, structural PAPER presence
- [ ] Fixture: `src/policy/__init__.py` — new package initialization file

---

## Security Domain

This project contains no authentication, session management, access control, cryptography, or user-facing web components. Security domain is not applicable to this phase.

---

## Sources

### Primary (HIGH confidence)
- Direct file inspection: `output/tables/discount_stats.csv`, `output/tables/table2_ols.tex`, `output/tables/table3_geo_risk.tex`, `output/tables/table1_summary_stats.tex`, `output/robustness/synthetic_control_weights.csv`
- Direct file inspection: `config.py`, `requirements.txt`, `src/robustness/synthetic_control.py`, `src/descriptive/figure1.py`
- Bash verification: `latexmk --version`, `pdflatex --version`, `xelatex --version`, `python3 --version`
- Direct file inspection: `papers/REFERENCES.md`, `papers/LITERATURE_REVIEW.md`, `papers/ECONOMETRIC_MODELS.md`

### Secondary (MEDIUM confidence)
- latexmk working directory behavior: standard documentation behavior (directory-change before processing input file)

### Tertiary (LOW confidence)
- `newtxtext`/`newtxmath` package preference over `times` alone [ASSUMED — training knowledge about TeX Live 2024 package quality]
- `latexmk` `-cd` flag behavior in 4.83 [ASSUMED]

---

## Metadata

**Confidence breakdown:**
- Output inventory: HIGH — all files directly verified by `ls` and `cat`
- Key numbers: HIGH — read directly from CSV/tex files
- Standard stack: HIGH — tools verified via Bash version checks
- Architecture patterns: HIGH — derived from existing source code
- LaTeX packages: MEDIUM — established conventions with one LOW-confidence package choice (`newtxtext`)
- BibTeX seed entries: MEDIUM — from project's own literature files; additional entries [ASSUMED] needed from memory

**Research date:** 2026-04-20
**Valid until:** 2026-05-20 (stable domain; TeX Live and Python versions locked in requirements.txt)
