# Phase 2: Data Pipeline - Research

**Researched:** 2026-05-08
**Domain:** Python data pipeline — DART FSS OpenAPI, pandas merge/pivot/winsorize, Korean corporate name matching
**Confidence:** HIGH (all critical API endpoints verified live; all data files inspected)

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**D-01 through D-19** from `02-CONTEXT.md` are locked. Key ones:

- **D-01/D-02:** `compliance_coded.csv` lives at `data/raw/krx/compliance_coded.csv`; required columns are `ticker` (6-digit), `compliance_code` (0/1/2), `disclosure_date` (YYYY-MM-DD).
- **D-03:** Code 0 firms have blank `disclosure_date`; `events.csv` includes only codes 1 and 2.
- **D-04:** Kappa check runs only when `compliance_coded_r2.csv` exists alongside primary; does not block execution.
- **D-05/D-06:** `src/01c_dart_pull.py` reads `universe_raw.csv` for ticker list; uses `FSS_API_KEY` from `.env`.
- **D-07:** Pull `controlling_pct_largest` (biggest single holder %) and `controlling_pct_group` (controlling family group total %) — both land in output CSV.
- **D-08:** Script skips firms with no DART match; prints list to stdout. Corp_code lookup from ticker required.
- **D-09/D-10/D-11:** KFTC source `data/raw/kftc/KFTC_large_business_groups_2026.csv`; name-prefix match; unmatched printed to stdout.
- **D-12:** Exact 25-column schema locked (ticker through disclosure_date).
- **D-13:** Bloomberg mnemonics renamed to human-readable names.
- **D-14:** ROE panel pivoted wide: one `roe_YYYY` column per year (2019-2023), one row per firm.
- **D-15:** `compliance_code` and `disclosure_date` are the last two columns.
- **D-16/D-17/D-18:** Left-join on compliance_coded.csv as base; missingness report to stdout; winsorize all continuous Bloomberg + ROE columns at 1st/99th percentiles.
- **D-19:** Strip `.KS` suffix from returns_panel.csv before joining.

### Claude's Discretion

- DART corp_code lookup implementation (API vs. pre-cached mapping file) — implement whichever is more reliable at runtime.
- Rate limiting and retry logic for DART API calls.
- Exact Korean suffix list for KFTC name-prefix matching — use: `주식회사`, `(주)`, `그룹`, `홀딩스`, `지주`, `코리아`.

### Deferred Ideas (OUT OF SCOPE)

None.

</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| COMP-01 | `src/02_build_compliance.py` reads `compliance_coded.csv` and produces `compliance.csv` with three-way classification (0/1/2) | Schema verified (D-01/D-02); `cohens_kappa()` in `utils/stats.py` ready |
| COMP-02 | `src/02_build_compliance.py` produces `events.csv` with disclosure dates for compliant firms (codes 1 and 2) | Simple filter + copy pattern; date column validated |
| COMP-03 | Script validates input schema and reports missingness; exits with informative error if `compliance_coded.csv` not found | Pattern established in `src/01_bloomberg_pull.py` (`sys.exit(1)` on missing file) |
| MSTR-01 | `src/03_merge_covariates.py` joins Bloomberg snapshot + compliance + chaebol + controlling shareholder % on ticker | All source files verified; DART API tested live |
| MSTR-02 | Output `sample.csv` contains all columns specified in ROADMAP Phase 4.3 | Locked 25-column schema in D-12 |
| MSTR-03 | Script winsorizes all continuous variables at 1st/99th percentiles and reports missingness by variable | `utils.stats.winsorize()` verified ready |

</phase_requirements>

---

## Summary

Phase 2 builds three scripts that transform raw CSVs into the master analysis dataset. `src/02_build_compliance.py` is a thin reader/validator over the hand-coded file. `src/01c_dart_pull.py` is the most technically complex piece — it calls the DART FSS OpenAPI `hyslrSttus.json` endpoint (not `majorstock.json`) to get per-firm, per-shareholder rows and aggregates them into two controlling shareholder percentages. `src/03_merge_covariates.py` joins five data sources on bare 6-digit ticker, pivots the ROE panel wide, winsorizes, and prints a missingness report.

