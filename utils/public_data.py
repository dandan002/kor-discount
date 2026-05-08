"""
Public-API data wrappers for Korea Discount study.

Drop-in alternative to utils/bbg.py — no Bloomberg terminal required.

Data sources:
  - FinanceDataReader: KOSPI constituent list + listing metadata
  - yfinance: fundamentals (balance sheet / income statement) and price history

Key functions (output formats mirror their bbg.py counterparts):
  get_kospi_universe()                    -> DataFrame  (mirrors bds + bdp metadata)
  get_snapshot(tickers, as_of_year=2023)  -> DataFrame  (mirrors bdp snapshot)
  get_roe_panel(tickers, ...)             -> DataFrame  (mirrors bdh ROE)
  get_returns_panel(tickers, ...)         -> DataFrame  (mirrors bdh PX_LAST)

Ticker format note:
  KRX 6-digit codes (e.g. "005930") are converted to Yahoo Finance format
  ("005930.KS") internally. The security column in returns_panel uses the
  Yahoo Finance format; KOSPI benchmark is "^KS11" (vs "KOSPI Index" in bbg).
"""

import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import pandas as pd
import yfinance as yf

log = logging.getLogger(__name__)

_KS_SUFFIX = ".KS"
KOSPI_YF_TICKER = "^KS11"

_MAX_WORKERS = 8
_RETRY_DELAY = 2.0
_MAX_RETRIES = 3
_INTER_TICKER_SLEEP = 0.35

# Bloomberg snapshot fields this module replicates
_SNAPSHOT_FIELDS = [
    "PX_TO_BOOK_RATIO",
    "PE_RATIO",
    "RETURN_COM_EQY",
    "RETURN_ON_ASSET",
    "EQY_FLOAT_PCT",
    "CUR_MKT_CAP",
    "EQY_DVD_YLD_IND",
    "TOT_DEBT_TO_TOT_EQY",
    "BS_TOT_ASSET",
    "SALES_GROWTH",
    "CASH_AND_NEAR_CASH_ITEM",
    "DVD_SH_12M",
]


def _to_yf(krx_ticker: str) -> str:
    """Convert 6-digit KRX ticker to Yahoo Finance format (e.g. '005930' -> '005930.KS')."""
    return str(krx_ticker).zfill(6) + _KS_SUFFIX


# ---------------------------------------------------------------------------
# Universe
# ---------------------------------------------------------------------------


def get_kospi_universe() -> pd.DataFrame:
    """
    Pull KOSPI constituent list and firm metadata via FinanceDataReader.

    Returns DataFrame with columns: ticker, name, sector, industry, country, ipo_date.
    Mirrors the output of bds('KOSPI Index', 'INDX_MEMBERS') + bdp metadata.
    """
    try:
        import FinanceDataReader as fdr
    except ImportError:
        raise RuntimeError(
            "FinanceDataReader is not installed.\n"
            "  pip install finance-datareader"
        )

    log.info("Fetching KOSPI constituent list via FinanceDataReader ...")
    raw = fdr.StockListing("KOSPI")
    log.info("  Raw KOSPI listing: %d firms.", len(raw))

    # FinanceDataReader column names vary by version; handle both.
    def _col(df, *candidates):
        for c in candidates:
            if c in df.columns:
                return df[c]
        return pd.Series([""] * len(df), index=df.index)

    result = pd.DataFrame(
        {
            "ticker": _col(raw, "Symbol", "Code").astype(str).str.zfill(6),
            "name": _col(raw, "Name", "Corp"),
            "sector": _col(raw, "Sector", "Industry"),
            "industry": _col(raw, "Industry", "Sector"),
            "country": "KR",
            "ipo_date": pd.to_datetime(
                _col(raw, "ListingDate", "Listing date"), errors="coerce"
            ),
        }
    )
    return result


# ---------------------------------------------------------------------------
# Snapshot (point-in-time cross-section)
# ---------------------------------------------------------------------------


def _safe_get(df: pd.DataFrame, col, *row_keys):
    """Return the first non-null scalar found across row_keys for column col."""
    for key in row_keys:
        try:
            if key in df.index:
                val = df.loc[key, col]
                if pd.notna(val):
                    return float(val)
        except Exception:
            pass
    return None


