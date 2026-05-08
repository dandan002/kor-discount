"""
Build KOSPI firm universe from Bloomberg.

OUTPUT: data/raw/universe_raw.csv
COLUMNS: ticker, name, sector, industry, country, ipo_date

Run from project root:
    python src/00_build_universe.py

Requires blpapi (Bloomberg terminal only):
    pip install blpapi
"""

import logging
import os
import sys
from datetime import datetime

# Ensure project root is on path so root-level utils/ is importable when
# invoked as: python src/00_build_universe.py
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd

from utils.bbg import bdp, bds

try:
    import blpapi  # noqa: F401
except ImportError:
    print(
        "Error: blpapi is not installed.\n"
        "This script must be run at a Bloomberg terminal:\n"
        "  pip install blpapi\n"
        "  python src/00_build_universe.py",
        file=sys.stderr,
    )
    sys.exit(1)


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

OUTPUT_PATH = os.path.join("data", "raw", "universe_raw.csv")
KOSPI_INDEX = "KOSPI Index"
MEMBERS_FIELD = "INDX_MEMBERS"
IDENTIFYING_FIELDS = [
    "TICKER",
    "NAME",
    "GICS_SECTOR_NAME",
    "GICS_INDUSTRY_NAME",
    "CNTRY_ISSUE_ISO",
    "EQY_FUND_DT",
]
IPO_CUTOFF = datetime(2023, 1, 1)
OUTPUT_COLUMNS = ["ticker", "name", "sector", "industry", "country", "ipo_date"]


def parse_date(value):
    """Parse Bloomberg date values while preserving missing or unknown dates."""
    if pd.isna(value) or str(value).strip() in {"", "None"}:
        return None

    text = str(value).strip()
    for fmt in ("%Y-%m-%d", "%m/%d/%Y"):
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            continue
    return None


def build_universe():
    """Pull, filter, and return the KOSPI non-financial universe."""
    log.info("Step 1: Pulling KOSPI members via BDS(%r, %r)", KOSPI_INDEX, MEMBERS_FIELD)
    members = bds("KOSPI Index", "INDX_MEMBERS")
    log.info("  Found %d raw KOSPI members.", len(members))

    if not members:
        log.error(
            "BDS returned an empty list. Possible cause: wrong INDX_MEMBERS "
            "sub-element key. See utils/bbg.py bds(), which logs sub-element "
            "names on stderr when the expected key fails."
        )
        sys.exit(1)

    log.info("Step 2: Pulling identifying fields via BDP for %d tickers.", len(members))
    df = bdp(members, IDENTIFYING_FIELDS)
    df.index.name = "bloomberg_ticker"
    df = df.reset_index()
    log.info("  BDP returned %d rows.", len(df))

    df = df.rename(
        columns={
            "TICKER": "ticker",
            "NAME": "name",
            "GICS_SECTOR_NAME": "sector",
            "GICS_INDUSTRY_NAME": "industry",
            "CNTRY_ISSUE_ISO": "country",
            "EQY_FUND_DT": "ipo_date",
        }
    )

    pre_filter = len(df)
    df = df[df["sector"] != "Financials"]
    log.info(
        "Step 3: Dropped %d financial firms (sector='Financials'). Remaining: %d.",
        pre_filter - len(df),
        len(df),
    )

    df["ipo_dt_parsed"] = df["ipo_date"].apply(parse_date)
    pre_filter = len(df)
    df = df[df["ipo_dt_parsed"].isna() | (df["ipo_dt_parsed"] <= IPO_CUTOFF)]
    log.info(
        "Step 4: Dropped %d firms with IPO after %s. Remaining: %d.",
        pre_filter - len(df),
        IPO_CUTOFF.strftime("%Y-%m-%d"),
        len(df),
    )

    df["ticker"] = df["ticker"].fillna(df["bloomberg_ticker"])
    return df[OUTPUT_COLUMNS].copy()


def main():
    try:
        df = build_universe()
    except RuntimeError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False)
    log.info(
        "Saved %d firms to %s. Expected ~600-700 rows for KOSPI non-financials.",
        len(df),
        OUTPUT_PATH,
    )
    if len(df) < 300:
        log.warning(
            "Only %d firms in universe; this is significantly below expected "
            "~600-700. Check BDS output and filter logic.",
            len(df),
        )


if __name__ == "__main__":
    main()
