"""
asia_panel.py - Shared utility for loading the canonical panel with MSCI EM Asia appended.
"""
import logging
import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import config

MSCI_EM_ASIA_COUNTRY = "MSCI_EM_ASIA"
MSCI_EM_ASIA_PB_PATH = config.RAW_DIR / "msci_em_asia_pb_2004_2026.csv"


def month_end_dates(series: pd.Series) -> pd.Series:
    return pd.to_datetime(series) + pd.offsets.MonthEnd(0)


def load_panel_with_em_asia() -> pd.DataFrame:
    """Load the canonical panel and append MSCI EM Asia P/B from raw data."""
    panel = pd.read_parquet(config.PROCESSED_DIR / "panel.parquet")
    panel["date"] = pd.to_datetime(panel["date"])

    if not MSCI_EM_ASIA_PB_PATH.exists():
        raise FileNotFoundError(
            f"Required raw data file is missing: {MSCI_EM_ASIA_PB_PATH}. "
            "Run src/data/pull_bloomberg.py or restore the version-controlled raw CSV."
        )

    asia_df = pd.read_csv(MSCI_EM_ASIA_PB_PATH)
    if list(asia_df.columns) != ["date", "pb"]:
        raise ValueError(
            f"{MSCI_EM_ASIA_PB_PATH} must have columns ['date', 'pb']; "
            f"found {list(asia_df.columns)}"
        )
    asia_df["date"] = month_end_dates(asia_df["date"])
    asia_df["country"] = MSCI_EM_ASIA_COUNTRY
    asia_df["pb"] = asia_df["pb"].astype("float64")
    if "pe" in panel.columns:
        asia_df["pe"] = pd.NA
    if "fx_rate" in panel.columns:
        asia_df["fx_rate"] = 1.0

    panel_cols = list(panel.columns)
    asia_rows = asia_df[[c for c in panel_cols if c in asia_df.columns]].copy()
    combined = pd.concat([panel, asia_rows], ignore_index=True)
    combined = combined.sort_values(["date", "country"]).reset_index(drop=True)
    logging.info(
        "Loaded panel with MSCI EM Asia: %d rows, countries=%s",
        len(combined),
        sorted(combined["country"].unique().tolist()),
    )
    return combined