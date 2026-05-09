---
phase: 04-synthetic-control-and-robustness
plan: 05
subsystem: robustness
tags: [python, panel-ols, linearmodels, robustness, em-benchmark]

requires:
  - phase: 03-primary-empirics
    provides: Phase 3 PanelOLS specification and canonical panel output
  - phase: 04-synthetic-control-and-robustness
    provides: Phase 4 robustness test harness and output directory
provides:
  - ROBUST-03 alternative EM control group robustness tables
  - Standalone PanelOLS script for MSCI EM Asia and EM ex-China controls
affects: [phase-04, final-paper, robustness-section]

tech-stack:
  added: []
  patterns:
    - Standalone robustness scripts copy required Phase 3 logic inline
    - Alternative raw benchmark dates are normalized to canonical month-end panel dates

key-files:
  created:
    - src/robustness/robustness_alt_control.py
    - output/robustness/robustness_alt_control_em_asia.tex
    - output/robustness/robustness_alt_control_em_exchina.tex
  modified: []

key-decisions:
  - "MSCI EM Asia used as the available EM ex-Korea proxy for ROBUST-03 variant A."
  - "EM ex-China proxy uses CHINA_WEIGHT_APPROX = 0.30 and must be described as an approximation in paper text."
  - "Raw alternative benchmark dates are converted to month-end to align with panel.parquet time fixed effects."

patterns-established:
  - "ROBUST-03 alt-control scripts validate raw P/B CSV schema before estimation."
  - "ROBUST-03 output tables report robust standard errors, without wild bootstrap p-values."

requirements-completed: [ROBUST-03]

duration: 4min
completed: 2026-04-20
---

# Phase 04 Plan 05: Alternative Control Group Robustness Summary

**Standalone ROBUST-03 PanelOLS checks with MSCI EM Asia and approximate EM ex-China benchmarks replacing MSCI EM**

## Performance

- **Duration:** 4 min
- **Started:** 2026-04-20T23:44:30Z
- **Completed:** 2026-04-20T23:47:53Z
- **Tasks:** 1
- **Files modified:** 3

## Accomplishments

- Added `src/robustness/robustness_alt_control.py`, a standalone script with no imports from `src.analysis` or `src.robustness`.
- Generated both ROBUST-03 LaTeX outputs in `output/robustness/`.
- Confirmed the later Japan reform interaction signs are robust to the alternative EM controls.

## Results

Phase 3 `+ reform x Japan` interaction estimates were:

| Term | Phase 3 coef | EM Asia coef | EM ex-China coef |
|------|--------------|--------------|------------------|
| Stewardship x Japan | 0.087 | -0.012 | 0.050 |
| Corporate Governance Code x Japan | -0.321 | -0.281 | -0.316 |
| TSE P/B Reform x Japan | -0.235 | -0.237 | -0.294 |

The CGC and TSE P/B reform estimates directionally confirm the Phase 3 PanelOLS findings under both alternative EM benchmarks. The Stewardship Code term is small and sensitive to benchmark choice, so it should not be emphasized as robust evidence in the paper.

## Data Alignment

The canonical `panel.parquet` uses month-end dates, while the raw alternative-control CSVs use the 20th of each month. The script normalizes raw alternative-control dates to month-end before constructing the regression panel, so the substituted EM benchmark rows align with the base panel's time fixed effects.

## Task Commits

Each task was committed atomically:

1. **Task 1: Implement robustness_alt_control.py - MSCI EM Asia and EM ex-China panel OLS variants** - `e372a5f` (feat)

## Files Created/Modified

- `src/robustness/robustness_alt_control.py` - Standalone ROBUST-03 script that loads the base panel, substitutes alternative EM controls, constructs reform interactions, and runs two-way FE PanelOLS.
- `output/robustness/robustness_alt_control_em_asia.tex` - LaTeX robustness table for MSCI EM Asia control group.
- `output/robustness/robustness_alt_control_em_exchina.tex` - LaTeX robustness table for approximate EM ex-China control group.

## Decisions Made

- Used `CHINA_WEIGHT_APPROX = 0.30` for the EM ex-China proxy, explicitly documented as an approximation in source comments.
- Kept the script standalone and copied the needed PanelOLS construction logic inline, preserving the Phase 4 anti-cross-import rule.
- Normalized raw alternative benchmark dates to month-end because `panel.parquet` is month-end indexed.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 - Missing Critical] Normalized raw alternative-control dates to month-end**
- **Found during:** Task 1 (ROBUST-03 script implementation)
- **Issue:** Raw alternative-control CSVs are dated on the 20th of each month, while `panel.parquet` uses month-end dates. Direct concatenation would create mismatched time fixed-effect periods.
- **Fix:** Added `_month_end_dates()` and applied it to every raw P/B CSV loaded by `robustness_alt_control.py`.
- **Files modified:** `src/robustness/robustness_alt_control.py`
- **Verification:** `python src/robustness/robustness_alt_control.py` completed; targeted ROBUST-03 tests passed.
- **Committed in:** `e372a5f`

---

**Total deviations:** 1 auto-fixed (Rule 2)
**Impact on plan:** The adjustment preserves the intended analysis and prevents a time-index alignment error. No scope expansion.

## Issues Encountered

None beyond the date alignment issue documented as an auto-fixed deviation.

## Known Stubs

None. Stub-pattern scan only found intentional empty specification lists used to represent the baseline model.

## Threat Flags

None. The implementation uses only the local file inputs and computed proxy boundary already covered by the plan threat model.

## User Setup Required

None - no external service configuration required.

## Verification

- `python src/robustness/robustness_alt_control.py`
- `pytest tests/test_phase4.py::test_robust03_outputs_exist tests/test_phase4.py::test_robustness_modules_do_not_import_each_other -v`
- Acceptance checks confirmed both LaTeX files exist and are non-empty, `CHINA_WEIGHT_APPROX = 0.30` is documented, and forbidden cross-imports are absent.

## Next Phase Readiness

ROBUST-03 is ready for Phase 4 aggregation and final paper integration. The paper should describe the EM ex-China control as an approximate proxy using a 30 percent MSCI EM China weight assumption.

## Self-Check: PASSED

- Found `src/robustness/robustness_alt_control.py`
- Found `output/robustness/robustness_alt_control_em_asia.tex`
- Found `output/robustness/robustness_alt_control_em_exchina.tex`
- Found task commit `e372a5f`

---
*Phase: 04-synthetic-control-and-robustness*
*Completed: 2026-04-20*
