# Milestones: Korea Discount Study

---

## v1.0 — Korea Discount Study MVP

**Shipped:** 2026-04-21
**Phases:** 1–5 (24 plans)
**Timeline:** 2026-04-14 → 2026-04-21 (7 days)
**Codebase:** 4,246 lines of Python; 443 files, 102,114 insertions
**Paper:** `paper/main.pdf` — 48 pages, 370 KB, compiled clean via `latexmk`

### Delivered

A complete, reproducible academic paper investigating the Korea Discount — from raw data pipeline through econometric analysis to submission-ready LaTeX PDF. All 40 v1 requirements shipped.

### Key Accomplishments

1. **Reproducible data pipeline** — `panel.parquet` (20-year monthly KOSPI/TOPIX/S&P500/MSCI EM P/B & P/E) from Bloomberg exports; locked event dates in `config.py`; verified via pytest + human gate
2. **Korea Discount quantified** — -0.177x P/B vs TOPIX, -0.601x vs MSCI EM (HAC-robust Newey-West); abstract-ready LaTeX macros
3. **Primary econometrics** — Stacked event study (Cengiz 2019 design), panel OLS with wild-bootstrap p-values, GPR geopolitical sub-analysis (Figures 2–3, Tables 2–3)
4. **Synthetic control + robustness** — ADH (2010) pysyncon, Taiwan/Indonesia placebo falsification, P/E replication, alt EM control groups; full robustness suite in `output/robustness/`
5. **48-page LaTeX paper** — All 10 required sections; all figures/tables included programmatically from `output/`; clean `latexmk` compile
6. **Replication package** — `run_all.py` orchestrates 11 scripts in dependency order; two-command README workflow; 38/38 pytest pass

### Known Deferred Items

- Synthetic-control RMSPE is high (0.2893) — accepted as paper-text caveat, not a blocking defect
- N=4 country panel limits formal pre-trends testing power — synthetic control pre-fit used as substitute

### Archive

- Roadmap: `.planning/milestones/v1.0-ROADMAP.md`
- Requirements: `.planning/milestones/v1.0-REQUIREMENTS.md`
