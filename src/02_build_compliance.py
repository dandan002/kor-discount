"""
Compliance classification for Korea Discount study.

READS: data/raw/krx/compliance_coded.csv (hand-coded by researcher)
OUTPUTS:
  data/processed/compliance.csv - three-way classification (0/1/2), all firms
  data/processed/events.csv - disclosure dates for compliant firms (codes 1 and 2)

Run from project root:
    python src/02_build_compliance.py

Requires data/raw/krx/compliance_coded.csv to be hand-coded before running.
Required columns: ticker (6-digit), compliance_code (0/1/2), disclosure_date (YYYY-MM-DD or blank for code 0).
"""

import logging
import os
import sys

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.stats import cohens_kappa

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

COMPLIANCE_PATH = os.path.join(PROJECT_ROOT, "data", "raw", "krx", "compliance_coded.csv")
COMPLIANCE_R2_PATH = os.path.join(PROJECT_ROOT, "data", "raw", "krx", "compliance_coded_r2.csv")
PROCESSED_DIR = os.path.join(PROJECT_ROOT, "data", "processed")
COMPLIANCE_OUT = os.path.join(PROCESSED_DIR, "compliance.csv")
EVENTS_OUT = os.path.join(PROCESSED_DIR, "events.csv")


def main():
    os.makedirs(PROCESSED_DIR, exist_ok=True)

    # Missing-input guard
    if not os.path.exists(COMPLIANCE_PATH):
        print(
            f"Error: {COMPLIANCE_PATH} not found.\n"
            "Hand-code KRX Value-Up disclosures and save as data/raw/krx/compliance_coded.csv\n"
            "Required columns: ticker (6-digit), compliance_code (0/1/2), "
            "disclosure_date (YYYY-MM-DD, blank for code 0)",
            file=sys.stderr,
        )
        sys.exit(1)

    # Load compliance data
    df = pd.read_csv(COMPLIANCE_PATH, dtype={"ticker": str, "compliance_code": int})

    # Schema validation
    required = {"ticker", "compliance_code", "disclosure_date"}
    missing_cols = required - set(df.columns)
    if missing_cols:
        print(
            f"Error: compliance_coded.csv missing columns: {missing_cols}",
            file=sys.stderr,
        )
        sys.exit(1)

    log.info("Loaded %d firms from %s.", len(df), COMPLIANCE_PATH)

    # Missingness report
    log.info("Missingness: %s", df.isna().sum().to_dict())

    # Validate compliance_code values are in {0, 1, 2}
    invalid_codes = set(df["compliance_code"].unique()) - {0, 1, 2}
    if invalid_codes:
        log.warning(
            "compliance_code contains out-of-range values: %s. "
            "Expected 0, 1, or 2 only.",
            invalid_codes,
        )

    # Save compliance.csv (all rows)
    df.to_csv(COMPLIANCE_OUT, index=False)
    log.info("Saved compliance.csv: %d rows.", len(df))

    # Filter events: codes 1 and 2 only
    events = df[df["compliance_code"].isin([1, 2])].copy()
    events.to_csv(EVENTS_OUT, index=False)
    log.info("Saved events.csv: %d rows (codes 1 and 2).", len(events))

    # Optional kappa check (per D-04)
    if os.path.exists(COMPLIANCE_R2_PATH):
        r2 = pd.read_csv(COMPLIANCE_R2_PATH, dtype={"ticker": str, "compliance_code": int})
        merged = df.merge(r2[["ticker", "compliance_code"]], on="ticker", suffixes=("_r1", "_r2"))
        kappa, pval = cohens_kappa(
            merged["compliance_code_r1"].tolist(),
            merged["compliance_code_r2"].tolist(),
            labels=[0, 1, 2],
        )
        print(f"Inter-rater Cohen's kappa = {kappa:.3f} (p = {pval:.4f})")
    else:
        log.info("No compliance_coded_r2.csv found; skipping kappa check.")

    # Final output verification
    for path in [COMPLIANCE_OUT, EVENTS_OUT]:
        if os.path.exists(path):
            log.info("%s (%d bytes)", path, os.path.getsize(path))
        else:
            log.error("MISSING: %s", path)


if __name__ == "__main__":
    main()