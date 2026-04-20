"""
event_study.py - Stacked event study for Japan governance reform dates.

Builds three Cengiz-style event cohorts around the locked Japan reform dates,
estimates abnormal KOSPI-TOPIX P/B spread changes, and writes machine-readable
CAR estimates plus a paper-ready LaTeX coefficient table.
"""
import logging
import sys
import warnings
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # headless backend - must come before pyplot import
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import statsmodels.api as sm

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import config

STACK_WINDOW_MIN = -36
STACK_WINDOW_MAX = 24
EVENT_WINDOW_MIN = -12
EVENT_WINDOW_MAX = 24
BASE_PERIOD = -1
ESTIMATION_WINDOW_MONTHS = 36
REQUIRE_COMPLETE_EVENT_WINDOWS = True

OUTPUT_COLUMNS = [
    "cohort",
    "event_label",
    "event_rel_time",
    "coefficient",
    "hc3_se",
    "t_stat",
    "p_value",
    "car",
]

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
    stream=sys.stdout,
)


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


def _event_cohort(event_date: pd.Timestamp) -> str:
    """Stable cohort identifier derived from the locked config event date."""
    return event_date.date().isoformat()


def build_stacked_dataset(panel: pd.DataFrame) -> pd.DataFrame:
    """Create three full event-window cohorts with abnormal KOSPI-TOPIX spread."""
    required_columns = {"date", "country", "pb"}
    missing_columns = required_columns - set(panel.columns)
    if missing_columns:
        raise ValueError(f"Panel is missing required columns: {sorted(missing_columns)}")

    df = panel.loc[:, ["date", "country", "pb"]].copy()
    df["date"] = pd.to_datetime(df["date"])

    event_dates = [pd.Timestamp(event_date) for event_date in config.EVENT_DATES]
    required_periods: set[pd.Period] = set()
    for event_date in event_dates:
        event_period = event_date.to_period("M")
        required_periods.update(
            event_period + offset
            for offset in range(STACK_WINDOW_MIN, STACK_WINDOW_MAX + 1)
        )

    pivot = (
        df.pivot(index="date", columns="country", values="pb")
        .sort_index()
        .loc[lambda frame: frame.index.to_period("M").isin(required_periods)]
    )
    for country in ("KOSPI", "TOPIX"):
        if country not in pivot.columns:
            raise ValueError(f"Panel is missing required country: {country}")

    spread = (pivot["KOSPI"] - pivot["TOPIX"]).rename("spread").dropna().to_frame()
    cohorts: list[pd.DataFrame] = []
    expected_rel_times = set(range(STACK_WINDOW_MIN, STACK_WINDOW_MAX + 1))
    expected_pre_times = set(range(STACK_WINDOW_MIN, BASE_PERIOD + 1))

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
                "Panel cannot supply complete event window "
                f"{STACK_WINDOW_MIN}..{STACK_WINDOW_MAX} for {_event_label(event_date)}; "
                f"missing={missing}, extra={extra}"
            )

        overlap_labels: list[str] = []
        for row_date in cohort.index:
            labels = []
            for other_date in event_dates:
                if other_date == event_date:
                    continue
                other_rel_time = _month_distance(pd.DatetimeIndex([row_date]), other_date).iloc[0]
                if STACK_WINDOW_MIN <= other_rel_time <= STACK_WINDOW_MAX:
                    labels.append(_event_label(other_date))
            overlap_labels.append("; ".join(labels))

        # Cengiz et al. (2019) stacked cohorts: this project preserves the
        # locked D-01/D-02 windows and flags overlap/contamination instead of
        # using a destructive clean-cohort exclusion.
        cohort["overlap_event_labels"] = overlap_labels
        cohort["overlaps_other_event_window"] = cohort["overlap_event_labels"].ne("")

        pre = cohort[cohort["event_rel_time"].between(STACK_WINDOW_MIN, BASE_PERIOD)].copy()
        observed_pre_times = set(pre["event_rel_time"])
        if observed_pre_times != expected_pre_times or len(pre) != ESTIMATION_WINDOW_MONTHS:
            missing = sorted(expected_pre_times - observed_pre_times)
            raise ValueError(
                "Panel cannot supply all 36 pre-event months "
                f"{STACK_WINDOW_MIN}..{BASE_PERIOD} for {_event_label(event_date)}; "
                f"missing={missing}"
            )

        trend_x = sm.add_constant(pre["event_rel_time"].astype(float), has_constant="add")
        trend_model = sm.OLS(pre["spread"].astype(float), trend_x).fit()
        predict_x = sm.add_constant(
            cohort["event_rel_time"].astype(float),
            has_constant="add",
        )
        cohort["expected_spread"] = trend_model.predict(predict_x)
        cohort["abnormal_spread"] = cohort["spread"] - cohort["expected_spread"]
        cohort["cohort"] = _event_cohort(event_date)
        cohort["event_label"] = _event_label(event_date)
        cohort = cohort.reset_index(names="date")

        # The 2014 and 2015 windows overlap; both windows are preserved for
        # comparability, and the overlap annotation must be discussed as a
        # limitation in the paper.
        cohorts.append(
            cohort[
                [
                    "date",
                    "cohort",
                    "event_label",
                    "event_rel_time",
                    "spread",
                    "expected_spread",
                    "abnormal_spread",
                    "overlaps_other_event_window",
                    "overlap_event_labels",
                ]
            ]
        )

    return pd.concat(cohorts, ignore_index=True)