def _find_col_for_year(df: pd.DataFrame, year: int):
    """Return first column whose .year attribute matches year, or None."""
    matches = [c for c in df.columns if hasattr(c, "year") and c.year == year]
    return matches[0] if matches else None


def _fetch_one_snapshot(yf_ticker: str, as_of_year: int) -> dict:
    """Fetch all 12 snapshot metrics for a single Yahoo Finance ticker."""
    result = {f: None for f in _SNAPSHOT_FIELDS}

    try:
        t = yf.Ticker(yf_ticker)
        bs = t.balance_sheet   # columns = fiscal year-end dates
        inc = t.financials     # income statement
        info = t.info or {}

        if bs is None or bs.empty or inc is None or inc.empty:
            return result

        bc = _find_col_for_year(bs, as_of_year)
        bp = _find_col_for_year(bs, as_of_year - 1)
        ic = _find_col_for_year(inc, as_of_year)
        ip = _find_col_for_year(inc, as_of_year - 1)

        if bc is None or ic is None:
            return result

        equity = _safe_get(
            bs, bc,
            "Stockholders Equity", "Total Stockholder Equity", "Common Stock Equity",
        )
        equity_prev = _safe_get(
            bs, bp,
            "Stockholders Equity", "Total Stockholder Equity", "Common Stock Equity",
        ) if bp else equity

        total_assets = _safe_get(bs, bc, "Total Assets")
        total_assets_prev = _safe_get(bs, bp, "Total Assets") if bp else total_assets

        net_income = _safe_get(
            inc, ic, "Net Income", "Net Income Common Stockholders",
        )
        revenue = _safe_get(inc, ic, "Total Revenue")
        revenue_prev = _safe_get(inc, ip, "Total Revenue") if ip else None

        cash = _safe_get(
            bs, bc,
            "Cash And Cash Equivalents",
            "Cash Cash Equivalents And Short Term Investments",
            "Cash",
        )
        total_debt = _safe_get(bs, bc, "Total Debt", "Long Term Debt")

        shares = info.get("sharesOutstanding") or info.get("impliedSharesOutstanding")
        float_shares = info.get("floatShares")

        # Year-end closing price
        px_hist = t.history(
            start=f"{as_of_year}-12-27",
            end=f"{as_of_year + 1}-01-05",
            auto_adjust=True,
        )
        price = float(px_hist["Close"].iloc[-1]) if not px_hist.empty else None

        avg_equity = (
            (equity + equity_prev) / 2
            if equity is not None and equity_prev is not None
            else equity
        )
        avg_assets = (
            (total_assets + total_assets_prev) / 2
            if total_assets is not None and total_assets_prev is not None
            else total_assets
        )

        # P/B
        if price and equity and shares:
            bvps = equity / shares
            result["PX_TO_BOOK_RATIO"] = price / bvps if bvps else None

        # P/E
        if price and net_income and shares:
            eps = net_income / shares
            result["PE_RATIO"] = price / eps if eps and eps > 0 else None

        # ROE, ROA
        if net_income is not None and avg_equity:
            result["RETURN_COM_EQY"] = net_income / avg_equity
        if net_income is not None and avg_assets:
            result["RETURN_ON_ASSET"] = net_income / avg_assets

        # Float %
        if float_shares and shares:
            result["EQY_FLOAT_PCT"] = float_shares / shares * 100

        # Market cap
        result["CUR_MKT_CAP"] = info.get("marketCap")

        # Dividend yield (%)
        dy = info.get("dividendYield")
        result["EQY_DVD_YLD_IND"] = dy * 100 if dy is not None else None

        # Debt/Equity
        if total_debt is not None and equity:
            result["TOT_DEBT_TO_TOT_EQY"] = total_debt / equity * 100

        result["BS_TOT_ASSET"] = total_assets
        result["CASH_AND_NEAR_CASH_ITEM"] = cash

        # Sales growth (%)
        if revenue is not None and revenue_prev:
            result["SALES_GROWTH"] = (revenue - revenue_prev) / abs(revenue_prev) * 100

        # Dividends paid in as_of_year
        divs = t.dividends
        if divs is not None and not divs.empty:
            yr_divs = divs[divs.index.year == as_of_year]
            result["DVD_SH_12M"] = float(yr_divs.sum()) if not yr_divs.empty else 0.0

    except Exception as exc:
        log.debug("Snapshot fetch failed for %s: %s", yf_ticker, exc)

    return result


