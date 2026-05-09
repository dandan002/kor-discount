---
phase: 02-data-pipeline
reviewed: 2026-05-08T12:00:00Z
depth: standard
files_reviewed: 3
files_reviewed_list:
  - src/01c_dart_pull.py
  - src/02_build_compliance.py
  - src/03_merge_covariates.py
findings:
  critical: 1
  warning: 5
  info: 3
  total: 9
status: issues_found
---

# Phase 02: Code Review Report

**Reviewed:** 2026-05-08T12:00:00Z
**Depth:** standard
**Files Reviewed:** 3
**Status:** issues_found

## Summary

Reviewed three Python data-pipeline scripts that form the core of Phase 02: DART API pull (`01c_dart_pull.py`), compliance classification (`02_build_compliance.py`), and merge pipeline (`03_merge_covariates.py`). All scripts follow established codebase patterns (docstrings, import ordering, path constants, logging, missing-input guards) and all must-have criteria from the plan specifications are satisfied.

One **critical** finding: the DART API exception handler catches only `requests.HTTPError`, leaving the script vulnerable to crashes from connection errors, timeouts, and DNS failures. Five **warnings** cover edge-case bugs in error reporting, dtype failures, missing input guards, and substring-vs-suffix semantics. Three **info** items note logging gaps for debugging.

## Critical Issues

### CR-01: Incomplete exception handling in DART API calls — connection/timeout errors crash script

**File:** `src/01c_dart_pull.py:122`
**Issue:** The `except requests.HTTPError` handler on line 122 only catches HTTP status errors (4xx/5xx after `raise_for_status()`). Connection errors (`requests.ConnectionError`), timeouts (`requests.Timeout`), and other `requests.RequestException` subclasses are **not caught**, causing the entire script to crash with an unhandled exception on network failures. With ~800-900+ tickers being queried, transient network issues are likely over a full run.

The threat model (T-02-03) explicitly rates "DART API rate limiting (429)" as mitigated, but the mitigation (0.5s sleep + exception handling) only works for HTTP errors. Rate-limit 429 responses would trigger `raise_for_status()` and be caught, but connection resets and timeouts would kill the run.

**Fix:**
```python
        except requests.RequestException:
            log.warning(
                "Request failed for corp_code=%s reprt_code=%s",
                corp_code,
                reprt_code,
            )
            continue
```

This catches `HTTPError`, `ConnectionError`, `Timeout`, and all other request failures, allowing the script to continue processing remaining firms. The current `log.warning` message inside the handler already logs the corp_code and reprt_code, so the behavior is preserved — just broadened.

## Warnings

### WR-01: Semantic conflation in `no_dart_match` list — two different failure modes mixed

**File:** `src/01c_dart_pull.py:180,184,190`
**Issue:** The `no_dart_match` list accumulates two distinct failure modes: (1) tickers that have no corp_code in the DART registry (line 184-186) and (2) tickers whose corp_code exists but shareholder data returned `(None, None)` (line 189-191). The final report on line 203 prints them together as a single count, making it impossible to distinguish "firm not registered in DART" from "firm registered but no data available." This matters for the analysis because missing shareholder data is qualitatively different from a missing identity mapping.

**Fix:** Use separate lists for the two failure modes and log them separately:
```python
no_corp_code = []
no_shareholder_data = []

for i, ticker in enumerate(tickers, 1):
    corp_code = corp_code_map.get(ticker)
    if corp_code is None:
        no_corp_code.append(ticker)
        continue
    largest_pct, group_pct = pull_hyslr_shareholder(corp_code, api_key)
    if largest_pct is None and group_pct is None:
        no_shareholder_data.append(ticker)
        continue
    # ... rest of loop

if no_corp_code:
    log.warning("No corp_code for %d tickers: %s", len(no_corp_code), no_corp_code)
if no_shareholder_data:
    log.warning("No shareholder data for %d tickers: %s", len(no_shareholder_data), no_shareholder_data)
```

### WR-02: `dtype=int` on `compliance_code` can crash before validation

**File:** `src/02_build_compliance.py:57`
**Issue:** `pd.read_csv(..., dtype={"ticker": str, "compliance_code": int})` will raise `ValueError: Cannot convert non-finite values (NA or inf) to integer` if any `compliance_code` cell is blank/NaN. This crash occurs **before** the schema validation (line 60-67) and value-range validation (line 75-81) can produce helpful error messages. If the researcher accidentally leaves a compliance_code blank in a row, the script will crash with an opaque pandas error rather than an informative message.

**Fix:** Use pandas nullable integer type to allow NaN during loading, then validate:
```python
df = pd.read_csv(COMPLIANCE_PATH, dtype={"ticker": str, "compliance_code": "Int64"})
# Then add a check for NaN compliance codes:
nan_codes = df["compliance_code"].isna().sum()
if nan_codes > 0:
    log.warning(
        "compliance_code has %d NaN values — these firms have no classification.",
        nan_codes,
    )
```

### WR-03: Missing input existence guards for KFTC, universe, and snapshot files

