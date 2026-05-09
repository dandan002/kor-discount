"""
LSEG Data Library wrappers for Korea Discount study.

Connects to the locally running LSEG Workspace desktop app — no App Key required.
Workspace must be open and logged in when you run the scripts.

Functions:
  get_data(rics, fields, parameters=None, batch_size=50)        -> DataFrame
  get_timeseries(rics, start_date, end_date, ...)               -> DataFrame (long)
  get_index_constituents(index_ric)                             -> list[str]

Requires:
    pip install lseg-data
    LSEG Workspace desktop app open and logged in

Connection test:
    python utils/refinitiv.py --test
"""

import logging
import os
import sys
import time

import pandas as pd

log = logging.getLogger(__name__)

try:
    import lseg.data as ld
    from lseg.data.content.historical_pricing import Intervals

    _LD_AVAILABLE = True
except ImportError:
    _LD_AVAILABLE = False

_session_open = False


def _require_ld():
    if not _LD_AVAILABLE:
        raise RuntimeError(
            "lseg-data is not installed.\n"
            "  pip install lseg-data\n"
            "  Ensure LSEG Workspace desktop is open and logged in."
        )


def _init():
    """Open a desktop session connecting to the running Workspace app."""
    global _session_open
    _require_ld()
    if not _session_open:
        ld.open_session()
        _session_open = True


# ---------------------------------------------------------------------------
# Core wrappers
# ---------------------------------------------------------------------------


def get_data(rics, fields, parameters=None, batch_size=50):
    """
    Fetch reference or fundamental data via ld.get_data().

    Args:
        rics:       str or list of Refinitiv RIC strings (e.g. "005930.KS")
        fields:     str or list of Refinitiv field mnemonics (e.g. "TR.F.PBk")
        parameters: dict passed to ld.get_data parameters= kwarg, e.g.
                    {"SDate": "2023-12-31", "FRQ": "FY"} to pin to FY2023.
        batch_size: RICs per request (default 50).

    Returns:
        pd.DataFrame with column 'Instrument' plus one column per field.
        For time-series parameters (SDate/EDate spanning multiple periods),
        returns one row per (instrument, period).
    """
    _init()
    if isinstance(rics, str):
        rics = [rics]
    if isinstance(fields, str):
        fields = [fields]

    frames = []
    for i in range(0, len(rics), batch_size):
        batch = rics[i : i + batch_size]
        try:
            df = ld.get_data(universe=batch, fields=fields, parameters=parameters)
        except Exception as exc:
            log.error(
                "get_data failed for batch %d: %s", i // batch_size + 1, exc
            )
            continue
        if df is not None and not df.empty:
            frames.append(df)
        if i + batch_size < len(rics):
            time.sleep(0.5)

    if not frames:
        return pd.DataFrame(columns=["Instrument"] + list(fields))
    return pd.concat(frames, ignore_index=True)


def get_timeseries(
    rics,
    start_date,
    end_date,
    field="CLOSE",
    interval="weekly",
    batch_size=20,
):
    """
    Fetch historical price data via ld.get_history().

    Args:
        rics:       str or list of RIC strings
        start_date: "YYYY-MM-DD"
        end_date:   "YYYY-MM-DD"
        field:      price field (default "CLOSE")
        interval:   "weekly" | "daily" | "monthly" (default "weekly")
        batch_size: RICs per request (default 20)

    Returns:
        Long-format DataFrame: security (str), date (datetime), px_last (float).
        'security' uses Refinitiv RIC format (e.g. "005930.KS"; KOSPI benchmark ".KS11").
    """
    _init()
    if isinstance(rics, str):
        rics = [rics]

    interval_map = {
        "daily": Intervals.DAILY,
        "weekly": Intervals.WEEKLY,
        "monthly": Intervals.MONTHLY,
    }
    ld_interval = interval_map.get(interval.lower(), Intervals.WEEKLY)

    all_rows = []
    for i in range(0, len(rics), batch_size):
        batch = rics[i : i + batch_size]
        try:
            ts = ld.get_history(
                universe=batch,
                fields=[field],
                start=start_date,
                end=end_date,
                interval=ld_interval,
            )
        except Exception as exc:
            log.warning(
                "get_history failed for batch %d (%d rics): %s",
                i // batch_size + 1,
                len(batch),
                exc,
            )
            if i + batch_size < len(rics):
                time.sleep(2.0)
            continue

        if ts is None or ts.empty:
            if i + batch_size < len(rics):
                time.sleep(1.0)
            continue

        # ld.get_history returns MultiIndex (Instrument, Date) when multiple RICs,
        # or DatetimeIndex when a single RIC.
        if isinstance(ts.index, pd.MultiIndex):
            ts = ts.reset_index()
            ts = ts.rename(columns={ts.columns[0]: "security", ts.columns[1]: "date"})
        else:
            # Single RIC: add 'security' column from the first element of batch.
            ts = ts.reset_index()
            date_col = ts.columns[0]
            ts = ts.rename(columns={date_col: "date"})
            ts["security"] = batch[0]

        # Rename the price field column to px_last
        price_col = [c for c in ts.columns if c not in ("security", "date")]
        if price_col:
            ts = ts.rename(columns={price_col[0]: "px_last"})

        long = ts[["security", "date", "px_last"]].dropna(subset=["px_last"])
        long["date"] = pd.to_datetime(long["date"])
        all_rows.append(long)

        if i + batch_size < len(rics):
            time.sleep(1.0)

    if not all_rows:
        return pd.DataFrame(columns=["security", "date", "px_last"])
    return pd.concat(all_rows, ignore_index=True).reset_index(drop=True)


def get_index_constituents(index_ric):
    """
    Return list of constituent RIC strings for an index.

    Example:
        get_index_constituents(".KS11") -> ["005930.KS", "000660.KS", ...]
    """
    _init()
    # Chain RIC format (0#.KS11) returns one row per constituent.
    # TR.RIC is the correct field; TR.IndexConstituentRIC is not valid here.
    chain_ric = index_ric if index_ric.startswith("0#") else f"0#{index_ric}"
    try:
        df = ld.get_data(universe=chain_ric, fields=["TR.RIC"])
    except Exception as exc:
        raise RuntimeError(
            f"get_index_constituents failed for {chain_ric}: {exc}"
        ) from exc
    if df is None or df.empty:
        return []
    ric_col = "RIC" if "RIC" in df.columns else df.columns[-1]
    return df[ric_col].dropna().tolist()


def close_session():
    """Close the LSEG Data session. Call at end of script if needed."""
    global _session_open
    if _LD_AVAILABLE and _session_open:
        ld.close_session()
        _session_open = False


# ---------------------------------------------------------------------------
# CLI connection test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(message)s")
        if not _LD_AVAILABLE:
            print(
                "Error: lseg-data is not installed.\n"
                "  pip install lseg-data",
                file=sys.stderr,
            )
            sys.exit(1)
        try:
            _init()
            df = ld.get_data(universe="005930.KS", fields=["TR.CommonName"])
            print("LSEG Workspace connection OK.")
            print(f"  Samsung common name: {df.iloc[0, 1]!r}")
            rics = get_index_constituents(".KS11")
            print(f"  KOSPI constituents returned: {len(rics)} RICs")
            if rics:
                print(f"  First few: {rics[:5]}")
            close_session()
        except Exception as exc:
            print(f"Error: {exc}", file=sys.stderr)
            sys.exit(1)
    else:
        print("Usage: python utils/refinitiv.py --test", file=sys.stderr)
        sys.exit(1)
