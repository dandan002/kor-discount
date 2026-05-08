# Phase 2: Data Pipeline - Context

**Gathered:** 2026-05-08
**Status:** Ready for planning

<domain>
## Phase Boundary

Phase 2 delivers three things: (1) `src/01c_dart_pull.py` — a new acquisition script that pulls controlling shareholder % from the DART FSS OpenAPI and saves to `data/raw/dart/controlling_shareholder.csv`; (2) `src/02_build_compliance.py` — reads the manually-coded `data/raw/krx/compliance_coded.csv` and produces `data/processed/compliance.csv` and `data/processed/events.csv`; (3) `src/03_merge_covariates.py` — joins Bloomberg snapshot + compliance + KFTC chaebol + DART controlling shareholder + ROE panel into `data/processed/sample.csv`.

No analysis runs in Phase 2. The output is a single, clean, winsorized master file that all Phase 3 scripts read.

</domain>

<decisions>
## Implementation Decisions

### compliance_coded.csv Format
- **D-01:** File lives at `data/raw/krx/compliance_coded.csv`.
- **D-02:** Required columns: `ticker` (bare 6-digit, e.g. `005930`), `compliance_code` (integer 0/1/2), `disclosure_date` (YYYY-MM-DD string). No other columns required.
- **D-03:** Code 0 firms leave `disclosure_date` blank/NaN — this is correct and expected. `events.csv` includes only codes 1 and 2.
- **D-04:** Inter-rater kappa: if `data/raw/krx/compliance_coded_r2.csv` exists alongside the primary file, `02_build_compliance.py` computes Cohen's kappa (via `utils.stats.cohens_kappa`) and prints to stdout. If absent, skip silently. Does not block execution.

### DART Controlling Shareholder Pull (src/01c_dart_pull.py)
- **D-05:** Separate acquisition script following the same pattern as `src/00_build_universe.py` and `src/01_bloomberg_pull.py`. Reads `data/raw/universe_raw.csv` for the ticker list. Saves to `data/raw/dart/controlling_shareholder.csv`.
- **D-06:** Uses `FSS_API_KEY` from `.env` (key `1981bd18dcd016b26e083fc27bd8c3b562c362ff` already set).
- **D-07:** Pull two fields per firm: `controlling_pct_largest` (최대주주 단독 보유 %, largest single holder) and `controlling_pct_group` (최대주주 및 특수관계인 합계 %, controlling family group total). Both columns land in the output CSV.
- **D-08:** Script skips firms with no DART match and prints a list to stdout. Uses the DART `majorstock` or equivalent endpoint; requires corp_code lookup from ticker first (DART corp_code ≠ KRX ticker).

### KFTC Chaebol Flag
- **D-09:** Source file: `data/raw/kftc/KFTC_large_business_groups_2026.csv` (102 groups, `Group_Name_Korean` column).
- **D-10:** Matching strategy: name-prefix match. Strip common Korean corporate suffixes (주식회사, 그룹, 홀딩스, etc.) from firm names in `universe_raw.csv`, then check if the cleaned name starts with a `Group_Name_Korean` value. Assign `chaebol = 1` if matched, `0` otherwise.
- **D-11:** Print all unmatched KFTC group names and any ambiguous matches to stdout after the merge — for manual review.

### sample.csv Column Set (locked schema)
- **D-12:** Exact column order: `ticker`, `name`, `sector`, `pbr`, `pe_ratio`, `roe_fy23`, `roa`, `foreign_pct`, `mkt_cap`, `dvd_yield`, `debt_equity`, `total_assets`, `sales_growth`, `cash`, `dvd_sh_12m`, `roe_2019`, `roe_2020`, `roe_2021`, `roe_2022`, `roe_2023`, `chaebol`, `controlling_pct_largest`, `controlling_pct_group`, `compliance_code`, `disclosure_date`.
- **D-13:** Bloomberg raw mnemonics are renamed to human-readable names: `PX_TO_BOOK_RATIO` → `pbr`, `PE_RATIO` → `pe_ratio`, `RETURN_COM_EQY` → `roe_fy23`, `RETURN_ON_ASSET` → `roa`, `EQY_FLOAT_PCT` → `foreign_pct`, `CUR_MKT_CAP` → `mkt_cap`, `EQY_DVD_YLD_IND` → `dvd_yield`, `TOT_DEBT_TO_TOT_EQY` → `debt_equity`, `BS_TOT_ASSET` → `total_assets`, `SALES_GROWTH` → `sales_growth`, `CASH_AND_NEAR_CASH_ITEM` → `cash`, `DVD_SH_12M` → `dvd_sh_12m`.
- **D-14:** ROE panel is pivoted wide: one `roe_YYYY` column per year (2019–2023), one row per firm.
- **D-15:** `compliance_code` and `disclosure_date` are the last two columns, in that order, matching the "ticker through disclosure_date" ROADMAP spec.