def estimate_event_study(stacked: pd.DataFrame) -> pd.DataFrame:
    """Estimate cohort x relative-time effects with HC3 standard errors."""
    windowed = stacked[
        stacked["event_rel_time"].between(EVENT_WINDOW_MIN, EVENT_WINDOW_MAX)
    ].copy()
    expected_times = list(range(EVENT_WINDOW_MIN, EVENT_WINDOW_MAX + 1))

    labels_by_cohort = (
        windowed[["cohort", "event_label"]]
        .drop_duplicates()
        .set_index("cohort")["event_label"]
        .to_dict()
    )

    design_names = []
    design_data: dict[str, np.ndarray] = {}
    cohort_values = windowed["cohort"].to_numpy()
    rel_values = windowed["event_rel_time"].to_numpy()
    for cohort in [_event_cohort(pd.Timestamp(event_date)) for event_date in config.EVENT_DATES]:
        for rel_time in expected_times:
            if rel_time == BASE_PERIOD:
                continue
            column = f"cohort_{cohort}__rel_{rel_time}"
            design_data[column] = (
                (cohort_values == cohort) & (rel_values == rel_time)
            ).astype(float)
            design_names.append(column)

    y = windowed["abnormal_spread"].astype(float)
    x = pd.DataFrame(design_data, index=windowed.index, columns=design_names)
    with warnings.catch_warnings():
        warnings.filterwarnings(
            "ignore",
            message="invalid value encountered in divide",
            category=RuntimeWarning,
            module="statsmodels.regression.linear_model",
        )
        robust = sm.OLS(y, x).fit().get_robustcov_results(cov_type="HC3")

    params = pd.Series(np.asarray(robust.params, dtype=float), index=design_names)
    bse = pd.Series(np.asarray(robust.bse, dtype=float), index=design_names)
    tvalues = pd.Series(np.asarray(robust.tvalues, dtype=float), index=design_names)
    pvalues = pd.Series(np.asarray(robust.pvalues, dtype=float), index=design_names)

    rows = []
    for event_date in [pd.Timestamp(event_date) for event_date in config.EVENT_DATES]:
        cohort = _event_cohort(event_date)
        event_label = labels_by_cohort.get(cohort, _event_label(event_date))
        for rel_time in expected_times:
            if rel_time == BASE_PERIOD:
                row = {
                    "cohort": cohort,
                    "event_label": event_label,
                    "event_rel_time": rel_time,
                    "coefficient": 0.0,
                    "hc3_se": 0.0,
                    "t_stat": 0.0,
                    "p_value": 1.0,
                }
            else:
                column = f"cohort_{cohort}__rel_{rel_time}"
                row = {
                    "cohort": cohort,
                    "event_label": event_label,
                    "event_rel_time": rel_time,
                    "coefficient": float(params[column]),
                    "hc3_se": float(bse[column]),
                    "t_stat": float(tvalues[column]),
                    "p_value": float(pvalues[column]),
                }
            rows.append(row)

    car = pd.DataFrame(rows)
    car["car"] = car.groupby("cohort", sort=False)["coefficient"].cumsum()
    return car.loc[:, OUTPUT_COLUMNS]


