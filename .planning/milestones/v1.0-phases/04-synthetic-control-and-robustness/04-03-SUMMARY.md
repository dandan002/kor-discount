---
phase: 04-synthetic-control-and-robustness
plan: 03
subsystem: robustness
tags: [python, pandas, statsmodels, matplotlib, placebo, event-study]

# Dependency graph
requires:
  - phase: 03-primary-empirics
    provides: Stacked event-study design and locked Japan reform event windows
  - phase: 04-synthetic-control-and-robustness
    provides: Robustness output directory and Phase 4 smoke-test scaffold
provides:
  - Taiwan and Indonesia placebo falsification CAR estimates
  - Combined placebo falsification PDF figure
  - Standalone robustness_placebo.py script with no src.analysis or src.robustness imports
affects: [phase-04, phase-05-paper-assembly, robustness, falsification]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - Standalone robustness script adapting Phase 3 event-study logic inline
    - Monthly date normalization for raw placebo CSVs before panel joins

key-files:
  created:
    - src/robustness/robustness_placebo.py
    - output/robustness/placebo_taiwan_car.csv
    - output/robustness/placebo_indonesia_car.csv
    - output/robustness/figure_placebo_falsification.pdf
  modified: []

key-decisions:
  - "Normalized raw placebo CSV dates and TOPIX panel dates to monthly periods before merging."
  - "Used the current Phase 3 pre-trend abnormal-spread construction for placebo cohorts, then estimated pooled event-time CARs with HC3 intervals."

patterns-established:
  - "ROBUST-01 placebo scripts load raw market P/B series plus TOPIX from panel.parquet and write all artifacts to output/robustness/."
  - "Placebo falsification outputs include event_rel_time, car, ci_lo, and ci_hi for downstream figure/table assembly."

requirements-completed: [ROBUST-01]

# Metrics
duration: 4min
completed: 2026-04-20
---

# Phase 04 Plan 03: Placebo Falsification Summary

**Taiwan and Indonesia placebo event studies using Japan reform windows, with CAR CSVs and a combined falsification figure**

## Performance

- **Duration:** 4 min
- **Started:** 2026-04-20T23:31:35Z
- **Completed:** 2026-04-20T23:35:19Z
- **Tasks:** 1
- **Files modified:** 4

## Accomplishments

- Added `src/robustness/robustness_placebo.py`, a standalone script that does not import from `src.analysis` or other `src.robustness` modules.
- Generated `placebo_taiwan_car.csv`, `placebo_indonesia_car.csv`, and `figure_placebo_falsification.pdf` in `output/robustness/`.
- Taiwan and Indonesia do not produce statistically clean placebo effects at the 24-month horizon: both final HC3 intervals include zero.

## Falsification Results

| Market | CAR at t=0 | 95% CI at t=0 | CAR at t=24 | 95% CI at t=24 |
|--------|------------|---------------|-------------|----------------|
| Taiwan | -0.0531 | [-0.3043, 0.1980] | 2.3311 | [-0.1906, 4.8528] |
| Indonesia | 0.1161 | [-0.0618, 0.2941] | 1.3698 | [-3.8116, 6.5513] |

Interpretation: the placebo CAR point estimates drift positive by month 24, especially Taiwan, but both confidence intervals include zero. The combined placebo figure should be used as falsification evidence with cautious wording: non-reform markets do not show precisely estimated Japan-like effects.

## Task Commits

Each task was committed atomically:

1. **Task 1: Implement robustness_placebo.py — Taiwan and Indonesia falsification event studies** - `f8872a4` (feat)

## Files Created/Modified

- `src/robustness/robustness_placebo.py` - Loads placebo market CSVs, builds placebo-minus-TOPIX stacked cohorts, estimates pooled CARs, and writes the combined figure.
- `output/robustness/placebo_taiwan_car.csv` - Taiwan placebo CAR estimates with event-time confidence intervals.
- `output/robustness/placebo_indonesia_car.csv` - Indonesia placebo CAR estimates with event-time confidence intervals.
- `output/robustness/figure_placebo_falsification.pdf` - Two-panel placebo falsification figure.

## Decisions Made

- Normalized raw placebo dates and TOPIX panel dates to monthly periods before merging. The raw MSCI placebo CSVs are dated on the 20th of each month, while `panel.parquet` uses month-end dates.
- Preserved the current Phase 3 event-study detrending pattern by estimating pre-event trends for each cohort and running the placebo OLS on abnormal spread values.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Normalized monthly dates before placebo/TOPIX merge**
- **Found during:** Task 1 (Implement robustness_placebo.py)
- **Issue:** Raw Taiwan and Indonesia CSVs use dates like `2004-01-20`, while TOPIX rows in `panel.parquet` use month-end dates like `2004-01-31`. A literal timestamp merge would produce an empty spread panel.
- **Fix:** Converted both sources to monthly periods and then to normalized timestamps before joining.
- **Files modified:** `src/robustness/robustness_placebo.py`
- **Verification:** `python src/robustness/robustness_placebo.py` produced both CAR CSVs and the combined PDF; targeted Phase 4 tests passed.
- **Committed in:** `f8872a4`

---

**Total deviations:** 1 auto-fixed (Rule 1).
**Impact on plan:** The fix was required for correctness and did not change the planned outputs or scope.

## Issues Encountered

- The placebo raw CSV date convention differed from the processed panel date convention. This was resolved with monthly-period normalization.

## Known Stubs

None. Stub scan found only normal accumulator initializations inside the script; no placeholder data sources or UI-facing empty values were introduced.

## User Setup Required

None - no external service configuration required.

## Verification

- `python src/robustness/robustness_placebo.py` exited 0.
- `python -m pytest tests/test_phase4.py::test_placebo_outputs_exist tests/test_phase4.py::test_robustness_modules_do_not_import_each_other -v` passed: 2 passed.
- Schema checks passed for both placebo CSV files.
- Forbidden cross-import check passed: no `src.analysis` or `src.robustness` imports in `robustness_placebo.py`.

## Next Phase Readiness

ROBUST-01 is ready for Phase 5 paper assembly. Use cautious falsification wording: placebo confidence intervals include zero, but Taiwan's positive month-24 point estimate should not be described as a strict zero effect.

## Self-Check: PASSED

- Found all created files on disk.
- Found task commit `f8872a4` in git history.

---
*Phase: 04-synthetic-control-and-robustness*
*Completed: 2026-04-20*
