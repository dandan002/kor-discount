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
    gap_df = ts_gap.reset_index()
    gap_df.columns = ["date", "gap"]
    gap_df.to_csv(ROBUSTNESS_DIR / "synthetic_control_gap.csv", index=False)
    logging.info("Saved synthetic_control_gap.csv")

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


def extract_results_and_plot(synth: Synth, dataprep: Dataprep) -> pd.Series:
    """Write primary synthetic-control outputs and return the gap series."""
    rmspe = extract_results(synth)
    return plot_gap(synth, dataprep, rmspe)


def run_intime_placebo(panel: pd.DataFrame) -> pd.Series:
    """Run the in-time placebo using a fake pre-COVID treatment date."""
    placebo_date = pd.Timestamp("2019-01-01")
    pre_placebo = pd.date_range(start="2004-01-01", end="2018-12-01", freq="MS")
    dataprep_it = Dataprep(
        foo=panel,
        predictors=["pb"],
        predictors_op="mean",
        dependent="pb",
        unit_variable="unit",
        time_variable="date",
        treatment_identifier="TOPIX",
        controls_identifier=list(DONORS.keys()),
        time_predictors_prior=pre_placebo,
        time_optimize_ssr=pre_placebo,
        special_predictors=[
            ("pb", pd.date_range("2010-01-01", "2010-12-01", freq="MS"), "mean"),
            ("pb", pd.date_range("2018-01-01", "2018-12-01", freq="MS"), "mean"),
        ],
    )
    synth_it = Synth()
    synth_it.fit(
        dataprep=dataprep_it,
        optim_method="Nelder-Mead",
        optim_initial="equal",
        optim_options={"maxiter": 1000},
    )
    rmspe_it = math.sqrt(synth_it.mspe())
    logging.info("In-time placebo RMSPE = %.4f", rmspe_it)

    all_period = pd.date_range(start="2004-01-01", end="2026-04-01", freq="MS")
    Z0, Z1 = dataprep_it.make_outcome_mats(time_period=all_period)
    gap_it = synth_it._gaps(Z0=Z0, Z1=Z1)

    actual_reform = pd.Timestamp(config.TSE_PB_REFORM_DATE)
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(gap_it.index, gap_it.values, color="black", linewidth=1, label="Japan gap")
    ax.axhline(0, color="black", linestyle="dashed", linewidth=0.8)
    ax.axvline(
        x=placebo_date,
        color="grey",
        linestyle="dashed",
        label=f"Fake treatment ({placebo_date.date().isoformat()})",
    )
    ax.axvline(
        x=actual_reform,
        color="darkgrey",
        linestyle="dashed",
        label=f"Actual TSE reform ({actual_reform.date().isoformat()})",
    )
    ax.set_ylabel("P/B gap (Japan - Synthetic Japan)")
    ax.set_title("In-Time Placebo Gap (Fake Treatment: 2019-01-01)")
    ax.legend()
    fig.savefig(
        ROBUSTNESS_DIR / "figure_placebo_intime.pdf",
        dpi=300,
        bbox_inches="tight",
        format="pdf",
        metadata={"CreationDate": None, "ModDate": None},
    )
    plt.close(fig)
    logging.info("Saved figure_placebo_intime.pdf")
    return gap_it


def run_inspace_placebo(panel: pd.DataFrame, ts_gap: pd.Series) -> dict[str, pd.Series]:
    """Run donor-as-treated in-space placebo fits and plot their gap distribution."""
    donors = list(DONORS.keys())
    pre_period = pd.date_range(start="2004-01-01", end="2023-02-01", freq="MS")
    all_period = pd.date_range(start="2004-01-01", end="2026-04-01", freq="MS")
    placebo_gaps = {}

    for placebo_unit in donors:
        remaining = [donor for donor in donors if donor != placebo_unit]
        dataprep_placebo = Dataprep(
            foo=panel,
            predictors=["pb"],
            predictors_op="mean",
            dependent="pb",
            unit_variable="unit",
            time_variable="date",
            treatment_identifier=placebo_unit,
            controls_identifier=["TOPIX"] + remaining,
            time_predictors_prior=pre_period,
            time_optimize_ssr=pre_period,
            special_predictors=[
                ("pb", pd.date_range("2010-01-01", "2010-12-01", freq="MS"), "mean"),
                ("pb", pd.date_range("2018-01-01", "2018-12-01", freq="MS"), "mean"),
            ],
        )
        synth_placebo = Synth()
        synth_placebo.fit(
            dataprep=dataprep_placebo,
            optim_method="Nelder-Mead",
            optim_initial="equal",
            optim_options={"maxiter": 1000},
        )
        Z0, Z1 = dataprep_placebo.make_outcome_mats(time_period=all_period)
        placebo_gaps[placebo_unit] = synth_placebo._gaps(Z0=Z0, Z1=Z1)
        logging.info(
            "In-space placebo %s RMSPE = %.4f",
            placebo_unit,
            math.sqrt(synth_placebo.mspe()),
        )

    fig, ax = plt.subplots(figsize=(10, 5))
    for gap in placebo_gaps.values():
        ax.plot(gap.index, gap.values, color="lightgrey", linewidth=0.8, alpha=0.7)
    ax.plot(ts_gap.index, ts_gap.values, color="black", linewidth=1.5, label="Japan (treated)")
    ax.axhline(0, color="black", linestyle="dashed", linewidth=0.8)
    ax.axvline(
        x=pd.Timestamp(config.TSE_PB_REFORM_DATE),
        color="grey",
        linestyle="dashed",
        label="TSE P/B Reform (Mar 2023)",
    )
    ax.set_ylabel("P/B gap")
    ax.set_title("In-Space Placebo Distribution - Japan vs. Donor Pool")
    ax.legend()
    fig.savefig(
        ROBUSTNESS_DIR / "figure_placebo_inspace.pdf",
        dpi=300,
        bbox_inches="tight",
        format="pdf",
        metadata={"CreationDate": None, "ModDate": None},
    )
    plt.close(fig)
    logging.info("Saved figure_placebo_inspace.pdf")
    return placebo_gaps


def main() -> None:
    """Run synthetic control and placebo checks."""
    ROBUSTNESS_DIR.mkdir(parents=True, exist_ok=True)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    panel = load_donor_panel()
    synth, dataprep = run_synth(panel)
    ts_gap = extract_results_and_plot(synth, dataprep)
    run_intime_placebo(panel)
    run_inspace_placebo(panel, ts_gap)
    logging.info("synthetic_control.py complete")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
