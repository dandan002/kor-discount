"""
Public-API financial data pull for Korea Discount study.

Drop-in alternative to src/01_bloomberg_pull.py — no Bloomberg terminal required.
Uses yfinance (fundamentals + prices) with parallel per-ticker fetching.

READS: data/raw/universe_raw.csv  (from 00_build_universe.py or 00b_build_universe_public.py)
OUTPUTS (identical paths to 01_bloomberg_pull.py):
  data/raw/bloomberg/snapshot_2023.csv   — 12-field cross-section, FY2023 year-end
  data/raw/bloomberg/roe_panel.csv       — annual ROE, 2019-2023
  data/raw/bloomberg/returns_panel.csv   — weekly prices, 2021-01-01 to 2026-03-31

Ticker note:
  Returns panel uses Yahoo Finance ticker format (e.g. "005930.KS"; KOSPI
  benchmark is "^KS11") instead of Bloomberg format ("005930 KS Equity";
  "KOSPI Index"). Adjust downstream joins accordingly.

Run from project root:
    python src/01b_public_pull.py

Dependencies:
    pip install yfinance finance-datareader
"""

import logging
import os
import sys

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.public_data import get_returns_panel, get_roe_panel, get_snapshot

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

SNAPSHOT_YEAR = 2023
ROE_START_YEAR = 2019
ROE_END_YEAR = 2023
RETURNS_START = "2021-01-01"
RETURNS_END = "2026-03-31"


def load_universe() -> list:
    if not os.path.exists(UNIVERSE_PATH):
        print(
            f"Error: {UNIVERSE_PATH} not found.\n"
            "Run src/00_build_universe.py or src/00b_build_universe_public.py first.",
            file=sys.stderr,
        )
        sys.exit(1)

    df = pd.read_csv(UNIVERSE_PATH)
    if "ticker" not in df.columns:
        print(f"Error: {UNIVERSE_PATH} missing 'ticker' column.", file=sys.stderr)
        sys.exit(1)

    tickers = df["ticker"].dropna().astype(str).str.zfill(6).tolist()
    log.info("Loaded %d tickers from %s.", len(tickers), UNIVERSE_PATH)
    return tickers


def main():
    os.makedirs(BLOOMBERG_DIR, exist_ok=True)
    tickers = load_universe()

    log.info("=== Snapshot (FY%d) ===", SNAPSHOT_YEAR)
    snap = get_snapshot(tickers, as_of_year=SNAPSHOT_YEAR)
    snap.reset_index(inplace=True)
    snap.to_csv(SNAPSHOT_PATH, index=False)
    log.info("Saved: %s (%d rows).", SNAPSHOT_PATH, len(snap))

    log.info("=== ROE Panel (%d-%d) ===", ROE_START_YEAR, ROE_END_YEAR)
    roe = get_roe_panel(tickers, start_year=ROE_START_YEAR, end_year=ROE_END_YEAR)
    roe.to_csv(ROE_PANEL_PATH, index=False)
    log.info("Saved: %s (%d rows).", ROE_PANEL_PATH, len(roe))

    log.info("=== Returns Panel (%s to %s) ===", RETURNS_START, RETURNS_END)
    ret = get_returns_panel(tickers, start_date=RETURNS_START, end_date=RETURNS_END)
    ret.to_csv(RETURNS_PANEL_PATH, index=False)
    log.info("Saved: %s (%d rows).", RETURNS_PANEL_PATH, len(ret))

    log.info("=== Done. Output summary: ===")
    for path in [SNAPSHOT_PATH, ROE_PANEL_PATH, RETURNS_PANEL_PATH]:
        if os.path.exists(path):
            log.info("  %s (%d bytes)", path, os.path.getsize(path))
        else:
            log.error("  MISSING: %s", path)


if __name__ == "__main__":
    main()
