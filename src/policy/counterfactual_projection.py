"""
counterfactual_projection.py - Japan-calibrated illustrative KOSPI P/B projection.

Reads data/processed/panel.parquet (KOSPI historical series) and
output/robustness/synthetic_control_gap.csv (post-reform gap series from
synthetic_control.py) to compute an illustrative projection of KOSPI P/B
if Korea were to implement a P/B governance reform analogous to Japan's
2023 TSE reform.

Outputs: output/figures/figure4_counterfactual_projection.pdf
"""
import logging
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import config

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s", stream=sys.stdout)

FIGURES_DIR = config.OUTPUT_DIR / "figures"
ROBUSTNESS_DIR = config.OUTPUT_DIR / "robustness"
RMSPE = 0.2893  # Pre-treatment RMSPE from synthetic_control_weights.csv


def main() -> None:
    # Read KOSPI historical P/B series
    panel = pd.read_parquet(config.PROCESSED_DIR / "panel.parquet")
    kospi = panel[panel["country"] == "KOSPI"].sort_values("date").reset_index(drop=True)
    kospi["date"] = pd.to_datetime(kospi["date"])

    # Read synthetic control gap series (written by synthetic_control.py)
    gap_path = ROBUSTNESS_DIR / "synthetic_control_gap.csv"
    gap_df = pd.read_csv(gap_path)

    # T-05-02: Validate CSV columns are exactly ["date", "gap"]
    assert list(gap_df.columns) == ["date", "gap"], (
        f"synthetic_control_gap.csv has unexpected columns: {gap_df.columns.tolist()}. "
        f"Expected ['date', 'gap']. Re-run synthetic_control.py."
    )
    gap_df["date"] = pd.to_datetime(gap_df["date"])

    # Extract post-reform gap: months 1-18 after TSE_PB_REFORM_DATE (2023-03-01)
    reform_date = pd.Timestamp(config.TSE_PB_REFORM_DATE)
    cutoff_date = reform_date + pd.DateOffset(months=18)
    post_reform = gap_df[
        (gap_df["date"] >= reform_date) & (gap_df["date"] <= cutoff_date)
    ].copy()

    if len(post_reform) < 2:
        logging.warning("Fewer than 2 post-reform gap observations; projection may be unreliable.")

    # Average monthly P/B change in post-reform gap (month-over-month diff of gap series)
    monthly_lift = post_reform["gap"].diff().mean()
    logging.info("Average monthly P/B lift (months 1-18 post-reform): %.4f", monthly_lift)

    # T-05-03: Guard against malformed gap series producing NaN monthly_lift
    assert not pd.isna(monthly_lift), (
        "monthly_lift is NaN — synthetic_control_gap.csv may be malformed or have "
        "fewer than 2 post-reform observations. Re-run synthetic_control.py."
    )

    # Project from last KOSPI observation at or before 2024-12-31
    kospi_2024 = kospi[kospi["date"] <= pd.Timestamp("2024-12-31")]
    base_level = float(kospi_2024["pb"].iloc[-1])
    base_date = kospi_2024["date"].iloc[-1]
    logging.info("KOSPI base P/B level (%.0f): %.4f", base_date.year, base_level)

    # 60-month (5-year) forward projection
    proj_dates = pd.date_range(start=base_date, periods=61, freq="MS")[1:]
    steps = np.arange(1, 61)
    proj_values = base_level + monthly_lift * steps
    upper_band = proj_values + RMSPE
    lower_band = proj_values - RMSPE

    # Plot
    fig, ax = plt.subplots(figsize=(10, 5))

    # Historical KOSPI P/B (solid black line)
    ax.plot(kospi["date"], kospi["pb"], color="black", linewidth=1.2, label="KOSPI P/B (historical)")

    # Projection (dashed)
    ax.plot(proj_dates, proj_values, color="black", linewidth=1.2, linestyle="--",
            label="Illustrative projection (Korea reform scenario)")

    # Uncertainty band
    ax.fill_between(proj_dates, lower_band, upper_band, alpha=0.15, color="grey",
                    label=f"Uncertainty band (\u00b1RMSPE = \u00b1{RMSPE})")

    # Reform date vertical line
    ax.axvline(x=reform_date, color="grey", linestyle="dashed", linewidth=0.8,
               label="Japan TSE P/B Reform (Mar 2023)")

    ax.set_ylabel("P/B Ratio")
    ax.set_xlabel("")
    ax.set_title(
        "Illustrative projection assuming Korea implements a P/B governance reform\n"
        "analogous to Japan's 2023 TSE reform"
    )
    ax.legend(fontsize=8, loc="upper left")

    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    output_path = FIGURES_DIR / "figure4_counterfactual_projection.pdf"
    fig.savefig(output_path, dpi=300, bbox_inches="tight", format="pdf",
                metadata={"CreationDate": None, "ModDate": None})
    plt.close(fig)
    logging.info("Saved %s", output_path)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
