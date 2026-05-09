# Phase 2: Data Pipeline - Pattern Map

**Mapped:** 2026-05-08
**Files analyzed:** 3 new scripts
**Analogs found:** 3 / 3

---

## File Classification

| New File | Role | Data Flow | Closest Analog | Match Quality |
|----------|------|-----------|----------------|---------------|
| `src/01c_dart_pull.py` | service / acquisition script | request-response (external API + file I/O) | `src/01_bloomberg_pull.py` | exact — same read→fetch→save pattern, same guard structure |
| `src/02_build_compliance.py` | transform / validator script | file I/O + batch transform | `src/00b_build_universe_public.py` | role-match — CSV read, filter, rename, save |
| `src/03_merge_covariates.py` | transform / merge script | batch transform (5-way join, pivot, winsorize) | `src/01b_public_pull.py` + `src/01_bloomberg_pull.py` | role-match — multi-stage transform with logging |

---

## Pattern Assignments

### `src/01c_dart_pull.py` (acquisition script, request-response)

**Analog:** `src/01_bloomberg_pull.py`

**Imports pattern** (`src/01_bloomberg_pull.py` lines 1–38):
```python
"""
<Module docstring: READS / OUTPUTS / Run instructions>
"""

import logging
import os
import sys

import pandas as pd

# Ensure project root is on path so utils/ is importable from project-root runs.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.stats import winsorize  # example; swap for dotenv/requests
```

Additional imports for DART pull (no analog in codebase — use stdlib + installed libs):
```python
import io
import time
import xml.etree.ElementTree as ET
import zipfile

import requests
from dotenv import load_dotenv
```

**Project root + path constants pattern** (`src/01_bloomberg_pull.py` lines 40–53):
```python
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

UNIVERSE_PATH = os.path.join(PROJECT_ROOT, "data", "raw", "universe_raw.csv")
# ... define all output paths here as module-level constants
```

**Missing-input guard pattern** (`src/01_bloomberg_pull.py` lines 87–93 and `src/01b_public_pull.py` lines 63–69):
```python
def load_universe():
    if not os.path.exists(UNIVERSE_PATH):
        print(
            f"Error: {UNIVERSE_PATH} not found.\n"
            "Run src/00_build_universe.py first to generate the KOSPI universe.",
            file=sys.stderr,
        )
        sys.exit(1)

    df = pd.read_csv(UNIVERSE_PATH)
    if "ticker" not in df.columns:
        print(
            f"Error: {UNIVERSE_PATH} does not contain a 'ticker' column.\n"
            "Re-run src/00_build_universe.py to regenerate it.",
            file=sys.stderr,
        )
        sys.exit(1)

    tickers = df["ticker"].dropna().tolist()
    log.info("Loaded %d tickers from %s.", len(tickers), UNIVERSE_PATH)
    return tickers
```

**Core fetch-per-ticker + save pattern** (`src/01_bloomberg_pull.py` lines 109–123):
```python
def pull_snapshot(tickers):
    """Pull 12-field BDP snapshot as of FY2023 year-end."""
    log.info("Pulling snapshot BDP for %d tickers ...", len(tickers))
    df = bdp(tickers, SNAPSHOT_FIELDS, overrides=SNAPSHOT_OVERRIDES)
    df.index.name = "ticker"
    df.reset_index(inplace=True)
    log.info("Snapshot: %d rows x %d columns.", len(df), len(df.columns))
    df.to_csv(SNAPSHOT_PATH, index=False)
    log.info("Saved to %s.", SNAPSHOT_PATH)
    return df
```

Apply this structure to DART: iterate per ticker with `time.sleep(0.5)` between calls (rate limit), collect results into a list of dicts, build DataFrame, save to `data/raw/dart/controlling_shareholder.csv`.

**DART corp_code lookup with caching** (from RESEARCH.md Pattern 2 — no codebase analog, use as-is):
```python
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

**DART hyslrSttus per-firm pull** (from RESEARCH.md Pattern 3 — no codebase analog, use as-is):
```python
def pull_hyslr_shareholder(corp_code, api_key):
    """Return (controlling_pct_largest, controlling_pct_group) for one firm."""
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
    common = [row for row in rows if row.get("stock_knd") == "보통주"]
    if not common:
        common = rows  # fallback: use all share classes

    largest_rows = [r for r in common if r.get("relate") == "최대주주 본인"]
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