All three Bloomberg data files exist and have been inspected. The ROE panel (`roe_panel.csv`) covers only 16 tickers and years 2021-2023 — this is a partial Bloomberg terminal run. The pivot step will produce `NaN` for most firms in `roe_2019` through `roe_2022`; the planner must treat this as expected data sparsity, not a pipeline bug. The returns panel covers 942 tickers and uses `.KS` suffix (confirmed).

The KFTC name-prefix matching algorithm (D-10) works well for standard Korean group names, but fails silently for firms using Latin-alphabet prefixes (`SK하이닉스`, `LG에너지솔루션`, `HD현대중공업`). These firms exist under KFTC groups whose Korean name starts with a Hangul transliteration of the Latin abbreviation (e.g., `에스케이` for SK, `엘지` for LG, `에이치디현대` for HD Hyundai). The script must handle this mismatch or it will under-count chaebol firms.

**Primary recommendation:** Use `hyslrSttus.json` (not `majorstock.json`) for DART data. Build the corp_code lookup by downloading and parsing `corpCode.xml` at runtime. For KFTC matching, augment the prefix list with a hard-coded alias table mapping Latin abbreviations to their KFTC Hangul group names.

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Compliance classification | Python script (`02_build_compliance.py`) | — | Pure CSV read/validate/filter |
| Inter-rater reliability | Python script (conditional) | `utils/stats.cohens_kappa` | Optional diagnostic; doesn't block |
| DART API acquisition | Python script (`01c_dart_pull.py`) | `requests` + `.env` | Network I/O; external API |
| Corp_code lookup | In-memory XML parse (runtime) | Cached mapping in `data/raw/dart/` | Most reliable; avoids stale cache |
| Chaebol flag | Python script (`03_merge_covariates.py`) | `data/raw/kftc/` CSV | String matching; no external API |
| Covariate merge | Python script (`03_merge_covariates.py`) | pandas | Five-way left-join on ticker |
| Winsorization | `utils/stats.winsorize` | — | Already built and tested |
| Missingness report | Inline print in merge script | — | stdout only; not persisted |

---

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| pandas | 2.2.1 [VERIFIED: pip] | DataFrame operations, CSV I/O, merge, pivot | Project-pinned; all existing scripts use it |
| numpy | 1.26.4 [VERIFIED: pip] | Numeric arrays, NaN propagation | Project-pinned; underpins pandas |
| requests | 2.31.0 [VERIFIED: pip] | DART API HTTP calls | Already installed; standard HTTP client |
| python-dotenv | >=1.0.0 [VERIFIED: pip] | Read `FSS_API_KEY` from `.env` | Project-established pattern |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `utils/stats.py` (internal) | — | `winsorize()`, `cohens_kappa()` | All continuous winsorization; kappa check |
| xml.etree.ElementTree | stdlib | Parse DART `CORPCODE.xml` zip | Corp_code lookup at runtime |
| zipfile | stdlib | Extract DART corp code zip download | Paired with ElementTree |
| logging | stdlib | Structured console output | Match existing script style |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Raw `requests` for DART | `dart-fss` PyPI package | dart-fss not installed; adds dependency; raw requests are cleaner and already tested live |
| Runtime XML parse for corp_code | Pre-cached `data/raw/dart/corp_code_map.csv` | Cache can be stale; runtime download always current; but costs ~5s per run — recommend caching after first download |
| Name-prefix only for KFTC | Full fuzzy match (thefuzz/rapidfuzz) | Not installed; alias table is smaller and more accurate for known mismatches |

---

## Architecture Patterns

### System Architecture Diagram

