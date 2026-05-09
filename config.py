"""
config.py — Project-wide constants for the Korea Discount study.

FIREWALL: Event dates are defined here and MUST be imported from this module
by all analysis scripts. Never re-define or hard-code event dates elsewhere.
This structural constraint eliminates look-ahead bias at the code level.

Japan reform event dates (locked to official policy records):
  - STEWARDSHIP_CODE_DATE : 2014-02-01
      FSC Japan Stewardship Code — announced and published February 2014.
  - CGC_DATE              : 2015-06-01
      Tokyo Stock Exchange Corporate Governance Code — effective June 2015.
  - TSE_PB_REFORM_DATE    : 2023-03-01
      TSE request to companies trading below P/B 1.0x — announced March 2023.
"""

import datetime

# ---------------------------------------------------------------------------
# Japan Reform Event Dates (DO NOT MODIFY)
# ---------------------------------------------------------------------------

STEWARDSHIP_CODE_DATE: datetime.date = datetime.date(2014, 2, 1)
CGC_DATE:              datetime.date = datetime.date(2015, 6, 1)
TSE_PB_REFORM_DATE:    datetime.date = datetime.date(2023, 3, 1)

JAPAN_EVENT_DATES: list[datetime.date] = [
    STEWARDSHIP_CODE_DATE,
    CGC_DATE,
    TSE_PB_REFORM_DATE,
]

JAPAN_EVENT_LABELS: dict[datetime.date, str] = {
    STEWARDSHIP_CODE_DATE: "Japan Stewardship Code (Feb 2014)",
    CGC_DATE:              "TSE Corporate Governance Code (Jun 2015)",
    TSE_PB_REFORM_DATE:    "TSE P/B Reform Request (Mar 2023)",
}

KOREA_VALUE_UP_NARROW_EVENT_DATES: list[datetime.date] = [
    datetime.date(2024, 2, 26),
    datetime.date(2024, 5, 2),
    datetime.date(2024, 8, 12),
]

KOREA_VALUE_UP_NARROW_EVENT_LABELS: dict[datetime.date, str] = {
    datetime.date(2024, 2, 26): "Korea Value-Up Program Launch (Feb 2024)",
    datetime.date(2024, 5, 2): "Korea Value-Up Guidelines Unveiled (May 2024)",
    datetime.date(2024, 8, 12): "Korea Value-Up Implementation Push (Aug 2024)",
}

KOREA_VALUE_UP_SPACED_EVENT_DATES: list[datetime.date] = [
    datetime.date(2024, 2, 26),
    datetime.date(2025, 7, 9),
    datetime.date(2026, 2, 24),
]

KOREA_VALUE_UP_SPACED_EVENT_LABELS: dict[datetime.date, str] = {
    datetime.date(2024, 2, 26): "Korea Value-Up Program Launch (Feb 2024)",
    datetime.date(2025, 7, 9): "Mandatory Governance Disclosure Expansion (Jul 2025)",
    datetime.date(2026, 2, 24): "Value-Up Dividend Disclosure Rule (Feb 2026)",
}

PAPER_STUDY_END: datetime.date = datetime.date(2024, 12, 31)
FOLLOW_ON_STUDY_END: datetime.date = datetime.date(2026, 4, 30)

KOREA_EVENT_SET_POLICY: dict[str, dict[str, object]] = {
    "primary": {
        "set_name": "narrow_2024_rollout",
        "dates": KOREA_VALUE_UP_NARROW_EVENT_DATES,
        "labels": KOREA_VALUE_UP_NARROW_EVENT_LABELS,
        "max_post_months": 20,
    },
    "robustness": {
        "set_name": "spaced_follow_through",
        "dates": KOREA_VALUE_UP_SPACED_EVENT_DATES,
        "labels": KOREA_VALUE_UP_SPACED_EVENT_LABELS,
        "max_post_months": 2,
    },
}

EVENT_DATES = JAPAN_EVENT_DATES
EVENT_LABELS = JAPAN_EVENT_LABELS

# ---------------------------------------------------------------------------
# Study Universe
# ---------------------------------------------------------------------------

COUNTRIES: list[str] = ["KOSPI", "TOPIX", "SP500", "MSCI_EM"]

# ---------------------------------------------------------------------------
# Data Paths
# ---------------------------------------------------------------------------

from pathlib import Path

PROJECT_ROOT: Path = Path(__file__).resolve().parent
RAW_DIR:      Path = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR:Path = PROJECT_ROOT / "data" / "processed"
OUTPUT_DIR:   Path = PROJECT_ROOT / "output"

# ---------------------------------------------------------------------------
# Known Data Limitations (documented here for traceability)
# ---------------------------------------------------------------------------

# kospi_pe_2004_2026.csv starts 2004-05-16 (not 2004-01-16).
# Four months of KOSPI P/E are unavailable at series start.
# build_panel.py will carry NaN for KOSPI PE rows 2004-01 through 2004-04.
KOSPI_PE_SERIES_START: datetime.date = datetime.date(2004, 5, 1)
