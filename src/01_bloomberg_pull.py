"""
Refinitiv financial data pull for Korea Discount study.

READS: data/raw/universe_raw.csv (from src/00_build_universe.py)
OUTPUTS (same paths as the original Bloomberg pull — downstream unchanged):
  data/raw/bloomberg/snapshot_2023.csv   — 12-field cross-section, FY2023
  data/raw/bloomberg/roe_panel.csv       — annual ROE, FY2019-FY2023
  data/raw/bloomberg/returns_panel.csv   — weekly closing prices, 2021-01-01 to 2026-03-31

Column names in snapshot_2023.csv use Bloomberg mnemonics (PX_TO_BOOK_RATIO etc.)
so that src/03_merge_covariates.py requires no changes.

Run from project root AFTER src/00_build_universe.py:
    python src/01_bloomberg_pull.py

Requires:
    pip install eikon
    REFINITIV_APP_KEY in .env
"""

import logging
import os
import sys

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import lseg.data  # noqa: F401
except ImportError:
    print(
        "Error: lseg-data is not installed.\n"
        "  pip install lseg-data\n"
        "  Ensure LSEG Workspace desktop is open and logged in.",
        file=sys.stderr,
    )
    sys.exit(1)

from utils.refinitiv import get_data, get_timeseries

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

UNIVERSE_PATH = os.path.join(PROJECT_ROOT, "data", "raw", "universe_raw.csv")
BLOOMBERG_DIR = os.path.join(PROJECT_ROOT, "data", "raw", "bloomberg")
SNAPSHOT_PATH = os.path.join(BLOOMBERG_DIR, "snapshot_2023.csv")
ROE_PANEL_PATH = os.path.join(BLOOMBERG_DIR, "roe_panel.csv")
RETURNS_PANEL_PATH = os.path.join(BLOOMBERG_DIR, "returns_panel.csv")

# ---------------------------------------------------------------------------
# Snapshot — 12 Refinitiv fields for FY2023 cross-section
# Pulled as two batches (fundamental TR.F.* vs market TR.*) to avoid
# parameter conflicts between fiscal-period and point-in-time fields.
# ---------------------------------------------------------------------------

# Fundamental fields pulled with FRQ="FY" to align to fiscal year-end.
# TR.F.* = raw Worldscope balance-sheet items (valid).
# TR.*   = calculated ratios (ROE, ROA, P/E, P/B live here, not TR.F.*).
FUNDAMENTAL_FIELDS_REF = [
    "TR.PriceToBVPerShare", # price-to-book (fiscal year)
    "TR.PriceToEarnings",   # price-to-earnings (fiscal year)
    "TR.ReturnOnEquity",    # return on equity
    "TR.ReturnOnAssets",    # return on assets
    "TR.F.TotDebtToTotEq", # total debt / total equity (%)
    "TR.F.TotAssets",      # total assets
    "TR.F.SalesGrPct",     # sales growth (%)
    "TR.F.CashAndEq",      # cash and equivalents
    "TR.F.DivPerShr",      # dividends per share (trailing 12 months)
]
FUNDAMENTAL_FIELDS_BBG = [
    "PX_TO_BOOK_RATIO",
    "PE_RATIO",
    "RETURN_COM_EQY",
    "RETURN_ON_ASSET",
    "TOT_DEBT_TO_TOT_EQY",
    "BS_TOT_ASSET",
    "SALES_GROWTH",
    "CASH_AND_NEAR_CASH_ITEM",
    "DVD_SH_12M",
]

# Market fields: pulled as of calendar date 2023-12-31 (no FRQ needed).
MARKET_FIELDS_REF = [
    "TR.FloatPct",    # float shares as % of total shares outstanding
    "TR.MktCap",      # market capitalisation (USD millions)
    "TR.DivYield",    # indicated dividend yield (%)
]
MARKET_FIELDS_BBG = [
    "EQY_FLOAT_PCT",
    "CUR_MKT_CAP",
    "EQY_DVD_YLD_IND",
]

SNAPSHOT_YEAR = 2023
ROE_START = "2019-01-01"
ROE_END = "2023-12-31"
RETURNS_START = "2021-01-01"
RETURNS_END = "2026-03-31"
KOSPI_BENCHMARK_RIC = ".KS11"


def ric_to_ticker(ric: str) -> str:
    """Convert Refinitiv RIC to 6-digit KRX code ('005930.KS' -> '005930')."""
    return ric.split(".")[0].zfill(6)


def ticker_to_ric(ticker: str) -> str:
    """Convert 6-digit KRX ticker to Refinitiv RIC ('005930' -> '005930.KS')."""
    return str(ticker).zfill(6) + ".KS"


def load_universe():
    """Load universe_raw.csv and return list of Refinitiv RICs."""
    if not os.path.exists(UNIVERSE_PATH):
        print(
            f"Error: {UNIVERSE_PATH} not found.\n"
            "Run src/00_build_universe.py first.",
            file=sys.stderr,
        )
        sys.exit(1)

    df = pd.read_csv(UNIVERSE_PATH, dtype={"ticker": str})
    if "ticker" not in df.columns:
        print(
            f"Error: {UNIVERSE_PATH} missing 'ticker' column.",
            file=sys.stderr,
        )
        sys.exit(1)

    rics = [ticker_to_ric(t) for t in df["ticker"].dropna()]
    log.info("Loaded %d tickers → %d RICs from %s.", len(rics), len(rics), UNIVERSE_PATH)
    return rics