```
[data/raw/krx/compliance_coded.csv]  ──►  src/02_build_compliance.py  ──►  data/processed/compliance.csv
                                                                        ──►  data/processed/events.csv

[DART FSS API]  ──────────────────►  src/01c_dart_pull.py  ──────────►  data/raw/dart/controlling_shareholder.csv

[compliance.csv]  ─────────────────────────────┐
[data/raw/bloomberg/snapshot_2023.csv]  ────────┤
[data/raw/bloomberg/roe_panel.csv]  ────────────┤── src/03_merge_covariates.py ──► data/processed/sample.csv
[data/raw/kftc/KFTC_large_business_groups_2026.csv] ┤                              (stdout: missingness report)
[data/raw/dart/controlling_shareholder.csv]  ───┘
```

### Recommended Project Structure

```
src/
├── 01c_dart_pull.py        # NEW: DART controlling shareholder acquisition
├── 02_build_compliance.py  # NEW: compliance classification
└── 03_merge_covariates.py  # NEW: master dataset merge
data/
├── raw/
│   ├── dart/
│   │   ├── corp_code_map.csv            # cached corp_code↔ticker lookup (generated by 01c_dart_pull.py)
│   │   └── controlling_shareholder.csv  # output of 01c_dart_pull.py
│   └── krx/
│       ├── compliance_coded.csv         # hand-coded (user provides)
│       └── compliance_coded_r2.csv      # optional second rater
└── processed/
    ├── compliance.csv
    ├── events.csv
    └── sample.csv
```

### Pattern 1: Missing-Input Guard (established in Phase 1)

**What:** Check for required input file at script entry; print informative error and `sys.exit(1)`.
**When to use:** Any script that requires a non-generated input file.

```python
# Source: src/01_bloomberg_pull.py (established pattern)
import sys, os
COMPLIANCE_PATH = os.path.join(PROJECT_ROOT, "data", "raw", "krx", "compliance_coded.csv")

if not os.path.exists(COMPLIANCE_PATH):
    print(
        f"Error: {COMPLIANCE_PATH} not found.\n"
        "Hand-code KRX disclosures and save as data/raw/krx/compliance_coded.csv\n"
        "Required columns: ticker (6-digit), compliance_code (0/1/2), disclosure_date (YYYY-MM-DD)",
        file=sys.stderr,
    )
    sys.exit(1)
```

### Pattern 2: DART Corp_Code Lookup with Caching

**What:** Download and parse `CORPCODE.xml` once; cache as `data/raw/dart/corp_code_map.csv` for subsequent runs.
**When to use:** `src/01c_dart_pull.py` only.

```python
# Source: DART API verified live 2026-05-08
import requests, zipfile, io, xml.etree.ElementTree as ET, pandas as pd

CORP_CODE_URL = "https://opendart.fss.or.kr/api/corpCode.xml"
CORP_CODE_CACHE = os.path.join(PROJECT_ROOT, "data", "raw", "dart", "corp_code_map.csv")

def get_corp_code_map(api_key):
    """Return dict {stock_code: corp_code} from DART, using cache if available."""
    if os.path.exists(CORP_CODE_CACHE):
        df = pd.read_csv(CORP_CODE_CACHE, dtype=str)
        return dict(zip(df["stock_code"], df["corp_code"]))
    
    r = requests.get(CORP_CODE_URL, params={"crtfc_key": api_key}, timeout=60)
    r.raise_for_status()
    z = zipfile.ZipFile(io.BytesIO(r.content))
    xml_data = z.read("CORPCODE.xml")
    root = ET.fromstring(xml_data)
    
    rows = []
    for item in root.findall("list"):
        code = item.findtext("corp_code", "").strip()
        stock = item.findtext("stock_code", "").strip()
        name = item.findtext("corp_name", "").strip()
        if stock:  # only listed firms
            rows.append({"stock_code": stock, "corp_code": code, "corp_name": name})
    
    df = pd.DataFrame(rows)
    df.to_csv(CORP_CODE_CACHE, index=False)
    return dict(zip(df["stock_code"], df["corp_code"]))
```

### Pattern 3: DART hyslrSttus — Controlling Shareholder Pull

**What:** For each corp_code, call `hyslrSttus.json` and aggregate percentages.
**When to use:** `src/01c_dart_pull.py` per-firm loop.

