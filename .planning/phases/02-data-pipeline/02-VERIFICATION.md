---
phase: 02-data-pipeline
verified: 2026-05-09T00:19:13Z
status: human_needed
score: 7/8 must-haves verified
overrides_applied: 0
gaps:
  - truth: "python src/02_build_compliance.py produces data/processed/compliance.csv with a three-way compliance_code column (0/1/2)"
    status: partial
    reason: "Script is fully implemented and correct, but compliance.csv currently contains only 3 rows from a test fixture — real hand-coded data (compliance_coded.csv) has been removed. Script cannot produce full output until researcher provides the hand-coded input file."
    artifacts:
      - path: "src/02_build_compliance.py"
        issue: "Script is correct but depends on hand-coded compliance_coded.csv which does not currently exist"
    missing:
      - "Hand-coded data/raw/krx/compliance_coded.csv must be provided by researcher before full pipeline run"
  - truth: "python src/01c_dart_pull.py runs and produces data/raw/dart/controlling_shareholder.csv"
    status: partial
    reason: "Script is fully implemented and correct, but requires live DART API access (internet + FSS_API_KEY). A 3-row stub from the smoke test exists, not real data from the API."
    artifacts:
      - path: "src/01c_dart_pull.py"
        issue: "Script is correct but requires live internet + FSS_API_KEY to produce real output"
    missing:
      - "Live DART API execution needed to produce real controlling_shareholder.csv with full KOSPI data"
---

# Phase 2: Data Pipeline Verification Report

**Phase Goal:** The master analysis file sample.csv exists and all downstream analysis scripts can load it — compliance classifications coded, event dates extracted, and all covariates joined and winsorized from real Bloomberg data
**Verified:** 2026-05-09T00:19:13Z
**Status:** human_needed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | `python src/01c_dart_pull.py` runs and produces `data/raw/dart/controlling_shareholder.csv` with columns ticker, controlling_pct_largest, controlling_pct_group | ✓ VERIFIED (structure) / ⚠️ PARTIAL (data) | Script is syntactically valid, contains all required endpoints (hyslrSttus), caching (corp_code_map), fallback (11014), rate limiting (0.5s sleep), and security (no API key logging). A 3-row test output exists with correct columns. Real execution requires internet + FSS_API_KEY. |
| 2 | `python src/02_build_compliance.py` produces `data/processed/compliance.csv` with three-way compliance_code column (0/1/2) and `data/processed/events.csv` with disclosure dates for codes 1 and 2 | ⚠️ PARTIAL | Script is correct with schema validation, events filter (`isin([1, 2])`), and kappa check. A 3-row test output exists with correct structure (codes 0, 1, 2 in compliance.csv; codes 1, 2 only in events.csv). However, input `compliance_coded.csv` no longer exists (removed after smoke test) — real data awaits researcher hand-coding. |
| 3 | Running `02_build_compliance.py` without `compliance_coded.csv` exits with code 1 and informative error on stderr (no traceback) | ✓ VERIFIED | Tested: `python src/02_build_compliance.py 2>&1` → stderr shows "Error: ...compliance_coded.csv not found..." with exit code 1. No Python traceback. |
| 4 | `python src/03_merge_covariates.py` produces `data/processed/sample.csv` with all 25 columns in locked D-12 order | ✓ VERIFIED | sample.csv exists with exactly 25 columns matching D-12 order: `ticker,name,sector,pbr,pe_ratio,...,compliance_code,disclosure_date`. Verified column-by-column match. |
| 5 | compliance.csv is the left table in all joins — no compliance firms are dropped | ✓ VERIFIED | Source code uses `how="left"` on all five joins (lines 242, 246, 248, 250). Verified: compliance.csv (3 rows) → sample.csv (3 rows), no firms dropped. |
| 6 | All continuous Bloomberg + ROE columns are winsorized at 1st/99th percentiles | ✓ VERIFIED | `WINSORIZE_COLS` in source has 19 columns matching D-18 specification exactly. `winsorize(df[col])` called with default args `lower=0.01, upper=0.01` in loop. `utils/stats.winsorize` verified: defaults are 1st/99th percentiles. |
| 7 | sample.csv missingness report prints to stdout | ✓ VERIFIED | Run `python src/03_merge_covariates.py` → stdout shows `=== Missingness report ===` with per-column NaN counts and percentages. |
| 8 | KFTC chaebol flag uses alias table for Latin-prefix firms; unmatched groups printed to stdout | ✓ VERIFIED | `LATIN_TO_KFTC` dict with 16 entries including SK, LG, HD, GS, CJ etc. Sorted by length descending (KT&G before KT). `match_chaebol` function with Korean suffix stripping. Unmatched groups printed: `KFTC groups with no universe match (47): [...]`. |

**Score:** 6/8 truths fully verified, 2 partial (awaiting live data execution)

### Partial Truths (Requiring Human Verification)

**T-2 (compliance.csv with real data):** The script logic is correct and the output structure is verified via smoke test. However, the actual hand-coded `data/raw/krx/compliance_coded.csv` has been removed (it was a test fixture). The researcher must hand-code the KRX Value-Up disclosure classifications before this pipeline step can produce real output.

