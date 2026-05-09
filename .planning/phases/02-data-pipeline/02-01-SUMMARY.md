---
phase: 02-data-pipeline
plan: 01
subsystem: data-pipeline
tags: [dart, fss-api, requests, python, pandas, xml, zipfile, dotenv]

# Dependency graph
requires:
  - phase: 01-foundation
    provides: src/00_build_universe.py (universe_raw.csv), src/01_bloomberg_pull.py (structural template)
provides:
  - src/01c_dart_pull.py (DART controlling shareholder acquisition script)
  - data/raw/dart/corp_code_map.csv (generated at runtime — ticker↔corp_code cache)
  - data/raw/dart/controlling_shareholder.csv (generated at runtime)
affects: [02-data-pipeline, 03-analysis]

# Tech tracking
tech-stack:
  added: [requests, python-dotenv, xml.etree.ElementTree, zipfile]
  patterns: [cache-first API lookup, per-firm rate-limited loop, reprt_code fallback]

key-files:
  created:
    - src/01c_dart_pull.py
  modified: []

key-decisions:
  - "Use hyslrSttus.json (not majorstock.json) for controlling shareholder data — provides per-shareholder rows with relate field"
  - "Cache corp_code_map.csv locally to avoid re-downloading the 5MB ZIP on every run"
  - "Fallback from reprt_code 11011 (annual) to 11014 (semi-annual) when annual report returns no data"
  - "Filter to 보통주 (common shares) only for percentage calculation, fall back to all shares if no common shares found"
  - "Skip firms with no DART match and print list to stdout rather than crash"

patterns-established:
  - "Per-firm API loop with 0.5s sleep for rate limiting (DART-specific pattern)"
  - "Cache-first pattern: check local CSV before downloading from external API"
  - "report_code fallback: try annual first, then semi-annual"

requirements-completed: [MSTR-01]

# Metrics
duration: 1min
completed: 2026-05-09
---

# Phase 2 Plan 1: DART Controlling Shareholder Pull Summary

**DART FSS OpenAPI acquisition script pulling controlling shareholder percentages via hyslrSttus.json with corp_code caching and reprt_code fallback**

## Performance

- **Duration:** 1 min (58 sec)
- **Started:** 2026-05-09T00:06:31Z
- **Completed:** 2026-05-09T00:07:28Z
- **Tasks:** 1
- **Files modified:** 1

## Accomplishments
- Built complete DART FSS OpenAPI acquisition script (src/01c_dart_pull.py) following established codebase patterns
- Implemented corp_code lookup with local CSV caching to avoid re-downloading 5MB ZIP on subsequent runs
- Added reprt_code fallback (11011 annual → 11014 semi-annual) for firms without annual report data
- Rate-limited per-firm API calls with 0.5s sleep to respect DART API limits
- Secured FSS_API_KEY handling: loaded from .env, never logged or printed

## Task Commits

Each task was committed atomically:

1. **Task 1: Write src/01c_dart_pull.py** - `f9f883a` (feat)

## Files Created/Modified
- `src/01c_dart_pull.py` — DART FSS OpenAPI controlling shareholder acquisition script (222 lines)

## Decisions Made
- Used hyslrSttus.json (not majorstock.json) for controlling shareholder data — provides per-shareholder rows with relate field enabling individual vs. group split
- Cached corp_code_map.csv locally to avoid re-downloading on subsequent runs
- Added reprt_code fallback from 11011 to 11014 for firms without annual report data
- Filtered to 보통주 (common shares) only for percentage calculation; fallback to all shares if no common shares exist

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
None

## User Setup Required
None - no external service configuration required. The FSS_API_KEY is already in .env.

## Next Phase Readiness
- src/01c_dart_pull.py is complete and ready for live execution (requires internet + FSS_API_KEY)
- Output data/raw/dart/controlling_shareholder.csv will be read by src/03_merge_covariates.py (Plan 02-03)
- corp_code_map.csv cache will be reused on subsequent runs

---
*Phase: 02-data-pipeline*
*Completed: 2026-05-09*