**Verified live:** [VERIFIED: DART API 2026-05-08]

```python
# Endpoint: https://opendart.fss.or.kr/api/hyslrSttus.json
# Parameters: crtfc_key, corp_code, bsns_year="2023", reprt_code="11011"
# Key response fields (verified from Samsung 삼성전자):
#   nm: shareholder name
#   relate: relationship — "최대주주 본인" | "최대주주의 특수관계인" | other
#   stock_knd: "보통주" | "우선주" (common | preferred)
#   trmend_posesn_stock_qota_rt: period-end ownership % (float as string)

def pull_hyslr_shareholder(corp_code, api_key):
    """Return (controlling_pct_largest, controlling_pct_group) for one firm."""
    import time
    time.sleep(0.5)  # rate limit
    r = requests.get(
        "https://opendart.fss.or.kr/api/hyslrSttus.json",
        params={"crtfc_key": api_key, "corp_code": corp_code,
                "bsns_year": "2023", "reprt_code": "11011"},
        timeout=20,
    )
    r.raise_for_status()
    data = r.json()
    if data.get("status") != "000":
        return None, None  # skip; no match
    
    rows = data.get("list", [])
    # Use common shares only for percentage calculation
    common = [row for row in rows if row.get("stock_knd") == "보통주"]
    if not common:
        common = rows  # fallback: use all share classes
    
    # largest single holder: "최대주주 본인"
    largest_rows = [r for r in common if r.get("relate") == "최대주주 본인"]
    # group total: "최대주주 본인" + "최대주주의 특수관계인"
    group_rows = [r for r in common
                  if r.get("relate") in ("최대주주 본인", "최대주주의 특수관계인")]
    
    def sum_pct(rows):
        total = 0.0
        for row in rows:
            try:
                total += float(row.get("trmend_posesn_stock_qota_rt", 0) or 0)
            except (ValueError, TypeError):
                pass
        return total if total > 0 else None
    
    return sum_pct(largest_rows), sum_pct(group_rows)
```

### Pattern 4: KFTC Name-Prefix Matching with Alias Table

**What:** Match firm names to chaebol groups using Korean prefix; alias table covers Latin-abbreviation firms.
**When to use:** `src/03_merge_covariates.py` chaebol flag construction.

```python
# KFTC alias table — covers firms whose universe name starts with Latin alphabet
# but whose KFTC group name is a Hangul transliteration
# [VERIFIED: inspected KFTC_large_business_groups_2026.csv + universe_raw.csv 2026-05-08]
LATIN_TO_KFTC = {
    "SK": "에스케이",
    "LG": "엘지",
    "HD": "에이치디현대",
    "KT": "케이티",         # KT&G is separate: 케이티앤지
    "KT&G": "케이티앤지",
    "GS": "지에스",
    "CJ": "씨제이",
    "LS": "엘에스",
    "LX": "엘엑스",
    "DL": "디엘",
    "DB": "디비",
    "SM": "에스엠",
    "HDC": "에이치디씨",
    "OCI": "오씨아이",
    "HMM": "에이치엠엠",
    "KG": "케이지",
    "KCC": "케이씨씨",
}
STRIP_SUFFIXES = ["주식회사", "(주)", "그룹", "홀딩스", "지주", "코리아"]

def match_chaebol(firm_name, kftc_korean_names):
    """Return matched KFTC group name or None."""
    if not firm_name or not isinstance(firm_name, str):
        return None
    # Check alias table first (Latin-prefix firms)
    for prefix, kftc_name in LATIN_TO_KFTC.items():
        if firm_name.startswith(prefix):
            if kftc_name in kftc_korean_names:
                return kftc_name
    # Standard Korean-prefix match
    cleaned = firm_name
    for s in STRIP_SUFFIXES:
        cleaned = cleaned.replace(s, "")
    cleaned = cleaned.strip()
    for kname in kftc_korean_names:
        if cleaned.startswith(kname):
            return kname
    return None
```

### Pattern 5: ROE Panel Pivot Wide

