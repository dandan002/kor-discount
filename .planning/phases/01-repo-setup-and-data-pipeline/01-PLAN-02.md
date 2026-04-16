---
phase: 01-repo-setup-and-data-pipeline
plan: 02
type: execute
wave: 2
depends_on:
  - "01-PLAN-01"
files_modified:
  - src/data/build_panel.py
  - data/processed/panel.parquet
autonomous: true
requirements:
  - DATA-01
  - DATA-02
  - DATA-04
  - DATA-05

must_haves:
  truths:
    - "Running `python src/data/build_panel.py` exits 0 and produces data/processed/panel.parquet"
    - "panel.parquet has exactly four columns: date (datetime64), country (object/string), pb (float64), pe (float64)"
    - "panel.parquet contains exactly 4 country values: KOSPI, TOPIX, SP500, MSCI_EM"
    - "panel.parquet date column contains month-end dates (last calendar day of each month)"
    - "All NaN values in the panel are documented — only KOSPI PE rows 2004-01 through 2004-04 are permitted to be NaN"
    - "Script logs a WARNING when it encounters the known KOSPI PE gap (2004-01 to 2004-04)"
  artifacts:
    - path: "src/data/build_panel.py"
      provides: "Canonical data pipeline script — reads 8 raw CSVs, outputs panel.parquet"
      contains: "import config"
    - path: "data/processed/panel.parquet"
      provides: "Canonical panel dataset for all downstream analyses"
      min_rows: 1000
  key_links:
    - from: "data/raw/kospi_pb_2004_2026.csv"
      to: "data/processed/panel.parquet"
      via: "build_panel.py reads raw CSV, converts to month-end dates, stacks into long format"
      pattern: "pd.read_csv.*kospi_pb"
    - from: "config.py"
      to: "src/data/build_panel.py"
      via: "import config; uses config.RAW_DIR, config.PROCESSED_DIR, config.KOSPI_PE_SERIES_START"
      pattern: "import config"
---

<objective>
Build `src/data/build_panel.py` — the canonical data pipeline script that reads all 8 raw Bloomberg CSVs (pb and pe for KOSPI, TOPIX, SP500, MSCI_EM) and produces `data/processed/panel.parquet` in long format.

Purpose: This script is the single reproducible transformation from immutable raw data to the analysis-ready panel. All downstream phases (descriptive analysis, event study, panel OLS, synthetic control) read exclusively from `panel.parquet`. Correctness here is the critical path.

Output: `src/data/build_panel.py` (the script) and `data/processed/panel.parquet` (the artifact produced by running it).
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/ROADMAP.md
@config.py
@src/data/pull_bloomberg.py
@data/raw/MANIFEST.md

<interfaces>
<!-- Key contracts the executor must implement against. -->

From config.py (created in Plan 01):
```python
import datetime
from pathlib import Path

STEWARDSHIP_CODE_DATE: datetime.date = datetime.date(2014, 2, 1)
CGC_DATE:              datetime.date = datetime.date(2015, 6, 1)
TSE_PB_REFORM_DATE:    datetime.date = datetime.date(2023, 3, 1)
COUNTRIES: list[str] = ["KOSPI", "TOPIX", "SP500", "MSCI_EM"]
RAW_DIR:      Path  # absolute path to data/raw/
PROCESSED_DIR:Path  # absolute path to data/processed/
KOSPI_PE_SERIES_START: datetime.date = datetime.date(2004, 5, 1)
```

Raw CSV file naming convention (from pull_bloomberg.py):
- `{index}_{metric}_{start_year}_{end_year}.csv`
- Two columns: `date,{metric}` — e.g., `date,pb` or `date,pe`
- Date format: YYYY-MM-DD mid-month (e.g., 2004-01-16)
- Files used by build_panel.py:
    kospi_pb_2004_2026.csv     topix_pb_2004_2026.csv
    kospi_pe_2004_2026.csv     topix_pe_2004_2026.csv
    sp500_pb_2004_2026.csv     msci_em_pb_2004_2026.csv
    sp500_pe_2004_2026.csv     msci_em_pe_2004_2026.csv

Known gap: kospi_pe_2004_2026.csv starts 2004-05-16 (not 2004-01-16).
KOSPI PB starts 2004-01-16. So KOSPI rows 2004-01 through 2004-04 will have NaN pe.
</interfaces>
</context>

<tasks>

<task type="auto">
  <name>Task 1: Implement build_panel.py</name>
  <files>src/data/build_panel.py</files>
  <read_first>
    - config.py (for RAW_DIR, PROCESSED_DIR, KOSPI_PE_SERIES_START, COUNTRIES — must import from here, not redefine)
    - src/data/pull_bloomberg.py (for file naming convention: `{index}_{metric}_2004_2026.csv`)
    - data/raw/kospi_pb_2004_2026.csv (confirm column names: `date,pb` — two cols, no header surprises)
    - data/raw/kospi_pe_2004_2026.csv (confirm gap starts at 2004-05-16 and column name is `pe`)
    - data/raw/MANIFEST.md (confirm all 8 required files are listed)
  </read_first>
  <action>