def pull_snapshot(rics):
    """Pull 12-field FY2023 cross-section and save snapshot_2023.csv."""
    date_str = f"{SNAPSHOT_YEAR}-12-31"

    log.info(
        "Pulling fundamental snapshot (%d fields) for %d RICs as of %s ...",
        len(FUNDAMENTAL_FIELDS_REF),
        len(rics),
        date_str,
    )
    fund_df = get_data(
        rics,
        FUNDAMENTAL_FIELDS_REF,
        parameters={"SDate": date_str, "FRQ": "FY"},
    )
    # Rename: Instrument → ticker (6-digit), then Bloomberg column names
    fund_cols = list(fund_df.columns)
    fund_rename = {fund_cols[0]: "ric"}
    for ref_col, bbg_col in zip(fund_cols[1:], FUNDAMENTAL_FIELDS_BBG):
        fund_rename[ref_col] = bbg_col
    fund_df = fund_df.rename(columns=fund_rename)
    fund_df["ticker"] = fund_df["ric"].apply(ric_to_ticker)
    fund_df = fund_df.drop(columns=["ric"])

    log.info(
        "Pulling market snapshot (%d fields) for %d RICs as of %s ...",
        len(MARKET_FIELDS_REF),
        len(rics),
        date_str,
    )
    mkt_df = get_data(
        rics,
        MARKET_FIELDS_REF,
        parameters={"SDate": date_str},
    )
    mkt_cols = list(mkt_df.columns)
    mkt_rename = {mkt_cols[0]: "ric"}
    for ref_col, bbg_col in zip(mkt_cols[1:], MARKET_FIELDS_BBG):
        mkt_rename[ref_col] = bbg_col
    mkt_df = mkt_df.rename(columns=mkt_rename)
    mkt_df["ticker"] = mkt_df["ric"].apply(ric_to_ticker)
    mkt_df = mkt_df.drop(columns=["ric"])

    # Merge on ticker; all 12 Bloomberg-named columns in final CSV
    snap = fund_df.merge(mkt_df, on="ticker", how="outer")
    all_bbg_cols = FUNDAMENTAL_FIELDS_BBG + MARKET_FIELDS_BBG
    col_order = ["ticker"] + [c for c in all_bbg_cols if c in snap.columns]
    snap = snap[col_order]

    log.info("Snapshot: %d rows x %d columns.", len(snap), len(snap.columns))
    snap.to_csv(SNAPSHOT_PATH, index=False)
    log.info("Saved to %s.", SNAPSHOT_PATH)
    return snap


def pull_roe_panel(rics):
    """Pull annual ROE for FY2019-FY2023 and save roe_panel.csv."""
    log.info(
        "Pulling ROE panel for %d RICs, %s to %s ...",
        len(rics),
        ROE_START,
        ROE_END,
    )
    df = get_data(
        rics,
        ["TR.ReturnOnEquity"],
        parameters={"SDate": ROE_START, "EDate": ROE_END, "FRQ": "FY"},
    )

    # ek.get_data with date range returns columns: Instrument, Date, <field label>
    cols = list(df.columns)
    # cols[0]=Instrument, cols[1]=Date (period end), cols[2]=ROE label
    rename = {cols[0]: "ric", cols[1]: "period_date", cols[2]: "roe"}
    df = df.rename(columns=rename)
    df["ticker"] = df["ric"].apply(ric_to_ticker)
    df["year"] = pd.to_datetime(df["period_date"], errors="coerce").dt.year
    df = df[["ticker", "year", "roe"]].dropna(subset=["year"]).copy()
    df["year"] = df["year"].astype(int)

    log.info("ROE panel: %d rows.", len(df))
    df.to_csv(ROE_PANEL_PATH, index=False)
    log.info("Saved to %s.", ROE_PANEL_PATH)
    return df


def pull_returns_panel(rics):
    """Pull weekly closing prices for firm RICs + KOSPI benchmark."""
    all_rics = rics + [KOSPI_BENCHMARK_RIC]
    log.info(
        "Pulling weekly returns for %d securities (%s to %s) ...",
        len(all_rics),
        RETURNS_START,
        RETURNS_END,
    )
    df = get_timeseries(
        all_rics,
        start_date=RETURNS_START,
        end_date=RETURNS_END,
        field="CLOSE",
        interval="weekly",
        batch_size=20,
    )
    log.info(
        "Returns panel: %d rows, %d unique securities.",
        len(df),
        df["security"].nunique(),
    )
    df.to_csv(RETURNS_PANEL_PATH, index=False)
    log.info("Saved to %s.", RETURNS_PANEL_PATH)
    return df


def main():
    os.makedirs(BLOOMBERG_DIR, exist_ok=True)

    rics = load_universe()
    pull_snapshot(rics)
    pull_roe_panel(rics)
    pull_returns_panel(rics)

    log.info("All done. Output summary:")
    for path in [SNAPSHOT_PATH, ROE_PANEL_PATH, RETURNS_PANEL_PATH]:
        if os.path.exists(path):
            log.info("  %s (%d bytes)", path, os.path.getsize(path))
        else:
            log.error("  MISSING: %s", path)

    log.info("Next step: Run src/02_build_compliance.py then src/03_merge_covariates.py.")


if __name__ == "__main__":
    main()