**What:** Aggregate weekly BDH ROE observations to annual (take last non-null per year), then pivot wide.
**When to use:** `src/03_merge_covariates.py` ROE section.

```python
# Source: inspected data/raw/bloomberg/roe_panel.csv 2026-05-08
# The panel is long format: ticker, year, roe
# Year range in current data: 2021-2023 (partial run); full data will be 2019-2023
import pandas as pd

roe = pd.read_csv(ROE_PANEL_PATH, dtype={"ticker": str})
# The BDH ROE pull produces multiple rows per (ticker, year) — take last non-null
roe_annual = (
    roe.dropna(subset=["roe"])
    .sort_values("year")
    .groupby(["ticker", "year"])["roe"]
    .last()
    .reset_index()
)
roe_wide = roe_annual.pivot(index="ticker", columns="year", values="roe")
roe_wide.columns = [f"roe_{int(yr)}" for yr in roe_wide.columns]
# Ensure all 5 year columns exist even if data is sparse
for yr in [2019, 2020, 2021, 2022, 2023]:
    if f"roe_{yr}" not in roe_wide.columns:
        roe_wide[f"roe_{yr}"] = float("nan")
roe_wide = roe_wide.reset_index()
```

### Anti-Patterns to Avoid

- **Using `majorstock.json` instead of `hyslrSttus.json`:** `majorstock.json` returns event-driven large-holding reports (5%+ threshold filings, not annual report data). `hyslrSttus.json` returns the annual report's controlling shareholder table with per-person rows and `relate` field, enabling the individual vs. group split. [VERIFIED: live API test 2026-05-08]
- **Joining on `.KS`-suffixed tickers:** All internal joins use bare 6-digit tickers. Strip `.KS` before any join. `returns_panel.csv` uses `.KS`; `snapshot_2023.csv` uses bare tickers. [VERIFIED: data inspection]
- **Winsorizing identifiers:** `ticker`, `name`, `sector`, `chaebol`, `compliance_code`, `disclosure_date` must be excluded from winsorization. Only continuous Bloomberg + ROE columns are winsorized. (D-18)
- **Treating ROE panel sparsity as a bug:** Current `roe_panel.csv` has only 16 tickers and years 2021-2023 — this is a partial terminal run. The pipeline must produce NaN for missing (ticker, year) combinations gracefully. When the full terminal run completes, all 948 tickers × 5 years will be present.
- **Breaking execution when `compliance_coded_r2.csv` is absent:** The kappa check is conditional (`os.path.exists(...)`) and must not raise an error or warning when the file is missing.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Winsorization at percentile bounds | Custom percentile clip | `utils.stats.winsorize()` | Already built; handles NaN correctly |
| Inter-rater reliability | Custom kappa calculation | `utils.stats.cohens_kappa()` | Already built; wraps statsmodels |
| HTTP retry on transient 429/5xx | Custom retry loop | `requests` with manual `time.sleep(0.5)` | Simple; DART API is stable; full retry library is overkill |
| Korean corp_code lookup | Manual mapping table | DART `corpCode.xml` download | Official; covers all 110k+ registered Korean companies |
| DataFrame pivot | Manual column-per-year loop | `pandas.DataFrame.pivot()` | Built-in; handles sparse data correctly with NaN |

**Key insight:** This phase is glue code, not algorithm development. Every complex operation (winsorize, kappa, pivot) has a one-liner in existing libraries. The implementation risk is in the DART API field semantics and KFTC name matching — both are now fully documented in this research.

---

## Common Pitfalls

### Pitfall 1: DART API Returns No Data for Firms Without Annual Reports

**What goes wrong:** `hyslrSttus.json` returns `status=020` ("데이터가 없습니다") for firms that filed only a semi-annual or quarterly report, or for newly listed firms. The script crashes or silently loses rows.
**Why it happens:** Many KOSPI firms that missed the annual filing date or were newly listed in 2023.
**How to avoid:** Check `data.get("status") != "000"` and skip with a logged warning. Try `reprt_code="11014"` (semi-annual) as fallback before giving up. Add the ticker to a "no DART match" list printed to stdout.
**Warning signs:** Result CSV has fewer rows than universe_raw.csv.

