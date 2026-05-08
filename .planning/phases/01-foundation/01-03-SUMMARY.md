---
phase: 01-foundation
plan: 03
subsystem: data-acquisition
tags: [python, blpapi, bloomberg, kospi, pandas]

requires:
  - phase: 01-foundation-02
    provides: Bloomberg BDP and BDS wrappers with safe import behavior when blpapi is unavailable
provides:
  - KOSPI universe acquisition script using BDS members and BDP identifying fields
  - Filtering logic for financial firms and post-2023 IPOs
  - Raw universe CSV writer for data/raw/universe_raw.csv
affects: [phase-01-foundation, phase-02-data-pipeline, bloomberg-terminal-run]

tech-stack:
  added: []
  patterns:
    - Acquisition scripts guard missing blpapi before live Bloomberg calls
    - Root utils package is imported from src scripts through a project-root sys.path insert
    - Runtime Bloomberg connection errors are printed cleanly and exit non-zero

key-files:
  created:
    - src/00_build_universe.py
  modified: []

key-decisions:
  - "Use the exact BDS call bds(\"KOSPI Index\", \"INDX_MEMBERS\") for KOSPI membership acquisition."
  - "Keep output columns limited to ticker, name, sector, industry, country, and ipo_date for downstream scripts."
  - "Catch Bloomberg RuntimeError failures at script entry so offline terminal-connection failures do not traceback."

patterns-established:
  - "Build acquisition scripts as thin orchestration layers over utils.bbg wrappers."
  - "Validate raw Bloomberg pulls before writing data/raw outputs."
  - "Preserve missing IPO dates while dropping only known post-2023 IPOs."

requirements-completed: [DATA-01, DATA-05]

duration: 3 min
completed: 2026-05-08
---

# Phase 01 Plan 03: Build Universe Script Summary

**Bloomberg-ready KOSPI universe acquisition with BDS membership pull, BDP identifiers, and offline-safe failure behavior**

## Performance

- **Duration:** 3 min
- **Started:** 2026-05-08T17:43:06Z
- **Completed:** 2026-05-08T17:46:23Z
- **Tasks:** 1
- **Files modified:** 1

## Accomplishments

- Created `src/00_build_universe.py` to pull KOSPI constituents with `bds("KOSPI Index", "INDX_MEMBERS")`.
- Added BDP identifying fields: `TICKER`, `NAME`, `GICS_SECTOR_NAME`, `GICS_INDUSTRY_NAME`, `CNTRY_ISSUE_ISO`, and `EQY_FUND_DT`.
- Implemented filters for `sector == "Financials"` and IPO dates after `2023-01-01`.
- Wrote the final universe to `data/raw/universe_raw.csv` with columns `ticker`, `name`, `sector`, `industry`, `country`, and `ipo_date`.
- Verified missing-`blpapi` behavior with a simulated import failure: clear Bloomberg terminal guidance, exit code 1, no traceback.

## Task Commits

Each task was committed atomically:

1. **Task 1: Implement src/00_build_universe.py** - `2cd0a3d` (feat)

## Files Created/Modified

- `src/00_build_universe.py` - KOSPI universe acquisition script, Bloomberg availability guard, identifying-field pull, filters, and CSV writer.

## Decisions Made

- Used the literal `bds("KOSPI Index", "INDX_MEMBERS")` call so terminal verification and static checks match the plan contract exactly.
- Added a project-root `sys.path.insert` before `utils.bbg` import, following the plan's Pitfall 4 mitigation for `python src/00_build_universe.py`.
- Preserved missing IPO dates rather than dropping them; only known IPO dates after `2023-01-01` are excluded.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 - Missing Critical] Cleanly handled Bloomberg terminal connection failures**
- **Found during:** Task 1 (Implement src/00_build_universe.py)
- **Issue:** The planned code handled missing `blpapi`, but if `blpapi` is installed and no Bloomberg terminal service is reachable, `utils.bbg` raises `RuntimeError`; without handling, the script would traceback in offline environments.
- **Fix:** Wrapped `build_universe()` in `main()` with a `RuntimeError` handler that prints `Error: ...` to stderr and exits with code 1.
- **Files modified:** `src/00_build_universe.py`
- **Verification:** `python src/00_build_universe.py` on this machine exits 1 with a Bloomberg terminal connection error and no Python traceback.
- **Committed in:** `2cd0a3d`

---

**Total deviations:** 1 auto-fixed (1 missing critical)
**Impact on plan:** The fix preserves the planned terminal behavior and improves offline failure handling without expanding the data contract.

## Issues Encountered

- The local environment has `blpapi` installed but no Bloomberg terminal service listening on `127.0.0.1:8194`. The script now reports that terminal connection failure cleanly and exits 1.
- `src/01_bloomberg_pull.py` was present as an untracked file during this plan, likely from concurrent plan 01-04 work. It was left untouched per ownership constraints.
- Shared tracking files contained mixed 01-03 and 01-04 updates after concurrent execution. They were not committed by the 01-03 metadata commit; the orchestrator should reconcile `STATE.md`, `ROADMAP.md`, and `REQUIREMENTS.md`.

## User Setup Required

None for this plan. A Bloomberg terminal is still required to generate `data/raw/universe_raw.csv`.

## Next Phase Readiness

Ready for plan 01-04 and the Phase 1 Bloomberg terminal run. `src/00_build_universe.py` can be run at a Bloomberg terminal after installing `blpapi`.

## Known Stubs

None.

## Self-Check: PASSED

- Summary file exists: `.planning/phases/01-foundation/01-03-SUMMARY.md`.
- Key implementation file exists: `src/00_build_universe.py`.
- Task commit exists: `2cd0a3d`.

---
*Phase: 01-foundation*
*Completed: 2026-05-08*
