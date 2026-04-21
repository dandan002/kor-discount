---
phase: 05-paper-assembly-and-replication-package
plan: "04"
subsystem: paper
tags: [latex, paper-assembly, causal-mechanisms, empirical-strategy, results, discussion, policy, appendices]
dependency_graph:
  requires: [05-02, 05-03]
  provides: [paper/main.tex-complete]
  affects: [paper/main.tex]
tech_stack:
  added: []
  patterns: [latex-prose, bare-input-tables, includegraphics-figures, two-way-fe-notation, stacked-event-study-equations]
key_files:
  created: []
  modified:
    - paper/main.tex
decisions:
  - "Event study 2023 cohort CARs are negative for KOSPI (Korea discount deepening relative to Japan reform trajectory) — prose states this correctly rather than claiming Japan CARs are negative"
  - "Figure3 (geo risk) and Table3 moved from appendix skeleton to Results section where they belong; duplicate skeleton removed"
  - "Wild-bootstrap p-values explicitly labeled as p-values not standard errors per RESEARCH.md Pitfall 3 (threat T-05-08 mitigated)"
  - "RMSPE=0.2893 caveat present in Results, Discussion, and Conclusion (threat T-05-10 mitigated)"
  - "Counterfactual projection labeled Illustrative in both caption and prose body; 'This is not a forecast' stated (threat T-05-09 mitigated)"
metrics:
  duration: "~35 minutes"
  completed: "2026-04-21"
  tasks_completed: 3
  tasks_total: 3
  files_changed: 1
---

# Phase 05 Plan 04: Remaining Sections (Causal Mechanisms Through Appendices) Summary

Wrote full publication-quality LaTeX prose for seven sections (Causal Mechanisms, Empirical Strategy, Results, Discussion and Limitations, Conclusion, Policy Recommendations, and Appendices), integrating all figures and tables from `output/` via `\includegraphics` and bare `\input{}` calls, with all required numerical values, citations, threat-model mitigations, and honest uncertainty communication embedded verbatim.

## Tasks Completed

| Task | Name | Commit | Key Files |
|------|------|--------|-----------|
| 1 | Causal Mechanisms + Empirical Strategy | 4687e68 | paper/main.tex (+219 lines) |
| 2 | Results + all figure/table integration | 8e3a541 | paper/main.tex (+140 lines, -35 skeleton lines) |
| 3 | Discussion + Conclusion + Policy + Appendices | ac266a1 | paper/main.tex (+288 lines, -11 stubs) |

## What Was Built

### Task 1: Causal Mechanisms and Empirical Strategy (PAPER-06, PAPER-07)

**Causal Mechanisms** (`\section{Causal Mechanisms}`, `\label{sec:mechanisms}`): Three subsections — (1) Chaebol Opacity and Agency Costs (principal-principal problem, tunneling, jensen1976, baek2004, claessens2000 citations, inheritance tax context); (2) Minority Shareholder Recourse Deficit (porta1998, porta2002, FSC Value-Up Program, Commercial Act amendments); (3) Geopolitical Risk Premium (caldara2022, imf2021, GPR coefficient −0.02 t=−0.84 p=0.40 stated).

**Empirical Strategy** (`\section{Empirical Strategy}`, `\label{sec:strategy}`): Three subsections — (1) Stacked Event Study with Equation 1 (cohort-level estimating equation with LaTeX math, cengiz2019, baker2022 citations); (2) Panel OLS with Equation 2 (two-way FE notation `\alpha_c + \alpha_t`, linearmodels.PanelOLS, wild-bootstrap rationale with cameron2008); (3) Synthetic Control (abadie2010, SUTVA justification, RMSPE=0.2893 caveat).

### Task 2: Results Section (PAPER-07 output integration)

**Results** (`\section{Results}`, `\label{sec:results}`): Four subsections — (1) Event Study Results: interprets 2023 cohort negative CARs correctly as KOSPI discount deepening relative to Japan's lift; includes `figure2_event_study.pdf` and bare `\input{table_event_study_coefs.tex}`; (2) Panel OLS Results: reports p=0.750/0.375/0.500 verbatim, explicitly states "wild-bootstrap p-values (999 Rademacher draws, clustered by country), not standard errors"; includes bare `\input{table2_ols.tex}`; (3) Geopolitical Risk Sub-Analysis: GPR −0.02 t=−0.84 p=0.40, TOPIX P/B +0.63 t=5.40; includes `figure3_geo_risk.pdf` and bare `\input{table3_geo_risk.tex}`; (4) Synthetic Control Results: RMSPE=0.2893 explicitly above 0.15 threshold, "corroborating evidence rather than primary causal identification"; includes `figure_synth_gap.pdf`.

Removed duplicate figure3/table3/synth gap from appendix skeleton (they had been placed in appendices by the plan 02 skeleton; moved to Results where they belong per plan 04 instructions).

