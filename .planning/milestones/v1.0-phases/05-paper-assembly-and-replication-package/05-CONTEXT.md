# Phase 5: Paper Assembly and Replication Package - Context

**Gathered:** 2026-04-20
**Status:** Ready for planning

<domain>
## Phase Boundary

Write all ten paper sections as full LaTeX prose, integrate all programmatically generated figures and tables from `output/` into a compiling PDF, write the policy section with a programmatic counterfactual projection figure, and deliver a `run_all.py` replication entry point. No new analyses — this phase assembles and narrates the existing outputs.

</domain>

<decisions>
## Implementation Decisions

### Prose Authorship
- **D-01:** Claude writes **full, publication-quality prose** for every section — abstract, introduction, institutional background, literature review, data, causal mechanisms, empirical strategy, discussion/limitations, conclusion, appendices. User reviews and edits; no placeholders.
- **D-02:** Numbers are **embedded directly** from the actual output files in `output/`. Claude reads CSVs and LaTeX fragments from `output/tables/` and `output/robustness/` and writes the values verbatim into the prose. No `\newcommand` macro infrastructure. Key numbers to embed:
  - Korea Discount: **−0.177x vs TOPIX** (t = −3.23, 95% CI: −0.284x to −0.069x), **−0.601x vs MSCI EM** (t = −10.30)
  - Panel OLS reform×Japan interactions: stewardship +0.09 [p=0.750], CGC −0.32 [p=0.375], TSE P/B reform −0.24 [p=0.500] — wild-bootstrap p-values in brackets
  - Synthetic control pre-treatment RMSPE: **0.2893** (accepted caveat; single donor MSCI HK received weight=1.0)
  - All CAR figures reference `output/tables/event_study_car.csv`

### LaTeX Template & Structure
- **D-03:** Document class: `\documentclass[12pt]{article}` with NBER-style geometry — 1-inch margins, Times New Roman font (`\usepackage{times}` or `newtxtext`), double-spaced, A4 or letter.
- **D-04:** Paper lives in `paper/` directory at repo root (does not exist yet — create it). Main file: `paper/main.tex`. Figures and tables included via `\includegraphics{}` and `\input{}` pointing to `../output/figures/` and `../output/tables/` (relative paths from `paper/`).
- **D-05:** BibTeX: Claude creates **`paper/references.bib` from scratch** with all citations needed — Korea Discount priors, Japan governance reform studies, Cengiz et al. 2019 stacked event study, Abadie-Diamond-Hainmueller 2010 synthetic control, Caldara-Iacoviello GPR index, corporate governance–valuation literature (~30–50 entries). Citation style: `\bibliographystyle{apa}` or similar author-year style appropriate for economics/finance.
- **D-06:** Required sections in `main.tex` (per REQUIREMENTS):
  1. Abstract (150–200 words)
  2. Introduction (3–5 pages)
  3. Institutional Background (3–5 pages): chaebol mechanics, FSC/KRX history, Japan three reform dates, NK risk history
  4. Literature Review (3–6 pages): Korea Discount priors, Japan governance event studies, governance–valuation literature, natural experiment methodology
  5. Data (2–4 pages): sources, coverage, variable construction, survivorship bias, missing data
  6. Causal Mechanisms (2–4 pages): three channels — chaebol opacity, minority-shareholder recourse deficit, geopolitical risk premium
  7. Empirical Strategy (1–2 pages): estimating equations and notation for event study, panel OLS, synthetic control
  8. Results (integrates figures/tables from output/)
  9. Discussion/Limitations (1–2 pages): single treated unit, Abenomics confound, Japan→Korea generalizability
  10. Conclusion (1–2 pages)
  11. Policy Recommendations (2–3 pages): FSC, KRX, stewardship code levers + counterfactual projection
  12. Appendices: variable definitions, overflow robustness tables

### run_all.py
- **D-07:** `run_all.py` at repo root regenerates **all figures and tables from `data/processed/panel.parquet`** (and `data/raw/` for GPR series). Does NOT re-run `build_panel.py` — raw data and `panel.parquet` must be present. Two-command workflow per README: `pip install -r requirements.txt` then `python run_all.py`.
- **D-08:** Failure mode: **fail fast** — any script that exits non-zero stops `run_all.py` immediately with a clear error naming the failed script. No continue-on-error behavior.
- **D-09:** Script execution order (dependency order): descriptive → event study → panel OLS → geo risk → synthetic control → robustness (placebo, P/E, alt-control) → counterfactual projection. Each is a `subprocess.run([sys.executable, "src/..."], check=True)` call.
- **D-10:** `run_all.py` prints a step banner before each script (e.g., `\n=== [1/N] Running descriptive analysis ===`) and a final `All outputs regenerated successfully.` message on completion.

