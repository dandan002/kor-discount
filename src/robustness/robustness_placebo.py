"""
robustness_placebo.py - Placebo falsification tests for ROBUST-01.

Runs the Phase 3 stacked event study design on MSCI Taiwan and MSCI Indonesia,
treating each as a pseudo-Japan with no P/B governance reform. Expected result:
null or negligible CARs, confirming Phase 3 Japan effects are reform-specific.

Decisions: D-14 (falsification markets), D-15 (output convention).
"""
import logging
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import config

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s", stream=sys.stdout)

ROBUSTNESS_DIR = config.OUTPUT_DIR / "robustness"

PLACEBO_MARKETS = {
    "taiwan": ("msci_taiwan_pb_2004_2026.csv", "MSCI_TAIWAN"),
    "indonesia": ("msci_indonesia_pb_2004_2026.csv", "MSCI_INDONESIA"),
}

STACK_WINDOW_MIN = -36
STACK_WINDOW_MAX = 24
EVENT_WINDOW_MIN = -12
EVENT_WINDOW_MAX = 24
BASE_PERIOD = -1
ESTIMATION_WINDOW_MONTHS = 36
REQUIRE_COMPLETE_EVENT_WINDOWS = True


def _month_distance(dates: pd.Series | pd.DatetimeIndex, event_date: pd.Timestamp) -> pd.Series:
    """Return whole calendar-month distance from event_date to each date."""
    date_index = pd.DatetimeIndex(dates)
    rel_time = (date_index.year - event_date.year) * 12 + (
        date_index.month - event_date.month
    )
    return pd.Series(rel_time, index=date_index)


def _event_label(event_date: pd.Timestamp) -> str:
    """Look up the locked event label for a pandas timestamp."""
    return config.EVENT_LABELS[event_date.date()]


def load_topix_pb() -> pd.DataFrame:
    """Load TOPIX P/B from the canonical panel."""
    panel = pd.read_parquet(config.PROCESSED_DIR / "panel.parquet")
    required_columns = {"date", "country", "pb"}
    missing_columns = required_columns - set(panel.columns)
    if missing_columns:
        raise ValueError(f"Panel is missing required columns: {sorted(missing_columns)}")

    topix = panel.loc[panel["country"].eq("TOPIX"), ["date", "pb"]].copy()
    if topix.empty:
        raise ValueError("panel.parquet does not contain TOPIX rows")
    topix["date"] = pd.to_datetime(topix["date"]).dt.to_period("M").dt.to_timestamp()
    return topix.rename(columns={"pb": "topix_pb"}).sort_values("date")


def load_placebo_market(fname: str) -> pd.DataFrame:
    """Load one placebo market P/B series from data/raw."""
    path = config.RAW_DIR / fname
    df = pd.read_csv(path)
    assert "pb" in df.columns, f"{fname} is missing required 'pb' column"
    if "date" not in df.columns:
        raise ValueError(f"{fname} is missing required 'date' column")

    df = df.loc[:, ["date", "pb"]].copy()
    df["date"] = pd.to_datetime(df["date"]).dt.to_period("M").dt.to_timestamp()
    return df.sort_values("date")


def build_placebo_stacked(placebo_pb: pd.DataFrame, topix_pb: pd.DataFrame) -> pd.DataFrame:
    """Create complete event-window cohorts for a placebo-minus-TOPIX P/B spread."""
    merged = placebo_pb.merge(topix_pb, on="date", how="inner").sort_values("date")
    if merged.empty:
        raise ValueError("No overlapping monthly observations between placebo market and TOPIX")

    merged["spread"] = merged["pb"].astype(float) - merged["topix_pb"].astype(float)
    spread = merged.set_index("date")[["spread"]].dropna()

    event_dates = [pd.Timestamp(event_date) for event_date in config.EVENT_DATES]
    expected_rel_times = set(range(STACK_WINDOW_MIN, STACK_WINDOW_MAX + 1))
    expected_pre_times = set(range(STACK_WINDOW_MIN, BASE_PERIOD + 1))
    cohorts: list[pd.DataFrame] = []

    for event_date in event_dates:
        cohort = spread.copy()
        cohort["event_rel_time"] = _month_distance(cohort.index, event_date).astype(int)
        cohort = cohort[
            cohort["event_rel_time"].between(STACK_WINDOW_MIN, STACK_WINDOW_MAX)
        ].copy()

        observed_rel_times = set(cohort["event_rel_time"])
        if REQUIRE_COMPLETE_EVENT_WINDOWS and observed_rel_times != expected_rel_times:
            missing = sorted(expected_rel_times - observed_rel_times)
            extra = sorted(observed_rel_times - expected_rel_times)
            raise ValueError(
                "Placebo data cannot supply complete event window "
                f"{STACK_WINDOW_MIN}..{STACK_WINDOW_MAX} for {_event_label(event_date)}; "
                f"missing={missing}, extra={extra}"
            )

        pre = cohort[cohort["event_rel_time"].between(STACK_WINDOW_MIN, BASE_PERIOD)].copy()
        observed_pre_times = set(pre["event_rel_time"])
        if observed_pre_times != expected_pre_times or len(pre) != ESTIMATION_WINDOW_MONTHS:
            missing = sorted(expected_pre_times - observed_pre_times)
            raise ValueError(
                "Placebo data cannot supply all 36 pre-event months "
                f"{STACK_WINDOW_MIN}..{BASE_PERIOD} for {_event_label(event_date)}; "
                f"missing={missing}"
            )

        trend_model = smf.ols("spread ~ event_rel_time", data=pre).fit()
        cohort["expected_spread"] = trend_model.predict(cohort)
        cohort["abnormal_spread"] = cohort["spread"] - cohort["expected_spread"]
        cohort["cohort"] = event_date.date().isoformat()
        cohort["event_label"] = _event_label(event_date)
        cohorts.append(
            cohort.reset_index()[
                [
                    "date",
                    "spread",
                    "expected_spread",
                    "abnormal_spread",
                    "event_label",
                    "event_rel_time",
                    "cohort",
                ]
            ]
        )

    return pd.concat(cohorts, ignore_index=True)


