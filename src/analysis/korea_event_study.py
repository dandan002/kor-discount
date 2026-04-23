"""
korea_event_study.py - Stacked event study for Korea Value-Up reform dates.
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

KOREA_STACK_WINDOW_MIN = -36
KOREA_EVENT_WINDOW_MIN = -12

KOREA_FIGURE_OUTPUT_PATH = config.OUTPUT_DIR / "figures" / "figure_korea_event_study.pdf"
KOREA_CAR_OUTPUT_PATH = config.OUTPUT_DIR / "tables" / "korea_event_study_car.csv"
KOREA_TABLE_OUTPUT_PATH = (
    config.OUTPUT_DIR / "tables" / "table_korea_event_study_coefs.tex"
)
KOREA_FIGURE_TITLE = "Korea Value-Up Event-Study CAR Around 2024 Reform Milestones"

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
    stream=sys.stdout,
)


def main() -> None:
    """Run the Korea event study off the locked primary Korea policy."""
    panel = pd.read_parquet(config.PROCESSED_DIR / "panel.parquet")
    primary_policy = config.KOREA_EVENT_SET_POLICY["primary"]
    event_dates = primary_policy["dates"]
    event_labels = primary_policy["labels"]
    max_post_months = int(primary_policy["max_post_months"])
    study_end = config.FOLLOW_ON_STUDY_END

    # Keep overlap handling explicit for the clustered 2024 dates rather than
    # mutating global config aliases or silently collapsing overlapping months.
    event_study_core.run_event_study(
        panel,
        event_dates=event_dates,
        event_labels=event_labels,
        study_end=study_end,
        stack_window_min=KOREA_STACK_WINDOW_MIN,
        stack_window_max=max_post_months,
        event_window_min=KOREA_EVENT_WINDOW_MIN,
        event_window_max=max_post_months,
        figure_title=KOREA_FIGURE_TITLE,
        figure_output_path=KOREA_FIGURE_OUTPUT_PATH,
        car_output_path=KOREA_CAR_OUTPUT_PATH,
        table_output_path=KOREA_TABLE_OUTPUT_PATH,
        table_comment_lines=[
            (
                "% Korea note: clustered 2024 Value-Up dates create overlap across "
                "cohort windows; those overlaps are retained and disclosed explicitly."
            ),
            (
                "% Korea note: the post window is shortened to "
                f"max_post_months={max_post_months} through {study_end.isoformat()}."
            ),
        ],
    )


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
