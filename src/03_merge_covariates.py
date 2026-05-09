"""
Build master sample dataset for Korea Discount study.

READS:
  data/processed/compliance.csv        (from src/02_build_compliance.py)
  data/raw/bloomberg/snapshot_2023.csv (Bloomberg cross-section)
  data/raw/bloomberg/roe_panel.csv     (Bloomberg ROE panel, long format)
  data/raw/kftc/KFTC_large_business_groups_2026.csv (KFTC chaebol list)
  data/raw/dart/controlling_shareholder.csv (from src/01c_dart_pull.py)

OUTPUTS:
  data/processed/sample.csv — 25-column master dataset, winsorized

Run from project root:
    python src/03_merge_covariates.py
"""

import logging
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.stats import winsorize

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Path constants
# ---------------------------------------------------------------------------
COMPLIANCE_PATH = os.path.join(PROJECT_ROOT, "data", "processed", "compliance.csv")
SNAPSHOT_PATH = os.path.join(PROJECT_ROOT, "data", "raw", "bloomberg", "snapshot_2023.csv")
ROE_PANEL_PATH = os.path.join(PROJECT_ROOT, "data", "raw", "bloomberg", "roe_panel.csv")
KFTC_PATH = os.path.join(PROJECT_ROOT, "data", "raw", "kftc", "KFTC_large_business_groups_2026.csv")
DART_PATH = os.path.join(PROJECT_ROOT, "data", "raw", "dart", "controlling_shareholder.csv")
UNIVERSE_PATH = os.path.join(PROJECT_ROOT, "data", "raw", "universe_raw.csv")
PROCESSED_DIR = os.path.join(PROJECT_ROOT, "data", "processed")
SAMPLE_OUT = os.path.join(PROCESSED_DIR, "sample.csv")

# ---------------------------------------------------------------------------
# Bloomberg rename map — D-13 (verified from snapshot_2023.csv headers)
# ---------------------------------------------------------------------------
BBG_RENAME = {
    "PX_TO_BOOK_RATIO": "pbr",
    "PE_RATIO": "pe_ratio",
    "RETURN_COM_EQY": "roe_fy23",
    "RETURN_ON_ASSET": "roa",
    "EQY_FLOAT_PCT": "foreign_pct",
    "CUR_MKT_CAP": "mkt_cap",
    "EQY_DVD_YLD_IND": "dvd_yield",
    "TOT_DEBT_TO_TOT_EQY": "debt_equity",
    "BS_TOT_ASSET": "total_assets",
    "SALES_GROWTH": "sales_growth",
    "CASH_AND_NEAR_CASH_ITEM": "cash",
    "DVD_SH_12M": "dvd_sh_12m",
}

# ---------------------------------------------------------------------------
# Columns to winsorize — D-18 (continuous Bloomberg + ROE + controlling share)
# ---------------------------------------------------------------------------
WINSORIZE_COLS = [
    "pbr", "pe_ratio", "roe_fy23", "roa", "foreign_pct", "mkt_cap",
    "dvd_yield", "debt_equity", "total_assets", "sales_growth", "cash",
    "dvd_sh_12m",
    "roe_2019", "roe_2020", "roe_2021", "roe_2022", "roe_2023",
    "controlling_pct_largest", "controlling_pct_group",
]

# ---------------------------------------------------------------------------
# Locked 25-column order — D-12
# ---------------------------------------------------------------------------
FINAL_COLS = [
    "ticker", "name", "sector",
    "pbr", "pe_ratio", "roe_fy23", "roa", "foreign_pct", "mkt_cap",
    "dvd_yield", "debt_equity", "total_assets", "sales_growth", "cash",
    "dvd_sh_12m",
    "roe_2019", "roe_2020", "roe_2021", "roe_2022", "roe_2023",
    "chaebol",
    "controlling_pct_largest", "controlling_pct_group",
    "compliance_code", "disclosure_date",
]