**Main function pattern** (`src/01_bloomberg_pull.py` lines 180–199):
```python
def main():
    os.makedirs(BLOOMBERG_DIR, exist_ok=True)

    tickers = load_universe()
    pull_snapshot(tickers)
    pull_roe_panel(tickers)
    pull_returns_panel(tickers)

    log.info("All done. Verify outputs:")
    for path in [SNAPSHOT_PATH, ROE_PANEL_PATH, RETURNS_PANEL_PATH]:
        if os.path.exists(path):
            log.info("%s (%d bytes)", path, os.path.getsize(path))
        else:
            log.error("MISSING: %s", path)


if __name__ == "__main__":
    main()
```

For `01c_dart_pull.py`: load `.env` with `load_dotenv()` in `main()` before reading `FSS_API_KEY = os.environ["FSS_API_KEY"]`. Print list of skipped tickers (no DART match) to stdout after the loop. Print summary of output rows and bytes at end.

---

### `src/02_build_compliance.py` (transform/validator script, file I/O)

**Analog:** `src/00b_build_universe_public.py`

**Module docstring pattern** (`src/01_bloomberg_pull.py` lines 1–15 — same across all scripts):
```python
"""
Compliance classification for Korea Discount study.

READS: data/raw/krx/compliance_coded.csv (hand-coded by researcher)
OUTPUTS:
  data/processed/compliance.csv - three-way classification (0/1/2), all firms
  data/processed/events.csv - disclosure dates for compliant firms (codes 1 and 2)

Run from project root:
    python src/02_build_compliance.py
"""
```

**Imports + sys.path + logging setup** (`src/00b_build_universe_public.py` lines 17–36):
```python
import logging
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

import pandas as pd

from utils.stats import cohens_kappa

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)
```

**Path constants** (pattern from `src/01_bloomberg_pull.py` lines 49–53):
```python
COMPLIANCE_PATH = os.path.join(PROJECT_ROOT, "data", "raw", "krx", "compliance_coded.csv")
COMPLIANCE_R2_PATH = os.path.join(PROJECT_ROOT, "data", "raw", "krx", "compliance_coded_r2.csv")
PROCESSED_DIR = os.path.join(PROJECT_ROOT, "data", "processed")
COMPLIANCE_OUT = os.path.join(PROCESSED_DIR, "compliance.csv")
EVENTS_OUT = os.path.join(PROCESSED_DIR, "events.csv")
```

**Missing-input guard** (`src/01_bloomberg_pull.py` lines 87–93 — exact same structure):
```python
if not os.path.exists(COMPLIANCE_PATH):
    print(
        f"Error: {COMPLIANCE_PATH} not found.\n"
        "Hand-code KRX disclosures and save as data/raw/krx/compliance_coded.csv\n"
        "Required columns: ticker (6-digit), compliance_code (0/1/2), disclosure_date (YYYY-MM-DD)",
        file=sys.stderr,
    )
    sys.exit(1)
```

**Read, validate schema, filter, save** (derived from `src/00b_build_universe_public.py` lines 61–96 structure):
```python
def main():
    os.makedirs(PROCESSED_DIR, exist_ok=True)

    df = pd.read_csv(COMPLIANCE_PATH, dtype={"ticker": str, "compliance_code": int})
    # Schema validation
    required = {"ticker", "compliance_code", "disclosure_date"}
    missing_cols = required - set(df.columns)
    if missing_cols:
        print(f"Error: compliance_coded.csv missing columns: {missing_cols}", file=sys.stderr)
        sys.exit(1)

    log.info("Loaded %d firms from %s.", len(df), COMPLIANCE_PATH)

    # compliance.csv: all firms
    df.to_csv(COMPLIANCE_OUT, index=False)
    log.info("Saved compliance.csv: %d rows.", len(df))

    # events.csv: codes 1 and 2 only
    events = df[df["compliance_code"].isin([1, 2])].copy()
    events.to_csv(EVENTS_OUT, index=False)
    log.info("Saved events.csv: %d rows (codes 1 and 2).", len(events))

    # Optional kappa check — does not block execution
    if os.path.exists(COMPLIANCE_R2_PATH):
        r2 = pd.read_csv(COMPLIANCE_R2_PATH, dtype={"ticker": str, "compliance_code": int})
        merged = df.merge(r2[["ticker", "compliance_code"]], on="ticker",
                         suffixes=("_r1", "_r2"))
        kappa, pval = cohens_kappa(
            merged["compliance_code_r1"].tolist(),
            merged["compliance_code_r2"].tolist(),
            labels=[0, 1, 2],
        )
        print(f"Inter-rater Cohen's kappa = {kappa:.3f} (p = {pval:.4f})")
    else:
        log.info("No compliance_coded_r2.csv found; skipping kappa check.")
```