### Pitfall 2: KFTC Latin-Prefix Mismatch Silently Under-Counts Chaebol

**What goes wrong:** `SK하이닉스`, `LG에너지솔루션`, `HD현대중공업` are missed by the Korean-prefix matcher because their KFTC group name is a Hangul transliteration (`에스케이`, `엘지`, `에이치디현대`).
**Why it happens:** KFTC uses Hangul transliterations of Latin abbreviations; firm names use the Latin abbreviation directly.
**How to avoid:** Apply the `LATIN_TO_KFTC` alias table (Pattern 4 above) before the standard prefix match.
**Warning signs:** Samsung group has 6+ matches but SK group has 0 — a dead giveaway.

### Pitfall 3: ROE Panel Multi-Row Per (Ticker, Year)

**What goes wrong:** The BDH pull produced weekly rows; if a naive `pivot()` is called without deduplication, it raises `ValueError: Index contains duplicate entries, cannot reshape`.
**Why it happens:** `roe_panel.csv` stores one row per weekly date, not one row per year. The `year` column groups multiple dates into the same year.
**How to avoid:** Deduplicate to one row per (ticker, year) before pivoting (Pattern 5 above — last non-null `roe` per year).
**Warning signs:** `pd.pivot` raises duplicate index error.

### Pitfall 4: Compliance Merge Base Loses Firms

**What goes wrong:** Using `snapshot_2023.csv` as the merge base (inner join) drops firms in `compliance_coded.csv` that are missing from Bloomberg snapshot.
**Why it happens:** Bloomberg coverage gaps; ~50% of `snapshot_2023.csv` columns are NaN (verified).
**How to avoid:** Left-join with `compliance_coded.csv` as the left table (D-16). Firms in compliance not in Bloomberg snapshot keep their row with NaN financials.
**Warning signs:** `sample.csv` has fewer rows than `compliance.csv`.

### Pitfall 5: Numeric Strings in DART Percentage Fields

**What goes wrong:** `trmend_posesn_stock_qota_rt` returns `"8.51"` (string), not `8.51` (float). Arithmetic fails silently if summing strings.
**Why it happens:** All DART JSON fields are returned as strings.
**How to avoid:** Wrap in `float(row.get("trmend_posesn_stock_qota_rt", 0) or 0)` with a try/except for empty strings.
**Warning signs:** `controlling_pct_group` values are implausibly large (string concatenation).

---

## Runtime State Inventory

> This is a greenfield phase (new scripts and new output files). No rename/refactor is involved. Runtime state inventory is not applicable.

**Data files that must exist before Phase 2 scripts run:**
- `data/raw/bloomberg/snapshot_2023.csv` — exists, 948 rows [VERIFIED]
- `data/raw/bloomberg/roe_panel.csv` — exists, 16 tickers only (partial run) [VERIFIED]
- `data/raw/bloomberg/returns_panel.csv` — exists, 942 tickers [VERIFIED]
- `data/raw/kftc/KFTC_large_business_groups_2026.csv` — exists, 102 groups [VERIFIED]
- `data/raw/universe_raw.csv` — exists, 948 rows [VERIFIED]
- `data/raw/krx/compliance_coded.csv` — DOES NOT EXIST (user must hand-code before Phase 2 runs) [VERIFIED: directory exists, file absent]
- `FSS_API_KEY` in `.env` — configured (40-char key) [VERIFIED]

---

## DART API: Verified Endpoint Summary

| Endpoint | URL | Use | Status |
|----------|-----|-----|--------|
| `corpCode.xml` | `https://opendart.fss.or.kr/api/corpCode.xml` | Download ticker↔corp_code XML zip | Working [VERIFIED] |
| `hyslrSttus.json` | `https://opendart.fss.or.kr/api/hyslrSttus.json` | 최대주주 현황 — per-shareholder rows, annual report | Working [VERIFIED] |
| `majorstock.json` | `https://opendart.fss.or.kr/api/majorstock.json` | Large-holding event filings (5%+ threshold) | Working but WRONG for this purpose |