def run_placebo_event_study(stacked_df: pd.DataFrame) -> pd.DataFrame:
    """Estimate placebo CARs with HC3 intervals for post-event relative months."""
    windowed = stacked_df[
        stacked_df["event_rel_time"].between(EVENT_WINDOW_MIN, EVENT_WINDOW_MAX)
    ].copy()
    windowed["spread"] = windowed["abnormal_spread"].astype(float)

    model = smf.ols(
        f"spread ~ C(event_rel_time, Treatment(reference={BASE_PERIOD}))",
        data=windowed,
    ).fit(cov_type="HC3")

    params = model.params
    cov = model.cov_params()
    rows = []
    cumulative_names: list[str] = []

    for rel_time in range(0, EVENT_WINDOW_MAX + 1):
        param_name = (
            f"C(event_rel_time, Treatment(reference={BASE_PERIOD}))[T.{rel_time}]"
        )
        if param_name in params.index:
            cumulative_names.append(param_name)

        car = float(params.reindex(cumulative_names, fill_value=0.0).sum())
        if cumulative_names:
            cov_sub = cov.reindex(index=cumulative_names, columns=cumulative_names, fill_value=0.0)
            se = float(np.sqrt(np.clip(cov_sub.to_numpy().sum(), a_min=0.0, a_max=None)))
        else:
            se = 0.0

        rows.append(
            {
                "event_rel_time": rel_time,
                "car": car,
                "ci_lo": car - 1.96 * se,
                "ci_hi": car + 1.96 * se,
            }
        )

    return pd.DataFrame(rows, columns=["event_rel_time", "car", "ci_lo", "ci_hi"])


def run_all_placebos() -> dict[str, pd.DataFrame]:
    """Run Taiwan and Indonesia placebo event studies and save CAR CSVs."""
    topix_pb = load_topix_pb()
    car_results: dict[str, pd.DataFrame] = {}

    for market_key, (fname, market_label) in PLACEBO_MARKETS.items():
        placebo_pb = load_placebo_market(fname)
        stacked = build_placebo_stacked(placebo_pb, topix_pb)
        car_df = run_placebo_event_study(stacked)
        output_path = ROBUSTNESS_DIR / f"placebo_{market_key}_car.csv"
        car_df.to_csv(output_path, index=False)
        car_results[market_key] = car_df
        final_car = car_df.loc[car_df["event_rel_time"].eq(EVENT_WINDOW_MAX), "car"].iloc[0]
        logging.info("Saved %s (%s final CAR %.4f)", output_path, market_label, final_car)

    return car_results


def plot_combined_placebo(car_results: dict[str, pd.DataFrame]) -> None:
    """Write the two-panel placebo falsification figure."""
    fig, axes = plt.subplots(1, 2, figsize=(10, 4), sharey=True)

    for ax, (market_key, car_df) in zip(axes, car_results.items()):
        plot_data = car_df.sort_values("event_rel_time")
        x = plot_data["event_rel_time"].to_numpy(dtype=float)
        car = plot_data["car"].to_numpy(dtype=float)
        ci_lo = plot_data["ci_lo"].to_numpy(dtype=float)
        ci_hi = plot_data["ci_hi"].to_numpy(dtype=float)

        ax.plot(x, car, color="#1f77b4", linewidth=1.6)
        ax.fill_between(x, ci_lo, ci_hi, alpha=0.2, color="#1f77b4")
        ax.axhline(0, color="black", linestyle="dashed", linewidth=0.8)
        ax.axvline(0, color="grey", linestyle="dashed", linewidth=0.8)
        ax.set_title(f"{market_key.title()} Placebo - No P/B Reform")
        ax.set_xlabel("Months relative to reform")
        ax.set_ylabel("CAR (P/B points)")

    fig.tight_layout()
    fig.savefig(
        ROBUSTNESS_DIR / "figure_placebo_falsification.pdf",
        dpi=300,
        bbox_inches="tight",
        format="pdf",
        metadata={"CreationDate": None, "ModDate": None},
    )
    plt.close(fig)
    logging.info("Saved %s", ROBUSTNESS_DIR / "figure_placebo_falsification.pdf")


def main() -> None:
    ROBUSTNESS_DIR.mkdir(parents=True, exist_ok=True)
    car_results = run_all_placebos()
    plot_combined_placebo(car_results)
    logging.info("robustness_placebo.py complete")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
