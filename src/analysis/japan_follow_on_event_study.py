"""
japan_follow_on_event_study.py - Stacked event study for all four Japan governance
reform events using the follow-on study window (through 2026-04-30).

Includes the 2025 Stewardship Code third revision alongside the original three reforms.
Uses a truncated post-event window (max 10 months) to accommodate the 2025 event.
The original three-event study with full 24-month post window remains in event_study.py.
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

FOLLOW_ON_MAX_POST_MONTHS = 10

JAPAN_FOLLOW_ON_FIGURE_OUTPUT_PATH = (
    config.OUTPUT_DIR / "figures" / "figure_japan_follow_on_event_study.png"
)
JAPAN_FOLLOW_ON_CAR_OUTPUT_PATH = (
    config.OUTPUT_DIR / "tables" / "japan_follow_on_event_study_car.csv"
)
JAPAN_FOLLOW_ON_TABLE_OUTPUT_PATH = (
    config.OUTPUT_DIR / "tables" / "table_japan_follow_on_event_study_coefs.tex"
)
JAPAN_FOLLOW_ON_FIGURE_TITLE = (
    "Japan Event-Study CAR: All Four Reforms (Follow-On Window)"
)

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
    stream=sys.stdout,
)


def main() -> None:
    """Run the Japan follow-on event study (4 events) and write its shipped artifacts."""
    panel = pd.read_parquet(config.PROCESSED_DIR / "panel.parquet")
    event_study_core.run_event_study(
        panel,
        event_dates=config.JAPAN_FOLLOW_ON_EVENT_DATES,
        event_labels=config.JAPAN_FOLLOW_ON_EVENT_LABELS,
        study_end=config.FOLLOW_ON_STUDY_END,
        stack_window_min=-36,
        stack_window_max=FOLLOW_ON_MAX_POST_MONTHS,
        event_window_min=-12,
        event_window_max=FOLLOW_ON_MAX_POST_MONTHS,
        figure_title=JAPAN_FOLLOW_ON_FIGURE_TITLE,
        figure_output_path=JAPAN_FOLLOW_ON_FIGURE_OUTPUT_PATH,
        car_output_path=JAPAN_FOLLOW_ON_CAR_OUTPUT_PATH,
        table_output_path=JAPAN_FOLLOW_ON_TABLE_OUTPUT_PATH,
        table_comment_lines=[
            "% Japan follow-on: includes Stewardship Code Rev. 3 (Jun 2025).",
            f"% Post-event window truncated at max_post_months={FOLLOW_ON_MAX_POST_MONTHS} "
            f"through {config.FOLLOW_ON_STUDY_END.isoformat()}.",
            "% The original three-event study with full 24-month post window "
            "is in event_study_car.csv.",
        ],
    )


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)