**`hyslrSttus.json` parameters:**
- `crtfc_key`: 40-char API key
- `corp_code`: 8-digit DART corp code (obtained from `corpCode.xml`)
- `bsns_year`: `"2023"` for FY2023 annual report
- `reprt_code`: `"11011"` (annual report)

**Key response fields:**
- `nm`: shareholder name
- `relate`: `"최대주주 본인"` | `"최대주주의 특수관계인"` | other
- `stock_knd`: `"보통주"` | `"우선주"`
- `trmend_posesn_stock_qota_rt`: period-end ownership % (returned as string, e.g., `"8.51"`)

**Computing the two target columns:**
- `controlling_pct_largest`: sum of `trmend_posesn_stock_qota_rt` for common shares where `relate == "최대주주 본인"`
- `controlling_pct_group`: sum of `trmend_posesn_stock_qota_rt` for common shares where `relate in ("최대주주 본인", "최대주주의 특수관계인")`

---

## Data Quality Facts (from Actual Files)

| File | Rows | Notes |
|------|------|-------|
| `snapshot_2023.csv` | 948 | ~47% rows missing per financial column; expected for small/thin-traded firms |
| `roe_panel.csv` | 45 obs, 16 tickers | PARTIAL Bloomberg run; 2021-2023 only; 13 NaN roe values |
| `returns_panel.csv` | 250,370 rows, 942 firms | Uses `.KS` suffix; includes KOSPI Index benchmark |
| `universe_raw.csv` | 948 firms | Bare 6-digit tickers; `sector`/`industry` columns mostly empty |
| `KFTC_large_business_groups_2026.csv` | 102 groups | Korean + English group names; no ticker column |

**Bloomberg mnemonic → column rename map (D-13) [VERIFIED from snapshot_2023.csv headers]:**

| Bloomberg Mnemonic | sample.csv Column Name |
|--------------------|------------------------|
| `PX_TO_BOOK_RATIO` | `pbr` |
| `PE_RATIO` | `pe_ratio` |
| `RETURN_COM_EQY` | `roe_fy23` |
| `RETURN_ON_ASSET` | `roa` |
| `EQY_FLOAT_PCT` | `foreign_pct` |
| `CUR_MKT_CAP` | `mkt_cap` |
| `EQY_DVD_YLD_IND` | `dvd_yield` |
| `TOT_DEBT_TO_TOT_EQY` | `debt_equity` |
| `BS_TOT_ASSET` | `total_assets` |
| `SALES_GROWTH` | `sales_growth` |
| `CASH_AND_NEAR_CASH_ITEM` | `cash` |
| `DVD_SH_12M` | `dvd_sh_12m` |

**Columns to winsorize (continuous Bloomberg + ROE panel):**
`pbr`, `pe_ratio`, `roe_fy23`, `roa`, `foreign_pct`, `mkt_cap`, `dvd_yield`, `debt_equity`, `total_assets`, `sales_growth`, `cash`, `dvd_sh_12m`, `roe_2019`, `roe_2020`, `roe_2021`, `roe_2022`, `roe_2023`, `controlling_pct_largest`, `controlling_pct_group`

**Columns excluded from winsorization:** `ticker`, `name`, `sector`, `chaebol`, `compliance_code`, `disclosure_date`

---

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python 3 | All scripts | Yes | system | — |
| pandas | All scripts | Yes | 2.2.1 | — |
| numpy | All scripts | Yes | 1.26.4 | — |
| requests | `01c_dart_pull.py` | Yes | 2.31.0 | — |
| python-dotenv | `01c_dart_pull.py` | Yes | >=1.0.0 | — |
| scipy | `utils/stats.py` | Yes | 1.12.0 | — |
| statsmodels | `utils/stats.py` | Yes | 0.14.4 | — |
| DART FSS API (`opendart.fss.or.kr`) | `01c_dart_pull.py` | Yes | — | No fallback — requires internet |
| `FSS_API_KEY` in `.env` | `01c_dart_pull.py` | Yes | 40-char key | — |
| `data/raw/krx/compliance_coded.csv` | `02_build_compliance.py` | **NO** | — | User must hand-code before running |
| `data/processed/` directory | `03_merge_covariates.py` | Yes (empty) | — | `os.makedirs(exist_ok=True)` |

