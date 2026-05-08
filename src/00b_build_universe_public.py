"""
Build KOSPI firm universe from public APIs (no Bloomberg terminal required).

Drop-in alternative to src/00_build_universe.py.
Uses FinanceDataReader for constituent list and firm metadata.

OUTPUT: data/raw/universe_raw.csv
COLUMNS: ticker, name, sector, industry, country, ipo_date

Run from project root:
    python src/00b_build_universe_public.py

Dependencies:
    pip install finance-datareader
"""

import logging
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

import pandas as pd

from utils.public_data import get_kospi_universe

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

OUTPUT_PATH = os.path.join(PROJECT_ROOT, "data", "raw", "universe_raw.csv")
IPO_CUTOFF = datetime(2023, 1, 1)

# KRX sector classification uses Korean names; yfinance/FDR may return English.
# Include both so the filter works regardless of language returned.
_FINANCIAL_SECTORS = {
    # Korean (KRX standard industry codes map to these sector labels)
    "금융업",
    "은행",
    "보험",
    "증권",
    "기타금융",
    # English (FDR or yfinance sector field)
    "Financials",
    "Financial Services",
    "Banks",
    "Insurance",
    "Capital Markets",
    "Diversified Financial Services",
    "Consumer Finance",
    "Thrifts & Mortgage Finance",
}


def main():
    try:
        df = get_kospi_universe()
    except RuntimeError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    log.info("Raw KOSPI universe: %d firms.", len(df))

    pre = len(df)
    df = df[~df["sector"].isin(_FINANCIAL_SECTORS)]
    log.info(
        "Dropped %d financial firms. Remaining: %d.",
        pre - len(df),
        len(df),
    )

    df["_ipo_dt"] = pd.to_datetime(df["ipo_date"], errors="coerce")
    pre = len(df)
    df = df[df["_ipo_dt"].isna() | (df["_ipo_dt"] <= IPO_CUTOFF)]
    log.info(
        "Dropped %d firms with IPO after %s. Remaining: %d.",
        pre - len(df),
        IPO_CUTOFF.strftime("%Y-%m-%d"),
        len(df),
    )

    out = df[["ticker", "name", "sector", "industry", "country", "ipo_date"]].copy()

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    out.to_csv(OUTPUT_PATH, index=False)
    log.info(
        "Saved %d firms to %s. Expected ~600-700 rows for KOSPI non-financials.",
        len(out),
        OUTPUT_PATH,
    )
    if len(out) < 300:
        log.warning(
            "Only %d firms; significantly below expected ~600-700. "
            "Check FinanceDataReader output and sector filter logic.",
            len(out),
        )


if __name__ == "__main__":
    main()
