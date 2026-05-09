"""
build_panel.py - Build the canonical valuation panel for the Korea Discount study.

Reads Bloomberg raw CSV exports for P/B and P/E across the study universe and
writes the analysis-ready long-format panel to data/processed/panel.parquet.
"""

import logging
import sys
import warnings
from pathlib import Path

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import config

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
    stream=sys.stdout,
)

INDEX_MAP = {
    "KOSPI": "kospi",
    "TOPIX": "topix",
    "SP500": "sp500",
    "MSCI_EM": "msci_em",
}


def load_series(prefix: str, metric: str) -> pd.Series:
    """Load one raw Bloomberg CSV as a date-indexed valuation series."""
    path = config.RAW_DIR / f"{prefix}_{metric}_2004_2026.csv"
    if not path.exists():
        raise FileNotFoundError(
            f"Required raw data file is missing: {path}. "
            "Run src/data/pull_bloomberg.py or restore the version-controlled raw CSV."
        )

    df = pd.read_csv(path)
    expected_columns = ["date", metric]
    if list(df.columns) != expected_columns:
        raise ValueError(
            f"{path} must have columns {expected_columns}; found {list(df.columns)}"
        )

    df["date"] = pd.to_datetime(df["date"], format="%Y-%m-%d")
    df = df.set_index("date")
    return df[metric].astype("float64").rename(metric)


def load_fx_series(country: str) -> pd.Series:
    """Load FX rate (Local/USD) for the given country. Default to 1.0 if N/A."""
    if country == "TOPIX":
        path = config.RAW_DIR / "fx_japan.csv"
    elif country == "KOSPI":
        path = config.RAW_DIR / "fx_korea.csv"
    else:
        # SP500 and MSCI_EM get FX=1.0 (baseline USD or USD-priced)
        return None
        
    df = pd.read_csv(path)
    df["date"] = pd.to_datetime(df["date"]).dt.to_period("M").dt.to_timestamp() + pd.offsets.MonthEnd(0)
    df = df.set_index("date")
    return df["fx_rate"].astype("float64")

def build_panel() -> pd.DataFrame:
    """Build and persist the canonical long-format valuation panel."""
    warnings.filterwarnings("default")

    series = {}
    for country, prefix in INDEX_MAP.items():
        for metric in ("pb", "pe"):
            series[(country, metric)] = load_series(prefix, metric)
            
        fx = load_fx_series(country)
        if fx is not None:
            series[(country, "fx")] = fx

    country_dfs = {}
    for country in config.COUNTRIES:
        if country not in INDEX_MAP:
            raise ValueError(f"config.COUNTRIES contains unsupported country: {country}")

        df = pd.concat(
            [series[(country, "pb")], series[(country, "pe")]],
            axis=1,
            join="outer",
        )
        df.index = df.index + pd.offsets.MonthEnd(0)
        
        # Add FX
        if (country, "fx") in series:
            # Reindex FX to match the df index (end of month)
            fx_series = series[(country, "fx")]
            # Interpolate or merge closely if dates slightly mismatched?
            # We already set fx index to MonthEnd(0)
            df = df.join(fx_series, how="left")
        else:
            df["fx_rate"] = 1.0
            
        country_dfs[country] = df

    kospi_df = country_dfs["KOSPI"]
    kospi_pe_gap = kospi_df[kospi_df["pe"].isna() & kospi_df["pb"].notna()]
    if len(kospi_pe_gap) > 0:
        logging.warning(
            "KNOWN LIMITATION: KOSPI PE data starts %s. "
            "%d rows (2004-01 through 2004-04) have NaN pe. "
            "See config.KOSPI_PE_SERIES_START for documentation.",
            config.KOSPI_PE_SERIES_START.isoformat(),
            len(kospi_pe_gap),
        )

    frames = []
    for country, prefix in INDEX_MAP.items():
        df = country_dfs[country].copy()
        df["country"] = country
        df = df.reset_index().rename(columns={"index": "date"})
        frames.append(df[["date", "country", "pb", "pe", "fx_rate"]])

    panel = (
        pd.concat(frames, ignore_index=True)
        .sort_values(["date", "country"])
        .reset_index(drop=True)
    )

    # Some FX rates might be NaN due to date mismatches at edges; ffill them
    panel["fx_rate"] = panel.groupby("country")["fx_rate"].ffill().bfill()

    nan_mask = panel.isna().any(axis=1)
    nan_rows = panel[nan_mask]
    invalid_nans = nan_rows[
        ~(
            (nan_rows["country"] == "KOSPI")
            & (nan_rows["date"] < pd.Timestamp(config.KOSPI_PE_SERIES_START))
            & (nan_rows["pb"].notna())
        )
    ]
    if len(invalid_nans) > 0:
        logging.error("UNDOCUMENTED NaN values found in panel:")
        logging.error(invalid_nans.to_string())
        raise ValueError(
            f"build_panel.py: {len(invalid_nans)} undocumented NaN rows. "
            "Inspect the error output above and update config.py if this is a known gap."
        )

    panel["date"] = pd.to_datetime(panel["date"])
    panel["country"] = panel["country"].astype("object")
    panel["pb"] = panel["pb"].astype("float64")
    panel["pe"] = panel["pe"].astype("float64")

    config.PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    out_path = config.PROCESSED_DIR / "panel.parquet"
    panel.to_parquet(out_path, engine="pyarrow", index=False)
    logging.info("Wrote %d rows to %s", len(panel), out_path)

    print("\n=== Panel Summary ===")
    print(f"Rows:      {len(panel)}")
    print(f"Date range: {panel['date'].min().date()} to {panel['date'].max().date()}")
    print(f"Countries:  {sorted(panel['country'].unique().tolist())}")
    print(f"NaN pe:    {panel['pe'].isna().sum()} rows (expected: 4 KOSPI rows)")
    print(f"NaN pb:    {panel['pb'].isna().sum()} rows (expected: 0)")
    print("Output:   ", out_path)

    return panel


if __name__ == "__main__":
    try:
        build_panel()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