**File:** `src/03_merge_covariates.py:196,209,212`
**Issue:** Three input files — `SNAPSHOT_PATH` (line 196), `KFTC_PATH` (line 209), and `UNIVERSE_PATH` (line 212) — are loaded without existence checks. If any is absent, the script crashes with an unhelpful `FileNotFoundError` traceback. This is inconsistent with the established pattern in this codebase: `01c_dart_pull.py` guards `UNIVERSE_PATH`, `02_build_compliance.py` guards `COMPLIANCE_PATH`, and `03_merge_covariates.py` itself guards `COMPLIANCE_PATH` (lines 183-189) and `DART_PATH` (lines 231-238). The omitted guards create a gap where the most cryptic error would come from `pd.read_csv` on a missing file.

**Fix:** Add existence checks mirroring the established pattern:
```python
for path, name in [
    (SNAPSHOT_PATH, "Bloomberg snapshot"),
    (KFTC_PATH, "KFTC chaebol list"),
    (UNIVERSE_PATH, "universe"),
]:
    if not os.path.exists(path):
        print(
            f"Error: {path} not found.\n"
            f"The {name} file is required. Run the appropriate upstream script first.",
            file=sys.stderr,
        )
        sys.exit(1)
```

### WR-04: `STRIP_SUFFIXES` uses substring replacement, not suffix stripping

**File:** `src/03_merge_covariates.py:166-167`
**Issue:** The `match_chaebol` function's Korean-preprocessing step uses `cleaned.replace(s, "")` which removes **all occurrences** of each suffix string from anywhere in the name, not just trailing suffixes. The variable and comment say "strip suffixes" but the implementation strips substrings. For example, `"코리아은행"` would have `"코리아"` (Korea) stripped to produce `"은행"` (bank), which could produce false chaebol matches. In practice, most Korean corporate names place these terms at the end, so this is a low-probability edge case, but the behavior contradicts the stated intent.

**Fix:** Use `removesuffix()` (Python 3.9+) or a manual suffix-only check:
```python
cleaned = firm_name
for s in STRIP_SUFFIXES:
    if cleaned.endswith(s):
        cleaned = cleaned[: -len(s)]
        break  # Only strip one suffix
cleaned = cleaned.strip()
```
This strips only the trailing-most suffix (one match), which is the intended behavior. The `break` ensures we don't over-strip. If multiple suffixes can co-occur (e.g., "주식회사홀딩스"), loop without the `break` — but this should be decided based on actual Korean naming patterns.

### WR-05: Nested function `sum_pct` redefined on each loop iteration

**File:** `src/01c_dart_pull.py:145-152`
**Issue:** The `sum_pct` helper function is defined inside the `for reprt_code in ("11011", "11014")` loop (line 108), meaning it's re-created as a new function object on each iteration. While this doesn't cause a correctness bug (the function doesn't close over any loop variables), it's unnecessary work and a minor code smell. The function's body only depends on its `row_list` parameter, so it could be defined once outside the loop.

**Fix:** Move the `sum_pct` definition before the `for` loop:
```python
def pull_hyslr_shareholder(corp_code, api_key):
    def sum_pct(row_list):
        total = 0.0
        for row in row_list:
            try:
                total += float(row.get("trmend_posesn_stock_qota_rt", 0) or 0)
            except (ValueError, TypeError):
                pass
        return total if total > 0 else None

    for reprt_code in ("11011", "11014"):
        # ... rest of loop body, calling sum_pct(largest_rows) etc.
```

## Info

### IN-01: No retry logic for DART API transient failures

**File:** `src/01c_dart_pull.py:108-160`
**Issue:** The `pull_hyslr_shareholder` function has no retry mechanism for transient network failures. If a request times out or fails intermittently (not an HTTP error), the firm's data is lost for that run (especially after CR-01 is fixed to catch all `RequestException`). The 0.5s sleep between calls prevents rate-limiting but doesn't help with transient errors.
**Fix suggestion:** Consider adding 1-2 retries with exponential backoff for network-related failures before falling through to the next `reprt_code` or returning `(None, None)`.

### IN-02: Silent skip of firms with no shareholder data

**File:** `src/01c_dart_pull.py:189-190`
**Issue:** When `pull_hyslr_shareholder` returns `(None, None)` for a firm with a valid corp_code, the firm is added to `no_dart_match` without any logging at the individual-firm level. During a run with 800+ tickers, there's no way to see which firms had corp_codes but returned no data.
**Fix suggestion:** Add `log.debug("No shareholder data for ticker=%s (corp_code=%s)", ticker, corp_code)` before the `continue` on line 191, so verbose mode reveals which firms were skipped.

### IN-03: No schema validation for KFTC or Bloomberg input columns

**File:** `src/03_merge_covariates.py:196,209`
**Issue:** The KFTC CSV is assumed to have a `Group_Name_Korean` column (line 210) and the Bloomberg snapshot is assumed to have columns matching `BBG_RENAME` keys. If the upstream data format changes (e.g., Bloomberg changes a field mnemonic), the rename would silently skip unknown columns and the merge would produce all-NaN values. The `02_build_compliance.py` script has good schema validation (lines 60-67), but the merge script has none for these inputs.
**Fix suggestion:** Add lightweight column-existence checks after loading: verify `Group_Name_Korean in kftc.columns` and that all `BBG_RENAME.keys()` exist in `snap.columns` before the merge, logging warnings for any mismatches.

---

_Reviewed: 2026-05-08T12:00:00Z_
_Reviewer: the agent (gsd-code-reviewer)_
_Depth: standard_