---

### `src/03_merge_covariates.py` (transform/merge script, batch transform)

**Analog:** `src/01b_public_pull.py` (multi-stage structure) + `src/01_bloomberg_pull.py` (path constants pattern)

**Module docstring**:
```python
"""
Build master sample dataset for Korea Discount study.

READS:
  data/processed/compliance.csv
  data/raw/bloomberg/snapshot_2023.csv
  data/raw/bloomberg/roe_panel.csv
  data/raw/kftc/KFTC_large_business_groups_2026.csv
  data/raw/dart/controlling_shareholder.csv

OUTPUTS:
  data/processed/sample.csv — 25-column master dataset, winsorized

Run from project root:
    python src/03_merge_covariates.py
"""
```

**Imports + sys.path + logging** (`src/01b_public_pull.py` lines 26–43 — exact pattern):
```python
import logging
import os
import sys

import pandas as pd
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.stats import winsorize

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)
```

**Path constants** (`src/01_bloomberg_pull.py` lines 49–53):
```python
COMPLIANCE_PATH  = os.path.join(PROJECT_ROOT, "data", "processed", "compliance.csv")
SNAPSHOT_PATH    = os.path.join(PROJECT_ROOT, "data", "raw", "bloomberg", "snapshot_2023.csv")
ROE_PANEL_PATH   = os.path.join(PROJECT_ROOT, "data", "raw", "bloomberg", "roe_panel.csv")
KFTC_PATH        = os.path.join(PROJECT_ROOT, "data", "raw", "kftc", "KFTC_large_business_groups_2026.csv")
DART_PATH        = os.path.join(PROJECT_ROOT, "data", "raw", "dart", "controlling_shareholder.csv")
PROCESSED_DIR    = os.path.join(PROJECT_ROOT, "data", "processed")
SAMPLE_OUT       = os.path.join(PROCESSED_DIR, "sample.csv")
```

**Bloomberg rename map** (D-13, verified from `snapshot_2023.csv` headers):
```python
BBG_RENAME = {
    "PX_TO_BOOK_RATIO":       "pbr",
    "PE_RATIO":               "pe_ratio",
    "RETURN_COM_EQY":         "roe_fy23",
    "RETURN_ON_ASSET":        "roa",
    "EQY_FLOAT_PCT":          "foreign_pct",
    "CUR_MKT_CAP":            "mkt_cap",
    "EQY_DVD_YLD_IND":        "dvd_yield",
    "TOT_DEBT_TO_TOT_EQY":    "debt_equity",
    "BS_TOT_ASSET":           "total_assets",
    "SALES_GROWTH":           "sales_growth",
    "CASH_AND_NEAR_CASH_ITEM":"cash",
    "DVD_SH_12M":             "dvd_sh_12m",
}

WINSORIZE_COLS = [
    "pbr", "pe_ratio", "roe_fy23", "roa", "foreign_pct", "mkt_cap",
    "dvd_yield", "debt_equity", "total_assets", "sales_growth", "cash",
    "dvd_sh_12m", "roe_2019", "roe_2020", "roe_2021", "roe_2022", "roe_2023",
    "controlling_pct_largest", "controlling_pct_group",
]

FINAL_COLS = [
    "ticker", "name", "sector", "pbr", "pe_ratio", "roe_fy23", "roa",
    "foreign_pct", "mkt_cap", "dvd_yield", "debt_equity", "total_assets",
    "sales_growth", "cash", "dvd_sh_12m",
    "roe_2019", "roe_2020", "roe_2021", "roe_2022", "roe_2023",
    "chaebol", "controlling_pct_largest", "controlling_pct_group",
    "compliance_code", "disclosure_date",
]
```