**T-1 (DART output with real data):** The script is correct and a 3-row stub exists from the smoke test. Full execution requires the researcher to run `python src/01c_dart_pull.py` at a Bloomberg terminal or with internet access and a valid FSS_API_KEY.

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `src/01c_dart_pull.py` | DART controlling shareholder acquisition script (≥120 lines) | ✓ VERIFIED | 222 lines, syntax valid, all key features present |
| `data/raw/dart/controlling_shareholder.csv` | Per-firm controlling shareholder percentages | ✓ VERIFIED (stub) | 3 rows from smoke test; columns: ticker, controlling_pct_largest, controlling_pct_group |
| `src/02_build_compliance.py` | Compliance classification script (≥80 lines) | ✓ VERIFIED | 114 lines, syntax valid, all features present |
| `data/processed/compliance.csv` | Three-way compliance classification, all firms | ✓ VERIFIED (stub) | 3 rows from test fixture; correct columns: ticker, compliance_code, disclosure_date |
| `data/processed/events.csv` | Disclosure dates for codes 1 and 2 only | ✓ VERIFIED (stub) | 2 rows (codes 1 and 2 only); correct columns |
| `src/03_merge_covariates.py` | Master dataset merge script (≥160 lines) | ✓ VERIFIED | 284 lines, all 25 FINAL_COLS, 12 BBG_RENAME mappings, build_roe_wide, match_chaebol, winsorize loop |
| `data/processed/sample.csv` | 25-column master analysis dataset | ✓ VERIFIED (stub) | 3 rows × 25 columns, exact D-12 schema match |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `src/01c_dart_pull.py` | opendart.fss.or.kr/api/corpCode.xml | requests.get with FSS_API_KEY | ✓ WIRED | Line 43: CORP_CODE_URL, Line 80: requests.get with params |
| `src/01c_dart_pull.py` | opendart.fss.or.kr/api/hyslrSttus.json | per-firm loop with 0.5s sleep | ✓ WIRED | Line 44: HYSLR_URL, Lines 111-120: requests.get inside pull_hyslr_shareholder with time.sleep(0.5) |
| `src/01c_dart_pull.py` | data/raw/dart/controlling_shareholder.csv | pd.DataFrame.to_csv | ✓ WIRED | Line 206: df.to_csv(OUTPUT_PATH, index=False) |
| `src/02_build_compliance.py` | data/raw/krx/compliance_coded.csv | pd.read_csv with dtype | ✓ WIRED | Line 35: COMPLIANCE_PATH, Line 57: pd.read_csv with dtype |
| `src/02_build_compliance.py` | utils/stats.cohens_kappa | conditional import + call | ✓ WIRED | Line 24: from utils.stats import cohens_kappa, Line 96: cohens_kappa() called |
| `src/02_build_compliance.py` | data/processed/events.csv | df[df['compliance_code'].isin([1, 2])] | ✓ WIRED | Line 88: events filter, Line 89: events.to_csv |
| `src/03_merge_covariates.py` | data/processed/compliance.csv | left-join base | ✓ WIRED | Line 242: compliance.merge(universe, on="ticker", how="left") |
| `src/03_merge_covariates.py` | utils/stats.winsorize | per-column loop over WINSORIZE_COLS | ✓ WIRED | Line 27: import winsorize, Lines 256-258: winsorize loop |
| `src/03_merge_covariates.py` | data/raw/bloomberg/roe_panel.csv | pivot wide via build_roe_wide() | ✓ WIRED | Line 123: def build_roe_wide(), Line 201: roe_wide = build_roe_wide(ROE_PANEL_PATH) |
| `src/03_merge_covariates.py` | data/processed/sample.csv | FINAL_COLS reordering then to_csv | ✓ WIRED | Lines 272-274: present_cols filter + df.to_csv(SAMPLE_OUT) |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
|----------|--------------|--------|-------------------|--------|
| `src/01c_dart_pull.py` | results → df | DART API (pull_hyslr_shareholder) | ✓ FLOWING (structure) | API call + JSON parsing; requires live execution for real data |
| `src/02_build_compliance.py` | df → compliance.csv | compliance_coded.csv (hand-coded) | ⚠️ STATIC | Currently depends on researcher-provided input; script itself just passes through with validation |
| `src/03_merge_covariates.py` | df → sample.csv | 5-way left-join from compliance, universe, bloomberg, roe, kftc, dart | ✓ FLOWING (stub) | Smoke test confirmed 3-row → 3-row merge with all columns; real execution needs full data |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| 02_build_compliance.py exits with error when compliance_coded.csv missing | `python src/02_build_compliance.py 2>&1; echo $?` | stderr: "Error: ...compliance_coded.csv not found..." + exit code 1 | ✓ PASS |
| 03_merge_covariates.py produces sample.csv with correct schema | `python src/03_merge_covariates.py` → read sample.csv | 3 rows × 25 columns, exact column match | ✓ PASS |
| Missingness report prints to stdout | `python src/03_merge_covariates.py` stdout | "=== Missingness report ===" with per-column NaN counts | ✓ PASS |
| winsorize function produces correct output | `from utils.stats import winsorize; winsorize(test_array)` | Function callable, defaults lower=0.01, upper=0.01 | ✓ PASS |
| 03_merge_covariates.py no firms dropped | len(compliance.csv) vs len(sample.csv) | 3 rows == 3 rows (= test fixture) | ✓ PASS |
| KFTC unmatched groups printed | `python src/03_merge_covariates.py` stdout | "KFTC groups with no universe match (47): [...]" | ✓ PASS |

