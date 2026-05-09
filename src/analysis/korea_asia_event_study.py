"""
korea_asia_event_study.py - Stacked event study for Korea Value-Up reform dates
using KOSPI - MSCI EM Asia P/B spread (instead of KOSPI - TOPIX).

Computes the cumulative abnormal spread: KOSPI - MSCI_EM_ASIA P/B around
Korea's three Value-Up milestones (Feb 2024, May 2024, Aug 2024).
Uses the same methodology and window parameters as the baseline Korea study.
"""
import logging
import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import config
from src.analysis import asia_panel, event_study_core

KOREA_STACK_WINDOW_MIN = -36
KOREA_EVENT_WINDOW_MIN = -12

KOREA_ASIA_FIGURE_OUTPUT_DIR = (
    config.OUTPUT_DIR / "figures" / "figure_korea_asia_event_study"
)
KOREA_ASIA_CAR_OUTPUT_PATH = (
    config.OUTPUT_DIR / "tables" / "korea_asia_event_study_car.csv"
)
KOREA_ASIA_TABLE_OUTPUT_PATH = (
    config.OUTPUT_DIR / "tables" / "table_korea_asia_event_study_coefs.tex"
)
KOREA_ASIA_FIGURE_TITLE = (
    "Korea Value-Up Event-Study CAR (KOSPI - MSCI EM Asia Spread)"
)

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
    stream=sys.stdout,
)


def main() -> None:
    """Run the Korea-Asia event study off the locked primary Korea policy."""
    panel = asia_panel.load_panel_with_em_asia()
    primary_policy = config.KOREA_EVENT_SET_POLICY["primary"]
    event_dates = primary_policy["dates"]
    event_labels = primary_policy["labels"]
    max_post_months = int(primary_policy["max_post_months"])
    study_end = config.FOLLOW_ON_STUDY_END

    event_study_core.run_event_study(
        panel,
        event_dates=event_dates,
        event_labels=event_labels,
        study_end=study_end,
        stack_window_min=KOREA_STACK_WINDOW_MIN,
        stack_window_max=max_post_months,
        event_window_min=KOREA_EVENT_WINDOW_MIN,
        event_window_max=max_post_months,
        figure_title=KOREA_ASIA_FIGURE_TITLE,
        figure_output_dir=KOREA_ASIA_FIGURE_OUTPUT_DIR,
        car_output_path=KOREA_ASIA_CAR_OUTPUT_PATH,
        table_output_path=KOREA_ASIA_TABLE_OUTPUT_PATH,
        spread_numerator="KOSPI",
        spread_denominator=asia_panel.MSCI_EM_ASIA_COUNTRY,
        spread_label="KOSPI - MSCI EM Asia P/B",
        spread_description="KOSPI-MSCI EM Asia P/B",
        table_comment_lines=[
            "% Korea-Asia variant: spread is KOSPI - MSCI EM Asia P/B, not KOSPI - TOPIX P/B.",
            "% MSCI EM Asia includes Korea as a constituent; this benchmark captures Korea",
            "% relative to the broader Asian EM complex including itself.",
            "% Korea note: clustered 2024 Value-Up dates create overlap across "
            "cohort windows; those overlaps are retained and disclosed explicitly.",
            f"% Korea note: the post window is shortened to "
            f"max_post_months={max_post_months} through {study_end.isoformat()}.",
        ],
    )


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)