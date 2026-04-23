"""
event_study_core.py - Shared helpers for Japan and Korea event studies.
"""
import datetime
import logging
from pathlib import Path
from typing import Sequence

import matplotlib

matplotlib.use("Agg")  # headless backend - must come before pyplot import
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import statsmodels.api as sm

from src.analysis.study_window import clip_to_study_end

BASE_PERIOD = -1
OUTPUT_COLUMNS = [
    "cohort",
    "event_label",
    "event_rel_time",
    "coefficient",
    "car",
]


def _month_distance(
    dates: pd.Series | pd.DatetimeIndex, event_date: pd.Timestamp
) -> pd.Series:
    """Return whole calendar-month distance from event_date to each date."""
    date_index = pd.DatetimeIndex(dates)
    rel_time = (date_index.year - event_date.year) * 12 + (
        date_index.month - event_date.month
    )
    return pd.Series(rel_time, index=date_index)


def _event_cohort(event_date: pd.Timestamp) -> str:
    """Stable cohort identifier derived from the event date."""
    return event_date.date().isoformat()


def _event_label(
    event_labels: dict[datetime.date, str], event_date: pd.Timestamp
) -> str:
    return event_labels[event_date.date()]


def _event_timestamps(event_dates: Sequence[datetime.date]) -> list[pd.Timestamp]:
    return [pd.Timestamp(event_date) for event_date in event_dates]


def prepare_event_study_panel(
    panel: pd.DataFrame,
    study_end: datetime.date | pd.Timestamp,
    metric: str = "pb",
) -> pd.DataFrame:
    required_columns = {"date", "country", metric}
    missing_columns = required_columns - set(panel.columns)
    if missing_columns:
        raise ValueError(f"Panel is missing required columns: {sorted(missing_columns)}")

    prepared = panel.loc[:, ["date", "country", metric]].copy()
    prepared["date"] = pd.to_datetime(prepared["date"])
    return clip_to_study_end(prepared, study_end)


