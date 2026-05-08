"""
Bloomberg API wrappers for Korea Discount study.

Exposes three functions that return pandas DataFrames / lists:
  bdp(securities, fields, overrides=None) -> DataFrame
  bdh(securities, fields, start_date, end_date, periodicity="DAILY") -> DataFrame
  bds(security, field) -> list[str]

IMPORTANT: blpapi must be installed at a Bloomberg terminal.
Without blpapi, importing this module is safe (no error), but calling any
function raises RuntimeError with an informative message.

Run connection test:
  python utils/bbg.py --test
"""

import os
import sys
import time

import pandas as pd
from dotenv import load_dotenv

load_dotenv()

try:
    import blpapi

    _BBG_AVAILABLE = True
except ImportError:
    _BBG_AVAILABLE = False

_session = None


def _require_bbg():
    """Raise RuntimeError with install instructions if blpapi is unavailable."""
    if not _BBG_AVAILABLE:
        raise RuntimeError(
            "blpapi is not installed.\n"
            "Run this script at a Bloomberg terminal:\n"
            "  pip install blpapi\n"
            "  python utils/bbg.py --test\n"
        )


def _get_session():
    """Return and lazily start the global blpapi session."""
    global _session
    _require_bbg()
    if _session is None:
        so = blpapi.SessionOptions()
        so.setServerHost(os.getenv("BBG_HOST", "127.0.0.1"))
        so.setServerPort(int(os.getenv("BBG_PORT", "8194")))
        _session = blpapi.Session(so)
        if not _session.start():
            raise RuntimeError(
                "Failed to start Bloomberg session. "
                "Check that you are at a Bloomberg terminal and the terminal is logged in."
            )
        if not _session.openService("//blp/refdata"):
            raise RuntimeError("Failed to open Bloomberg refdata service.")
    return _session


def _raise_bbg_errors(msg, security_data=None):
    """Check for Bloomberg response or per-security errors and raise RuntimeError."""
    if msg.hasElement("responseError"):
        raise RuntimeError(
            f"Bloomberg response error: {msg.getElement('responseError')}"
        )
    if security_data is not None and security_data.hasElement("securityError"):
        security = security_data.getElementAsString("security")
        raise RuntimeError(
            f"Bloomberg security error for {security}: "
            f"{security_data.getElement('securityError')}"
        )
    if security_data is not None and security_data.hasElement("fieldExceptions"):
        security = security_data.getElementAsString("security")
        raise RuntimeError(
            f"Bloomberg field exceptions for {security}: "
            f"{security_data.getElement('fieldExceptions')}"
        )


def bdp(securities, fields, overrides=None):
    """
    Bloomberg BDP point-in-time reference data.

    Args:
        securities: str or list of Bloomberg ticker strings (e.g. "005930 KS Equity")
        fields: str or list of Bloomberg field mnemonics (e.g. "PX_TO_BOOK_RATIO")
        overrides: dict of override fieldId -> value pairs, e.g.
            {"FUNDAMENTAL_DATABASE_DATE": "20231231"} to pin snapshot to FY2023.

    Returns:
        pd.DataFrame with index=securities, columns=fields.
        Missing values represented as None / NaN.
    """
    session = _get_session()
    svc = session.getService("//blp/refdata")
    request = svc.createRequest("ReferenceDataRequest")

    if isinstance(securities, str):
        securities = [securities]
    if isinstance(fields, str):
        fields = [fields]

    for sec in securities:
        request.append("securities", sec)
    for fld in fields:
        request.append("fields", fld)

    if overrides:
        ovrd_elem = request.getElement("overrides")
        for key, value in overrides.items():
            override = ovrd_elem.appendElement()
            override.setElement("fieldId", key)
            override.setElement("value", str(value))

    session.sendRequest(request)

    rows = {}
    while True:
        ev = session.nextEvent(500)
        for msg in ev:
            _raise_bbg_errors(msg)
            sec_data = msg.getElement("securityData")
            for i in range(sec_data.numValues()):
                sd = sec_data.getValueAsElement(i)
                _raise_bbg_errors(msg, sd)
                ticker = sd.getElementAsString("security")
                fd = sd.getElement("fieldData")
                rows[ticker] = {}
                for fld in fields:
                    if fd.hasElement(fld):
                        try:
                            rows[ticker][fld] = fd.getElementAsString(fld)
                        except Exception:
                            rows[ticker][fld] = None
                    else:
                        rows[ticker][fld] = None
        if ev.eventType() == blpapi.Event.RESPONSE:
            break

    return pd.DataFrame(rows).T


