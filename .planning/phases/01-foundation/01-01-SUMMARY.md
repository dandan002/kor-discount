---
phase: 01-foundation
plan: 01
subsystem: infra
tags: [python, project-scaffold, gitignore, environment, documentation]

requires: []
provides:
  - Root utils Python package marker
  - Paper directory scaffold
  - Python dependency manifest with lower-bound pins
  - Bloomberg/FSS environment template
  - Contributor setup and project-root execution documentation
  - Local ignored storage for prior-project raw and processed data
affects: [phase-01-foundation, phase-02-data-pipeline, phase-03-analysis, phase-04-paper-validation]

tech-stack:
  added: [pandas, numpy, scipy, statsmodels, python-dotenv, matplotlib, seaborn, stargazer]
  patterns:
    - Run scripts from project root so root utils package is importable
    - Keep prior-project data in ignored local directories outside active raw/processed paths

key-files:
  created:
    - utils/__init__.py
    - paper/.gitkeep
    - paper/sections/.gitkeep
    - paper/style/.gitkeep
    - requirements.txt
    - .env.example
    - README.md
  modified:
    - .gitignore
    - data/raw/
    - data/processed/

key-decisions:
  - "Use root-level utils/ as the importable Python package per D-03/D-04."
  - "Use lower-bound dependency pins to remain compatible with Bloomberg terminal environments."
  - "Keep prior-project data locally under ignored directories and remove it from tracked active paths."

patterns-established:
  - "Project-root execution: invoke scripts as python src/<script>.py from repository root."
  - "Secrets pattern: commit .env.example only; real .env remains ignored."

requirements-completed: [INFR-01, INFR-02, INFR-04, INFR-05]

duration: 2 min
completed: 2026-05-08
---

# Phase 01 Plan 01: Cleanup + Infrastructure Scaffold Summary

**Root Python package, ignored legacy data storage, dependency manifest, env template, and contributor setup docs for the Korea Discount pipeline**

## Performance

- **Duration:** 2 min
- **Started:** 2026-05-08T17:28:40Z
- **Completed:** 2026-05-08T17:31:29Z
- **Tasks:** 2
- **Files modified:** 302 tracked files plus local ignored prior-project data copies

## Accomplishments

- Moved 293 prior-project files into ignored local storage under `data/raw/prior-project/` and `data/prior-project/`.
- Created the root-level `utils/` package marker required by downstream imports.
- Added the paper directory scaffold, dependency manifest, environment template, and README setup flow.
- Preserved the existing `.env` ignore entry and added protections for prior-project data.

## Task Commits

Each task was committed atomically:

1. **Task 1: Update .gitignore and move prior-project data** - `af4a162` (chore)
2. **Task 2: Create directory scaffold and setup files** - `8862ba2` (chore)

## Files Created/Modified

- `.gitignore` - Keeps `.env`, prior-project raw data, and prior-project processed data out of git.
- `utils/__init__.py` - Marks the root `utils/` directory as a Python package and documents import/run conventions.
- `paper/.gitkeep`, `paper/sections/.gitkeep`, `paper/style/.gitkeep` - Preserve the paper scaffold in git.
- `requirements.txt` - Lists 8 Python dependencies with lower-bound version pins.
- `.env.example` - Documents Bloomberg host/port and FSS API key variable names without secrets.
- `README.md` - Documents venv setup, project-root execution, Bloomberg terminal run, make targets, and layout.
- `data/raw/` and `data/processed/` - Removed tracked prior-project data from active paths; local copies remain in ignored directories.

## Decisions Made

- Followed the locked D-03/D-04 decision to create `utils/` at the repository root, not under `src/`.
- Used lower-bound dependency pins rather than exact pins, matching the plan's Bloomberg-terminal compatibility requirement.
- Kept `.env.example` secret-free; `FSS_API_KEY` is intentionally blank as a template value.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Removed previously tracked legacy data from active paths**
- **Found during:** Task 1 (Update .gitignore and move prior-project data)
- **Issue:** The prior-project raw files and `data/processed/panel.parquet` were already tracked, so ignoring their new destinations alone would still leave tracked active-path deletions unresolved.
- **Fix:** Committed the tracked deletions from `data/raw/` and `data/processed/` while keeping the moved local copies in ignored prior-project directories.
- **Files modified:** `.gitignore`, `data/raw/`, `data/processed/`
- **Verification:** `git status --short | grep -c prior-project | grep -x 0`; local ignored prior-project directories contain the moved files.
- **Committed in:** `af4a162`

---

**Total deviations:** 1 auto-fixed (1 blocking)
**Impact on plan:** Required to achieve the intended repository state. No scope expansion.

## Issues Encountered

- One verification command was rerun with proper shell quoting because `>` in `pandas>=2.2.1` must be quoted in zsh. No files were changed by the failed attempt.

## User Setup Required

None - no external service configuration required for this plan.

## Next Phase Readiness

Ready for `01-02-PLAN.md`: the root `utils/` package exists, dependency metadata is present, and prior-project data no longer clutters active raw/processed paths.

## Known Stubs

None. `.env.example` intentionally contains a blank `FSS_API_KEY` template value and does not flow to UI rendering.

## Self-Check: PASSED

- Summary file exists.
- Key created files exist: `utils/__init__.py`, `requirements.txt`, `.env.example`.
- Task commits exist: `af4a162`, `8862ba2`.

---
*Phase: 01-foundation*
*Completed: 2026-05-08*