def build_stacked_dataset(
    panel: pd.DataFrame,
    *,
    event_dates: Sequence[datetime.date],
    event_labels: dict[datetime.date, str],
    study_end: datetime.date | pd.Timestamp,
    stack_window_min: int,
    stack_window_max: int,
) -> pd.DataFrame:
    """Create full event-window cohorts with abnormal KOSPI-TOPIX spread."""
    required_columns = {"date", "country", "pb"}
    missing_columns = required_columns - set(panel.columns)
    if missing_columns:
        raise ValueError(f"Panel is missing required columns: {sorted(missing_columns)}")

    event_timestamps = _event_timestamps(event_dates)
    required_study_end = max(
        (event_date.to_period("M") + stack_window_max).to_timestamp(how="end")
        for event_date in event_timestamps
    )
    resolved_study_end = max(pd.Timestamp(study_end), required_study_end)
    df = prepare_event_study_panel(panel, resolved_study_end, metric="pb")

    required_periods: set[pd.Period] = set()
    for event_date in event_timestamps:
        event_period = event_date.to_period("M")
        required_periods.update(
            event_period + offset
            for offset in range(stack_window_min, stack_window_max + 1)
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
    expected_rel_times = set(range(stack_window_min, stack_window_max + 1))
    expected_pre_times = set(range(stack_window_min, BASE_PERIOD + 1))

    for event_date in event_timestamps:
        cohort = spread.copy()
        cohort["event_rel_time"] = _month_distance(cohort.index, event_date).astype(int)
        cohort = cohort[
            cohort["event_rel_time"].between(stack_window_min, stack_window_max)
        ].copy()

        observed_rel_times = set(cohort["event_rel_time"])
        if observed_rel_times != expected_rel_times:
            missing = sorted(expected_rel_times - observed_rel_times)
            extra = sorted(observed_rel_times - expected_rel_times)
            raise ValueError(
                "Panel cannot supply complete event window "
                f"{stack_window_min}..{stack_window_max} for "
                f"{_event_label(event_labels, event_date)}; "
                f"missing={missing}, extra={extra}"
            )

        overlap_labels: list[str] = []
        for row_date in cohort.index:
            labels = []
            for other_date in event_timestamps:
                if other_date == event_date:
                    continue
                other_rel_time = _month_distance(
                    pd.DatetimeIndex([row_date]), other_date
                ).iloc[0]
                if stack_window_min <= other_rel_time <= stack_window_max:
                    labels.append(_event_label(event_labels, other_date))
            overlap_labels.append("; ".join(labels))

        # Preserve overlap annotations explicitly. Korea's clustered 2024 dates
        # make overlap a design feature to disclose, not a reason to silently
        # drop contaminated months or mutate the event sequence globally.
        cohort["overlap_event_labels"] = overlap_labels
        cohort["overlaps_other_event_window"] = cohort["overlap_event_labels"].ne("")

        pre = cohort[cohort["event_rel_time"].between(stack_window_min, BASE_PERIOD)].copy()
        observed_pre_times = set(pre["event_rel_time"])
        if observed_pre_times != expected_pre_times or len(pre) != len(expected_pre_times):
            missing = sorted(expected_pre_times - observed_pre_times)
            raise ValueError(
                "Panel cannot supply all pre-event months "
                f"{stack_window_min}..{BASE_PERIOD} for "
                f"{_event_label(event_labels, event_date)}; missing={missing}"
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
        cohort["event_label"] = _event_label(event_labels, event_date)
        cohort = cohort.reset_index(names="date")
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


def estimate_event_study(
    stacked: pd.DataFrame,
    *,
    event_dates: Sequence[datetime.date],
    event_labels: dict[datetime.date, str],
    event_window_min: int,
    event_window_max: int,
) -> pd.DataFrame:
    """Estimate cohort x relative-time effects as descriptive estimates."""
    windowed = stacked[
        stacked["event_rel_time"].between(event_window_min, event_window_max)
    ].copy()
    expected_times = list(range(event_window_min, event_window_max + 1))

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
    for event_date in _event_timestamps(event_dates):
        cohort = _event_cohort(event_date)
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
    # The saturated cohort x relative-time design makes robust inference
    # undefined, so coefficients and CARs are descriptive only.
    ols_result = sm.OLS(y, x).fit()
    params = pd.Series(np.asarray(ols_result.params, dtype=float), index=design_names)

    rows = []
    for event_date in _event_timestamps(event_dates):
        cohort = _event_cohort(event_date)
        event_label = labels_by_cohort.get(cohort, _event_label(event_labels, event_date))
        for rel_time in expected_times:
            if rel_time == BASE_PERIOD:
                coefficient = 0.0
            else:
                column = f"cohort_{cohort}__rel_{rel_time}"
                coefficient = float(params[column])
            rows.append(
                {
                    "cohort": cohort,
                    "event_label": event_label,
                    "event_rel_time": rel_time,
                    "coefficient": coefficient,
                }
            )

    car = pd.DataFrame(rows)
    car["car"] = car.groupby("cohort", sort=False)["coefficient"].cumsum()
    return car.loc[:, OUTPUT_COLUMNS]


def write_latex_table(car_df: pd.DataFrame, path: Path) -> None:
    """Write the event-study coefficient table as descriptive CARs."""
    table = car_df.copy()
    table = table.rename(
        columns={
            "event_label": "Event",
            "event_rel_time": "Month",
            "coefficient": "Coefficient",
            "car": "CAR",
        }
    )
    table = table.drop(columns=["cohort"])
    latex = table.to_latex(
        index=False,
        escape=False,
        float_format="%.2f",
        na_rep="--",
        caption="Stacked event-study descriptive CAR estimates (no inference reported).",
        label="tab:event_study_coefs",
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "% Descriptive CARs: coefficients and cumulative abnormal KOSPI-TOPIX P/B spread.\n"
        "% Standard errors are not reported: the saturated cohort x relative-time design\n"
        "% makes sandwich robust inference undefined. See paper text for robustness discussion.\n"
        + latex,
        encoding="utf-8",
    )


def plot_event_study(
    car_df: pd.DataFrame,
    *,
    event_dates: Sequence[datetime.date],
    event_labels: dict[datetime.date, str],
    figure_title: str,
    figure_output_path: Path,
) -> None:
    """Write the event-study figure as a multi-panel CAR PDF."""
    sns.set_theme(style="whitegrid")
    fig, axes = plt.subplots(len(event_dates), 1, figsize=(8, 9), sharex=True)
    if len(event_dates) == 1:
        axes = [axes]

    for ax, event_date in zip(axes, _event_timestamps(event_dates)):
        cohort = _event_cohort(event_date)
        plot_data = car_df[car_df["cohort"] == cohort].sort_values("event_rel_time")
        ax.plot(
            plot_data["event_rel_time"],
            plot_data["car"],
            color="#1f77b4",
            linewidth=1.6,
        )
        ax.axvline(x=0, color="grey", linestyle="--", linewidth=0.9, alpha=0.8)
        ax.axhline(y=0, color="black", linestyle="-", linewidth=0.8, alpha=0.7)
        ax.set_title(_event_label(event_labels, event_date), fontsize=10)
        ax.set_ylabel("CAR: KOSPI - TOPIX P/B")

    axes[-1].set_xlabel("Months relative to reform")
    fig.suptitle(figure_title, fontsize=11)
    fig.tight_layout()

    figure_output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(
        figure_output_path,
        dpi=300,
        bbox_inches="tight",
        format="pdf",
        metadata={"CreationDate": None, "ModDate": None},
    )
    plt.close(fig)
    logging.info("Saved %s", figure_output_path)


def run_event_study(
    panel: pd.DataFrame,
    *,
    event_dates: Sequence[datetime.date],
    event_labels: dict[datetime.date, str],
    study_end: datetime.date | pd.Timestamp,
    stack_window_min: int,
    stack_window_max: int,
    event_window_min: int,
    event_window_max: int,
    figure_title: str,
    figure_output_path: Path,
    car_output_path: Path,
    table_output_path: Path,
) -> pd.DataFrame:
    stacked = build_stacked_dataset(
        panel,
        event_dates=event_dates,
        event_labels=event_labels,
        study_end=study_end,
        stack_window_min=stack_window_min,
        stack_window_max=stack_window_max,
    )
    car = estimate_event_study(
        stacked,
        event_dates=event_dates,
        event_labels=event_labels,
        event_window_min=event_window_min,
        event_window_max=event_window_max,
    )

    car_output_path.parent.mkdir(parents=True, exist_ok=True)
    car.to_csv(car_output_path, index=False)
    logging.info("Saved %s", car_output_path)

    write_latex_table(car, table_output_path)
    logging.info("Saved %s", table_output_path)

    plot_event_study(
        car,
        event_dates=event_dates,
        event_labels=event_labels,
        figure_title=figure_title,
        figure_output_path=figure_output_path,
    )
    return car