def bdh(securities, fields, start_date, end_date, periodicity="DAILY"):
    """
    Bloomberg BDH historical time series.

    Args:
        securities: str or list of Bloomberg ticker strings
        fields: str or list of Bloomberg field mnemonics (e.g. "PX_LAST")
        start_date: ISO date string "YYYY-MM-DD" (dashes stripped internally)
        end_date: ISO date string "YYYY-MM-DD"
        periodicity: "DAILY" | "MONTHLY" | "YEARLY" (default: "DAILY")

    Returns:
        pd.DataFrame in long format with columns:
            security (str), date (datetime.date), <field1>, <field2>, ...
        Batches requests if len(securities) > 100 to avoid throttling.
    """
    if isinstance(securities, str):
        securities = [securities]
    if isinstance(fields, str):
        fields = [fields]

    batch_size = 100
    all_rows = []

    for batch_start in range(0, len(securities), batch_size):
        batch = securities[batch_start : batch_start + batch_size]
        rows = _bdh_batch(batch, fields, start_date, end_date, periodicity)
        all_rows.extend(rows)
        if batch_start + batch_size < len(securities):
            time.sleep(0.5)

    if not all_rows:
        return pd.DataFrame(columns=["security", "date"] + list(fields))
    return pd.DataFrame(all_rows)


def _bdh_batch(securities, fields, start_date, end_date, periodicity):
    """Run one BDH batch request and return a list of row dictionaries."""
    session = _get_session()
    svc = session.getService("//blp/refdata")
    request = svc.createRequest("HistoricalDataRequest")

    for sec in securities:
        request.append("securities", sec)
    for fld in fields:
        request.append("fields", fld)

    request.set("startDate", start_date.replace("-", ""))
    request.set("endDate", end_date.replace("-", ""))
    request.set("periodicitySelection", periodicity)

    session.sendRequest(request)

    rows = []
    while True:
        ev = session.nextEvent(500)
        for msg in ev:
            _raise_bbg_errors(msg)
            sec_data = msg.getElement("securityData")
            _raise_bbg_errors(msg, sec_data)
            ticker = sec_data.getElementAsString("security")
            fd_array = sec_data.getElement("fieldData")
            for j in range(fd_array.numValues()):
                pt = fd_array.getValueAsElement(j)
                row = {
                    "security": ticker,
                    "date": pt.getElementAsDatetime("date").date(),
                }
                for fld in fields:
                    if pt.hasElement(fld):
                        try:
                            row[fld] = pt.getElementAsFloat(fld)
                        except Exception:
                            row[fld] = None
                    else:
                        row[fld] = None
                rows.append(row)
        if ev.eventType() == blpapi.Event.RESPONSE:
            break

    return rows


def bds(security, field):
    """
    Bloomberg BDS bulk reference data for array-valued fields.

    Designed for INDX_MEMBERS to pull KOSPI constituents:
        bds("KOSPI Index", "INDX_MEMBERS")

    The sub-element name for INDX_MEMBERS tickers can vary by Bloomberg API
    version. This implementation tries the known key first, then falls back
    to iterating sub-elements. Verify output at the Bloomberg terminal during
    the connection test; fallback mode logs element names to stderr.

    Returns:
        list of str ticker strings from the bulk field.
    """
    session = _get_session()
    svc = session.getService("//blp/refdata")
    request = svc.createRequest("ReferenceDataRequest")
    request.append("securities", security)
    request.append("fields", field)
    session.sendRequest(request)

    results = []
    while True:
        ev = session.nextEvent(500)
        for msg in ev:
            _raise_bbg_errors(msg)
            sec_data_elem = msg.getElement("securityData")
            sd = sec_data_elem.getValueAsElement(0)
            _raise_bbg_errors(msg, sd)
            fd = sd.getElement("fieldData")
            bulk = fd.getElement(field)
            for i in range(bulk.numValues()):
                elem = bulk.getValueAsElement(i)
                try:
                    ticker = elem.getElementAsString("Member Ticker and Exchange Code")
                except Exception:
                    names = [
                        str(elem.getElement(k).name())
                        for k in range(elem.numElements())
                    ]
                    print(
                        f"[bbg.bds] INDX_MEMBERS sub-element keys: {names}. "
                        "Update bds() if 'Member Ticker and Exchange Code' is wrong.",
                        file=sys.stderr,
                    )
                    if elem.numElements() > 0:
                        ticker = elem.getElement(0).getValueAsString()
                    else:
                        continue
                results.append(ticker)
        if ev.eventType() == blpapi.Event.RESPONSE:
            break

    return results


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        if not _BBG_AVAILABLE:
            print(
                "Error: blpapi is not installed.\n"
                "Install at a Bloomberg terminal: pip install blpapi",
                file=sys.stderr,
            )
            sys.exit(1)
        try:
            _get_session()
            host = os.getenv("BBG_HOST", "127.0.0.1")
            port = os.getenv("BBG_PORT", "8194")
            print("Bloomberg session started OK.")
            print(f"  Host: {host}  Port: {port}")
        except RuntimeError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            sys.exit(1)
    else:
        print("Usage: python utils/bbg.py --test", file=sys.stderr)
        sys.exit(1)
