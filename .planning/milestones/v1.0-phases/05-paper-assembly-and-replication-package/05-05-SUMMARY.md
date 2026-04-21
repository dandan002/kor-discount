---
phase: 05-paper-assembly-and-replication-package
plan: "05"
subsystem: paper-compilation
tags: [latex, compilation, readme, pytest, replication-package]
dependency_graph:
  requires: [05-03, 05-04]
  provides: [paper/main.pdf, README.md]
  affects: []
tech_stack:
  added: []
  patterns: [latexmk-pdf-bibtex, pytest-gate]
key_files:
  created:
    - paper/main.pdf
  modified:
    - paper/main.tex
    - paper/references.bib
    - output/tables/table1_summary_stats.tex
    - output/tables/table2_ols.tex
    - output/tables/table3_geo_risk.tex
    - output/robustness/robustness_pe_ols.tex
    - README.md
decisions:
  - "Fixed sec:empirical undefined reference -> sec:results (correct label already defined)"
  - "Added cameron2008 citation to references.bib (wild-bootstrap inference methodology)"
  - "Escaped bare underscores in auto-generated .tex files (MSCI_EM, post_stewardship, etc.)"
  - "Added \\label{tab:geo_risk} to table3_geo_risk.tex to resolve undefined table reference"
metrics:
  duration: "~25 minutes"
  completed: "2026-04-20"
  tasks_completed: 3
  files_changed: 8
---

# Phase 05 Plan 05: Final Integration — Compilation, README, and Pytest Gate Summary

One-liner: Resolved 5 LaTeX errors in auto-generated table files, compiled paper/main.pdf (370 KB, 48 pages), updated README with two-command reproduction workflow, and confirmed all 9 pytest tests pass.

## Tasks Completed

### Task 1: Fix LaTeX Compilation Errors and Compile paper/main.pdf

**Status:** Complete — latexmk exit 0, PDF 370 KB, 48 pages

**Errors fixed:**

1. **[Rule 1 - Bug] Missing cameron2008 citation**
   - Found during: Task 1 compilation
   - Issue: `bibtex` reported warning "I didn't find a database entry for cameron2008" — citation used 4 times in main.tex for wild-bootstrap inference methodology
   - Fix: Added full `@article{cameron2008}` entry (Cameron, Gelbach & Miller 2008, ReStat) to `paper/references.bib`
   - Files modified: `paper/references.bib`
   - Commit: bf72176

2. **[Rule 1 - Bug] Undefined `\ref{sec:empirical}` in main.tex**
   - Found during: Task 1 compilation
   - Issue: `main.tex` line 309 referenced `\ref{sec:empirical}` which was never defined; the correct label is `\ref{sec:results}` (defined at line 800)
   - Fix: Changed `sec:empirical` to `sec:results` in main.tex
   - Files modified: `paper/main.tex`
   - Commit: bf72176

3. **[Rule 1 - Bug] Missing `\label{tab:geo_risk}` in table3_geo_risk.tex**
   - Found during: Task 1 compilation
   - Issue: `main.tex` references `\ref{tab:geo_risk}` but the auto-generated `table3_geo_risk.tex` had no `\label{}` directive
   - Fix: Added `\label{tab:geo_risk}` after `\caption{}` in table3_geo_risk.tex
   - Files modified: `output/tables/table3_geo_risk.tex`
   - Commit: bf72176

4. **[Rule 1 - Bug] Bare underscore `GPRC_KOR` in table3_geo_risk.tex footnote**
   - Found during: Task 1 compilation
   - Issue: `\begin{flushleft}...\end{flushleft}` block contained `GPRC_KOR` — LaTeX treats `_` as math subscript in text mode, causing "Command \\end{flushleft} invalid in math mode" fatal error
   - Fix: Escaped to `GPRC\_KOR`
   - Files modified: `output/tables/table3_geo_risk.tex`
   - Commit: bf72176

