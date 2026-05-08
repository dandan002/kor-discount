"""
Bloomberg financial data pull for Korea Discount study.

READS: data/raw/universe_raw.csv (from src/00_build_universe.py)
OUTPUTS:
  data/raw/bloomberg/snapshot_2023.csv - 12-field BDP snapshot, FY2023
  data/raw/bloomberg/roe_panel.csv - annual ROE (RETURN_COM_EQY), 2019-2023
  data/raw/bloomberg/returns_panel.csv - daily PX_LAST, 2021-01-01 to 2026-03-31

Run from project root AFTER src/00_build_universe.py:
    python src/01_bloomberg_pull.py

Requires blpapi (Bloomberg terminal only):
    pip install blpapi
"""

import logging
import os
import sys

import pandas as pd

# Ensure project root is on path so utils/ is importable from project-root runs.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import blpapi  # noqa: F401
except ImportError:
    print(
        "Error: blpapi is not installed.\n"
        "This script must be run at a Bloomberg terminal:\n"
        "  pip install blpapi\n"
        "  python src/01_bloomberg_pull.py",
        file=sys.stderr,
    )
    sys.exit(1)

from utils.bbg import bdp, bdh  # noqa: E402

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

UNIVERSE_PATH = os.path.join("data", "raw", "universe_raw.csv")
BLOOMBERG_DIR = os.path.join("data", "raw", "bloomberg")
SNAPSHOT_PATH = os.path.join(BLOOMBERG_DIR, "snapshot_2023.csv")
ROE_PANEL_PATH = os.path.join(BLOOMBERG_DIR, "roe_panel.csv")
RETURNS_PANEL_PATH = os.path.join(BLOOMBERG_DIR, "returns_panel.csv")

# 12 snapshot fields from ROADMAP Phase 2.1.
SNAPSHOT_FIELDS = [
    "PX_TO_BOOK_RATIO",
    "PE_RATIO",
    "RETURN_COM_EQY",
    "RETURN_ON_ASSET",
    "EQY_FLOAT_PCT",
    "CUR_MKT_CAP",
    "EQY_DVD_YLD_IND",
    "TOT_DEBT_TO_TOT_EQY",
    "BS_TOT_ASSET",
    "SALES_GROWTH",
    "CASH_AND_NEAR_CASH_ITEM",
    "DVD_SH_12M",
]

# Pin BDP snapshot to FY2023 year-end fundamentals.
# TODO: Confirm FUNDAMENTAL_DATABASE_DATE is the correct Bloomberg override at terminal.
SNAPSHOT_OVERRIDES = {"FUNDAMENTAL_DATABASE_DATE": "20231231"}

ROE_FIELD = "RETURN_COM_EQY"
ROE_START = "2019-01-01"
ROE_END = "2023-12-31"

RETURNS_FIELD = "PX_LAST"
RETURNS_START = "2021-01-01"
RETURNS_END = "2026-03-31"
KOSPI_BENCHMARK = "KOSPI Index"


def load_universe():
    """Load Bloomberg tickers from universe_raw.csv."""
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


def pull_snapshot(tickers):
    """Pull 12-field BDP snapshot as of FY2023 year-end."""
    log.info(
        "Pulling snapshot BDP for %d tickers, %d fields, override=%s ...",
        len(tickers),
        len(SNAPSHOT_FIELDS),
        SNAPSHOT_OVERRIDES,
    )
    df = bdp(tickers, SNAPSHOT_FIELDS, overrides=SNAPSHOT_OVERRIDES)
    df.index.name = "ticker"
    df.reset_index(inplace=True)
    log.info("Snapshot: %d rows x %d columns.", len(df), len(df.columns))
    df.to_csv(SNAPSHOT_PATH, index=False)
    log.info("Saved to %s.", SNAPSHOT_PATH)
    return df


def pull_roe_panel(tickers):
    """Pull annual RETURN_COM_EQY for 2019-2023."""
    log.info(
        "Pulling ROE panel BDH for %d tickers, field=%s, %s to %s, YEARLY ...",
        len(tickers),
        ROE_FIELD,
        ROE_START,
        ROE_END,
    )
    df = bdh(tickers, [ROE_FIELD], ROE_START, ROE_END, periodicity="YEARLY")
    df = df.rename(columns={"security": "ticker", ROE_FIELD: "roe"})
    df["year"] = pd.to_datetime(df["date"]).dt.year
    df = df[["ticker", "year", "roe"]].copy()
    log.info("ROE panel: %d rows.", len(df))
    df.to_csv(ROE_PANEL_PATH, index=False)
    log.info("Saved to %s.", ROE_PANEL_PATH)
    return df


def pull_returns_panel(tickers):
    """Pull daily PX_LAST for firm tickers plus KOSPI Index benchmark."""
    all_securities = tickers + [KOSPI_BENCHMARK]
    log.info(
        "Pulling returns BDH for %d securities including KOSPI Index benchmark, "
        "field=%s, %s to %s, DAILY ...",
        len(all_securities),
        RETURNS_FIELD,
        RETURNS_START,
        RETURNS_END,
    )
    log.info(
        "bdh() batches in chunks of 10 with 0.5s sleep; "
        "this may take several minutes for a large universe."
    )
    df = bdh(
        all_securities,
        [RETURNS_FIELD],
        RETURNS_START,
        RETURNS_END,
        periodicity="DAILY",
        batch_size=10,  # ~5yr daily × 10 secs ≈ 13k pts, under Desktop API -4002 limit
    )
    df = df.rename(columns={RETURNS_FIELD: "px_last"})
    df["date"] = pd.to_datetime(df["date"])
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

    log.info("Next step: Transfer the project directory offline and proceed to Phase 2.")


if __name__ == "__main__":
    main()
