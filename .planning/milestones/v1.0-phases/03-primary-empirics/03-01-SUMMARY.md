---
phase: 03-primary-empirics
plan: 01
subsystem: testing-data-foundation
tags: [pytest, pandas, xlrd, gpr, nyquist]

requires:
  - phase: 01-data-foundation
    provides: canonical processed panel and raw-data manifest convention
  - phase: 02-descriptive
    provides: pytest bootstrap and output directory conventions
provides:
  - Phase 3 Nyquist pytest scaffold covering event study, Panel OLS, and geopolitical risk requirements
  - Local Caldara-Iacoviello GPR workbook with manifest provenance
  - xlrd dependency pin for reproducible .xls reads
  - src.analysis package marker for standalone Phase 3 scripts
affects: [03-primary-empirics, event-study, panel-ols, geopolitical-risk]

tech-stack:
  added: [xlrd==2.0.1]
  patterns:
    - analysis modules are imported inside test bodies so collection succeeds before downstream scripts exist
    - GPR source data is downloaded once and read locally by analysis code

key-files:
  created:
    - data/raw/data_gpr_export.xls
    - src/analysis/__init__.py
    - tests/test_phase3.py
  modified:
    - requirements.txt
    - data/raw/MANIFEST.md

key-decisions:
  - "Stored the Caldara-Iacoviello GPR workbook as a local raw data artifact with exact source URL provenance."
  - "Kept Phase 3 analysis imports inside test functions so pytest collection is safe before Wave 2 modules exist."
  - "Treated the full Phase 3 pytest run as an intentional red scaffold; Plan 03-01 gates on collection success."

patterns-established:
  - "Phase 3 tests derive output paths from config.OUTPUT_DIR and raw/processed paths from config constants."
  - "Downstream analysis modules must remain standalone and avoid importing sibling src.analysis modules."

requirements-completed:
  - EVNT-01
  - EVNT-02
  - EVNT-03
  - EVNT-04
  - OLS-01
  - OLS-02
  - OLS-03
  - GEO-01
  - GEO-02
  - GEO-03

duration: 3 min
completed: 2026-04-20
---

# Phase 03 Plan 01: Primary Empirics Foundation Summary

**Phase 3 pytest scaffold and local Caldara-Iacoviello GPR raw data foundation with xlrd-backed Excel verification**

## Performance

- **Duration:** 3 min
- **Started:** 2026-04-20T20:23:29Z
- **Completed:** 2026-04-20T20:26:51Z
- **Tasks:** 2
- **Files modified:** 5

## Accomplishments

- Added `xlrd==2.0.1`, created `src/analysis/__init__.py`, downloaded `data/raw/data_gpr_export.xls`, and documented the exact Caldara-Iacoviello source URL in `data/raw/MANIFEST.md`.
- Created `tests/test_phase3.py` with all 11 planned tests for EVNT-01 through GEO-03.
- Verified the GPR workbook reads with `pd.read_excel(..., engine="xlrd")` and that pytest collects all 11 Phase 3 tests without import-time errors.

## Task Commits

Each task was committed atomically:

1. **Task 1: Pin xlrd, create analysis package, and register GPR provenance** - `a9b4fac` (feat)
2. **Task 2: Create Phase 3 Nyquist test scaffold** - `e89434c` (test)

## Files Created/Modified

- `requirements.txt` - Pins `xlrd==2.0.1` for the Caldara-Iacoviello `.xls` file.
- `src/analysis/__init__.py` - Package marker for standalone Phase 3 analysis modules.
- `data/raw/data_gpr_export.xls` - Local GPR country-level workbook used by the geopolitical risk analysis.
- `data/raw/MANIFEST.md` - Adds external research-data provenance for the GPR workbook.
- `tests/test_phase3.py` - Adds the 11-test Phase 3 validation scaffold.

## Decisions Made

- Stored the GPR export as a local raw data artifact instead of downloading during analysis runs.
- Kept imports of future Phase 3 analysis modules inside test functions so `pytest --collect-only` remains green before Wave 2 implementation.
- Confirmed the full `pytest tests/test_phase3.py -x -q` command is intentionally red at this point because `src.analysis.event_study` and other downstream modules are not created until later plans.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

- `pytest tests/test_phase3.py -x -q` failed as expected on `ImportError: cannot import name 'event_study' from 'src.analysis'`; this is the planned red scaffold state before downstream analysis modules exist.
- Pytest created untracked `__pycache__` directories during verification; they were removed as generated artifacts and not committed.

## Known Stubs

None - no placeholder, TODO, or unwired mock-data stubs were found in the files created or modified by this plan. The empty `src/analysis/__init__.py` is an intentional package marker.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

Plan 03-02 can implement `src/analysis/event_study.py` against the now-present tests and local GPR foundation. Plan-level verification commands passed:

- `python -c "import pandas as pd; df = pd.read_excel('data/raw/data_gpr_export.xls', usecols=['month','GPRC_KOR'], engine='xlrd'); assert len(df) > 0; print('GPR XLS OK')"`
- `pytest tests/test_phase3.py --collect-only -q`

STATE.md and ROADMAP.md were intentionally not updated in this worktree because the parallel orchestrator owns those shared writes after all wave agents complete.

## Self-Check: PASSED

- Verified all created/modified plan files exist.
- Verified task commits `a9b4fac` and `e89434c` exist in git history.
- Re-ran `pytest tests/test_phase3.py --collect-only -q`; it collected 11 tests and exited 0.

---
*Phase: 03-primary-empirics*
*Completed: 2026-04-20*