def _fetch_with_retry(krx_ticker: str, as_of_year: int) -> tuple[str, dict]:
    yf_ticker = _to_yf(krx_ticker)
    for attempt in range(_MAX_RETRIES):
        try:
            result = _fetch_one_snapshot(yf_ticker, as_of_year)
            time.sleep(_INTER_TICKER_SLEEP)
            return krx_ticker, result
        except Exception as exc:
            if attempt < _MAX_RETRIES - 1:
                delay = _RETRY_DELAY * (2 ** attempt)
                log.info("Retry %d/%d for %s (snapshot): sleeping %.1fs — %s", attempt + 1, _MAX_RETRIES, krx_ticker, delay, exc)
                time.sleep(delay)
            else:
                log.warning("Gave up on %s after %d retries: %s", krx_ticker, _MAX_RETRIES, exc)
    return krx_ticker, {f: None for f in _SNAPSHOT_FIELDS}


def get_snapshot(
    krx_tickers: list,
    as_of_year: int = 2023,
    max_workers: int = _MAX_WORKERS,
) -> pd.DataFrame:
    """
    Pull 12-field fundamental snapshot for each ticker as of fiscal year-end.

    Output: DataFrame indexed by ticker with Bloomberg-named columns
    (PX_TO_BOOK_RATIO, PE_RATIO, RETURN_COM_EQY, ...).
    Mirrors bdp() output.
    """
    log.info(
        "Fetching snapshot for %d tickers (as_of_year=%d, workers=%d) ...",
        len(krx_tickers), as_of_year, max_workers,
    )
    rows = {}

    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = {pool.submit(_fetch_with_retry, t, as_of_year): t for t in krx_tickers}
        done = 0
        for future in as_completed(futures):
            ticker, data = future.result()
            rows[ticker] = data
            done += 1
            if done % 50 == 0 or done == len(krx_tickers):
                log.info("  Snapshot: %d / %d tickers done.", done, len(krx_tickers))

    df = pd.DataFrame(rows).T
    df.index.name = "ticker"
    log.info(
        "Snapshot complete: %d rows, %d non-null cells.",
        len(df), int(df.notna().sum().sum()),
    )
    return df


# ---------------------------------------------------------------------------
# ROE panel (annual, long format)
# ---------------------------------------------------------------------------


def _fetch_roe_one(krx_ticker: str, years: list) -> list:
    yf_ticker = _to_yf(krx_ticker)
    for attempt in range(_MAX_RETRIES):
        try:
            ticker_rows = []
            t = yf.Ticker(yf_ticker)
            bs = t.balance_sheet
            inc = t.financials

            if bs is None or bs.empty or inc is None or inc.empty:
                return ticker_rows

            for year in years:
                bc = _find_col_for_year(bs, year)
                bp = _find_col_for_year(bs, year - 1)
                ic = _find_col_for_year(inc, year)
                if bc is None or ic is None:
                    continue

                equity = _safe_get(
                    bs, bc,
                    "Stockholders Equity", "Total Stockholder Equity", "Common Stock Equity",
                )
                equity_prev = _safe_get(
                    bs, bp,
                    "Stockholders Equity", "Total Stockholder Equity", "Common Stock Equity",
                ) if bp else equity
                net_income = _safe_get(inc, ic, "Net Income", "Net Income Common Stockholders")

                avg_eq = (
                    (equity + equity_prev) / 2
                    if equity is not None and equity_prev is not None
                    else equity
                )
                roe = net_income / avg_eq if net_income is not None and avg_eq else None
                ticker_rows.append({"ticker": krx_ticker, "year": year, "roe": roe})

            time.sleep(_INTER_TICKER_SLEEP)
            return ticker_rows
        except Exception as exc:
            if attempt < _MAX_RETRIES - 1:
                delay = _RETRY_DELAY * (2 ** attempt)
                log.info("Retry %d/%d for %s (ROE): sleeping %.1fs — %s", attempt + 1, _MAX_RETRIES, krx_ticker, delay, exc)
                time.sleep(delay)
            else:
                log.warning("Gave up on %s ROE after %d retries: %s", krx_ticker, _MAX_RETRIES, exc)
                return []
    return []