### Counterfactual Projection (POLICY-02)
- **D-11:** Method: **apply Japan's observed post-2023 TSE reform P/B lift directly to Korea**. Measure the average monthly TOPIX P/B change in the 12–18 months post-reform from the synthetic control gap (treatment effect), then project KOSPI P/B on the same trajectory starting from its 2024 level. Clearly labeled "Illustrative projection assuming Korea implements a P/B governance reform analogous to Japan's 2023 TSE reform."
- **D-12:** Output: a **new programmatic figure** (`output/figures/figure4_counterfactual_projection.pdf`) — KOSPI P/B historical series through 2024 (solid line), then a dashed line projecting the reform-adjusted path for ~5 years forward. Shaded uncertainty band. Save as PDF consistent with Figures 1–3 style.
- **D-13:** Script: `src/policy/counterfactual_projection.py` — reads `data/processed/panel.parquet` + `output/robustness/synthetic_control_weights.csv` for the RMSPE/gap data, computes the projection, writes the figure. This script is included in `run_all.py` execution order.

### Claude's Discretion
- Exact section lengths and subsection structure within the prose constraints above
- BibTeX citation key naming convention
- Exact citation-count target for the literature review
- Whether the Results section is a standalone section or folds into the empirical strategy section
- Shaded uncertainty band width for the counterfactual projection figure (e.g., ±1 RMSPE or ±1 SD of post-reform gap)
- Exact LaTeX packages (geometry, fontenc, natbib, booktabs, graphicx, hyperref, etc.)

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Configuration and Data
- `config.py` — Event dates firewall; Japan reform dates (2014-02-01, 2015-06-01, 2023-03-01). All scripts MUST read from here, never hardcode.
- `data/processed/panel.parquet` — Canonical panel: (date, country, pb, pe), monthly, KOSPI/TOPIX/SP500/MSCI_EM, 2004–2024.
- `data/raw/MANIFEST.md` — Data provenance; GPR index source documented here.

### Existing Output Files (integrate into paper)
- `output/figures/figure1_pb_comparison.pdf` — Figure 1: 20-year KOSPI P/B vs peers
- `output/figures/figure2_event_study.pdf` — Figure 2: stacked event study CARs (3-panel)
- `output/figures/figure3_geo_risk.pdf` — Figure 3: GPR overlay + KOSPI response
- `output/figures/figure_synth_gap.pdf` — Synthetic control gap plot
- `output/tables/table1_summary_stats.tex` — Table 1 LaTeX fragment
- `output/tables/table2_ols.tex` — Table 2: panel OLS with wild-bootstrap p-values
- `output/tables/table3_geo_risk.tex` — Table 3: GPR regression
- `output/tables/table_event_study_coefs.tex` — Event study coefficient table
- `output/tables/discount_stats.tex` — Korea Discount magnitude macros (source of truth for key numbers)
- `output/robustness/robustness_alt_control_em_asia.tex` — Alt control robustness table
- `output/robustness/robustness_alt_control_em_exchina.tex` — Alt control robustness table
- `output/robustness/robustness_pe_ols.tex` — P/E robustness OLS table
- `output/robustness/robustness_pe_event_coefs.tex` — P/E event study table
- `output/robustness/synthetic_control_weights.csv` — Donor weights + pre-RMSPE = 0.2893

### Robustness Figures (appendix candidates)
- `output/robustness/figure_placebo_falsification.pdf`
- `output/robustness/figure_placebo_inspace.pdf`
- `output/robustness/figure_placebo_intime.pdf`

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `src/descriptive/figure1.py`, `table1.py`, `discount_stats.py` — Phase 2 scripts; patterns for publication-plain matplotlib style
- `src/analysis/event_study.py`, `panel_ols.py`, `geo_risk.py` — Phase 3 scripts; follow for run_all.py ordering
- `src/robustness/synthetic_control.py`, `robustness_pe.py`, `robustness_alt_control.py`, `robustness_placebo.py` — Phase 4 scripts

### Established Patterns
- All analysis scripts read from `data/processed/panel.parquet` and write to `output/`; `run_all.py` must follow this fan-out pattern
- LaTeX tables use `booktabs` style (already in `table2_ols.tex`)
- Figures use publication-plain matplotlib style (no grid, clean axes, PDF output)

### Integration Points
- `paper/main.tex` includes figures via `\includegraphics{../output/figures/X.pdf}` and tables via `\input{../output/tables/X.tex}` (relative paths from `paper/` directory)
- New `src/policy/` package needed for `counterfactual_projection.py`

</code_context>

<specifics>
## Specific Ideas

- Synthetic control RMSPE = 0.2893 is high (single donor MSCI HK weight = 1.0); the paper text must frame this as a caveat — not a blocker — per the Phase 4 human checkpoint decision
- Panel OLS wild-bootstrap p-values are all > 0.35 for the reform×Japan interactions; interpretation should be honest that these are estimated with noise given N=4 country clusters
- Korea Discount magnitude for abstract: −0.177x P/B vs TOPIX (t=−3.23) and −0.601x vs MSCI EM (t=−10.30)

</specifics>

<deferred>
## Deferred Ideas

- LaTeX `\newcommand` macro infrastructure — discussed but deferred; numbers embedded directly is sufficient for v1
- DVC pipeline for end-to-end data versioning (v2 requirement REP-V2-01)
- CI/CD reproducibility verification (v2 requirement REP-V2-02)
- Full end-to-end `run_all.py` including `build_panel.py` — deferred; raw data → panel regeneration left to user

</deferred>

---

*Phase: 05-paper-assembly-and-replication-package*
*Context gathered: 2026-04-20*