Create `/Users/dandan/Desktop/Projects/kor-discount/src/data/build_panel.py` implementing the following exact pipeline:

**Imports and constants:**
```python
import logging
import sys
import warnings
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import config  # MUST import config — never redefine paths or event dates here
```

**Logging setup:** Use `logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")`.

**INDEX_MAP:** Map internal country labels to raw file prefixes:
```python
INDEX_MAP = {
    "KOSPI":   "kospi",
    "TOPIX":   "topix",
    "SP500":   "sp500",
    "MSCI_EM": "msci_em",
}
```

**load_series(prefix, metric) function:**
- Reads `config.RAW_DIR / f"{prefix}_{metric}_2004_2026.csv"`
- Parses `date` column with `pd.to_datetime(..., format="%Y-%m-%d")`
- Sets `date` as index
- Returns the single-column Series (named `metric`)
- Raises `FileNotFoundError` with a clear message if the file is missing

**build_panel() function — main pipeline:**

Step 1 — Load all 8 series into a dict keyed by `(country, metric)`.

Step 2 — For each country, merge pb and pe on date index using `pd.concat([pb_series, pe_series], axis=1, join="outer")` to preserve all dates from either series.

Step 3 — Convert mid-month dates to month-end using `pd.offsets.MonthEnd(0)`:
```python
df.index = df.index + pd.offsets.MonthEnd(0)
```
This maps 2004-01-16 → 2004-01-31, 2004-02-16 → 2004-02-28, etc. Apply to each country DataFrame before stacking.

Step 4 — KOSPI PE gap handling: After merging KOSPI pb and pe, check rows where `pe` is NaN AND `pb` is NOT NaN. These rows correspond to the known 2004-01 through 2004-04 gap. Log a WARNING:
```python
kospi_pe_gap = kospi_df[kospi_df["pe"].isna() & kospi_df["pb"].notna()]
if len(kospi_pe_gap) > 0:
    logging.warning(
        "KNOWN LIMITATION: KOSPI PE data starts %s. "
        "%d rows (2004-01 through 2004-04) have NaN pe. "
        "See config.KOSPI_PE_SERIES_START for documentation.",
        config.KOSPI_PE_SERIES_START.isoformat(),
        len(kospi_pe_gap),
    )
```

Step 5 — Validate that the ONLY NaN values in the entire panel are the documented KOSPI PE gap rows:
```python
# Build long-format panel first
frames = []
for country, prefix in INDEX_MAP.items():
    df = country_dfs[country].copy()
    df["country"] = country
    df = df.reset_index().rename(columns={"index": "date"})
    frames.append(df[["date", "country", "pb", "pe"]])

panel = pd.concat(frames, ignore_index=True).sort_values(["date", "country"]).reset_index(drop=True)

# Validate NaN — only KOSPI PE rows 2004-01 to 2004-04 are permitted
nan_mask = panel.isna().any(axis=1)
nan_rows = panel[nan_mask]
invalid_nans = nan_rows[
    ~((nan_rows["country"] == "KOSPI") &
      (nan_rows["date"] < pd.Timestamp(config.KOSPI_PE_SERIES_START)) &
      (nan_rows["pb"].notna()))
]
if len(invalid_nans) > 0:
    logging.error("UNDOCUMENTED NaN values found in panel:")
    logging.error(invalid_nans.to_string())
    raise ValueError(
        f"build_panel.py: {len(invalid_nans)} undocumented NaN rows. "
        "Inspect the error output above and update config.py if this is a known gap."
    )
```

Step 6 — Ensure correct dtypes:
- `date` column: `pd.Timestamp` (already from pd.to_datetime)
- `country` column: keep as string (object dtype)
- `pb`, `pe`: float64

Step 7 — Write parquet:
```python
config.PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
out_path = config.PROCESSED_DIR / "panel.parquet"
panel.to_parquet(out_path, engine="pyarrow", index=False)
logging.info("Wrote %d rows to %s", len(panel), out_path)
```

Step 8 — Print summary table to stdout after writing:
```python
print("\n=== Panel Summary ===")
print(f"Rows:      {len(panel)}")
print(f"Date range: {panel['date'].min().date()} to {panel['date'].max().date()}")
print(f"Countries:  {sorted(panel['country'].unique().tolist())}")
print(f"NaN pe:    {panel['pe'].isna().sum()} rows (expected: 4 KOSPI rows)")
print(f"NaN pb:    {panel['pb'].isna().sum()} rows (expected: 0)")
print("Output:   ", out_path)
```

**`if __name__ == "__main__":` block:** calls `build_panel()`, catches exceptions, prints clean error message, exits with `sys.exit(1)` on failure.

