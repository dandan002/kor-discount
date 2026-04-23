---
phase: 07-korea-value-up-event-study
plan: 01
subsystem: analysis
tags: [python, pytest, event-study, japan, korea]
requires:
  - phase: 06-korea-reform-date-locking-and-sample-horizon
    provides: "Locked Korea event-set policy and follow-on study horizon"
provides:
  - "Phase 7 contract tests covering Korea-vs-Japan artifact isolation"
  - "Reusable event-study core with explicit event inputs and output paths"
  - "Standalone Korea event-study scaffold using the primary policy directly"
affects: [phase-07-plan-02, phase-07-plan-03, output-contracts]
tech-stack:
  added: []
  patterns: [shared-event-study-core, preserved-japan-entrypoint, explicit-korea-policy-selection]
key-files:
  created: [tests/test_phase7.py, src/analysis/event_study_core.py, src/analysis/korea_event_study.py]
  modified: [src/analysis/event_study.py]
key-decisions:
  - "Kept src/analysis/event_study.py as the Japan CLI and moved reusable logic into src/analysis/event_study_core.py."
  - "Bound the Korea scaffold to config.KOREA_EVENT_SET_POLICY['primary'] instead of mutating config.EVENT_DATES or config.EVENT_LABELS."
patterns-established:
  - "Event-study entrypoints should pass locked dates, labels, horizons, and artifact paths explicitly into the shared core."
  - "Japan artifact names remain fixed while Korea outputs use distinct filenames under the same output directories."
requirements-completed: [KEVNT-03, KEVNT-04]
duration: 8min
completed: 2026-04-23
---

# Phase 7 Plan 01: Korea Event-Study Foundation Summary

**Shared event-study core with preserved Japan artifact paths, a Korea primary-policy scaffold, and Phase 7 contract coverage for output isolation**

## Performance

- **Duration:** 8 min
- **Started:** 2026-04-23T19:49:18Z
- **Completed:** 2026-04-23T19:57:31Z
- **Tasks:** 2
- **Files modified:** 4

## Accomplishments

- Added `tests/test_phase7.py` to encode the Korea-versus-Japan path contract, the primary Korea policy contract, and the deferred Korea output expectations.
- Extracted reusable cohort-building, estimation, overlap annotation, and output-writing logic into `src/analysis/event_study_core.py`.
- Preserved `src/analysis/event_study.py` as the Japan entrypoint with the shipped artifact filenames while adding `src/analysis/korea_event_study.py` as a standalone Korea scaffold.

## Task Commits

Each task was committed atomically:

1. **Task 1: Create the Phase 7 Korea event-study test contract** - `535e9e3` (`test`)
2. **Task 2: Factor a shared event-study core and add the Korea entrypoint scaffold** - `23f8e4b` (`feat`)

**Plan metadata:** pending summary commit

## Files Created/Modified

- `tests/test_phase7.py` - Phase 7 contract checks for Korea policy selection, artifact-name separation, source-level overlap handling, and deferred Korea outputs.
- `src/analysis/event_study_core.py` - Shared event-study helpers parameterized by event dates, labels, study horizon, event windows, titles, and output paths.
- `src/analysis/event_study.py` - Thin Japan wrapper that preserves the shipped CLI and artifact filenames while delegating reusable work to the shared core.
- `src/analysis/korea_event_study.py` - Standalone Korea scaffold wired to `config.KOREA_EVENT_SET_POLICY["primary"]` and Korea-specific artifact paths.

## Decisions Made

- Kept the Japan entrypoint surface stable for `tests/test_phase3.py` by wrapping the shared core instead of replacing the public functions outright.
- Used Korea-specific filenames under `output/figures/` and `output/tables/` so later Korea generation cannot silently overwrite the shipped Japan artifacts.
- Left the two Korea artifact-content tests red by design because Plan `07-02` is responsible for generating `korea_event_study_car.csv`, `table_korea_event_study_coefs.tex`, and `figure_korea_event_study.pdf`.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

- A transient `.git/index.lock` blocked the Task 2 commit after overlapping git operations. The lock was no longer present on re-check, and the commit succeeded when retried serially.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Plan `07-02` can now generate the Korea CSV, LaTeX, and PDF artifacts through the standalone Korea entrypoint without changing Japan artifact names.
- `pytest tests/test_phase7.py -q` now fails only on the two Korea artifact-generation checks, which is the expected handoff state for the next plan.
- `STATE.md`, `ROADMAP.md`, and `REQUIREMENTS.md` were left untouched in this dirty main-tree execution to avoid absorbing unrelated baseline planning changes into this plan’s commits.

## Self-Check

PASSED

- Found `.planning/phases/07-korea-value-up-event-study/07-01-SUMMARY.md`
- Found task commits `535e9e3` and `23f8e4b` in `git log --oneline --all`

---
*Phase: 07-korea-value-up-event-study*
*Completed: 2026-04-23*
