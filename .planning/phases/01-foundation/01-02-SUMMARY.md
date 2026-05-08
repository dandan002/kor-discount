---
phase: 01-foundation
plan: 02
subsystem: utilities
tags: [python, blpapi, pandas, scipy, statsmodels, latex, booktabs]

requires:
  - phase: 01-foundation-01
    provides: Root utils Python package marker and dependency manifest
provides:
  - Bloomberg BDP, BDH, and BDS wrappers with safe import behavior when blpapi is unavailable
  - Statistical helper functions for winsorization, Cohen's Kappa, and robust standard errors
  - DataFrame-to-LaTeX table exporter using pandas booktabs output
affects: [phase-01-foundation, phase-02-data-pipeline, phase-03-analysis, phase-04-paper-validation]

tech-stack:
  added: []
  patterns:
    - Guard Bloomberg API import at module load and fail only when Bloomberg functions are called
    - Keep acquisition-specific Bloomberg access isolated in utils.bbg
    - Use scipy/statsmodels wrappers for shared statistical behavior
    - Use pandas to_latex booktabs output for analysis table fragments

key-files:
  created:
    - utils/bbg.py
    - utils/stats.py
    - utils/latex_tables.py
  modified: []

key-decisions:
  - "Use root-level utils modules for Bloomberg, stats, and LaTeX helpers per D-03/D-04."
  - "Keep utils.bbg importable without blpapi; Bloomberg availability is checked lazily at call time."
  - "Use pandas DataFrame.to_latex default booktabs output for compatibility with pandas 2.2.1."

patterns-established:
  - "Bloomberg wrappers normalize scalar security/field inputs to lists before request construction."
  - "BDH requests batch securities in chunks of 100 with a 0.5 second pause between batches."
  - "BDS parsing logs bulk sub-element names to stderr when the expected INDX_MEMBERS key is unavailable."
  - "Stats wrappers return plain numpy/pandas objects rather than masked arrays or statsmodels result objects."

requirements-completed: [UTIL-01, UTIL-02, UTIL-03, UTIL-04]

duration: 5 min
completed: 2026-05-08
---

# Phase 01 Plan 02: Utils Package Implementation Summary

**Bloomberg API wrappers, statistical helper functions, and booktabs LaTeX table export for downstream acquisition and analysis scripts**

## Performance

- **Duration:** 5 min
- **Started:** 2026-05-08T17:34:19Z
- **Completed:** 2026-05-08T17:39:38Z
- **Tasks:** 2
- **Files modified:** 3

## Accomplishments

- Created `utils/bbg.py` with BDP, BDH, and BDS wrappers plus a `python utils/bbg.py --test` connection check.
- Implemented safe Bloomberg import behavior so `from utils.bbg import bdp, bdh, bds` works without requiring blpapi at import time.
- Created `utils/stats.py` with `winsorize`, `cohens_kappa`, and `robust_se`.
- Created `utils/latex_tables.py` with `df_to_latex` returning standalone booktabs table fragments with captions, labels, and optional footnotes.

## Task Commits

Each task was committed atomically:

1. **Task 1: Implement utils/bbg.py - Bloomberg wrappers with graceful ImportError** - `547bde2` (feat)
2. **Task 2: Implement utils/stats.py and utils/latex_tables.py** - `5baace3` (feat)

## Files Created/Modified

- `utils/bbg.py` - Bloomberg session setup, BDP/BDH/BDS wrappers, batching, fallback BDS parsing, and CLI connection test.
- `utils/stats.py` - Winsorization wrapper, Cohen's Kappa wrapper, and robust standard error extraction helper.
- `utils/latex_tables.py` - DataFrame-to-LaTeX table exporter using pandas booktabs tabular output.

## Decisions Made

- Followed the locked root `utils/` package decision; no `src/utils/` modules or path hacks were introduced.
- Kept Bloomberg availability checks lazy so offline analysis environments can import the module safely.
- Used pandas 2.2.1-compatible `DataFrame.to_latex` behavior, which already emits `\toprule`, `\midrule`, and `\bottomrule`.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Preserved NaN values during winsorization**
- **Found during:** Task 2 (Implement utils/stats.py and utils/latex_tables.py)
- **Issue:** The planned direct `scipy.stats.mstats.winsorize` wrapper can replace NaN values instead of propagating them, contradicting the documented helper contract.
- **Fix:** Winsorize only non-NaN values and reinsert them into a plain numpy array, preserving NaN positions.
- **Files modified:** `utils/stats.py`
- **Verification:** `winsorize([1, 2, np.nan, 100], lower=0.25, upper=0.25)` preserves the NaN element.
- **Committed in:** `5baace3`

**2. [Rule 1 - Bug] Used the statsmodels two-sided p-value attribute**
- **Found during:** Task 2 (Implement utils/stats.py and utils/latex_tables.py)
- **Issue:** The planned code referenced `KappaResults.pvalue`, but statsmodels 0.14.4 exposes `pvalue_two_sided`.
- **Fix:** Return `float(result.pvalue_two_sided)` as the p-value component.
- **Files modified:** `utils/stats.py`
- **Verification:** `cohens_kappa([0,1,2,0,1], [0,1,2,1,0])` returns a `(float, float)` tuple.
- **Committed in:** `5baace3`

**3. [Rule 1 - Bug] Removed unsupported pandas `booktabs` keyword**
- **Found during:** Task 2 (Implement utils/stats.py and utils/latex_tables.py)
- **Issue:** pandas 2.2.1 `DataFrame.to_latex` does not accept `booktabs=True`, causing `TypeError`.
- **Fix:** Removed the unsupported keyword because this pandas version already emits booktabs rules by default.
- **Files modified:** `utils/latex_tables.py`
- **Verification:** `df_to_latex(pd.DataFrame({'a':[1]}), 'T', 'tab:t')` returns a string containing `\begin{table}`, `\toprule`, `\caption{T}`, and `\label{tab:t}`.
- **Committed in:** `5baace3`

---

**Total deviations:** 3 auto-fixed (3 bugs)
**Impact on plan:** All fixes were required for the planned utility contracts to work in the project environment. No scope expansion.

## Issues Encountered

- The local environment has `blpapi` installed but no Bloomberg terminal service listening on `127.0.0.1:8194`, so the normal `python utils/bbg.py --test` path exits non-zero with a Bloomberg connection error. The no-blpapi branch was verified by shadowing `blpapi` with a temporary module that raises `ImportError`; it prints the expected install guidance and exits non-zero without a traceback.

## User Setup Required

None - no external service configuration required for this plan. A Bloomberg terminal is still required later to run the actual acquisition scripts and confirm live connectivity.

## Next Phase Readiness

Ready for `01-03-PLAN.md`: downstream scripts can import `utils.bbg`, `utils.stats`, and `utils.latex_tables` from the project root.

## Known Stubs

None.

## Self-Check: PASSED

- Summary file exists: `.planning/phases/01-foundation/01-02-SUMMARY.md`.
- Key utility files exist: `utils/bbg.py`, `utils/stats.py`, `utils/latex_tables.py`.
- Task commits exist: `547bde2`, `5baace3`.

---
*Phase: 01-foundation*
*Completed: 2026-05-08*