5. **[Rule 1 - Bug] Bare underscores in MSCI_EM, post_stewardship, etc. across auto-generated tables**
   - Found during: Task 1 compilation
   - Issue: `table1_summary_stats.tex` had `MSCI_EM` in 8 rows; `table2_ols.tex` and `robustness_pe_ols.tex` had variable names like `post_stewardship`, `stewardship_x_japan`, etc. — all causing "Missing $ inserted" errors
   - Fix: Escaped all bare underscores with `\_` in text-mode table cells across three files
   - Files modified: `output/tables/table1_summary_stats.tex`, `output/tables/table2_ols.tex`, `output/robustness/robustness_pe_ols.tex`
   - Commit: bf72176

**Final compilation result:**
- Command: `latexmk -pdf -bibtex -interaction=nonstopmode main.tex`
- Exit: 0 ("All targets (main.pdf) are up-to-date")
- Output: `paper/main.pdf`, 48 pages, 370 KB
- Remaining warnings: Font shape `OMS/ntxtlf/m/n` undefined (harmless font substitution, non-fatal)

### Task 2: Update README.md with Reproduction Workflow

Added a full "Reproduction" section to `README.md` documenting:
- Two-command reproduction: `pip install -r requirements.txt` + `python run_all.py`
- Optional PDF compilation: `cd paper && latexmk -pdf main.tex`
- Prerequisites: `data/processed/panel.parquet`, raw CSV files, TeX Live 2024

Commit: 681da96

### Task 3: Run pytest suite

All 9 tests passed:

```
tests/test_phase5.py::test_counterfactual_figure_exists PASSED
tests/test_phase5.py::test_all_figures_exist PASSED
tests/test_phase5.py::test_synthetic_control_gap_csv_exists PASSED
tests/test_phase5.py::test_gap_csv_columns PASSED
tests/test_phase5.py::test_run_all_exists PASSED
tests/test_phase5.py::test_paper_dir_exists PASSED
tests/test_phase5.py::test_main_tex_exists PASSED
tests/test_phase5.py::test_required_sections_present PASSED
tests/test_phase5.py::test_references_bib_exists PASSED

9 passed in 0.59s
```

## Checkpoint: Auto-Verified

Checkpoint auto-verified: latexmk exit 0, PDF 370 KB (> 100 KB threshold), pytest 9/9 passed.

All three auto-approve conditions satisfied:
- latexmk exits 0 (no fatal LaTeX errors)
- paper/main.pdf size = 370 KB > 100 KB
- pytest tests/test_phase5.py: 9/9 passed

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Missing cameron2008 citation**
- Found during: Task 1
- bibtex warning "didn't find database entry for cameron2008" — reference used throughout for wild-bootstrap methodology
- Fix: Added @article entry to references.bib

**2. [Rule 1 - Bug] \ref{sec:empirical} undefined — label mismatch in main.tex**
- Found during: Task 1
- main.tex used sec:empirical; correct label is sec:results
- Fix: Updated cross-reference in main.tex line 309

**3. [Rule 1 - Bug] Missing \label{tab:geo_risk} in auto-generated table3_geo_risk.tex**
- Found during: Task 1
- Auto-generated file omitted the label directive required by main.tex \ref{tab:geo_risk}
- Fix: Added \label after \caption in table3_geo_risk.tex

**4. [Rule 1 - Bug] Bare underscores in auto-generated .tex table files causing LaTeX math-mode errors**
- Found during: Task 1
- table1_summary_stats.tex (MSCI_EM), table2_ols.tex (post_stewardship, cgc_x_japan, etc.), table3_geo_risk.tex (GPRC_KOR), robustness_pe_ols.tex — all bare underscores in text mode
- Fix: Escaped all to \_ across four files

## Known Stubs

None — all figures, tables, and prose are fully wired with real analysis outputs.

## Threat Flags

None — no new network endpoints, auth paths, or security-relevant surfaces introduced in this plan.

## Self-Check: PASSED

- paper/main.pdf exists: FOUND (370 KB, 48 pages)
- Commit bf72176 exists: FOUND
- Commit 681da96 exists: FOUND
- All 10 required sections in main.tex: PASSED
- pytest 9/9: PASSED
- README contains "run_all.py": FOUND
- README contains "pip install -r requirements.txt": FOUND
