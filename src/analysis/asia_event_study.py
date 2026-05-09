"""
asia_event_study.py - Stacked event study comparing Japan governance reforms
against MSCI EM Asia (instead of Korea-only KOSPI).

Computes the cumulative abnormal spread: MSCI_EM_ASIA - TOPIX P/B around
Japan's three reform events (2014 Stewardship Code, 2015 CGC, 2023 TSE P/B Reform).
Uses the same methodology and window parameters as the baseline Japan study.
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

STACK_WINDOW_MIN = -36
STACK_WINDOW_MAX = 24
EVENT_WINDOW_MIN = -12
EVENT_WINDOW_MAX = 24

ASIA_FIGURE_OUTPUT_DIR = config.OUTPUT_DIR / "figures" / "figure_asia_event_study"
ASIA_CAR_OUTPUT_PATH = config.OUTPUT_DIR / "tables" / "asia_event_study_car.csv"
ASIA_TABLE_OUTPUT_PATH = config.OUTPUT_DIR / "tables" / "table_asia_event_study_coefs.tex"
ASIA_FIGURE_TITLE = "Event-Study CAR: Japan Governance Reforms (MSCI EM Asia - TOPIX)"

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
    stream=sys.stdout,
)


def main() -> None:
    """Run the Asia event study and write its shipped artifacts."""
    panel = asia_panel.load_panel_with_em_asia()
    event_study_core.run_event_study(
        panel,
        event_dates=config.JAPAN_EVENT_DATES,
        event_labels=config.JAPAN_EVENT_LABELS,
        study_end=config.PAPER_STUDY_END,
        stack_window_min=STACK_WINDOW_MIN,
        stack_window_max=STACK_WINDOW_MAX,
        event_window_min=EVENT_WINDOW_MIN,
        event_window_max=EVENT_WINDOW_MAX,
        figure_title=ASIA_FIGURE_TITLE,
        figure_output_dir=ASIA_FIGURE_OUTPUT_DIR,
        car_output_path=ASIA_CAR_OUTPUT_PATH,
        table_output_path=ASIA_TABLE_OUTPUT_PATH,
        spread_numerator=asia_panel.MSCI_EM_ASIA_COUNTRY,
        spread_denominator="TOPIX",
        spread_label="MSCI EM Asia - TOPIX P/B",
        spread_description="MSCI EM Asia-TOPIX P/B",
        table_comment_lines=[
            "% Asia variant: spread is MSCI EM Asia - TOPIX P/B, not KOSPI - TOPIX P/B.",
            "% MSCI EM Asia includes Korea; this benchmark captures Japan vs. the broader",
            "% Asian emerging-market complex rather than Japan vs. Korea alone.",
        ],
    )


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)