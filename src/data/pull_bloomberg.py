"""
pull_bloomberg.py — Fetch 20-year monthly valuation and fundamental data for equity
indices via Bloomberg Desktop API (blpapi).

Requirements:
    pip install blpapi
    Bloomberg Terminal must be running and logged in on the same machine.

Output:
    data/raw/<index>_<metric>_2004_<year>.csv
    data/raw/MANIFEST.md

Notes on index-level fundamentals:
    Bloomberg aggregates fundamental fields (margins, returns) as market-cap-weighted
    composites of constituent companies. Coverage depth varies by index — Chinese and
    EM indices often have sparser history before ~2006. Fields that return no data are
    logged to data/raw/MISSING.txt with suggested fallback field codes.
"""

import blpapi
import csv
import datetime
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

START_DATE = datetime.date(2004, 1, 1)
END_DATE   = datetime.date.today()

# fmt: off
INDICES = {
    # Core study markets
    "kospi":        "KOSPI Index",
    "kospi200":     "KOSPI2 Index",
    "topix":        "TPX Index",
    "sp500":        "SPX Index",
    "msci_em":      "MXEF Index",
    # Additional developed markets
    "dji":          "INDU Index",
    "ndx":          "NDX Index",
    "hsi":          "HSI Index",
    "stoxx600":     "SXXP Index",
    "ftse100":      "UKX Index",
    # MSCI country indices (developed Asia + HK)
    "msci_japan":   "MXJP Index",
    "msci_taiwan":  "MXTW Index",
    "msci_korea":   "MXKR Index",
    "msci_hk":      "MXHK Index",
    # MSCI large emerging market economies
    "msci_china":   "MXCN Index",
    "msci_india":   "MXIN Index",
    "msci_brazil":  "MXBR Index",
    "msci_em_asia": "MXAS Index",
    "msci_indonesia":"MXID Index",
    "msci_mexico":  "MXMX Index",
    "msci_s_africa":"MXZA Index",
    # Local broad indices for key EM markets
    "shcomp":       "SHCOMP Index",
    "sensex":       "SENSEX Index",
    "bovespa":      "IBOV Index",
}

# Bloomberg field codes for index-level historical fundamentals.
# Fallbacks listed in FIELD_FALLBACKS below — used automatically on empty response.
FIELDS = {
    # Valuation
    "pb":           "PX_TO_BOOK_RATIO",
    "pe":           "PE_RATIO",
    "ev_ebitda":    "EV_TO_T12M_EBITDA",
    "ev_ebit":      "EV_TO_T12M_EBIT",
    "div_yield":    "EQY_DVD_YLD_IND",
    # Profitability margins
    "gross_margin": "GROSS_MARGIN",
    "oper_margin":  "OPER_MARGIN",
    "profit_margin":"PROF_MARGIN",
    "ebitda_margin":"EBITDA_MARGIN",
    # Returns
    "roa":          "RETURN_ON_ASSET",
    "roe":          "RETURN_ON_EQY",
    "roce":         "RETURN_COM_EQY",
    "roc":          "RETURN_ON_CAP",
}

# If a primary field returns no data, retry with these alternatives before giving up.
FIELD_FALLBACKS: dict[str, list[str]] = {
    "PX_TO_BOOK_RATIO": ["EQY_P2BK_RATIO"],
    "PE_RATIO":         ["BEST_PE_RATIO", "TRAIL_12M_EPS"],
    "EV_TO_T12M_EBITDA":["CURR_ENTP_VAL_TO_EBITDA"],
    "EV_TO_T12M_EBIT":  ["CURR_ENTP_VAL_TO_EBIT"],
    "EQY_DVD_YLD_IND":  ["DVD_YLD", "EQY_DVD_YLD_12M"],
    "GROSS_MARGIN":     ["T12M_GROSS_MARGIN"],
    "OPER_MARGIN":      ["T12M_OPER_MARGIN"],
    "PROF_MARGIN":      ["T12M_PROF_MARGIN", "NET_MARGIN"],
    "EBITDA_MARGIN":    ["T12M_EBITDA_MARGIN"],
    "RETURN_ON_ASSET":  ["T12M_RETURN_ON_ASSET"],
    "RETURN_ON_EQY":    ["T12M_RETURN_ON_EQY"],
    "RETURN_COM_EQY":   ["T12M_RETURN_COM_EQY"],
    "RETURN_ON_CAP":    ["T12M_RETURN_ON_CAP"],
}
# fmt: on

RAW_DIR = Path(__file__).resolve().parents[2] / "data" / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)

BLOOMBERG_HOST = "localhost"
BLOOMBERG_PORT = 8194

TOTAL = len(INDICES) * len(FIELDS)  # 143

# ---------------------------------------------------------------------------
# Bloomberg session
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


# ---------------------------------------------------------------------------
# Historical data fetch (single ticker / single field)
# ---------------------------------------------------------------------------