def get_roe_panel(
    krx_tickers: list,
    start_year: int = 2019,
    end_year: int = 2023,
    max_workers: int = _MAX_WORKERS,
) -> pd.DataFrame:
    """
    Pull annual ROE (net income / avg equity) for start_year..end_year.

    Returns long DataFrame: ticker, year, roe.
    Mirrors bdh() ROE output (with security renamed to ticker).
    """
    years = list(range(start_year, end_year + 1))
    log.info(
        "Fetching ROE panel for %d tickers, years %d-%d (workers=%d) ...",
        len(krx_tickers), start_year, end_year, max_workers,
    )
    rows = []

    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = {pool.submit(_fetch_roe_one, t, years): t for t in krx_tickers}
        done = 0
        for future in as_completed(futures):
            rows.extend(future.result())
            done += 1
            if done % 50 == 0 or done == len(krx_tickers):
                log.info("  ROE panel: %d / %d tickers done.", done, len(krx_tickers))

    df = (
        pd.DataFrame(rows, columns=["ticker", "year", "roe"])
        if rows
        else pd.DataFrame(columns=["ticker", "year", "roe"])
    )
    log.info("ROE panel: %d rows.", len(df))
    return df


# ---------------------------------------------------------------------------
# Returns panel (weekly price history, long format)
# ---------------------------------------------------------------------------


def get_returns_panel(
    krx_tickers: list,
    start_date: str = "2021-01-01",
    end_date: str = "2026-03-31",
    include_benchmark: bool = True,
) -> pd.DataFrame:
    """
    Pull weekly closing prices for all tickers plus KOSPI Index benchmark.

    Returns long DataFrame: security, date, px_last.
    'security' uses Yahoo Finance format ("005930.KS"; benchmark is "^KS11").
    Mirrors bdh() PX_LAST output.

    Uses yfinance bulk download (far more efficient than per-ticker calls).
    """
    yf_tickers = [_to_yf(t) for t in krx_tickers]
    if include_benchmark:
        yf_tickers.append(KOSPI_YF_TICKER)

    log.info(
        "Fetching weekly prices for %d securities (%s to %s) via yfinance bulk download ...",
        len(yf_tickers), start_date, end_date,
    )

    raw = None
    for attempt in range(_MAX_RETRIES):
        try:
            raw = yf.download(
                yf_tickers,
                start=start_date,
                end=end_date,
                interval="1wk",
                auto_adjust=True,
                progress=False,
                threads=True,
            )
            break
        except Exception as exc:
            if attempt < _MAX_RETRIES - 1:
                delay = _RETRY_DELAY * (2 ** attempt)
                log.info("Retry %d/%d for returns panel download: sleeping %.1fs — %s", attempt + 1, _MAX_RETRIES, delay, exc)
                time.sleep(delay)
            else:
                log.error("Failed to download returns panel after %d attempts: %s", _MAX_RETRIES, exc)
                raise

    if raw.empty:
        log.warning("yfinance download returned empty DataFrame.")
        return pd.DataFrame(columns=["security", "date", "px_last"])

    # Extract Close; result may be MultiIndex when >1 ticker
    close = raw["Close"] if isinstance(raw.columns, pd.MultiIndex) else raw[["Close"]]

    long = (
        close.reset_index()
        .rename(columns={"Date": "date", "Datetime": "date"})
        .melt(id_vars="date", var_name="security", value_name="px_last")
        .dropna(subset=["px_last"])
    )
    long["date"] = pd.to_datetime(long["date"])

    log.info(
        "Returns panel: %d rows, %d unique securities.",
        len(long), long["security"].nunique(),
    )
    return long[["security", "date", "px_last"]].reset_index(drop=True)
