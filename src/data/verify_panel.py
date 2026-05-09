"""
verify_panel.py - Verify data/processed/panel.parquet against Phase 1 criteria.

Exit codes:
  0 - all checks passed
  1 - one or more checks failed (details printed to stdout)

Run: python src/data/verify_panel.py
"""

import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import config

PASS = "[PASS]"
FAIL = "[FAIL]"

REQUIRED_SERIES = [
    "kospi_pb",
    "kospi_pe",
    "topix_pb",
    "topix_pe",
    "sp500_pb",
    "sp500_pe",
    "msci_em_pb",
    "msci_em_pe",
]


def get_pb(df: pd.DataFrame, country: str, year: int, month: int) -> float | None:
    """Return the first P/B observation for a country and calendar month."""
    if not {"country", "date", "pb"}.issubset(df.columns):
        return None

    mask = (
        (df["country"] == country)
        & (df["date"].dt.year == year)
        & (df["date"].dt.month == month)
    )
    rows = df[mask]
    if len(rows) == 0:
        return None
    return float(rows["pb"].iloc[0])


def check_gfc_compression(
    df: pd.DataFrame,
    country: str,
) -> tuple[str, bool, str]:
    """Check that October 2008 P/B is lower than October 2007 P/B."""
    pre = get_pb(df, country, 2007, 10)
    gfc = get_pb(df, country, 2008, 10)
    passed = pre is not None and gfc is not None and gfc < pre
    if pre is not None and gfc is not None:
        detail = f"{country} pb: 2007-10={pre:.4f}, 2008-10={gfc:.4f}"
    else:
        detail = "data missing for comparison dates"

    return (
        f"GFC compression: {country} pb(2008-10) < pb(2007-10)",
        passed,
        detail,
    )


def check_manifest() -> tuple[str, bool, str]:
    """Verify the raw data manifest exists and lists required core series."""
    manifest_path = PROJECT_ROOT / "data" / "raw" / "MANIFEST.md"

    if not manifest_path.exists():
        return (
            "Manifest: data/raw/MANIFEST.md lists all 8 series",
            False,
            f"MANIFEST.md not found at {manifest_path}",
        )

    manifest_text = manifest_path.read_text()
    missing = [series for series in REQUIRED_SERIES if series not in manifest_text]
    passed = len(missing) == 0
    detail = (
        f"missing series: {missing}"
        if missing
        else f"all 8 series listed ({manifest_path})"
    )
    return ("Manifest: data/raw/MANIFEST.md lists all 8 series", passed, detail)


def run_checks(
    df: pd.DataFrame,
    manifest_result: tuple[str, bool, str],
) -> list[tuple[str, bool, str]]:
    """
    Returns list of (check_name, passed, detail) tuples.
    """
    results: list[tuple[str, bool, str]] = []

    expected_cols = {"date", "country", "pb", "pe"}
    actual_cols = set(df.columns)
    has_expected_cols = actual_cols == expected_cols
    detail = f"columns: {sorted(actual_cols)}" if not has_expected_cols else ""
    results.append(("Schema: columns are (date, country, pb, pe)", has_expected_cols, detail))

    required_cols_present = expected_cols.issubset(actual_cols)

    if required_cols_present:
        dtypes_passed = (
            pd.api.types.is_datetime64_any_dtype(df["date"])
            and pd.api.types.is_float_dtype(df["pb"])
            and pd.api.types.is_float_dtype(df["pe"])
        )
        detail = f"dtypes: {df.dtypes.to_dict()}" if not dtypes_passed else ""
    else:
        dtypes_passed = False
        detail = f"missing columns: {sorted(expected_cols - actual_cols)}"
    results.append(("Schema: date=datetime64, pb=float64, pe=float64", dtypes_passed, detail))

    if "country" in df.columns:
        expected_countries = set(config.COUNTRIES)
        actual_countries = set(df["country"].unique())
        countries_passed = actual_countries == expected_countries
        detail = f"found: {sorted(actual_countries)}" if not countries_passed else ""
    else:
        countries_passed = False
        detail = "missing country column"
    results.append(("Countries: exactly KOSPI, TOPIX, SP500, MSCI_EM", countries_passed, detail))

    if "date" in df.columns and pd.api.types.is_datetime64_any_dtype(df["date"]):
        min_date = df["date"].min()
        max_date = df["date"].max()
        date_range_passed = (
            min_date <= pd.Timestamp("2004-01-31")
            and max_date >= pd.Timestamp("2024-12-31")
        )
        detail = f"range: {min_date.date()} to {max_date.date()}"
    else:
        date_range_passed = False
        detail = "missing date column or date is not datetime64"
    results.append(("Date range: 2004-01-31 to >= 2024-12-31", date_range_passed, detail))

    if "date" in df.columns and pd.api.types.is_datetime64_any_dtype(df["date"]):
        all_month_end = bool(df["date"].dt.is_month_end.all())
        n_non_month_end = int((~df["date"].dt.is_month_end).sum())
        detail = f"{n_non_month_end} non-month-end dates found" if not all_month_end else ""
    else:
        all_month_end = False
        detail = "missing date column or date is not datetime64"
    results.append(("All dates are month-end", all_month_end, detail))

    if "pb" in df.columns:
        n_nan_pb = int(df["pb"].isna().sum())
        nan_pb_passed = n_nan_pb == 0
        detail = f"{n_nan_pb} NaN pb rows found" if not nan_pb_passed else ""
    else:
        nan_pb_passed = False
        detail = "missing pb column"
    results.append(("NaN pb: zero rows", nan_pb_passed, detail))

    if {"country", "date", "pe"}.issubset(df.columns):
        nan_pe_rows = df[df["pe"].isna()]
        n_nan_pe = len(nan_pe_rows)
        all_kospi = (nan_pe_rows["country"] == "KOSPI").all() if n_nan_pe > 0 else True
        all_pre_may_2004 = (
            (nan_pe_rows["date"] < pd.Timestamp("2004-05-01")).all()
            if n_nan_pe > 0
            else True
        )
        nan_pe_passed = (n_nan_pe == 4) and all_kospi and all_pre_may_2004
        detail = (
            "4 KOSPI NaN pe rows for 2004-01 to 2004-04 (documented)"
            if nan_pe_passed
            else (
                f"found {n_nan_pe} NaN pe rows; "
                f"countries={nan_pe_rows['country'].unique().tolist() if n_nan_pe > 0 else []}"
            )
        )
    else:
        nan_pe_passed = False
        detail = "missing country, date, or pe column"
    results.append(
        (
            "NaN pe: exactly 4 KOSPI rows (2004-01 to 2004-04)",
            nan_pe_passed,
            detail,
        )
    )

    for country in config.COUNTRIES:
        results.append(check_gfc_compression(df, country))

    results.append(manifest_result)
    return results


def main() -> None:
    panel_path = config.PROCESSED_DIR / "panel.parquet"
    if not panel_path.exists():
        print(f"{FAIL} panel.parquet not found at {panel_path}")
        print("       Run: python src/data/build_panel.py")
        sys.exit(1)

    manifest_result = check_manifest()
    df = pd.read_parquet(panel_path)
    results = run_checks(df, manifest_result)

    print("\n=== Panel Verification ===")
    all_passed = True
    for name, passed, detail in results:
        tag = PASS if passed else FAIL
        print(f"  {tag}  {name}")
        if detail:
            print(f"         {detail}")
        if not passed:
            all_passed = False

    total = len(results)
    n_passed = sum(1 for _, passed, _ in results if passed)
    print(f"\nResult: {n_passed}/{total} checks passed")
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
