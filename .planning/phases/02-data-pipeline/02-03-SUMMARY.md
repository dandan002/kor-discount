---
phase: 02-data-pipeline
plan: 03
subsystem: data-pipeline
tags: [pandas, merge, winsorize, pivot, kftc, chaebol, dart, bloomberg]

# Dependency graph
requires:
  - phase: 01-foundation
    provides: "utils/stats.py (winsorize function), established script patterns"
  - phase: 02-data-pipeline
    provides: "src/02_build_compliance.py (produces compliance.csv), data/raw/bloomberg/*.csv, data/raw/universe_raw.csv"
provides:
  - "src/03_merge_covariates.py — master dataset merge script"
  - "data/processed/sample.csv — 25-column master dataset (generated at runtime)"
affects: [03-analysis, 03-logit, 03-event-study, 03-fundamentals]

# Tech tracking
tech-stack:
  added: []
  patterns: ["five-way left-join on bare 6-digit ticker", "KFTC Latin-prefix alias table for chaebol matching", "ROE panel pivot-wide with year-column guarantee", "per-column winsorize loop using utils.stats.winsorize", "stdout missingness report with NaN counts and percentages", "optional DART file graceful degradation (NaN columns when absent)"]

key-files:
  created:
    - src/03_merge_covariates.py
  modified: []

key-decisions:
  - "Use universe_raw.csv for name and sector columns (compliance.csv only has ticker, compliance_code, disclosure_date)"
  - "KFTC alias table sorts by length descending so KT&G matches before KT"
  - "DART file absence handled via os.path.exists check with warning and NaN fallback columns"
  - "Missingness report uses print() to stdout (not logging) per plan specification"
  - "Left-join semantics ensure compliance.csv firms are never dropped (D-16)"

patterns-established:
  - "Five-way merge pattern: compliance as left base, then sequentially merge universe, Bloomberg snapshot, ROE wide, DART"
  - "KFTC chaebol matching: LATIN_TO_KFTC alias table + Korean prefix matching with suffix stripping"
  - "ROE pivot guarantee: build_roe_wide() ensures all 5 year columns (roe_2019 through roe_2023) exist, filling NaN for sparse data"

requirements-completed: [MSTR-01, MSTR-02, MSTR-03]

# Metrics
duration: 2min
completed: 2026-05-09
---

# Phase 2 Plan 3: Merge Covariates Summary

**Five-way left-join merge pipeline producing 25-column winsorized master dataset with KFTC chaebol alias matching and ROE pivot-wide**

## Performance

- **Duration:** 2 min
- **Started:** 2026-05-09T00:12:19Z
- ** **Completed:** 2026-05-09T00:14:46Z
- **Tasks:** 2
- **Files modified:** 1

## Accomplishments
- Built src/03_merge_covariates.py (284 lines) with full five-way merge pipeline
- Compliance.csv as left base ensures no firms are dropped (D-16)
- Bloomberg mnemonics renamed via BBG_RENAME dict (all 12 mappings per D-13)
- ROE panel pivoted wide with build_roe_wide() guaranteeing all 5 year columns
- KFTC chaebol flag with LATIN_TO_KFTC alias table matching SK, LG, HD, GS, etc.
- DART absence handled gracefully with NaN columns and log warning
- Winsorization of 19 continuous columns at 1st/99th percentiles
- Missingness report printed to stdout with NaN counts and percentages
- Smoke test passed: 3 rows × 25 columns with correct D-12 schema

## Task Commits

Each task was committed atomically:

1. **Task 1: Write src/03_merge_covariates.py** - `e966166` (feat)
2. **Task 2: End-to-end pipeline smoke test** - No commit (no bugs found, no changes needed)

## Files Created/Modified
- `src/03_merge_covariates.py` - Master dataset merge script (284 lines): five-way left-join, ROE pivot-wide, KFTC chaebol matching, winsorization, missingness report

## Decisions Made
- Used universe_raw.csv for name and sector columns since compliance.csv only has ticker, compliance_code, disclosure_date
- KFTC alias table sorted by key length descending so KT&G (longer) matches before KT (shorter)
- DART file absence handled via os.path.exists check with NaN fill rather than sys.exit — graceful degradation
- Missingness report uses print() to stdout per plan spec, not logging module
- Left compliance_coded.csv in place (pre-existing from Plan 02-02, not our test fixture)

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 - Missing Critical] Preserved pre-existing compliance_coded.csv**
- **Found during:** Task 2 (Smoke test)
- **Issue:** Plan Step 6 says to `rm data/raw/krx/compliance_coded.csv` after the test, but this file was pre-existing data from Plan 02-02, not a test fixture we created
- **Fix:** Left the file in place — deleting researcher data would break downstream scripts
- **Files modified:** None
- **Verification:** Pipeline still runs correctly with the existing file
- **Committed in:** N/A (no change needed)

---

**Total deviations:** 1 auto-fixed (1 missing critical — preserved pre-existing data file)
**Impact on plan:** Minimal — pipeline test verified correctly without deleting source data.

## Issues Encountered

None — smoke test passed on first run with no bugs found in 03_merge_covariates.py.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- src/03_merge_covariates.py is complete and verified with 3-ticker smoke test
- data/processed/sample.csv produced with correct 25-column schema (D-12)
- Pipeline handles partial data gracefully (ROE panel with only 16 tickers, empty sector column)
- Next: Phase 3 (analysis) can now consume data/processed/sample.csv for all regression scripts
- Note: When researcher runs full pipeline at Bloomberg terminal, sample.csv will have full 948-ticker data

## Self-Check: PASSED

- ✅ src/03_merge_covariates.py exists (284 lines)
- ✅ Commit e966166 found in git log

---
*Phase: 02-data-pipeline*
*Completed: 2026-05-09*