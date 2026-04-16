"""
pull_bloomberg.py — Fetch 20-year monthly P/B and P/E for KOSPI, TOPIX, S&P 500, MSCI EM
via Bloomberg Desktop API (blpapi).

Requirements:
    pip install blpapi
    Bloomberg Terminal must be running and logged in on the same machine.

Output:
    data/raw/<index>_<metric>_2004_2026.csv   (8 files)
    data/raw/MANIFEST.md
"""

import blpapi
import csv
import datetime
import os
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

START_DATE = datetime.date(2004, 1, 1)
END_DATE   = datetime.date.today()

INDICES = {
    "kospi":   "KOSPI Index",
    "topix":   "TPX Index",
    "sp500":   "SPX Index",
    "msci_em": "MXEF Index",
}

FIELDS = {
    "pb": "PX_TO_BOOK_RATIO",
    "pe": "PE_RATIO",
}

RAW_DIR = Path(__file__).resolve().parents[2] / "data" / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)

BLOOMBERG_HOST = "localhost"
BLOOMBERG_PORT = 8194

# ---------------------------------------------------------------------------
# Bloomberg session helpers
# ---------------------------------------------------------------------------

def start_session() -> blpapi.Session:
    opts = blpapi.SessionOptions()
    opts.setServerHost(BLOOMBERG_HOST)
    opts.setServerPort(BLOOMBERG_PORT)
    session = blpapi.Session(opts)
    if not session.start():
        sys.exit("ERROR: Could not start Bloomberg session. Is the Terminal running?")
    if not session.openService("//blp/refdata"):
        sys.exit("ERROR: Could not open //blp/refdata service.")
    return session


def fetch_historical(
    session: blpapi.Session,
    ticker: str,
    field: str,
    start: datetime.date,
    end: datetime.date,
) -> list[tuple[datetime.date, float]]:
    """Return [(date, value), ...] for one ticker/field pair, monthly frequency."""
    refdata = session.getService("//blp/refdata")
    request = refdata.createRequest("HistoricalDataRequest")

    request.append("securities", ticker)
    request.append("fields", field)
    request.set("periodicityAdjustment", "ACTUAL")
    request.set("periodicitySelection", "MONTHLY")
    request.set("startDate", start.strftime("%Y%m%d"))
    request.set("endDate",   end.strftime("%Y%m%d"))
    request.set("nonTradingDayFillOption", "NON_TRADING_WEEKDAYS")
    request.set("nonTradingDayFillMethod", "PREVIOUS_VALUE")

    session.sendRequest(request)

    results: list[tuple[datetime.date, float]] = []

    while True:
        event = session.nextEvent(timeout=10_000)  # 10 s timeout

        for msg in event:
            if msg.hasElement("responseError"):
                err = msg.getElement("responseError")
                print(f"  WARNING: responseError for {ticker}/{field}: {err}")
                continue

            if not msg.hasElement("securityData"):
                continue

            sec_data = msg.getElement("securityData")

            if sec_data.hasElement("securityError"):
                print(f"  WARNING: securityError for {ticker}/{field}")
                continue

            field_data_array = sec_data.getElement("fieldData")

            for i in range(field_data_array.numValues()):
                fd = field_data_array.getValueAsElement(i)
                if not fd.hasElement(field):
                    continue
                raw_date = fd.getElementAsDatetime("date")
                value    = fd.getElementAsFloat(field)
                results.append((
                    datetime.date(raw_date.year, raw_date.month, raw_date.day),
                    value,
                ))

        if event.eventType() == blpapi.Event.RESPONSE:
            break

    return results


# ---------------------------------------------------------------------------
# CSV writer
# ---------------------------------------------------------------------------

def save_csv(
    rows: list[tuple[datetime.date, float]],
    out_path: Path,
    field_name: str,
) -> None:
    with open(out_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["date", field_name])
        for date, value in sorted(rows):
            writer.writerow([date.isoformat(), value])
    print(f"  Saved {len(rows)} rows → {out_path.relative_to(RAW_DIR.parent.parent)}")


# ---------------------------------------------------------------------------
# Manifest writer
# ---------------------------------------------------------------------------

def write_manifest(entries: list[dict]) -> None:
    path = RAW_DIR / "MANIFEST.md"
    today = datetime.date.today().isoformat()
    lines = [
        "# Data Manifest\n",
        f"Generated: {today}\n\n",
        "| File | Source | Index | Bloomberg Ticker | Field | Vintage Date | Download Method |\n",
        "|------|--------|-------|-----------------|-------|-------------|----------------|\n",
    ]
    for e in entries:
        lines.append(
            f"| {e['file']} | Bloomberg Terminal | {e['index']} | {e['ticker']} "
            f"| {e['field_code']} | {today} | blpapi HistoricalDataRequest |\n"
        )
    path.write_text("".join(lines))
    print(f"\nManifest written → data/raw/MANIFEST.md")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    print(f"Connecting to Bloomberg ({BLOOMBERG_HOST}:{BLOOMBERG_PORT})…")
    session = start_session()
    print("Connected.\n")

    end_year = END_DATE.year
    manifest_entries = []
    missing: list[str] = []

    for index_key, ticker in INDICES.items():
        for metric_key, field_code in FIELDS.items():
            label = f"{index_key}/{metric_key}"
            filename = f"{index_key}_{metric_key}_2004_{end_year}.csv"
            out_path = RAW_DIR / filename

            print(f"Fetching {label}  ({ticker}  {field_code})…")
            rows = fetch_historical(session, ticker, field_code, START_DATE, END_DATE)

            if not rows:
                print(f"  ERROR: no data returned for {label}")
                missing.append(label)
                continue

            save_csv(rows, out_path, metric_key)
            manifest_entries.append({
                "file":       filename,
                "index":      index_key.upper(),
                "ticker":     ticker,
                "field_code": field_code,
            })

    session.stop()

    write_manifest(manifest_entries)

    if missing:
        print(f"\nWARNING: No data returned for: {', '.join(missing)}")
        print("Check that the Bloomberg field is valid for these index types.")
        print("Alternatives: PX_TO_BOOK_RATIO → EQY_P2BK_RATIO; PE_RATIO → BEST_PE_RATIO")
        sys.exit(1)

    print("\nDone. All 8 series downloaded.")
    print("Next step: run  python src/data/build_panel.py  to produce panel.parquet")


if __name__ == "__main__":
    main()
