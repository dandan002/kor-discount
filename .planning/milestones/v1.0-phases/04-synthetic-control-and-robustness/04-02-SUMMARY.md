---
phase: 04-synthetic-control-and-robustness
plan: 02
subsystem: robustness
tags: [synthetic-control, pysyncon, placebo, robustness, matplotlib]

requires:
  - phase: 04-synthetic-control-and-robustness
    provides: Phase 4 test scaffold, robustness package, and pinned pysyncon dependency from 04-01
provides:
  - ADH synthetic control estimator for Japan's 2023 TSE P/B reform
  - donor weights CSV with pre-treatment RMSPE
  - primary synthetic-control gap figure
  - in-time and in-space placebo robustness figures
affects: [phase-04, final-paper, robustness-section]

tech-stack:
  added: []
  patterns: [pysyncon Dataprep/Synth, manual _gaps plotting, month-start raw-date normalization]

key-files:
  created:
    - src/robustness/synthetic_control.py
    - output/robustness/synthetic_control_weights.csv
    - output/figures/figure_synth_gap.pdf
    - output/robustness/figure_placebo_intime.pdf
    - output/robustness/figure_placebo_inspace.pdf
  modified: []

key-decisions:
  - "Normalized raw donor CSV dates from month-day observations to month starts so pysyncon time periods match the plan's monthly DatetimeIndex windows."
  - "Kept TSE reform references sourced from config.TSE_PB_REFORM_DATE while using the plan-specified 2019-01-01 fake treatment date for the in-time placebo."
  - "Recorded RMSPE > 0.15 as an interpretation caution rather than a hard failure, per the plan."

patterns-established:
  - "Standalone robustness modules inject PROJECT_ROOT and import config directly."
  - "Synthetic-control figures use dataprep.make_outcome_mats() plus synth._gaps(), never synth.gaps_plot()."

requirements-completed: [SYNTH-01, SYNTH-02, SYNTH-03, ROBUST-04]

duration: 5min
completed: 2026-04-20
---

# Phase 04 Plan 02: Synthetic Control and Placebo Robustness Summary

**ADH synthetic control for Japan's 2023 TSE P/B reform with donor weights, RMSPE, gap plot, and in-time/in-space placebo figures**

## Performance

- **Duration:** 5 min
- **Started:** 2026-04-20T23:24:40Z
- **Completed:** 2026-04-20T23:28:50Z
- **Tasks:** 2
- **Files modified:** 5

## Accomplishments

- Built `src/robustness/synthetic_control.py` with TOPIX as treated unit and STOXX600, FTSE100, MSCI_HK, MSCI_TAIWAN, and SP500 as donors.
- Generated `synthetic_control_weights.csv` with weights summing to 1.0 and pre-treatment RMSPE `0.2892855456344879`.
- Created the primary synthetic-control gap PDF plus in-time and in-space placebo PDFs.
- Preserved the required SUTVA comment containing `SUTVA`, `STOXX600`, and `KOSPI`.

## Synthetic Control Results

- **Pre-treatment RMSPE:** `0.2892855456344879`
- **RMSPE threshold note:** RMSPE is above `0.15`; paper text should interpret the synthetic-control fit with caution.
- **Dominant donor weights:** MSCI_HK `1.0000`; STOXX600 `0.0000`; FTSE100 `0.0000`. The fitted convex combination places all rounded weight on MSCI_HK.
- **In-time placebo date:** `2019-01-01`
- **In-space placebo loop:** ran all five donor units as placebo treated units.

## Task Commits

Each task was committed atomically:

1. **Task 1: Implement synthetic control core** - `71ff76b` (feat)
2. **Task 2: Add placebo tests and generated outputs** - `b8fe0b0` (feat)

## Files Created/Modified

- `src/robustness/synthetic_control.py` - Standalone ADH synthetic-control and placebo script.
- `output/robustness/synthetic_control_weights.csv` - Donor weights and repeated pre-treatment RMSPE column.
- `output/figures/figure_synth_gap.pdf` - Primary Japan-minus-synthetic-Japan gap plot.
- `output/robustness/figure_placebo_intime.pdf` - Fake 2019 treatment-date gap plot.
- `output/robustness/figure_placebo_inspace.pdf` - Donor-as-treated placebo distribution plot.

## Decisions Made

- Used `pysyncon.Dataprep` and `Synth` exactly as planned, with `math.sqrt(synth.mspe())` for RMSPE.
- Used `config.TSE_PB_REFORM_DATE` for actual reform markers instead of embedding the date literal in code.
- Normalized raw CSV dates to month starts during loading because source files use the 20th of each month and `pysyncon` requires exact time-period matches.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Normalized raw donor dates to month starts**
- **Found during:** Task 1
- **Issue:** The plan specified `pd.date_range(..., freq="MS")`, but all donor CSV dates are observed on the 20th of each month. Without normalization, the monthly pre-treatment and plotting windows would not match the panel dates.
- **Fix:** Converted loaded dates with `.dt.to_period("M").dt.to_timestamp()` in `load_donor_panel()`.
- **Files modified:** `src/robustness/synthetic_control.py`
- **Verification:** `python src/robustness/synthetic_control.py` exited 0 and the four targeted Phase 4 tests passed.
- **Committed in:** `71ff76b`

---

**Total deviations:** 1 auto-fixed (Rule 3)
**Impact on plan:** Required for runtime correctness with the actual checked-in raw data. No methodological scope change.

## Issues Encountered

- Pre-treatment RMSPE is `0.2893`, above the `0.15` caution threshold. The script logs this warning and continues as required.
- No authentication gates or external service setup were needed.

## Known Stubs

None.

## User Setup Required

None - no external service configuration required.

## Verification

- `python src/robustness/synthetic_control.py` -> exited 0.
- `pytest tests/test_phase4.py::test_synth_weights_sum_to_one tests/test_phase4.py::test_synth_outputs_exist tests/test_phase4.py::test_sutva_comment_present tests/test_phase4.py::test_robust04_outputs_exist -v` -> 4 passed.
- File existence self-check found all created source and output artifacts.
- Commit self-check found task commits `71ff76b` and `b8fe0b0`.

## Self-Check: PASSED

- Found `src/robustness/synthetic_control.py`.
- Found `output/robustness/synthetic_control_weights.csv`.
- Found `output/figures/figure_synth_gap.pdf`.
- Found `output/robustness/figure_placebo_intime.pdf`.
- Found `output/robustness/figure_placebo_inspace.pdf`.
- Found commit `71ff76b`.
- Found commit `b8fe0b0`.

## Next Phase Readiness

Plans 04-03 through 04-05 can build the remaining Phase 4 robustness modules against the Phase 4 test scaffold. Plan 04-06 can later include these generated synthetic-control artifacts in its visual and artifact audit.

---
*Phase: 04-synthetic-control-and-robustness*
*Completed: 2026-04-20*