# ---------------------------------------------------------------------------
# KFTC alias table — Latin-prefix firms whose KFTC group name is Hangul
# Sorted by length descending in matching so KT&G matches before KT.
# ---------------------------------------------------------------------------
LATIN_TO_KFTC = {
    "KT&G": "케이티앤지",
    "KT": "케이티",
    "SK": "에스케이",
    "LG": "엘지",
    "HD": "에이치디현대",
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


# ---------------------------------------------------------------------------
# ROE panel pivot — Pattern 5 from research
# ---------------------------------------------------------------------------
def build_roe_wide(roe_panel_path):
    """Pivot long-format ROE panel to wide (one row per ticker, roe_YYYY columns).

    Handles duplicate (ticker, year) pairs by keeping the last non-null value.
    Guarantees all five year columns roe_2019 through roe_2023 exist, filling
    with NaN for years not present in the data.
    """
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


# ---------------------------------------------------------------------------
# KFTC chaebol matching — Pattern 4 from research
# ---------------------------------------------------------------------------
def match_chaebol(firm_name, kftc_korean_names):
    """Return matched KFTC group name or None.

    Uses Latin-prefix alias table first (longer prefixes checked first so
    KT&G matches before KT), then Korean-prefix matching with corporate
    suffix stripping.
    """
    if not firm_name or not isinstance(firm_name, str):
        return None
    # Latin-prefix lookup — sort by length descending so KT&G matches before KT
    for prefix in sorted(LATIN_TO_KFTC, key=len, reverse=True):
        if firm_name.startswith(prefix):
            kftc_name = LATIN_TO_KFTC[prefix]
            if kftc_name in kftc_korean_names:
                return kftc_name
    # Korean-prefix match: strip common suffixes then prefix-match
    cleaned = firm_name
    for s in STRIP_SUFFIXES:
        cleaned = cleaned.replace(s, "")
    cleaned = cleaned.strip()
    for kname in kftc_korean_names:
        if cleaned.startswith(kname):
            return kname
    return None


# ---------------------------------------------------------------------------
# Main merge pipeline
# ---------------------------------------------------------------------------
def main():
    # Step 0: Ensure output directory exists
    os.makedirs(PROCESSED_DIR, exist_ok=True)

    # Step 1: Guard on compliance.csv
    if not os.path.exists(COMPLIANCE_PATH):
        print(
            f"Error: {COMPLIANCE_PATH} not found.\n"
            "Run src/02_build_compliance.py first.",
            file=sys.stderr,
        )
        sys.exit(1)

    # Step 2: Load compliance as left base (D-16)
    compliance = pd.read_csv(COMPLIANCE_PATH, dtype={"ticker": str})
    log.info("Compliance base: %d firms.", len(compliance))

    # Step 3: Load Bloomberg snapshot and rename columns (D-13)
    snap = pd.read_csv(SNAPSHOT_PATH, dtype={"ticker": str})
    snap = snap.rename(columns=BBG_RENAME)
    log.info("Snapshot loaded: %d rows.", len(snap))

    # Step 4: Build ROE wide (D-14)
    roe_wide = build_roe_wide(ROE_PANEL_PATH)
    log.info(
        "ROE wide: %d rows, columns: %s",
        len(roe_wide),
        [c for c in roe_wide.columns if c.startswith("roe_")],
    )

    # Step 5: KFTC chaebol flag (D-09/D-10/D-11)
    kftc = pd.read_csv(KFTC_PATH)
    kftc_names = set(kftc["Group_Name_Korean"].dropna().str.strip())

    universe = pd.read_csv(UNIVERSE_PATH, dtype={"ticker": str})[
        ["ticker", "name", "sector"]
    ]
    universe["chaebol"] = universe["name"].apply(
        lambda n: 1 if match_chaebol(n, kftc_names) else 0
    )

    # Print unmatched KFTC groups for manual review (D-11)
    matched_groups = {
        match_chaebol(n, kftc_names)
        for n in universe["name"].dropna()
        if match_chaebol(n, kftc_names)
    }
    unmatched_groups = kftc_names - matched_groups
    print(f"KFTC groups with no universe match ({len(unmatched_groups)}): {sorted(unmatched_groups)}")
    chaebol_count = universe["chaebol"].sum()
    log.info("Chaebol firms matched: %d of %d.", chaebol_count, len(universe))

    # Step 6: DART controlling shareholder
    dart = None
    if os.path.exists(DART_PATH):
        dart = pd.read_csv(DART_PATH, dtype={"ticker": str})
        log.info("DART loaded: %d rows.", len(dart))
    else:
        log.warning(
            "DART file not found at %s; controlling_pct columns will be NaN.",
            DART_PATH,
        )

    # Step 7: Five-way left-join (compliance as left base, all how="left" on "ticker")
    df = compliance.merge(universe, on="ticker", how="left")
    df = df.merge(
        snap[["ticker"] + [c for c in snap.columns if c in BBG_RENAME.values()]],
        on="ticker",
        how="left",
    )
    df = df.merge(roe_wide, on="ticker", how="left")
    if dart is not None:
        df = df.merge(dart, on="ticker", how="left")
    else:
        df["controlling_pct_largest"] = float("nan")
        df["controlling_pct_group"] = float("nan")

    # Step 8: Winsorize continuous columns (D-18)
    for col in WINSORIZE_COLS:
        if col in df.columns:
            df[col] = winsorize(df[col])

    # Step 9: Missingness report to stdout (D-17)
    print("=== Missingness report ===")
    for col in FINAL_COLS:
        if col in df.columns:
            n_nan = df[col].isna().sum()
            if n_nan > 0:
                print(f"  {col}: {n_nan} NaN ({100 * n_nan / len(df):.1f}%)")
        else:
            print(f"  {col}: {len(df)} NaN (column missing)")
    print(f"Total rows: {len(df)}")

    # Step 10: Reorder columns and save
    present_cols = [c for c in FINAL_COLS if c in df.columns]
    df = df[present_cols]
    df.to_csv(SAMPLE_OUT, index=False)
    log.info("Saved sample.csv: %d rows x %d columns.", len(df), len(df.columns))

    # Step 11: Final verification (path + size)
    if os.path.exists(SAMPLE_OUT):
        log.info("%s (%d bytes)", SAMPLE_OUT, os.path.getsize(SAMPLE_OUT))
    else:
        log.error("MISSING: %s", SAMPLE_OUT)


if __name__ == "__main__":
    main()