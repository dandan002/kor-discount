"""
Refinitiv ownership data pull for Korea Discount study.

Replaces the original DART FSS API pull. Pulls top-20 shareholder data from
LSEG Workspace and aggregates to the two controlling-shareholder metrics used
in the regression:
  controlling_pct_largest  — % held by the single largest shareholder
  controlling_pct_group    — % held by all insider (I) + strategic (S) holders combined

READS: data/raw/universe_raw.csv (from src/00_build_universe.py)
OUTPUTS:
  data/raw/dart/controlling_shareholder.csv — same schema as the former DART pull

Output path kept at data/raw/dart/ so src/03_merge_covariates.py requires no changes.

Run from project root:
    python src/01c_dart_pull.py

Requires:
    pip install lseg-data
    LSEG Workspace desktop app open and logged in
"""

import logging
import os
import sys

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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

from utils.refinitiv import get_data

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

UNIVERSE_PATH = os.path.join(PROJECT_ROOT, "data", "raw", "universe_raw.csv")
DART_DIR = os.path.join(PROJECT_ROOT, "data", "raw", "dart")
OUTPUT_PATH = os.path.join(DART_DIR, "controlling_shareholder.csv")

# Pull top 20 shareholders of every type so we can identify the largest holder
# and sum insider + strategic stakes for the group total.
OWNERSHIP_FIELDS = [
    "TR.ShareholderName",        # shareholder name (for audit trail)
    "TR.ShareholderTotalPctOwn", # direct + indirect % ownership
    "TR.ShareholderTypeCode",    # "I"=insider, "S"=strategic, "F"=funds, "G"=govt
]
OWNERSHIP_PARAMS = {
    "ShareholderType": "All",
    "TopN": "20",
}

# Type codes treated as "controlling group" — insiders and strategic cross-holders.
# Funds ("F"), government ("G"), and other institutional types are excluded.
CONTROLLING_TYPES = {"I", "S"}

# Process in batches to stay within API response size limits.
_BATCH_SIZE = 25


def ticker_to_ric(ticker: str) -> str:
    return str(ticker).zfill(6) + ".KS"


def ric_to_ticker(ric: str) -> str:
    return ric.split(".")[0].zfill(6)


def load_universe():
    if not os.path.exists(UNIVERSE_PATH):
        print(
            f"Error: {UNIVERSE_PATH} not found.\n"
            "Run src/00_build_universe.py first.",
            file=sys.stderr,
        )
        sys.exit(1)
    df = pd.read_csv(UNIVERSE_PATH, dtype={"ticker": str})
    rics = [ticker_to_ric(t) for t in df["ticker"].dropna()]
    log.info("Loaded %d tickers → %d RICs from %s.", len(rics), len(rics), UNIVERSE_PATH)
    return rics


def pull_ownership(rics):
    """
    Pull top-20 shareholder rows for all RICs and aggregate to firm-level metrics.

    Returns DataFrame: ticker, controlling_pct_largest, controlling_pct_group.
    """
    all_frames = []
    n_batches = (len(rics) + _BATCH_SIZE - 1) // _BATCH_SIZE

    for i in range(0, len(rics), _BATCH_SIZE):
        batch = rics[i : i + _BATCH_SIZE]
        batch_num = i // _BATCH_SIZE + 1
        log.info("Ownership batch %d / %d (%d RICs) ...", batch_num, n_batches, len(batch))
        try:
            df = get_data(batch, OWNERSHIP_FIELDS, parameters=OWNERSHIP_PARAMS, batch_size=len(batch))
        except Exception as exc:
            log.error("Batch %d failed: %s — skipping.", batch_num, exc)
            continue
        if df is not None and not df.empty:
            all_frames.append(df)

    if not all_frames:
        log.error("All ownership batches returned empty. Check Workspace connection.")
        return pd.DataFrame(columns=["ticker", "controlling_pct_largest", "controlling_pct_group"])

    raw = pd.concat(all_frames, ignore_index=True)

    # Rename by column position — ld.get_data returns human-readable labels that
    # vary by Workspace version; positional rename is version-agnostic.
    cols = list(raw.columns)
    # cols[0]=Instrument, cols[1]=name, cols[2]=pct_own, cols[3]=type_code
    raw = raw.rename(columns={
        cols[0]: "ric",
        cols[1]: "shareholder_name",
        cols[2]: "pct_own",
        cols[3]: "type_code",
    })

    raw["ticker"] = raw["ric"].apply(ric_to_ticker)
    raw["pct_own"] = pd.to_numeric(raw["pct_own"], errors="coerce")
    raw["type_code"] = raw["type_code"].astype(str).str.strip().str.upper()

    results = []
    for ticker, grp in raw.groupby("ticker"):
        grp = grp.dropna(subset=["pct_own"])

        # Largest single holder — take the maximum individual stake.
        largest = grp["pct_own"].max() if not grp.empty else None

        # Group total — sum all insider (I) and strategic (S) holdings.
        group_rows = grp[grp["type_code"].isin(CONTROLLING_TYPES)]
        group_total = group_rows["pct_own"].sum() if not group_rows.empty else None

        results.append({
            "ticker": ticker,
            "controlling_pct_largest": largest,
            "controlling_pct_group": group_total,
        })

    out = pd.DataFrame(results)
    no_data = out["controlling_pct_largest"].isna().sum()
    if no_data:
        log.warning(
            "%d / %d firms have no ownership data.",
            no_data, len(out),
        )
    return out


def main():
    os.makedirs(DART_DIR, exist_ok=True)

    rics = load_universe()
    df = pull_ownership(rics)
    df.to_csv(OUTPUT_PATH, index=False)

    log.info(
        "Saved controlling_shareholder.csv: %d rows x %d columns.",
        len(df), len(df.columns),
    )
    if os.path.exists(OUTPUT_PATH):
        log.info("%s (%d bytes)", OUTPUT_PATH, os.path.getsize(OUTPUT_PATH))
    else:
        log.error("MISSING: %s", OUTPUT_PATH)


if __name__ == "__main__":
    main()
