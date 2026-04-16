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

EVENT_DATES: list[datetime.date] = [
    STEWARDSHIP_CODE_DATE,
    CGC_DATE,
    TSE_PB_REFORM_DATE,
]

EVENT_LABELS: dict[datetime.date, str] = {
    STEWARDSHIP_CODE_DATE: "Japan Stewardship Code (Feb 2014)",
    CGC_DATE:              "TSE Corporate Governance Code (Jun 2015)",
    TSE_PB_REFORM_DATE:    "TSE P/B Reform Request (Mar 2023)",
}

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