### Task 3: Discussion, Conclusion, Policy, Appendices (PAPER-08, PAPER-09, PAPER-10, POLICY-01, POLICY-02)

**Discussion** (`\section{Discussion and Limitations}`): Three subsections — (1) Single Treated Unit Problem: N=1 caveat prominent, wild-bootstrap conservatism explained, synthetic control permutation inference discussed; (2) Abenomics Confound: honest attribution of confound, three mitigations (donor pool, narrow windows, time FE), caveated; (3) Japan-to-Korea Generalizability: structural similarities and differences (chaebol concentration, FSC enforcement, geopolitical risk not resolved by governance reform), counterfactual labeled illustrative.

**Conclusion** (`\section{Conclusion}`): Summarizes −0.177x vs TOPIX (t=−3.23), −0.601x vs MSCI EM (t=−10.30), RMSPE=0.2893; states three contributions (stacked design, uncertainty quantification, counterfactual projection); outlines three future research directions.

**Policy Recommendations** (`\section{Policy Recommendations}`): Two subsections — (1) Recommendations: three specific FSC/KRX/Stewardship Code recommendations with operational detail; (2) Counterfactual Projection: includes `figure4_counterfactual_projection.pdf` with "Illustrative projection" caption, "This is not a forecast" in prose.

**Appendices**: Variable Definitions table with P/B, P/E, GPR, three reform dummies (manually created LaTeX table); Additional Robustness Tables prose (B.1-B.4 description); four bare `\input{}` calls for robustness fragments confirmed present.

## Figures and Tables Wired In

| Asset | Location in Paper | Integration Method |
|-------|------------------|--------------------|
| figure2_event_study.pdf | Results §7.1 | `\includegraphics` |
| figure3_geo_risk.pdf | Results §7.3 | `\includegraphics` |
| figure_synth_gap.pdf | Results §7.4 | `\includegraphics` |
| figure4_counterfactual_projection.pdf | Policy §11.2 | `\includegraphics` |
| table_event_study_coefs.tex | Results §7.1 | bare `\input{}` |
| table2_ols.tex | Results §7.2 | bare `\input{}` |
| table3_geo_risk.tex | Results §7.3 | bare `\input{}` |
| robustness_alt_control_em_asia.tex | Appendix B | bare `\input{}` |
| robustness_alt_control_em_exchina.tex | Appendix B | bare `\input{}` |
| robustness_pe_ols.tex | Appendix B | bare `\input{}` |
| robustness_pe_event_coefs.tex | Appendix B | bare `\input{}` |

## Threat Model Mitigations Verified

| Threat | Mitigation Applied |
|--------|--------------------|
| T-05-08: Wild-bootstrap p-value mischaracterization | Prose states "Bracketed values are wild-bootstrap p-values (999 Rademacher draws, clustered by country), not standard errors" in Results §7.2 |
| T-05-09: Counterfactual projection as forecast | "This projection is illustrative" and "This is not a forecast" in Policy §11.2; figure caption labels "Illustrative projection" |
| T-05-10: RMSPE caveat buried | Dedicated Discussion §8.1 subsection; Results §7.4 states "RMSPE exceeds conventional acceptance threshold of ~0.15"; Conclusion repeats RMSPE=0.2893 |

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Removed duplicate figures/tables from appendices**
- **Found during:** Task 2
- **Issue:** The plan 02 skeleton had placed figure3_geo_risk, table3_geo_risk, and figure_synth_gap in the `\begin{appendices}` block. Plan 04 explicitly instructs these to appear in the Results section. Leaving them in both locations would cause duplicate labels and double-counted content in the compiled PDF.
- **Fix:** Removed the skeleton's duplicate figure3, table3, and synth gap entries from the appendices; kept the robustness table `\input{}` calls which belong there.
- **Files modified:** paper/main.tex
- **Commit:** 8e3a541

## Known Stubs

None. All sections contain full publication-quality prose with real numbers embedded from output files. No placeholder text, "TODO", or "coming soon" content remains.

## Threat Flags

None. No new network endpoints, auth paths, file access patterns, or schema changes introduced.

## Self-Check: PASSED

- paper/main.tex: FOUND (1174 lines)
- Commit 4687e68: FOUND (feat(05-04): Causal Mechanisms and Empirical Strategy)
- Commit 8e3a541: FOUND (feat(05-04): Results section)
- Commit ac266a1: FOUND (feat(05-04): Discussion, Conclusion, Policy, Appendices)
- `grep -c "\\section{" paper/main.tex` = 12 (>= 10 required)
- `grep "figure4_counterfactual_projection" paper/main.tex` = 1 match
- `grep "wild-bootstrap p-values" paper/main.tex` = 1 match
- `grep "Abenomics" paper/main.tex` = 11 matches
- `grep "0.2893" paper/main.tex` = 9 matches (>= 2 required)
- `pytest tests/test_phase5.py::test_required_sections_present -x -q` = PASSED
