"""
synthetic_control.py - ADH (2010) synthetic control for the 2023 TSE P/B reform.

Estimates a synthetic Japan using pysyncon and the donor pool (STOXX600, FTSE100,
MSCI_HK, MSCI_TAIWAN, SP500). Runs in-time and in-space placebo tests (ROBUST-04).
Writes all outputs to output/robustness/ and output/figures/.
"""
import logging
import math
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # headless backend - must come before pyplot import
import matplotlib.pyplot as plt
import pandas as pd
from pysyncon import Dataprep, Synth

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import config

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s", stream=sys.stdout)

ROBUSTNESS_DIR = config.OUTPUT_DIR / "robustness"
FIGURES_DIR = config.OUTPUT_DIR / "figures"

# SUTVA JUSTIFICATION (D-07):
# Donor pool: STOXX600, FTSE100, MSCI_HK, MSCI_TAIWAN, SP500.
# Korea (KOSPI) is excluded to avoid conflating the estimand with the primary
# comparison market (D-05). India and Indonesia are excluded due to high-growth
# P/B premium; they are used in ROBUST-01 placebo tests (D-06).
# STOXX600/FTSE100 governance reforms in this period did not involve TSE-style
# P/B mandates. HSI and MSCI Taiwan are Hong Kong and Taiwan markets with no
# equivalent reform event in 2023. The 19-year pre-treatment window (2004-2023)
# averages out global ESG/governance trends common to all markets.

DONORS = {
    "STOXX600": "stoxx600_pb_2004_2026.csv",
    "FTSE100": "ftse100_pb_2004_2026.csv",
    "MSCI_HK": "msci_hk_pb_2004_2026.csv",
    "MSCI_TAIWAN": "msci_taiwan_pb_2004_2026.csv",
    "SP500": "sp500_pb_2004_2026.csv",
}


def _load_unit_csv(filename: str, unit: str) -> pd.DataFrame:
    """Load and validate one PB series, returning a labelled unit panel."""
    path = config.RAW_DIR / filename
    df = pd.read_csv(path)
    assert "pb" in df.columns, f"{filename} is missing required 'pb' column"
    assert df["pb"].notna().all(), f"{filename} has null 'pb' values"
    df["unit"] = unit
    return df


def load_donor_panel() -> pd.DataFrame:
    """Load TOPIX and donor PB series into one long panel."""
    rows = [_load_unit_csv("topix_pb_2004_2026.csv", "TOPIX")]
    for unit_name, filename in DONORS.items():
        rows.append(_load_unit_csv(filename, unit_name))

    panel = pd.concat(rows, ignore_index=True)
    panel["date"] = pd.to_datetime(panel["date"]).dt.to_period("M").dt.to_timestamp()
    return panel


def run_synth(panel: pd.DataFrame) -> tuple[Synth, Dataprep]:
    """Fit the ADH synthetic control for TOPIX against the donor pool."""
    pre_period = pd.date_range(start="2004-01-01", end="2023-02-01", freq="MS")
    dataprep = Dataprep(
        foo=panel,
        predictors=["pb"],
        predictors_op="mean",
        dependent="pb",
        unit_variable="unit",
        time_variable="date",
        treatment_identifier="TOPIX",
        controls_identifier=list(DONORS.keys()),
        time_predictors_prior=pre_period,
        time_optimize_ssr=pre_period,
        special_predictors=[
            ("pb", pd.date_range("2010-01-01", "2010-12-01", freq="MS"), "mean"),
            ("pb", pd.date_range("2018-01-01", "2018-12-01", freq="MS"), "mean"),
        ],
    )

    synth = Synth()
    synth.fit(
        dataprep=dataprep,
        optim_method="Nelder-Mead",
        optim_initial="equal",
        optim_options={"maxiter": 1000},
    )
    return synth, dataprep


def extract_results(synth: Synth) -> float:
    """Write donor weights and return the pre-treatment RMSPE."""
    weights = synth.weights(round=4)
    rmspe = math.sqrt(synth.mspe())
    weights_df = weights.reset_index()
    weights_df.columns = ["donor", "weight"]
    weights_df["pre_rmspe"] = rmspe
    weights_df.to_csv(ROBUSTNESS_DIR / "synthetic_control_weights.csv", index=False)
    logging.info("Weights saved. RMSPE = %.4f", rmspe)
    if rmspe > 0.15:
        logging.warning("RMSPE %.4f > 0.15 threshold - interpret with caution", rmspe)
    return rmspe


def plot_gap(synth: Synth, dataprep: Dataprep, rmspe: float) -> pd.Series:
    """Write the synthetic-control gap figure and return the gap series."""
    all_period = pd.date_range(start="2004-01-01", end="2026-04-01", freq="MS")
    Z0, Z1 = dataprep.make_outcome_mats(time_period=all_period)
    ts_gap = synth._gaps(Z0=Z0, Z1=Z1)

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(ts_gap.index, ts_gap.values, color="black", linewidth=1, label="Japan gap")
    ax.axhline(0, color="black", linestyle="dashed", linewidth=0.8)
    ax.axvline(
        x=pd.Timestamp(config.TSE_PB_REFORM_DATE),
        color="grey",
        linestyle="dashed",
        label="TSE P/B Reform (Mar 2023)",
    )
    ax.set_ylabel("P/B gap (Japan - Synthetic Japan)")
    ax.set_title(f"Synthetic Control Gap - Pre-treatment RMSPE: {rmspe:.4f}")
    ax.legend()
    fig.savefig(
        FIGURES_DIR / "figure_synth_gap.pdf",
        dpi=300,
        bbox_inches="tight",
        format="pdf",
        metadata={"CreationDate": None, "ModDate": None},
    )
    plt.close(fig)
    logging.info("Saved figure_synth_gap.pdf")
    return ts_gap