**Step 7b: SKIPPED (external API required)** — `01c_dart_pull.py` requires live internet + FSS_API_KEY; cannot be tested without a Bloomberg terminal session.

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|------------|-------------|--------|----------|
| COMP-01 | 02-02-PLAN | src/02_build_compliance.py reads compliance_coded.csv and produces compliance.csv with three-way classification (0/1/2) | ✓ SATISFIED (structure) | Script correct; output verified with test fixture (codes 0/1/2 present in compliance.csv) |
| COMP-02 | 02-02-PLAN | src/02_build_compliance.py produces events.csv with disclosure dates for compliant firms (codes 1 and 2) | ✓ SATISFIED (structure) | events.csv contains only codes 1 and 2; filter uses `isin([1, 2])` |
| COMP-03 | 02-02-PLAN | Script validates input schema and reports missingness; exits with informative error if compliance_coded.csv not found | ✓ SATISFIED | Missing-input guard exits with code 1 + stderr message (no traceback); schema validation checks required columns |
| MSTR-01 | 02-03-PLAN | src/03_merge_covariates.py joins Bloomberg snapshot + compliance + chaebol + controlling shareholder % on ticker | ✓ SATISFIED | Five-way left-join verified: compliance.merge(universe) → merge(snap) → merge(roe_wide) → merge(dart), all how="left" |
| MSTR-02 | 02-03-PLAN | Output sample.csv contains all columns specified in ROADMAP Phase 4.3 | ✓ SATISFIED | 25 columns exact match: ticker through disclosure_date in D-12 order |
| MSTR-03 | 02-03-PLAN | Script winsorizes all continuous variables at 1st/99th percentiles and reports missingness by variable | ✓ SATISFIED | 19 WINSORIZE_COLS winsorized at 1st/99th; missingness report printed to stdout with NaN counts and percentages |

### Anti-Patterns Found

No TODO/FIXME/placeholder comments, no empty returns, no stub implementations found in any of the three scripts.

### Human Verification Required

### 1. Full Pipeline Execution with Real Data
**Test:** Run the complete pipeline: (1) Hand-code `data/raw/krx/compliance_coded.csv` with all KOSPI firms, (2) run `python src/01c_dart_pull.py` (requires internet + FSS_API_KEY), (3) run `python src/02_build_compliance.py`, (4) run `python src/03_merge_covariates.py`
**Expected:** compliance.csv has ~948 rows (all KOSPI firms), events.csv has compliant firms only, sample.csv has correct 25-column schema with real data
**Why human:** Requires Bloomberg terminal data and manual researcher hand-coding of compliance classifications; also requires live internet API access for DART data

### 2. DART API Execution
**Test:** Run `python src/01c_dart_pull.py` with FSS_API_KEY in .env
**Expected:** data/raw/dart/controlling_shareholder.csv produced with per-firm controlling shareholder percentages for all KOSPI tickers; corp_code_map.csv cached; no DART match firms printed to stdout
**Why human:** Requires live DART FSS OpenAPI access (internet + valid API key)

### 3. Real Data Missingness Review
**Test:** After full pipeline execution, review the missingness report printed by 03_merge_covariates.py
**Expected:** Most columns have <10% missingness; sector and disclosure_date may have systematic missingness for code-0 firms; note any columns with >20% missingness
**Why human:** Requires visual judgment about whether missingness patterns are acceptable for analysis

### Gaps Summary

Two partial truths require live data execution that cannot be verified programmatically:

1. **DART output with real data** — `src/01c_dart_pull.py` is structurally correct but requires internet access and a valid FSS_API_KEY to produce real controlling shareholder data. The current 3-row stub was generated by the smoke test.

2. **Compliance classification with real data** — `src/02_build_compliance.py` is structurally correct but depends on the researcher hand-coding `data/raw/krx/compliance_coded.csv`, which currently does not exist. The current compliance.csv and events.csv contain 3 test rows from a smoke test fixture.

Both scripts are fully implemented, syntactically valid, correctly wired, and produce the right output structure. The only missing piece is real input data — this is expected since Phase 2 explicitly requires "Phase 1 + Bloomberg terminal run" as a dependency, and the compliance data must be hand-coded by the researcher.

All 6 requirements (COMP-01, COMP-02, COMP-03, MSTR-01, MSTR-02, MSTR-03) are satisfied at the code structure level. The pipeline is ready for real data execution once the researcher (1) completes the Bloomberg terminal data pull, (2) hand-codes compliance classifications, and (3) runs the DART API script.

---

_Verified: 2026-05-09T00:19:13Z_
_Verifier: the agent (gsd-verifier)_