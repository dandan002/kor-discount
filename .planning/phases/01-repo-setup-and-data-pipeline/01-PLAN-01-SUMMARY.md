---
phase: 01-repo-setup-and-data-pipeline
plan: 01
subsystem: data-pipeline
tags: [python, config, dependencies, pandas, pyarrow, linearmodels]

# Dependency graph
requires: []
provides:
  - Event dates firewall in config.py
  - Pinned Python dependency manifest in requirements.txt
affects: [phase-01-data-pipeline, phase-02-descriptive-analysis, phase-03-primary-empirics]

# Tech tracking
tech-stack:
  added:
    - pandas==2.2.3
    - numpy==1.26.4
    - pyarrow==15.0.2
    - scipy==1.13.1
    - statsmodels==0.14.4
    - linearmodels==6.1
    - wildboottest==0.3.2
    - matplotlib==3.9.2
    - seaborn==0.13.2
    - tqdm==4.66.5
  patterns:
    - Centralized event date constants imported from config.py
    - Exact version pins for analysis-affecting dependencies

key-files:
  created:
    - config.py
    - requirements.txt
  modified: []

key-decisions:
  - "Japan reform event dates are locked as module-level datetime.date constants in config.py."
  - "Bloomberg blpapi is excluded from requirements.txt because it is a terminal SDK dependency, not a reproducible public pip dependency."
  - "wildboottest is pinned to the latest PyPI-resolvable version, 0.3.2, because planned version 0.9.1 is not published for this environment."

patterns-established:
  - "Analysis scripts must import event dates from config.py rather than redefining dates locally."
  - "Dependency versions that can affect numerical output use exact == pins."

requirements-completed: [DATA-01, DATA-03, DATA-05]

# Metrics
duration: 3min
completed: 2026-04-16
---

# Phase 01 Plan 01: Repo Scaffold Summary

**Event-date firewall and pinned Python dependency manifest for the Korea Discount empirical pipeline**

## Performance

- **Duration:** 3 min
- **Started:** 2026-04-16T17:58:45Z
- **Completed:** 2026-04-16T18:01:43Z
- **Tasks:** 2
- **Files modified:** 3

## Accomplishments

- Created `config.py` with locked Japan reform event dates as `datetime.date` constants for 2014-02-01, 2015-06-01, and 2023-03-01.
- Added canonical project path constants and documented the known KOSPI P/E series start limitation.
- Created `requirements.txt` with exact pins for data, statistics, econometrics, bootstrap inference, visualization, and utility packages.

## Task Commits

Each task was committed atomically:

1. **Task 1: Create config.py with event dates firewall** - `f283e43` (feat)
2. **Task 2: Create requirements.txt with pinned dependencies** - `3cdfb5d` (chore)

## Files Created/Modified

- `config.py` - Central event-date firewall, study universe constants, project data/output paths, and KOSPI P/E start limitation.
- `requirements.txt` - Pinned Python dependency manifest for the empirical pipeline.
- `.planning/phases/01-repo-setup-and-data-pipeline/01-PLAN-01-SUMMARY.md` - Execution summary and verification record.

## Decisions Made

- Followed the plan's event dates exactly and kept `config.py` free of file reads, functions, classes, or data-loading logic.
- Kept `blpapi` out of `requirements.txt`; Bloomberg Terminal SDK setup remains external to the reproducible public environment.
- Deferred `pysyncon` and `mlsynth` as planned for the Phase 4 synthetic-control library decision.
- Changed the planned `wildboottest` pin from `0.9.1` to `0.3.2` because PyPI resolution showed `0.9.1` is unavailable while `0.3.2` resolves with the rest of the manifest.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Replaced unavailable wildboottest pin**
- **Found during:** Task 2 (Create requirements.txt with pinned dependencies)
- **Issue:** `python -m pip install --dry-run -r requirements.txt` reached PyPI and failed because `wildboottest==0.9.1` is not available; PyPI listed only `0.2.0`, `0.3.0`, `0.3.1`, and `0.3.2`.
- **Fix:** Pinned `wildboottest==0.3.2`, the latest resolvable published version.
- **Files modified:** `requirements.txt`
- **Verification:** `python -m pip install --dry-run -r requirements.txt` exited 0 and included `wildboottest-0.3.2` in the dry-run install set.
- **Committed in:** `3cdfb5d`

---

**Total deviations:** 1 auto-fixed (1 blocking)
**Impact on plan:** The dependency manifest now satisfies the plan's reproducibility requirement by resolving successfully against PyPI; no additional scope was added.

## Issues Encountered

- Initial pip verification inside the restricted sandbox could not resolve PyPI package metadata. The command was rerun with approved network access.
- After network access was available, the planned `wildboottest==0.9.1` pin failed because that release was unavailable. This was resolved as the Rule 3 deviation above.

## User Setup Required

None - no external service configuration required for this plan.

## Known Stubs

None.

## Next Phase Readiness

- Downstream data-pipeline scripts can import `config.py` for event dates and path constants.
- The dependency manifest resolves with pip dry-run and is ready for a fresh environment install.
- `src/data/build_panel.py` should import event dates from `config.py` rather than redefining them.

## Verification

- `python -c "import config; print(config.EVENT_DATES)"` printed `[datetime.date(2014, 2, 1), datetime.date(2015, 6, 1), datetime.date(2023, 3, 1)]`.
- `python -m pip install --dry-run -r requirements.txt` exited 0.
- `grep "blpapi\|pysyncon\|mlsynth" requirements.txt` returned no matches.
- `python -c "import config; print(config.RAW_DIR)"` printed `/Users/dandan/Desktop/Projects/kor-discount/data/raw`.
- `grep -n "def \|class \|open(\|read_csv\|parquet" config.py` returned no matches.

---
*Phase: 01-repo-setup-and-data-pipeline*
*Completed: 2026-04-16*

## Self-Check: PASSED

- Found created files: `config.py`, `requirements.txt`, and `01-PLAN-01-SUMMARY.md`.
- Found task commits: `f283e43` and `3cdfb5d`.