### Missing Data Handling
- **D-16:** `03_merge_covariates.py` does a left-join on `ticker` from `compliance_coded.csv` as the base. Firms in compliance not found in Bloomberg snapshot keep their row with NaN financials.
- **D-17:** After the merge, script prints a missingness report to stdout: count and list of NaN values per column. Downstream scripts (Phase 3) are responsible for dropping NaN rows per-regression.
- **D-18:** Winsorize all continuous Bloomberg financial columns and ROE panel columns at 1st/99th percentiles using `utils.stats.winsorize`. Excluded: `ticker`, `name`, `sector`, `chaebol`, `compliance_code`, `disclosure_date`.

### Ticker Format Standardization
- **D-19:** `returns_panel.csv` uses Yahoo Finance format (`000150.KS`); strip the `.KS` suffix before any join. All joins within Phase 2 use bare 6-digit tickers (e.g. `005930`).

### Claude's Discretion
- DART corp_code lookup implementation (whether to use DART company search API or a pre-cached mapping file) — implement whichever is more reliable at runtime.
- Rate limiting and retry logic for DART API calls — add reasonable delays between requests to avoid 429s.
- Exact Korean suffix list for KFTC name-prefix matching — use a standard list covering 주식회사, (주), 그룹, 홀딩스, 지주, 코리아.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase Specifications
- `.planning/ROADMAP.md` §"Phase 2: Data Pipeline" — Goal, success criteria, and the exact output files required
- `.planning/REQUIREMENTS.md` §"Compliance Dataset" (COMP-01–COMP-03) — acceptance criteria for `02_build_compliance.py`
- `.planning/REQUIREMENTS.md` §"Master Dataset" (MSTR-01–MSTR-03) — acceptance criteria for `03_merge_covariates.py`

### Data Sources
- `data/raw/kftc/KFTC_large_business_groups_2026.csv` — chaebol group list; columns `Group_Name_Korean`, `Group_Name_English`, `Cross_Shareholding_Restricted`
- `data/raw/bloomberg/snapshot_2023.csv` — 12-field Bloomberg cross-section; see D-13 for column rename mapping
- `data/raw/bloomberg/roe_panel.csv` — annual ROE panel 2019–2023; columns `ticker`, `year`, `roe`
- `data/raw/bloomberg/returns_panel.csv` — weekly prices; `security` column uses `.KS` suffix format (see D-19)
- `data/raw/universe_raw.csv` — KOSPI firm list; columns `ticker`, `name`, `sector`, `industry`, `country`, `ipo_date`
- `.env` — contains `FSS_API_KEY` for DART API authentication

### Utilities
- `utils/stats.py` — `winsorize(arr, lower=0.01, upper=0.01)` for 1st/99th clipping; `cohens_kappa(rater1, rater2, labels)` for inter-rater check
- `.planning/phases/01-foundation/01-CONTEXT.md` — Phase 1 decisions; especially D-03/D-04 (utils/ import path) and D-05 (run scripts from project root)

### Prior Phase Context
- `.planning/phases/01-foundation/01-CONTEXT.md` §"Python Import Path and utils Layout" — all scripts import from root-level `utils/`

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `utils/stats.winsorize()` — ready to call; accepts pd.Series, propagates NaN, returns np.ndarray
- `utils/stats.cohens_kappa()` — ready to call; wraps statsmodels inter-rater with p-value
- `src/01_bloomberg_pull.py` — use as structural template for `src/01c_dart_pull.py` (same read→pull→save pattern, same graceful error handling)

### Established Patterns
- All scripts run from project root: `python src/XX_script.py`
- All scripts import utilities as `from utils.X import Y` (D-03/D-04 from Phase 1)
- Bloomberg CSVs use bare 6-digit tickers; returns panel uses `.KS` suffix — strip before joining
- `data/raw/bloomberg/` is a sentinel directory: scripts skip if outputs already exist (acquire guard pattern from Phase 1 Makefile)

### Integration Points
- `data/raw/krx/compliance_coded.csv` — hand-coded by user before Phase 2 executes; Phase 2 cannot proceed without it
- `data/raw/dart/controlling_shareholder.csv` — produced by `src/01c_dart_pull.py`; read by `src/03_merge_covariates.py`
- `data/processed/sample.csv` — produced by `src/03_merge_covariates.py`; the single input for all Phase 3 analysis scripts

</code_context>

<specifics>
## Specific Ideas

- DART pull: pull both `controlling_pct_largest` and `controlling_pct_group` — researcher decides which to use in the logit
- KFTC matching: use name-prefix matching with stdout report of unmatched/ambiguous firms for manual review
- ROE panel in sample.csv: wide format with `roe_2019` … `roe_2023` columns (one row per firm, not long format)
- Kappa check: triggered only when `compliance_coded_r2.csv` exists alongside the primary file — no blocking

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 2-Data Pipeline*
*Context gathered: 2026-05-08*
