---
phase: 03-primary-empirics
plan: 02
subsystem: empirics
tags: [event-study, statsmodels, HC3, matplotlib, seaborn, CAR]

requires:
  - phase: 03-01
    provides: Phase 3 test/data foundation and event-study smoke tests
provides:
  - Standalone stacked event-study script for locked Japan reform dates
  - Machine-readable event-study CAR table
  - Paper-ready event-study coefficient LaTeX table
  - Figure 2 three-panel event-study CAR PDF
affects: [phase-03-primary-empirics, phase-05-paper-assembly, robustness]

tech-stack:
  added: []
  patterns:
    - Standalone analysis script with config event-date firewall
    - Cengiz-style stacked cohorts with overlap annotations
    - Deterministic matplotlib PDF output metadata

key-files:
  created:
    - src/analysis/event_study.py
    - output/tables/event_study_car.csv
    - output/tables/table_event_study_coefs.tex
    - output/figures/figure2_event_study.pdf
  modified: []

key-decisions:
  - "Preserved all 2014/2015 overlapping event-window rows and flagged contamination instead of dropping rows, matching the Cengiz-style stacked design specified in the plan."
  - "Used config.EVENT_DATES and config.EVENT_LABELS exclusively for reform timing and labels to preserve the event-date firewall."
  - "Rendered undefined saturated-cell HC3 diagnostics as -- in LaTeX while retaining machine-readable blank values in CSV."

patterns-established:
  - "Event-study scripts read only panel.parquet plus config event metadata and do not import other analysis modules."
  - "Figure PDFs use Agg backend, seaborn whitegrid, and deterministic CreationDate/ModDate metadata."

requirements-completed: [EVNT-01, EVNT-02, EVNT-03, EVNT-04]

duration: 5 min
completed: 2026-04-20
---

# Phase 03 Plan 02: Stacked Event Study Summary

**Stacked Japan reform event study with complete cohort windows, overlap annotations, CAR table outputs, and a three-panel Figure 2 PDF**

## Performance

- **Duration:** 5 min
- **Started:** 2026-04-20T20:30:03Z
- **Completed:** 2026-04-20T20:35:55Z
- **Tasks:** 2
- **Files modified:** 4

## Accomplishments

- Built `src/analysis/event_study.py` as a standalone executable script that reads `config.EVENT_DATES`, consumes `data/processed/panel.parquet`, constructs three complete -36..+24 stacked cohorts, and estimates -12..+24 CAR paths.
- Wrote `output/tables/event_study_car.csv` with the required columns and 111 rows: 3 cohorts x 37 relative months.
- Wrote `output/tables/table_event_study_coefs.tex` with HC3/CAR notation and `output/figures/figure2_event_study.pdf` as a single non-empty three-panel PDF.

## Task Commits

Each task was committed atomically:

1. **Task 1: Implement stacked cohort construction and HC3 CAR estimates** - `3017e21` (feat)
2. **Task 2: Generate Figure 2 as a combined 3-panel CAR PDF** - `f68ff5d` (feat)

**Plan metadata:** created in final docs commit.

## Files Created/Modified

- `src/analysis/event_study.py` - Stacked cohort construction, HC3 event regression call, CAR output, LaTeX table writer, and Figure 2 plotting.
- `output/tables/event_study_car.csv` - Machine-readable cohort x event-month coefficient/CAR output.
- `output/tables/table_event_study_coefs.tex` - Paper-ready event-study table with HC3 and CAR notation.
- `output/figures/figure2_event_study.pdf` - Combined three-panel event-study CAR figure.

## Decisions Made

- Preserved overlapping 2014/2015 exposure and added `overlaps_other_event_window` plus `overlap_event_labels` rather than excluding contaminated months, because dropping overlap would destroy the locked D-01/D-02 windows.
- Used cohort identifiers derived from the locked event dates and human-readable labels from `config.EVENT_LABELS`.
- Kept Figure 2 as a vertical 3x1 layout, matching the plan's requested `plt.subplots(3, 1, figsize=(8, 9), sharex=True)` contract.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Normalized month-distance helper return type**
- **Found during:** Task 1 (Implement stacked cohort construction and HC3 CAR estimates)
- **Issue:** `_month_distance` returned a pandas `Index` for `DatetimeIndex` inputs, but overlap annotation expected `.iloc`.
- **Fix:** Normalized the helper to return a pandas `Series` for all date-like inputs.
- **Files modified:** `src/analysis/event_study.py`
- **Verification:** `python src/analysis/event_study.py && pytest tests/test_phase3.py::test_three_cohorts tests/test_phase3.py::test_event_study_coefs -x -q`
- **Committed in:** `3017e21`

**2. [Rule 1 - Bug] Removed fragmented dummy-column construction**
- **Found during:** Task 1 (Implement stacked cohort construction and HC3 CAR estimates)
- **Issue:** Building 108 dummy columns by repeated assignment produced pandas fragmentation warnings during every run.
- **Fix:** Built the event-regression design matrix from a dictionary of arrays in one `DataFrame` construction.
- **Files modified:** `src/analysis/event_study.py`
- **Verification:** `python src/analysis/event_study.py && pytest tests/test_phase3.py::test_three_cohorts tests/test_phase3.py::test_event_study_coefs -x -q`
- **Committed in:** `3017e21`

---

**Total deviations:** 2 auto-fixed (2 Rule 1 bug fixes)
**Impact on plan:** Both fixes were local implementation corrections needed for successful and clean execution. No scope expansion.

## Issues Encountered

- The mandated cohort x relative-time dummy design is saturated at the cohort-month cell level: each non-base coefficient has one observation. Statsmodels still executes the required `get_robustcov_results(cov_type="HC3")` call, but HC3 SE/t/p diagnostics are undefined for those saturated cells. The CSV keeps those values machine-readable as blanks and the LaTeX table renders them as `--`; CAR coefficients and Figure 2 are still generated for every required month.
- Existing unrelated worktree changes were present in `.planning/STATE.md`, `.planning/ROADMAP.md`, `src/analysis/panel_ols.py`, and `output/tables/panel_ols_results.csv`. They were not modified or staged by this plan.

## User Setup Required

None - no external service configuration required.

## Known Stubs

None - no placeholder data sources, TODO/FIXME markers, or UI-flow empty stubs were introduced. Empty list/dict initializers in `event_study.py` are local accumulators, not output stubs.

## Threat Flags

None - the implemented trust boundaries match the plan: local `panel.parquet` input, config-sourced event dates, and fixed output paths under `config.OUTPUT_DIR`.

## Verification

- `python src/analysis/event_study.py` exited 0.
- `pytest tests/test_phase3.py::test_three_cohorts tests/test_phase3.py::test_figure2_exists tests/test_phase3.py::test_figure2_panels tests/test_phase3.py::test_event_study_coefs -x -q` exited 0 with 4 passed.
- `grep -q "config.EVENT_DATES" src/analysis/event_study.py` exited 0.
- `grep -q "cov_type=\"HC3\"" src/analysis/event_study.py` exited 0.

## Next Phase Readiness

Event-study outputs are ready for paper assembly and for downstream Phase 3 integration checks. The saturated HC3 diagnostic limitation should be considered in methodology prose or a later robustness/refinement plan if finite event-month inference is required.

## Self-Check: PASSED

- Found created files: `src/analysis/event_study.py`, `output/tables/event_study_car.csv`, `output/tables/table_event_study_coefs.tex`, `output/figures/figure2_event_study.pdf`, and this summary.
- Found task commits in git history: `3017e21` and `f68ff5d`.

---
*Phase: 03-primary-empirics*
*Completed: 2026-04-20*
