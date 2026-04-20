---
phase: 03-primary-empirics
plan: 04
subsystem: empirics
tags: [python, pandas, statsmodels, matplotlib, seaborn, gpr, geopolitics]

# Dependency graph
requires:
  - phase: 03-01
    provides: GPR raw data provenance and local data_gpr_export.xls artifact
provides:
  - Korea GPR escalation dummy from the 2004-2024 GPRC_KOR 75th percentile
  - KOSPI valuation regression with TOPIX P/B control and year fixed effects
  - Figure 3 geopolitical risk and valuation overlay PDF
  - Geo-risk CSV and LaTeX table with partial-identification caveat
affects: [paper-assembly, phase-03-primary-empirics, geopolitical-risk]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - Standalone analysis script reading config.py paths and canonical panel.parquet
    - statsmodels formula OLS with HC3 robust covariance for KOSPI monthly regression
    - Deterministic matplotlib PDF export with metadata stripped

key-files:
  created:
    - src/analysis/geo_risk.py
    - output/figures/figure3_geo_risk.pdf
    - output/tables/table3_geo_risk.tex
    - output/tables/geo_risk_results.csv
  modified: []

key-decisions:
  - "Used existing Phase 3 Nyquist tests as the TDD RED baseline to avoid editing shared test files during parallel wave execution."
  - "Kept year fixed effects, not month fixed effects, so the one-observation-per-month KOSPI regression does not saturate TOPIX P/B."

patterns-established:
  - "Geo-risk analyses compute GPR thresholds from the filtered study period before constructing escalation indicators."
  - "Geo-risk outputs carry an explicit partial-identification caveat in both machine-readable and LaTeX artifacts."

requirements-completed: [GEO-01, GEO-02, GEO-03]

# Metrics
duration: 4min
completed: 2026-04-20
---

# Phase 03 Plan 04: Geopolitical Risk Sub-Analysis Summary

**Korea GPR escalation analysis with HC3 KOSPI valuation regression, caveated result table, and Figure 3 overlay PDF**

## Performance

- **Duration:** 4 min
- **Started:** 2026-04-20T20:30:18Z
- **Completed:** 2026-04-20T20:33:56Z
- **Tasks:** 2
- **Files modified:** 4

## Accomplishments

- Created `src/analysis/geo_risk.py` as a standalone executable analysis script.
- Loaded `data/raw/data_gpr_export.xls` via fixed `month` and `GPRC_KOR` columns with `xlrd`, filtered to 2004-2024, and computed the 75th percentile escalation threshold.
- Estimated `kospi_pb ~ gpr_escalation_dummy + topix_pb + C(year)` using statsmodels formula OLS with HC3 robust standard errors.
- Wrote `output/tables/geo_risk_results.csv` and `output/tables/table3_geo_risk.tex`, including the required partial-identification caveat.
- Generated `output/figures/figure3_geo_risk.pdf` with GPRC_KOR, KOSPI P/B, TOPIX P/B, and shaded escalation months.

## Task Commits

Each task was committed atomically:

1. **Task 1: Implement GPR escalation dummy and KOSPI valuation regression** - `9b5772c` (feat)
2. **Task 2: Generate Figure 3 geopolitical risk PDF** - `06e2af9` (feat)

## Files Created/Modified

- `src/analysis/geo_risk.py` - Standalone geo-risk loading, merge, regression, table, and figure script.
- `output/tables/geo_risk_results.csv` - Machine-readable threshold and regression coefficient output.
- `output/tables/table3_geo_risk.tex` - Booktabs-style regression table with partial-identification caveat.
- `output/figures/figure3_geo_risk.pdf` - Paper-ready geopolitical risk and valuation overlay figure.

## Decisions Made

- Used the existing `tests/test_phase3.py` geo-risk tests as the RED baseline rather than adding tests to a shared file during parallel execution.
- Preserved year fixed effects in the geo-risk regression to avoid saturating the monthly KOSPI-only model.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

- The worktree contained unrelated orchestrator changes in `.planning/STATE.md` and `.planning/ROADMAP.md`, plus unrelated Wave 2 artifacts. They were left untouched.
- The stub scan matched an optional function default `note: str = ""` in `src/analysis/geo_risk.py`; this is not a UI/data stub and does not block the plan goal.

## User Setup Required

None - no external service configuration required.

## Verification

- `python src/analysis/geo_risk.py` - passed
- `pytest tests/test_phase3.py::test_gpr_threshold tests/test_phase3.py::test_figure3_exists tests/test_phase3.py::test_geo_caveats -x -q` - passed (`3 passed`)
- `grep -qi "partial identification\\|caveat" output/tables/table3_geo_risk.tex` - passed

## Next Phase Readiness

Geo-risk artifacts are ready for paper assembly and Phase 3 verification. The GPR threshold, regression coefficients, caveat text, and Figure 3 output are reproducible from `python src/analysis/geo_risk.py`.

## Self-Check: PASSED

- Found `src/analysis/geo_risk.py`
- Found `output/figures/figure3_geo_risk.pdf`
- Found `output/tables/table3_geo_risk.tex`
- Found `output/tables/geo_risk_results.csv`
- Found `.planning/phases/03-primary-empirics/03-04-SUMMARY.md`
- Found commit `9b5772c`
- Found commit `06e2af9`

---
*Phase: 03-primary-empirics*
*Completed: 2026-04-20*
