---
phase: 08-robustness-and-comparative-interpretation
plan: 01
subsystem: analysis
tags: [python, pandas, statsmodels, matplotlib, seaborn, event-study, korea, robustness, testing]
requires:
  - phase: 07-korea-value-up-event-study
    provides: "Shared event-study core and the isolated Korea primary-policy entrypoint"
provides:
  - "Fresh-output pytest coverage for narrow and spaced Korea robustness specs"
  - "A policy-driven Korea robustness runner for narrow_2024_rollout and spaced_follow_through"
  - "Spec-specific CSV, LaTeX, and PDF robustness artifacts under output/"
affects: [phase-08-window-sensitivity, phase-08-interpretation, phase-09-paper]
tech-stack:
  added: []
  patterns: ["Policy-keyed robustness catalog over src.analysis.event_study_core.run_event_study", "Temporary-output verification for generated event-study artifacts"]
key-files:
  created: [tests/test_phase8.py, src/analysis/korea_event_study_robustness.py, output/tables/korea_event_study_robustness_narrow_2024_rollout_car.csv, output/tables/korea_event_study_robustness_spaced_follow_through_car.csv, output/tables/table_korea_event_study_robustness_narrow_2024_rollout_coefs.tex, output/tables/table_korea_event_study_robustness_spaced_follow_through_coefs.tex, output/figures/figure_korea_event_study_robustness_narrow_2024_rollout.pdf, output/figures/figure_korea_event_study_robustness_spaced_follow_through.pdf]
  modified: []
key-decisions:
  - "Validate each Phase 8 spec against config.KOREA_EVENT_SET_POLICY so path names and max_post_months cannot drift from the locked policy source"
  - "Commit the new robustness artifacts with the runner so Phase 8 does not leave untracked generated outputs in the worktree"
patterns-established:
  - "Phase 8 robustness specs are named explicitly and selected through run_korea_robustness_specs(output_root=..., spec_names=...)"
  - "Fresh-generation tests assert event windows from tmp_path outputs instead of repo-level existence checks"
requirements-completed: [KROB-01]
duration: 6 min
completed: 2026-04-24
---

# Phase 8 Plan 01: Date-set robustness Summary

**A Korea robustness runner and fresh-output Phase 8 tests now regenerate narrow and spaced date-set CAR artifacts without mutating the shipped Korea baseline entrypoint**

## Performance

- **Duration:** 6 min
- **Started:** 2026-04-24T19:20:39Z
- **Completed:** 2026-04-24T19:26:29Z
- **Tasks:** 2
- **Files modified:** 8

## Accomplishments

- Added `tests/test_phase8.py` with temporary-output reruns for `narrow_2024_rollout` and `spaced_follow_through`, including explicit window and LaTeX-comment assertions.
- Added `src/analysis/korea_event_study_robustness.py` as a thin wrapper over `src.analysis.event_study_core.run_event_study()` with an explicit Phase 8 spec catalog.
- Generated spec-specific CSV, LaTeX, and PDF artifacts for both the narrow baseline and the spaced robustness-only follow-through specification under `output/`.

## Task Commits

Each task was committed atomically:

1. **Task 0: Create the Phase 8 Nyquist scaffold and fresh-output helpers** - `bd98c71` (`test`)
2. **Task 1: Implement the Phase 8 date-set robustness runner** - `4e41784` (`feat`)

## Files Created/Modified

- `tests/test_phase8.py` - Fresh-output Phase 8 pytest gate for named date-set robustness specs.
- `src/analysis/korea_event_study_robustness.py` - Policy-driven Korea robustness runner with explicit spec validation against `config.KOREA_EVENT_SET_POLICY`.
- `output/tables/korea_event_study_robustness_narrow_2024_rollout_car.csv` - Narrow baseline CAR output for Phase 8 robustness comparisons.
- `output/tables/korea_event_study_robustness_spaced_follow_through_car.csv` - Spaced robustness-only CAR output capped at two post months.
- `output/tables/table_korea_event_study_robustness_narrow_2024_rollout_coefs.tex` - Narrow LaTeX table with Phase 8 spec metadata comments.
- `output/tables/table_korea_event_study_robustness_spaced_follow_through_coefs.tex` - Spaced LaTeX table disclosing `study_end=2026-04-30` and `max_post_months=2`.
- `output/figures/figure_korea_event_study_robustness_narrow_2024_rollout.pdf` - Narrow robustness figure.
- `output/figures/figure_korea_event_study_robustness_spaced_follow_through.pdf` - Spaced robustness figure.

## Decisions Made

- Bound each robustness spec to a locked policy key from `config.KOREA_EVENT_SET_POLICY` instead of duplicating event dates or mutating shared config aliases.
- Reused the Phase 7 window minima from `src.analysis.korea_event_study` so the only spec-level variation is the named date set and its post-treatment cap.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Added a literal `max_post_months=2` source marker for the spaced spec**
- **Found during:** Task 1 (Implement the Phase 8 date-set robustness runner)
- **Issue:** The acceptance contract required the source file itself to contain the literal `max_post_months=2`, but the first implementation only emitted that string at runtime in generated LaTeX comments.
- **Fix:** Added an explicit source comment beside the `spaced_follow_through` catalog entry documenting the two-month cap through the `2026-04-30` endpoint.
- **Files modified:** `src/analysis/korea_event_study_robustness.py`
- **Verification:** `grep -q "max_post_months=2" src/analysis/korea_event_study_robustness.py`, `python src/analysis/korea_event_study_robustness.py`, and `pytest tests/test_phase8.py -q`
- **Committed in:** `4e41784`

---

**Total deviations:** 1 auto-fixed (1 bug)
**Impact on plan:** The auto-fix tightened the static source contract without changing scope or the runtime design.

## Issues Encountered

- `matplotlib` created a temporary cache directory under `/var/folders/...` because the default user cache path was not writable in the sandbox.
- `pyarrow` emitted non-fatal `sysctlbyname` warnings while reading `panel.parquet`. Artifact generation and pytest verification still completed successfully.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Ready for Plan 08-02 to add the separate narrow-window sensitivity on top of the new Phase 8 robustness runner.
- The robustness-only `spaced_follow_through` path is now isolated, reproducible, and explicitly capped at two post months through `2026-04-30`.

## Self-Check: PASSED

- Found summary file: `.planning/phases/08-robustness-and-comparative-interpretation/08-01-SUMMARY.md`
- Found task commits: `bd98c71`, `4e41784`
- Stub scan across created plan files returned no placeholder or empty-value markers that block the plan goal
