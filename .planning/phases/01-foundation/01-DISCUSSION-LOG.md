# Phase 1: Foundation - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-05-08
**Phase:** 1-Foundation
**Areas discussed:** Returns panel date range, Python import path for utils, Old index data in data/raw/

---

## Returns Panel Date Range

| Option | Description | Selected |
|--------|-------------|----------|
| Keep 2025-06-30 | Sufficient for Value-Up events through mid-2024, matches ROADMAP | |
| Extend to 2025-12-31 | Adds 6 months of buffer | |
| Extend to 2026-03-31 | Pulls through Q1 2026 | ✓ |

**User's choice:** Extend end date to 2026-03-31

---

| Option | Description | Selected |
|--------|-------------|----------|
| 2022-01-01 is fine | 120+21 trading days before Feb 2024 event reaches Aug 2023 — well within range | |
| Extend start to 2021-01-01 | Extra year of buffer, defensive | ✓ |

**User's choice:** Extend start date to 2021-01-01

---

| Option | Description | Selected |
|--------|-------------|----------|
| Same range as firm returns | One consistent range for both firm-level and KOSPI index series | ✓ |
| Wider range for benchmark only | Further back for longer market model calibration | |

**User's choice:** KOSPI benchmark uses same range (2021-01-01 to 2026-03-31)

**Notes:** Final range locked: 2021-01-01 → 2026-03-31 for both firm returns and KOSPI Index benchmark.

---

## Python Import Path for Utils

| Option | Description | Selected |
|--------|-------------|----------|
| utils/ at project root | Move to root; `from utils.stats import winsorize` works without PYTHONPATH | ✓ |
| src/utils/ + PYTHONPATH=src | Keep in src/; Makefile exports PYTHONPATH | |
| src/utils/ + sys.path hacks | Each script patches sys.path | |

**User's choice:** utils/ at project root

---

| Option | Description | Selected |
|--------|-------------|----------|
| Proper package with __init__.py | Standard; `from utils.bbg import bdp` works reliably | ✓ |
| No __init__.py (namespace package) | Works in Python 3.3+ but less explicit | |

**User's choice:** Proper package with __init__.py

**Notes:** src/utils/ (currently empty) should be removed; new utils/ created at project root.

---

## Old Index Data in data/raw/

| Option | Description | Selected |
|--------|-------------|----------|
| Delete them | Clean slate; files irrelevant to new project | |
| Move to data/raw/prior-project/ | Archive in place without deleting | ✓ |
| Leave them untouched | Ignore; no pipeline script references them | |

**User's choice:** Move to data/raw/prior-project/

---

| Option | Description | Selected |
|--------|-------------|----------|
| Yes, move panel.parquet to data/prior-project/ | Keep processed/ clean for this paper's outputs | ✓ |
| Leave it in data/processed/ | Won't cause errors, just visual clutter | |

**User's choice:** Move panel.parquet to data/prior-project/ as well

---

| Option | Description | Selected |
|--------|-------------|----------|
| .gitignore data/raw/prior-project/ | Data files don't belong in git; create folder locally only | ✓ |
| Commit directory with README | Commit a placeholder README.md inside the folder | |

**User's choice:** Add data/raw/prior-project/ to .gitignore

**Notes:** MANIFEST.md and MISSING.txt from the prior project also move to prior-project/.

---

## Claude's Discretion

- **Makefile acquire guard** (not discussed): implement a check for existing snapshot_2023.csv that skips and prints a message if found
- **Virtual environment approach** (not discussed): standard `python -m venv venv`; document in README
- **requirements.txt pinning** (not discussed): pin with `>=` lower bounds to accommodate Bloomberg terminal's environment

## Deferred Ideas

None — discussion stayed within Phase 1 scope.
