"""
DART FSS OpenAPI controlling shareholder pull for Korea Discount study.

READS: data/raw/universe_raw.csv (from src/00_build_universe.py)
OUTPUTS:
  data/raw/dart/corp_code_map.csv  - ticker↔corp_code lookup cache (generated once)
  data/raw/dart/controlling_shareholder.csv - per-firm controlling shareholder %

Run from project root:
    python src/01c_dart_pull.py

Requires internet access and FSS_API_KEY in .env
"""

import io
import logging
import os
import sys
import time
import xml.etree.ElementTree as ET
import zipfile

import pandas as pd
import requests
from dotenv import load_dotenv

# Ensure project root is on path so utils/ is importable from project-root runs.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

UNIVERSE_PATH = os.path.join(PROJECT_ROOT, "data", "raw", "universe_raw.csv")
DART_DIR = os.path.join(PROJECT_ROOT, "data", "raw", "dart")
CORP_CODE_CACHE = os.path.join(DART_DIR, "corp_code_map.csv")
OUTPUT_PATH = os.path.join(DART_DIR, "controlling_shareholder.csv")
CORP_CODE_URL = "https://opendart.fss.or.kr/api/corpCode.xml"
HYSLR_URL = "https://opendart.fss.or.kr/api/hyslrSttus.json"


def load_universe():
    """Load bare 6-digit ticker strings from universe_raw.csv."""
    if not os.path.exists(UNIVERSE_PATH):
        print(
            f"Error: {UNIVERSE_PATH} not found.\n"
            "Run src/00_build_universe.py first to generate the KOSPI universe.",
            file=sys.stderr,
        )
        sys.exit(1)

    df = pd.read_csv(UNIVERSE_PATH, dtype={"ticker": str})
    if "ticker" not in df.columns:
        print(
            f"Error: {UNIVERSE_PATH} does not contain a 'ticker' column.\n"
            "Re-run src/00_build_universe.py to regenerate it.",
            file=sys.stderr,
        )
        sys.exit(1)

    tickers = df["ticker"].dropna().tolist()
    log.info("Loaded %d tickers from %s.", len(tickers), UNIVERSE_PATH)
    return tickers


def get_corp_code_map(api_key):
    """Return dict {stock_code: corp_code} from DART, using cache if available."""
    if os.path.exists(CORP_CODE_CACHE):
        df = pd.read_csv(CORP_CODE_CACHE, dtype=str)
        mapping = dict(zip(df["stock_code"], df["corp_code"]))
        log.info("Loaded corp_code map from cache (%d entries).", len(mapping))
        return mapping

    log.info("Downloading corp_code map from DART API...")
    r = requests.get(CORP_CODE_URL, params={"crtfc_key": api_key}, timeout=60)
    r.raise_for_status()
    z = zipfile.ZipFile(io.BytesIO(r.content))
    xml_data = z.read("CORPCODE.xml")
    root = ET.fromstring(xml_data)

    rows = []
    for item in root.findall("list"):
        code = item.findtext("corp_code", "").strip()
        stock = item.findtext("stock_code", "").strip()
        name = item.findtext("corp_name", "").strip()
        if stock:
            rows.append({"stock_code": stock, "corp_code": code, "corp_name": name})

    df = pd.DataFrame(rows)
    df.to_csv(CORP_CODE_CACHE, index=False)
    mapping = dict(zip(df["stock_code"], df["corp_code"]))
    log.info("Downloaded and cached corp_code map (%d listed firms).", len(mapping))
    return mapping


def pull_hyslr_shareholder(corp_code, api_key):
    """Return (controlling_pct_largest, controlling_pct_group) for one firm.

    Uses hyslrSttus.json endpoint with reprt_code="11011" (annual report).
    Falls back to reprt_code="11014" (semi-annual) if annual returns no data.
    Returns (None, None) if both attempts yield no data.
    """
    for reprt_code in ("11011", "11014"):
        time.sleep(0.5)
        try:
            r = requests.get(
                HYSLR_URL,
                params={
                    "crtfc_key": api_key,
                    "corp_code": corp_code,
                    "bsns_year": "2023",
                    "reprt_code": reprt_code,
                },
                timeout=20,
            )
            r.raise_for_status()
        except requests.HTTPError:
            log.warning("HTTP error for corp_code=%s reprt_code=%s", corp_code, reprt_code)
            continue

        data = r.json()
        if data.get("status") != "000":
            # No data for this report code; try fallback
            continue

        rows = data.get("list", [])
        # Use common shares only for percentage calculation
        common = [row for row in rows if row.get("stock_knd") == "보통주"]
        if not common:
            common = rows  # fallback: use all share classes

        # Largest single holder: 최대주주 본인
        largest_rows = [r for r in common if r.get("relate") == "최대주주 본인"]
        # Group total: 최대주주 본인 + 최대주주의 특수관계인
        group_rows = [
            r for r in common
            if r.get("relate") in ("최대주주 본인", "최대주주의 특수관계인")
        ]

        def sum_pct(row_list):
            total = 0.0
            for row in row_list:
                try:
                    total += float(row.get("trmend_posesn_stock_qota_rt", 0) or 0)
                except (ValueError, TypeError):
                    pass
            return total if total > 0 else None

        largest_pct = sum_pct(largest_rows)
        group_pct = sum_pct(group_rows)

        if largest_pct is not None or group_pct is not None:
            return largest_pct, group_pct

    return None, None


def main():
    load_dotenv()
    api_key = os.environ.get("FSS_API_KEY")
    if not api_key:
        print(
            "Error: FSS_API_KEY not set.\n"
            "Add FSS_API_KEY to your .env file.",
            file=sys.stderr,
        )
        sys.exit(1)

    os.makedirs(DART_DIR, exist_ok=True)

    tickers = load_universe()
    corp_code_map = get_corp_code_map(api_key)

    results = []
    no_dart_match = []

    for i, ticker in enumerate(tickers, 1):
        corp_code = corp_code_map.get(ticker)
        if corp_code is None:
            no_dart_match.append(ticker)
            continue

        largest_pct, group_pct = pull_hyslr_shareholder(corp_code, api_key)
        if largest_pct is None and group_pct is None:
            no_dart_match.append(ticker)
            continue

        results.append({
            "ticker": ticker,
            "controlling_pct_largest": largest_pct,
            "controlling_pct_group": group_pct,
        })

        if i % 50 == 0:
            log.info("Processed %d / %d tickers...", i, len(tickers))

    if no_dart_match:
        print(f"No DART match for {len(no_dart_match)} tickers: {no_dart_match}")

    df = pd.DataFrame(results)
    df.to_csv(OUTPUT_PATH, index=False)

    log.info("All done. Verify outputs:")
    for path in [OUTPUT_PATH, CORP_CODE_CACHE]:
        if os.path.exists(path):
            log.info("%s (%d bytes)", path, os.path.getsize(path))
        else:
            log.error("MISSING: %s", path)

    log.info(
        "Saved controlling_shareholder.csv: %d rows x %d columns.",
        len(df),
        len(df.columns),
    )


if __name__ == "__main__":
    main()