def _write_latex_table(car_df: pd.DataFrame, path: Path) -> None:
    """Write the event-study coefficient table with HC3/CAR notation."""
    table = car_df.copy()
    table = table.rename(
        columns={
            "event_label": "Event",
            "event_rel_time": "Month",
            "coefficient": "Coefficient",
            "hc3_se": "HC3 SE",
            "t_stat": "t-stat",
            "p_value": "p-value",
            "car": "CAR",
        }
    )
    table = table.drop(columns=["cohort"])
    latex = table.to_latex(
        index=False,
        escape=False,
        float_format="%.2f",
        na_rep="--",
        caption="Stacked event-study cumulative abnormal valuation changes.",
        label="tab:event_study_coefs",
    )
    path.write_text(
        "% HC3 robust standard errors; CAR is cumulative abnormal KOSPI-TOPIX P/B spread.\n"
        + latex,
        encoding="utf-8",
    )


def plot_event_study(car_df: pd.DataFrame) -> None:
    """Write Figure 2 as one three-panel CAR event-study PDF."""
    sns.set_theme(style="whitegrid")
    fig, axes = plt.subplots(3, 1, figsize=(8, 9), sharex=True)

    for ax, event_date in zip(axes, config.EVENT_DATES):
        event_label = config.EVENT_LABELS[event_date]
        cohort = _event_cohort(pd.Timestamp(event_date))
        plot_data = car_df[car_df["cohort"] == cohort].sort_values("event_rel_time")
        ax.plot(
            plot_data["event_rel_time"],
            plot_data["car"],
            color="#1f77b4",
            linewidth=1.6,
        )
        ax.axvline(x=0, color="grey", linestyle="--", linewidth=0.9, alpha=0.8)
        ax.axhline(y=0, color="black", linestyle="-", linewidth=0.8, alpha=0.7)
        ax.set_title(event_label, fontsize=10)
        ax.set_ylabel("CAR: KOSPI - TOPIX P/B")

    axes[-1].set_xlabel("Months relative to reform")
    fig.suptitle("Figure 2: Event-Study CAR Around Japan Governance Reforms", fontsize=11)
    fig.tight_layout()

    output_path = config.OUTPUT_DIR / "figures" / "figure2_event_study.pdf"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(
        output_path,
        dpi=300,
        bbox_inches="tight",
        format="pdf",
        metadata={"CreationDate": None, "ModDate": None},
    )
    plt.close(fig)
    logging.info("Saved %s", output_path)


def main() -> None:
    """Run the stacked event study and write table artifacts."""
    panel = pd.read_parquet(config.PROCESSED_DIR / "panel.parquet")
    stacked = build_stacked_dataset(panel)
    car = estimate_event_study(stacked)

    tables_dir = config.OUTPUT_DIR / "tables"
    tables_dir.mkdir(parents=True, exist_ok=True)

    car_path = tables_dir / "event_study_car.csv"
    car.to_csv(car_path, index=False)
    logging.info("Saved %s", car_path)

    tex_path = tables_dir / "table_event_study_coefs.tex"
    _write_latex_table(car, tex_path)
    logging.info("Saved %s", tex_path)

    plot_event_study(car)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