**ROE panel pivot wide** (from RESEARCH.md Pattern 5 — no codebase analog):
```python
def build_roe_wide(roe_panel_path):
    roe = pd.read_csv(roe_panel_path, dtype={"ticker": str})
    roe_annual = (
        roe.dropna(subset=["roe"])
        .sort_values("year")
        .groupby(["ticker", "year"])["roe"]
        .last()
        .reset_index()
    )
    roe_wide = roe_annual.pivot(index="ticker", columns="year", values="roe")
    roe_wide.columns = [f"roe_{int(yr)}" for yr in roe_wide.columns]
    for yr in [2019, 2020, 2021, 2022, 2023]:
        if f"roe_{yr}" not in roe_wide.columns:
            roe_wide[f"roe_{yr}"] = float("nan")
    return roe_wide.reset_index()
```

**KFTC chaebol matching with alias table** (from RESEARCH.md Pattern 4 — no codebase analog):
```python
LATIN_TO_KFTC = {
    "SK": "에스케이", "LG": "엘지", "HD": "에이치디현대",
    "KT&G": "케이티앤지", "KT": "케이티", "GS": "지에스",
    "CJ": "씨제이", "LS": "엘에스", "LX": "엘엑스",
    "DL": "디엘", "DB": "디비", "SM": "에스엠",
    "HDC": "에이치디씨", "OCI": "오씨아이", "HMM": "에이치엠엠",
    "KG": "케이지", "KCC": "케이씨씨",
}
STRIP_SUFFIXES = ["주식회사", "(주)", "그룹", "홀딩스", "지주", "코리아"]

def match_chaebol(firm_name, kftc_korean_names):
    if not firm_name or not isinstance(firm_name, str):
        return None
    # Latin-prefix alias lookup first (KT&G before KT — longer match wins)
    for prefix in sorted(LATIN_TO_KFTC, key=len, reverse=True):
        if firm_name.startswith(prefix):
            kftc_name = LATIN_TO_KFTC[prefix]
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

**Multi-stage main function** (`src/01b_public_pull.py` lines 95–130 — same logging pattern per stage):
```python
def main():
    os.makedirs(PROCESSED_DIR, exist_ok=True)

    # 1. Load compliance as merge base (left table — D-16)
    compliance = pd.read_csv(COMPLIANCE_PATH, dtype={"ticker": str})

    # 2. Load Bloomberg snapshot; rename columns
    snap = pd.read_csv(SNAPSHOT_PATH, dtype={"ticker": str})
    snap = snap.rename(columns=BBG_RENAME)

    # 3. Build ROE wide
    roe_wide = build_roe_wide(ROE_PANEL_PATH)

    # 4. KFTC chaebol flag
    kftc = pd.read_csv(KFTC_PATH)
    kftc_names = set(kftc["Group_Name_Korean"].dropna())
    # ... match and print unmatched stdout report

    # 5. DART controlling shareholder
    dart = pd.read_csv(DART_PATH, dtype={"ticker": str})

    # 6. Left-join on ticker (compliance as base)
    df = compliance.merge(snap, on="ticker", how="left")
    df = df.merge(roe_wide, on="ticker", how="left")
    df = df.merge(dart, on="ticker", how="left")
    # chaebol column already built on snap+compliance df

    # 7. Winsorize continuous columns
    for col in WINSORIZE_COLS:
        if col in df.columns:
            df[col] = winsorize(df[col])

    # 8. Print missingness report (D-17)
    log.info("=== Missingness report ===")
    for col in df.columns:
        n_nan = df[col].isna().sum()
        if n_nan > 0:
            log.info("  %s: %d NaN", col, n_nan)

    # 9. Reorder columns and save
    df = df[[c for c in FINAL_COLS if c in df.columns]]
    df.to_csv(SAMPLE_OUT, index=False)
    log.info("Saved sample.csv: %d rows x %d columns.", len(df), len(df.columns))


if __name__ == "__main__":
    main()