def fetch_historical(
    session: blpapi.Session,
    ticker: str,
    field: str,
    start: datetime.date,
    end: datetime.date,
) -> list[tuple[datetime.date, float]]:
    """Return [(date, value), ...] sorted ascending. Empty list on failure."""
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
        event = session.nextEvent(timeout=10_000)

        for msg in event:
            if msg.hasElement("responseError"):
                print(f"    responseError: {msg.getElement('responseError')}")
                continue

            if not msg.hasElement("securityData"):
                continue

            sec_data = msg.getElement("securityData")

            if sec_data.hasElement("securityError"):
                print(f"    securityError for {ticker}")
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

    return sorted(results)


def fetch_with_fallback(
    session: blpapi.Session,
    ticker: str,
    primary_field: str,
    start: datetime.date,
    end: datetime.date,
) -> tuple[list[tuple[datetime.date, float]], str]:
    """Try primary field, then each fallback. Return (rows, field_used)."""
    candidates = [primary_field] + FIELD_FALLBACKS.get(primary_field, [])
    for field in candidates:
        rows = fetch_historical(session, ticker, field, start, end)
        if rows:
            if field != primary_field:
                print(f"    (used fallback field: {field})")
            return rows, field
    return [], primary_field


# ---------------------------------------------------------------------------
# CSV writer
# ---------------------------------------------------------------------------

def save_csv(
    rows: list[tuple[datetime.date, float]],
    out_path: Path,
    col_name: str,
) -> None:
    with open(out_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["date", col_name])
        for date, value in rows:
            writer.writerow([date.isoformat(), value])


# ---------------------------------------------------------------------------
# Manifest + missing log writers
# ---------------------------------------------------------------------------

def write_manifest(entries: list[dict]) -> None:
    today = datetime.date.today().isoformat()
    path  = RAW_DIR / "MANIFEST.md"
    lines = [
        "# Data Manifest\n\n",
        f"Generated: {today}  |  "
        f"Source: Bloomberg Terminal (blpapi HistoricalDataRequest, monthly)\n\n",
        "| File | Index | Bloomberg Ticker | Field Code | Vintage Date |\n",
        "|------|-------|-----------------|------------|-------------|\n",
    ]
    for e in sorted(entries, key=lambda x: x["file"]):
        lines.append(
            f"| {e['file']} | {e['index']} | {e['ticker']} "
            f"| {e['field_code']} | {today} |\n"
        )
    path.write_text("".join(lines))
    print(f"Manifest  → data/raw/MANIFEST.md  ({len(entries)} entries)")


def write_missing_log(missing: list[dict]) -> None:
    if not missing:
        return
    path = RAW_DIR / "MISSING.txt"
    lines = ["# Series with no Bloomberg data\n",
             "# Check field availability with: <ticker> DES <GO> → Field Search\n\n"]
    for m in missing:
        tried = ", ".join(m["tried"])
        lines.append(f"{m['index']:12s}  {m['metric']:14s}  tried: {tried}\n")
    path.write_text("".join(lines))
    print(f"Missing log → data/raw/MISSING.txt  ({len(missing)} series)")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    print(f"Connecting to Bloomberg ({BLOOMBERG_HOST}:{BLOOMBERG_PORT})…")
    session = start_session()
    print(f"Connected. Fetching {TOTAL} series "
          f"({len(INDICES)} indices × {len(FIELDS)} fields)…\n")

    end_year = END_DATE.year
    manifest_entries: list[dict] = []
    missing_series:   list[dict] = []
    done = 0

    for index_key, ticker in INDICES.items():
        print(f"── {index_key.upper()}  ({ticker})")
        for metric_key, primary_field in FIELDS.items():
            done += 1
            label    = f"{index_key}/{metric_key}"
            filename = f"{index_key}_{metric_key}_2004_{end_year}.csv"
            out_path = RAW_DIR / filename

            print(f"  [{done:3d}/{TOTAL}] {label}")
            rows, field_used = fetch_with_fallback(
                session, ticker, primary_field, START_DATE, END_DATE
            )

            if not rows:
                print(f"    NO DATA — logged to MISSING.txt")
                missing_series.append({
                    "index":  index_key,
                    "metric": metric_key,
                    "tried":  [primary_field] + FIELD_FALLBACKS.get(primary_field, []),
                })
                continue

            save_csv(rows, out_path, metric_key)
            print(f"    {len(rows)} obs → {filename}")
            manifest_entries.append({
                "file":       filename,
                "index":      index_key.upper(),
                "ticker":     ticker,
                "field_code": field_used,
            })

        print()

    session.stop()

    write_manifest(manifest_entries)
    write_missing_log(missing_series)

    n_ok      = len(manifest_entries)
    n_missing = len(missing_series)
    print(f"\n{'─'*50}")
    print(f"Complete:  {n_ok}/{TOTAL} series saved")
    if n_missing:
        print(f"Missing:   {n_missing} series — see data/raw/MISSING.txt")
        print("           Re-run after checking field codes in the Terminal.")
    print("\nNext step: python src/data/build_panel.py")

    if n_missing:
        sys.exit(1)


if __name__ == "__main__":
    main()
