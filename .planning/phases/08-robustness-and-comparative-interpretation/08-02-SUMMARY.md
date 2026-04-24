---
phase: 08-robustness-and-comparative-interpretation
plan: 02
subsystem: analysis
tags: [python, pandas, event-study, korea, robustness, testing, comparative-interpretation]
requires:
  - phase: 08-robustness-and-comparative-interpretation
    provides: "Policy-driven Phase 8 robustness runner and tmp-output Phase 8 test harness from 08-01"
provides:
  - "Named narrow_2024_rollout_post12 sensitivity anchored to the Korea primary policy dates"
  - "Machine-readable Phase 8 summary CSV spanning baseline, +12 sensitivity, and spaced +2 robustness windows"
  - "Comparator scope note that routes benchmark sensitivity to existing repo surfaces without touching event_study_core.py"
affects: [phase-08-interpretation, phase-09-paper, phase-09-replication]
tech-stack:
  added: []
  patterns: ["Summary rows derived from freshly generated CAR outputs", "Comparator sensitivity documented via note artifact instead of core API expansion"]
key-files:
  created: [output/figures/figure_korea_event_study_robustness_narrow_2024_rollout_post12.pdf, output/tables/korea_event_study_robustness_narrow_2024_rollout_post12_car.csv, output/tables/table_korea_event_study_robustness_narrow_2024_rollout_post12_coefs.tex, output/tables/korea_event_study_robustness_summary.csv, output/tables/korea_event_study_comparator_scope_note.tex]
  modified: [tests/test_phase8.py, src/analysis/korea_event_study_robustness.py]
key-decisions:
  - "Kept src/analysis/event_study_core.py fixed at the KOSPI-TOPIX spread and routed comparator sensitivity into a standalone scope note"
  - "Derived the Phase 8 summary CSV from just-generated CAR outputs so tmp-path reruns and downstream note generation consume the same contract"
patterns-established:
  - "Phase 8 default robustness order is narrow_2024_rollout -> narrow_2024_rollout_post12 -> spaced_follow_through"
  - "run_korea_robustness_specs(output_root=...) writes both korea_event_study_robustness_summary.csv and korea_event_study_comparator_scope_note.tex under the requested root"
requirements-completed: [KROB-02]
duration: 4 min
completed: 2026-04-24
---

# Phase 8 Plan 02: Window/comparator sensitivity Summary

**A +12 narrow Korea rerun, generated robustness summary CSV, and comparator scope note now extend the Phase 8 runner without refactoring the shared KOSPI-TOPIX event-study core**

## Performance

- **Duration:** 4 min
- **Started:** 2026-04-24T15:32:47-04:00
- **Completed:** 2026-04-24T19:36:38Z
- **Tasks:** 2
- **Files modified:** 7

## Accomplishments

- Added a fresh-output Phase 8 test gate for `narrow_2024_rollout_post12` and a source-level contract test that rejects comparator API creep in `event_study_core.py`.
- Extended the Phase 8 robustness runner with the required `+12` narrow sensitivity while preserving the shipped `narrow_2024_rollout` baseline and the `spaced_follow_through` `+2` robustness-only spec.
- Generated the new `post12` CAR/table/figure outputs plus a machine-readable summary CSV and comparator-scope note for downstream interpretation work.

## Task Commits

Each task was committed atomically:

1. **Task 1: Extend the Phase 8 test gate for the `+12` narrow sensitivity and comparator contract** - `c4972eb` (`test`)
2. **Task 2: Add the `+12` narrow rerun, summary CSV, and comparator-scope note** - `612e3bc` (`feat`)

## Files Created/Modified

- `tests/test_phase8.py` - Adds the `narrow_2024_rollout_post12` rerun gate and guards the fixed KOSPI-TOPIX comparator contract plus scope-note paths.
- `src/analysis/korea_event_study_robustness.py` - Adds the explicit `post12` spec, writes the summary CSV from generated CAR outputs, and emits the comparator scope note for any output root.
- `output/tables/korea_event_study_robustness_narrow_2024_rollout_post12_car.csv` - Machine-readable CAR output for the required narrow `+12` sensitivity.
- `output/tables/table_korea_event_study_robustness_narrow_2024_rollout_post12_coefs.tex` - LaTeX table for the `post12` rerun.
- `output/figures/figure_korea_event_study_robustness_narrow_2024_rollout_post12.pdf` - Figure artifact for the `post12` rerun.
- `output/tables/korea_event_study_robustness_summary.csv` - One-row-per-spec summary of the baseline, required sensitivity, and robustness-only spaced follow-through windows.
- `output/tables/korea_event_study_comparator_scope_note.tex` - Interpretation-ready note pointing comparator sensitivity to the already-shipped descriptive and robustness artifacts.

## Decisions Made

- Kept comparator sensitivity outside the shared estimator and encoded that boundary through both the source-level test and the generated scope note.
- Used `set_role` values `baseline`, `window_sensitivity`, and `robustness_only` so `08-03` can consume a stable semantic contract from the summary CSV.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

- `matplotlib` created a temporary cache directory under `/var/folders/...` because the default user cache path was not writable in the sandbox.
- `pyarrow` emitted non-fatal `sysctlbyname` warnings while reading `panel.parquet`. Artifact generation and all verification commands still completed successfully.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- `08-03` can now read `output/tables/korea_event_study_robustness_summary.csv` and `output/tables/korea_event_study_comparator_scope_note.tex` to generate the Japan-versus-Korea interpretation note without recomputing the event-study logic.
- The tmp-output Phase 8 runner now regenerates every prerequisite robustness artifact needed for the remaining interpretation work.

## Self-Check: PASSED

- Found summary file: `.planning/phases/08-robustness-and-comparative-interpretation/08-02-SUMMARY.md`
- Found task commits: `c4972eb`, `612e3bc`
- Stub scan across modified plan files returned no placeholder or empty-value markers that block the plan goal
