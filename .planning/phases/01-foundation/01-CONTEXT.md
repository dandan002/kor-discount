# Phase 1: Foundation - Context

**Gathered:** 2026-05-08
**Status:** Ready for planning

<domain>
## Phase Boundary

Phase 1 delivers the complete project skeleton: directory layout, Python virtual environment setup, Makefile targets, utility modules (bbg.py, stats.py, latex_tables.py), and both Bloomberg acquisition scripts (00_build_universe.py, 01_bloomberg_pull.py) — ready to run at a Bloomberg terminal. No analysis runs in Phase 1. All Phase 1 outputs are either infrastructure files or Bloomberg-ready scripts that produce raw CSVs when executed at the terminal.

</domain>

<decisions>
## Implementation Decisions

### Returns Panel Date Range
- **D-01:** Returns panel date range: **2021-01-01 to 2026-03-31** (extended from ROADMAP's 2025-06-30). Rationale: user wants full coverage through Q1 2026; extended start provides buffer for estimation windows of any early-2024 events.
- **D-02:** KOSPI Index benchmark series uses the **same date range** (2021-01-01 to 2026-03-31) — aligned with firm-level returns for event study alignment.

### Python Import Path and utils Layout
- **D-03:** `utils/` lives at the **project root** (not inside `src/`). The existing empty `src/utils/` directory should be removed; a new `utils/` directory is created at root level.
- **D-04:** `utils/` is a **proper Python package** with `__init__.py`. Scripts import as `from utils.bbg import bdp`, `from utils.stats import winsorize`, `from utils.latex_tables import df_to_latex` — all working when run from the project root with no PYTHONPATH manipulation needed.
- **D-05:** All `src/` scripts are run from the project root: `python src/00_build_universe.py`. No `sys.path` hacks inside scripts.

### Old Index Data (Prior Project)
- **D-06:** The 200+ index-level CSVs in `data/raw/` (Bovespa, S&P 500, KOSPI, MSCI, etc.) are from a prior project. Phase 1 moves them to **`data/raw/prior-project/`** locally. The `panel.parquet` in `data/processed/` is also moved to `data/prior-project/`.
- **D-07:** `data/raw/prior-project/` and `data/prior-project/` are **added to .gitignore** — not committed. The existing MANIFEST.md and MISSING.txt (from prior project) are moved into prior-project/ as well.

### Claude's Discretion
- Makefile acquire guard behavior (whether `make acquire` skips if CSVs already exist) — user chose not to discuss; implement a simple guard that checks for `data/raw/bloomberg/snapshot_2023.csv` and skips with a message if it exists.
- Virtual environment approach — standard `python -m venv venv` unless Bloomberg terminal constraints suggest otherwise; document in README.
- requirements.txt pinning strategy — pin major versions with `>=` lower bounds rather than exact pins to accommodate Bloomberg terminal's environment.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase Specifications
- `ROADMAP.md` §"Phase 1: Foundation" — Goal, success criteria, and the Bloomberg terminal checkpoint procedure
- `ROADMAP.md` §"Phase 2: Bloomberg Data Pull" — Bloomberg field list for snapshot (12 fields), ROE panel, and returns panel; this section contains the exact BDP/BDH field mnemonics and overrides the scripts must use
- `ROADMAP.md` §"Phase 1 — Build the Firm Universe" — BDS universe pull spec, BDP identifying fields, filtering rules (drop financials, drop post-2023 IPOs)
- `.planning/REQUIREMENTS.md` §"Infrastructure", §"Utilities", §"Data Acquisition" — INFR-01 through DATA-05; acceptance criteria for all Phase 1 deliverables

### Data Layout
- `data/raw/MANIFEST.md` — Bloomberg field code reference from prior project; useful for cross-checking field mnemonics
- `data/raw/MISSING.txt` — documents Bloomberg field availability issues encountered in prior project (ROE fields not available at index level; firm-level `RETURN_COM_EQY` should work)

### Configuration
- `.env` — Bloomberg connection config (FSS_API_KEY present; host/port pattern goes here)

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `data/raw/MANIFEST.md` — contains Bloomberg ticker and field code patterns already validated at the terminal; reuse field mnemonics (PX_TO_BOOK_RATIO, RETURN_COM_EQY, EQY_DVD_YLD_12M, etc.) directly in bbg.py wrapper
- `data/raw/MISSING.txt` — documents failed field lookups; `RETURN_ON_EQY` / `T12M_RETURN_ON_EQY` not available at index level (irrelevant for firm-level pull but good to know)

### Established Patterns
- Existing `data/raw/bloomberg/`, `data/raw/dart/`, `data/raw/kftc/`, `data/raw/krx/` directories already created — scaffold is partially in place
- `outputs/figures/`, `outputs/tables/`, `outputs/logs/` already exist — no need to create
- `.env` already present with FSS_API_KEY — extend with Bloomberg host/port per INFR-04

### Integration Points
- All Phase 2+ scripts import from `utils/` — the import path decision (D-03/D-04) locks the contract
- `data/raw/bloomberg/` is the handoff point between Phase 1 (Bloomberg terminal run) and Phase 2 (offline processing)

</code_context>

<specifics>
## Specific Ideas

- Returns panel: **2021-01-01 to 2026-03-31** — extended from ROADMAP spec; both firm tickers and KOSPI Index benchmark use this same range
- utils/ placement: **project root** (not src/utils/) — existing src/utils/ should be cleaned up
- Old data: **move to data/raw/prior-project/**, gitignored — not deleted, not left in place

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 1-Foundation*
*Context gathered: 2026-05-08*