**Missing dependencies with no fallback:**
- `data/raw/krx/compliance_coded.csv` — must be created by human before `02_build_compliance.py` can run. Script must exit with informative error if absent (COMP-03).

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | `reprt_code="11011"` reliably returns FY2023 annual report data for all KOSPI firms | DART API Patterns | Some firms may use a different report code; fallback to `11014` handles most |
| A2 | ROE panel intended to be full 948-firm, 2019-2023 dataset after complete Bloomberg run; current 16-ticker version is partial | Data Quality Facts | If researcher intentionally only pulled 16 firms, phase produces mostly-NaN `roe_*` columns |
| A3 | `controlling_pct_largest` should use only `보통주` (common shares) to avoid double-counting preferred | DART Pattern 3 | If preferred shares should also count, both column values will be understated |
| A4 | KFTC `LATIN_TO_KFTC` alias table is complete for all relevant KOSPI-listed SK/LG/HD/GS/CJ/LS firms | KFTC Pattern 4 | Missed aliases produce 0-match for those groups; stdout report allows manual review |

---

## Open Questions

1. **ROE panel coverage: partial or intentional?**
   - What we know: `roe_panel.csv` covers only 16 tickers, years 2021-2023. Bloomberg terminal run occurred.
   - What's unclear: Was this a test run with a small subset, or did BDH fail for most tickers?
   - Recommendation: Phase 2 scripts must handle NaN gracefully. If researcher re-runs at terminal, full data replaces the file.

2. **DART API: should preferred shares be included in controlling %?**
   - What we know: `hyslrSttus.json` returns separate rows for `보통주` and `우선주`. Samsung's Lee family holds significant preferred shares.
   - What's unclear: The ROADMAP does not specify whether `controlling_pct_group` should include preferred.
   - Recommendation: Default to common shares only (`stock_knd == "보통주"`); document the choice with a comment.

---

## Sources

### Primary (HIGH confidence)

- DART FSS OpenAPI `hyslrSttus.json` — verified live with Samsung (corp_code 00126380) on 2026-05-08; response fields documented from actual API response
- DART FSS OpenAPI `corpCode.xml` — verified live on 2026-05-08; XML structure confirmed
- `data/raw/bloomberg/*.csv` — inspected directly; row counts, column names, ticker formats confirmed
- `data/raw/kftc/KFTC_large_business_groups_2026.csv` — inspected directly; 102 groups, column names confirmed
- `utils/stats.py` — read directly; `winsorize()` and `cohens_kappa()` signatures confirmed
- `src/01_bloomberg_pull.py` — read directly; structural template pattern confirmed

### Secondary (MEDIUM confidence)

- DART API guide page `DS002/2019007` (최대주주 현황) — field names `trmend_posesn_stock_qota_rt`, `relate`, `nm` fetched via WebFetch
- DART API guide page `DS002/2019008` (최대주주 변동현황) — alternative endpoint; confirmed NOT the right one for this use case

### Tertiary (LOW confidence — not needed)

- `dart-fss` PyPI library documentation — referenced only to confirm raw `requests` approach is equivalent

---

## Metadata

**Confidence breakdown:**
- DART API endpoints and field names: HIGH — verified with live API calls
- KFTC matching strategy: HIGH — tested against real data files; alias table derived from inspection
- Bloomberg column rename map: HIGH — verified from actual snapshot_2023.csv headers
- ROE panel sparsity: HIGH — observed directly; 16 tickers only
- Architecture patterns: HIGH — modeled on existing scripts in same codebase

**Research date:** 2026-05-08
**Valid until:** 2026-08-08 (DART API structure is stable; KFTC file is an annual publication)