Do NOT hardcode any paths. All paths come from `config.RAW_DIR` and `config.PROCESSED_DIR`. Do NOT redefine any constants that already exist in config.py.
  </action>
  <verify>
    <automated>cd /Users/dandan/Desktop/Projects/kor-discount && python src/data/build_panel.py</automated>
  </verify>
  <acceptance_criteria>
    - `python src/data/build_panel.py` exits with code 0
    - `ls data/processed/panel.parquet` shows the file exists
    - `python -c "import pandas as pd; df = pd.read_parquet('data/processed/panel.parquet'); print(list(df.columns))"` prints `['date', 'country', 'pb', 'pe']`
    - `python -c "import pandas as pd; df = pd.read_parquet('data/processed/panel.parquet'); print(sorted(df['country'].unique().tolist()))"` prints `['KOSPI', 'MSCI_EM', 'SP500', 'TOPIX']`
    - `python -c "import pandas as pd; df = pd.read_parquet('data/processed/panel.parquet'); print(df['pe'].isna().sum())"` prints `4` (exactly 4 NaN pe rows)
    - `python -c "import pandas as pd; df = pd.read_parquet('data/processed/panel.parquet'); print(df['pb'].isna().sum())"` prints `0`
    - `python -c "import pandas as pd; df = pd.read_parquet('data/processed/panel.parquet'); kospi_nan = df[(df['country']=='KOSPI') & df['pe'].isna()]; print(kospi_nan['date'].dt.to_period('M').astype(str).tolist())"` prints the 4 months `['2004-01', '2004-02', '2004-03', '2004-04']`
    - `python -c "import pandas as pd; df = pd.read_parquet('data/processed/panel.parquet'); last_day = df['date'].dt.is_month_end.all(); print(last_day)"` prints `True` (all dates are month-end)
    - `grep "import config" src/data/build_panel.py` returns a match
    - `grep "KOSPI_PE_SERIES_START" src/data/build_panel.py` returns a match (uses config constant)
    - Script output to stdout contains the line `WARNING: KNOWN LIMITATION: KOSPI PE data starts`
  </acceptance_criteria>
  <done>build_panel.py creates data/processed/panel.parquet with schema (date, country, pb, pe); exactly 4 NaN pe rows for KOSPI 2004-01 to 2004-04; all dates are month-end; no undocumented NaN values; script exits 0.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| data/raw/ CSVs → build_panel.py | Raw files are the trust root; script must not silently ignore malformed or truncated files |
| build_panel.py → data/processed/panel.parquet | Output parquet is consumed by all downstream analyses; silent NaN propagation here corrupts all results |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-01-05 | Tampering | Raw CSV files mutated post-ingestion | mitigate | data/raw/ is version-controlled (git); any mutation is visible in `git diff data/raw/`; MANIFEST.md records vintage date 2026-04-16 as the reference point |
| T-01-06 | Tampering | panel.parquet overwritten with stale or corrupted data | mitigate | build_panel.py raises ValueError on undocumented NaN; if validation fails, parquet is not written (write happens after validation in Step 7); running script always regenerates from raw |
| T-01-07 | Information Disclosure | Reproducibility break from non-deterministic sort | mitigate | panel is sorted by `["date", "country"]` with `reset_index(drop=True)` — deterministic output regardless of OS or pandas version |
| T-01-08 | Denial of Service | Missing raw CSV file causes silent partial panel | mitigate | `load_series()` raises `FileNotFoundError` with a clear message if any of the 8 required files is missing; script exits 1 |
| T-01-09 | Repudiation | No audit trail for known data gaps | mitigate | KOSPI PE gap documented in three places: MANIFEST.md, config.KOSPI_PE_SERIES_START, and WARNING log line printed at runtime |
</threat_model>

<verification>
After build_panel.py runs successfully:
1. `python -c "import pandas as pd; df = pd.read_parquet('data/processed/panel.parquet'); print(df.dtypes)"` shows `date: datetime64[ns]`, `country: object`, `pb: float64`, `pe: float64`
2. `python -c "import pandas as pd; df = pd.read_parquet('data/processed/panel.parquet'); print(df.groupby('country').size())"` shows equal counts per country (KOSPI count same as others — NaN rows ARE included)
3. `python -c "import pandas as pd; df = pd.read_parquet('data/processed/panel.parquet'); print(df['date'].min(), df['date'].max())"` prints a date range starting 2004-01-31 (or similar month-end) through late 2026
4. Panel row count is approximately 264 months × 4 countries = ~1056 rows (may vary slightly based on Bloomberg vintage date coverage)
</verification>

<success_criteria>
- `python src/data/build_panel.py` exits 0
- panel.parquet exists at data/processed/panel.parquet
- Schema: exactly 4 columns (date, country, pb, pe)
- Exactly 4 country values: KOSPI, TOPIX, SP500, MSCI_EM
- All dates are month-end
- Exactly 4 NaN pe rows (KOSPI 2004-01 to 2004-04)
- Zero NaN pb rows
- WARNING log line printed for KOSPI PE gap
- No undocumented NaN values (validation raises ValueError if found)
</success_criteria>

<output>
After completion, create `.planning/phases/01-repo-setup-and-data-pipeline/01-02-SUMMARY.md` following the summary template at `@$HOME/.claude/get-shit-done/templates/summary.md`.
</output>
