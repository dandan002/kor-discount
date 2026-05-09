"""
event_study.py - Japan event-study entrypoint preserved through Phase 7.
"""
import logging
import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import config
from src.analysis import event_study_core

STACK_WINDOW_MIN = -36
STACK_WINDOW_MAX = 24
EVENT_WINDOW_MIN = -12
EVENT_WINDOW_MAX = 24
JAPAN_FIGURE_OUTPUT_PATH = config.OUTPUT_DIR / "figures" / "figure2_event_study.pdf"
JAPAN_CAR_OUTPUT_PATH = config.OUTPUT_DIR / "tables" / "event_study_car.csv"
JAPAN_TABLE_OUTPUT_PATH = config.OUTPUT_DIR / "tables" / "table_event_study_coefs.tex"
JAPAN_FIGURE_TITLE = "Figure 2: Event-Study CAR Around Japan Governance Reforms"

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
    stream=sys.stdout,
)


def prepare_event_study_panel(
    panel: pd.DataFrame,
    study_end=config.PAPER_STUDY_END,
    metric: str = "pb",
) -> pd.DataFrame:
    return event_study_core.prepare_event_study_panel(panel, study_end, metric=metric)


def build_stacked_dataset(panel: pd.DataFrame) -> pd.DataFrame:
    return event_study_core.build_stacked_dataset(
        panel,
        event_dates=config.JAPAN_EVENT_DATES,
        event_labels=config.JAPAN_EVENT_LABELS,
        study_end=config.PAPER_STUDY_END,
        stack_window_min=STACK_WINDOW_MIN,
        stack_window_max=STACK_WINDOW_MAX,
    )


def estimate_event_study(stacked: pd.DataFrame) -> pd.DataFrame:
    return event_study_core.estimate_event_study(
        stacked,
        event_dates=config.JAPAN_EVENT_DATES,
        event_labels=config.JAPAN_EVENT_LABELS,
        event_window_min=EVENT_WINDOW_MIN,
        event_window_max=EVENT_WINDOW_MAX,
    )


def _write_latex_table(car_df: pd.DataFrame, path: Path) -> None:
    event_study_core.write_latex_table(car_df, path)


def plot_event_study(car_df: pd.DataFrame) -> None:
    event_study_core.plot_event_study(
        car_df,
        event_dates=config.JAPAN_EVENT_DATES,
        event_labels=config.JAPAN_EVENT_LABELS,
        figure_title=JAPAN_FIGURE_TITLE,
        figure_output_path=JAPAN_FIGURE_OUTPUT_PATH,
    )


def main() -> None:
    """Run the preserved Japan event study and write its shipped artifacts."""
    panel = pd.read_parquet(config.PROCESSED_DIR / "panel.parquet")
    event_study_core.run_event_study(
        panel,
        event_dates=config.JAPAN_EVENT_DATES,
        event_labels=config.JAPAN_EVENT_LABELS,
        study_end=config.PAPER_STUDY_END,
        stack_window_min=STACK_WINDOW_MIN,
        stack_window_max=STACK_WINDOW_MAX,
        event_window_min=EVENT_WINDOW_MIN,
        event_window_max=EVENT_WINDOW_MAX,
        figure_title=JAPAN_FIGURE_TITLE,
        figure_output_path=JAPAN_FIGURE_OUTPUT_PATH,
        car_output_path=JAPAN_CAR_OUTPUT_PATH,
        table_output_path=JAPAN_TABLE_OUTPUT_PATH,
    )


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