```

**Ticker format normalization** (D-19 — strip `.KS` before any join; pattern from `src/01b_public_pull.py` line 76):
```python
# Strip .KS suffix (returns_panel uses Yahoo Finance format; all internal joins use bare 6-digit)
df["ticker"] = df["ticker"].str.replace(r"\.KS$", "", regex=True)
```

---

## Shared Patterns

### Module header (docstring → imports → sys.path → logging → PROJECT_ROOT → path constants)

**Source:** `src/01_bloomberg_pull.py` lines 1–53 and `src/01b_public_pull.py` lines 1–50
**Apply to:** All three new scripts — `01c_dart_pull.py`, `02_build_compliance.py`, `03_merge_covariates.py`

The consistent ordering is:
1. Module-level docstring with READS / OUTPUTS / "Run from project root" instructions
2. stdlib imports
3. `sys.path.insert(0, ...)` to make `utils/` importable
4. third-party imports (`pandas`, etc.)
5. `PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))`
6. `from utils.X import Y`
7. `logging.basicConfig(...)` then `log = logging.getLogger(__name__)`
8. All file paths as module-level `*_PATH` / `*_DIR` constants

### Missing-input guard (sys.exit on absent file)

**Source:** `src/01_bloomberg_pull.py` lines 87–93; `src/01b_public_pull.py` lines 63–69
**Apply to:** `01c_dart_pull.py` (universe_raw.csv guard), `02_build_compliance.py` (compliance_coded.csv guard)

Pattern: `if not os.path.exists(PATH): print(..., file=sys.stderr); sys.exit(1)`

### Logging style (structured, with counts and bytes)

**Source:** `src/01_bloomberg_pull.py` lines 42–47 and lines 188–196
**Apply to:** All three new scripts

Pattern: `log.info("Stage label: %d rows.", len(df))` and final verification loop over output paths with `os.path.getsize()`.

### `os.makedirs(dir, exist_ok=True)` at start of main()

**Source:** `src/01_bloomberg_pull.py` line 181; `src/00_build_universe.py` line 138
**Apply to:** `01c_dart_pull.py` (create `data/raw/dart/`), `02_build_compliance.py` (create `data/processed/`), `03_merge_covariates.py` (create `data/processed/`)

### `utils.stats.winsorize()` call pattern

**Source:** `utils/stats.py` lines 16–39
**Apply to:** `src/03_merge_covariates.py` — winsorize all columns in `WINSORIZE_COLS` list, one column at a time, replacing in-place with `df[col] = winsorize(df[col])`. Signature: `winsorize(arr, lower=0.01, upper=0.01)`. Returns `np.ndarray`; assign back to DataFrame column.

### `utils.stats.cohens_kappa()` call pattern

**Source:** `utils/stats.py` lines 42–73
**Apply to:** `src/02_build_compliance.py` — conditional call only when `compliance_coded_r2.csv` exists. Signature: `cohens_kappa(rater1_list, rater2_list, labels=[0, 1, 2])`. Returns `(kappa: float, pvalue: float)`.

---

## No Analog Found

Files or sub-patterns with no close match in the codebase (planner should use RESEARCH.md patterns directly):

| Sub-pattern | Used In | Reason |
|-------------|---------|--------|
| DART `corpCode.xml` download + XML parse | `01c_dart_pull.py` | No external API calls with XML parsing exist in codebase |
| DART `hyslrSttus.json` per-firm loop | `01c_dart_pull.py` | No REST API iteration loops in codebase; use RESEARCH.md Pattern 3 verbatim |
| KFTC name-prefix matching + alias table | `03_merge_covariates.py` | No string matching / Korean text processing in codebase; use RESEARCH.md Pattern 4 verbatim |
| ROE panel pivot wide | `03_merge_covariates.py` | No pivot operations in codebase; use RESEARCH.md Pattern 5 verbatim |
| `python-dotenv` `load_dotenv()` + `os.environ` | `01c_dart_pull.py` | `.env` reading not used in any existing script |

---

## Metadata

**Analog search scope:** `src/`, `utils/`
**Files scanned:** `src/00_build_universe.py`, `src/00b_build_universe_public.py`, `src/01_bloomberg_pull.py`, `src/01b_public_pull.py`, `utils/stats.py`
**Pattern extraction date:** 2026-05-08
