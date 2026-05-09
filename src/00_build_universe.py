"""
Build KOSPI firm universe from Refinitiv Eikon.

OUTPUT: data/raw/universe_raw.csv
COLUMNS: ticker, name, sector, industry, country, ipo_date
  ticker: 6-digit KRX code (e.g. "005930"), derived from Refinitiv RIC

Run from project root:
    python src/00_build_universe.py

Requires:
    pip install eikon
    REFINITIV_APP_KEY in .env
"""

import logging
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

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

from utils.refinitiv import get_data, get_index_constituents

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

OUTPUT_PATH = os.path.join(PROJECT_ROOT, "data", "raw", "universe_raw.csv")
KOSPI_INDEX_RIC = ".KS11"
IPO_CUTOFF = datetime(2023, 1, 1)
OUTPUT_COLUMNS = ["ticker", "name", "sector", "industry", "country", "ipo_date"]

# Fields to pull for each constituent.
# ek.get_data returns columns in this order: Instrument, field1, field2, ...
METADATA_FIELDS = [
    "TR.CommonName",       # full company name
    "TR.GICSSectorName",   # GICS sector (e.g. "Information Technology")
    "TR.GICSIndustryName", # GICS industry
    "TR.ExchangeCountry",  # ISO country code (e.g. "KOR")
    "TR.IPODate",          # listing / IPO date
]

# Sector labels to exclude — covers both English GICS and Korean KRX labels.
FINANCIAL_SECTORS = {
    "Financials",
    "Financial Services",
    "Banks",
    "Insurance",
    "Capital Markets",
    "Diversified Financials",
    "Consumer Finance",
    "Thrifts & Mortgage Finance",
    "금융업",
    "은행",
    "보험",
    "증권",
    "기타금융",
}


def ric_to_ticker(ric: str) -> str:
    """Convert Refinitiv RIC to 6-digit KRX code ('005930.KS' -> '005930')."""
    return ric.split(".")[0].zfill(6)


def parse_date(value):
    if pd.isna(value) or str(value).strip() in {"", "None", "nan"}:
        return None
    text = str(value).strip()[:10]
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y"):
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            continue
    return None


def build_universe():
    """Pull, filter, and return the KOSPI non-financial universe."""
    log.info("Step 1: Pulling KOSPI constituent RICs from %s ...", KOSPI_INDEX_RIC)
    rics = get_index_constituents(KOSPI_INDEX_RIC)
    # Keep only KS-listed equities; filter out warrants, ETFs, etc.
    rics = [r for r in rics if str(r).endswith(".KS")]
    log.info("  Found %d KOSPI constituent RICs ending in .KS.", len(rics))

    if not rics:
        log.error(
            "get_index_constituents returned no .KS RICs for %s. "
            "Check REFINITIV_APP_KEY and index RIC.",
            KOSPI_INDEX_RIC,
        )
        sys.exit(1)

    log.info("Step 2: Pulling firm metadata for %d RICs ...", len(rics))
    raw = get_data(rics, METADATA_FIELDS)
    log.info("  get_data returned %d rows.", len(raw))

    # Rename by position: ek.get_data always returns Instrument first, then fields in order.
    cols = list(raw.columns)
    rename_map = {
        cols[0]: "ric",
        cols[1]: "name",
        cols[2]: "sector",
        cols[3]: "industry",
        cols[4]: "country",
        cols[5]: "ipo_date",
    }
    df = raw.rename(columns=rename_map)
    df["ticker"] = df["ric"].apply(ric_to_ticker)

    pre = len(df)
    df = df[~df["sector"].isin(FINANCIAL_SECTORS)]
    log.info(
        "Step 3: Dropped %d financial firms (sector filter). Remaining: %d.",
        pre - len(df),
        len(df),
    )

    df["_ipo_dt"] = df["ipo_date"].apply(parse_date)
    pre = len(df)
    df = df[df["_ipo_dt"].isna() | (df["_ipo_dt"] <= IPO_CUTOFF)]
    log.info(
        "Step 4: Dropped %d firms with IPO after %s. Remaining: %d.",
        pre - len(df),
        IPO_CUTOFF.strftime("%Y-%m-%d"),
        len(df),
    )

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
            "Only %d firms; significantly below expected ~600-700. "
            "Check RIC filtering, sector labels, and REFINITIV_APP_KEY.",
            len(df),
        )


if __name__ == "__main__":
    main()
