"""
tests/test_phase6.py - Regression coverage for Phase 6 date locking and horizon plumbing.

Run: pytest tests/test_phase6.py --collect-only -q
"""
import datetime
import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import config

PANEL_PATH = config.PROCESSED_DIR / "panel.parquet"


def test_japan_event_aliases_preserved():
    assert config.EVENT_DATES == config.JAPAN_EVENT_DATES
    assert config.EVENT_LABELS == config.JAPAN_EVENT_LABELS


def test_korea_value_up_date_sets_locked():
    assert config.KOREA_VALUE_UP_NARROW_EVENT_DATES == [
        datetime.date(2024, 2, 26),
        datetime.date(2024, 5, 2),
        datetime.date(2024, 8, 12),
    ]
    assert config.KOREA_VALUE_UP_SPACED_EVENT_DATES == [
        datetime.date(2024, 2, 26),
        datetime.date(2025, 7, 9),
        datetime.date(2026, 2, 24),
    ]


def test_korea_event_policy_contract():
    policy = config.KOREA_EVENT_SET_POLICY

    assert policy["primary"]["set_name"] == "narrow_2024_rollout"
    assert policy["primary"]["dates"] == config.KOREA_VALUE_UP_NARROW_EVENT_DATES
    assert policy["primary"]["labels"] == config.KOREA_VALUE_UP_NARROW_EVENT_LABELS
    assert policy["primary"]["max_post_months"] == 20

    assert policy["robustness"]["set_name"] == "spaced_follow_through"
    assert policy["robustness"]["dates"] == config.KOREA_VALUE_UP_SPACED_EVENT_DATES
    assert policy["robustness"]["labels"] == config.KOREA_VALUE_UP_SPACED_EVENT_LABELS
    assert policy["robustness"]["max_post_months"] == 2


def test_study_end_constants_include_follow_on_window():
    assert config.PAPER_STUDY_END == datetime.date(2024, 12, 31)
    assert config.FOLLOW_ON_STUDY_END == datetime.date(2026, 4, 30)


def test_clip_to_study_end_allows_2026_04_30_rows():
    from src.analysis.study_window import clip_to_study_end

    panel = pd.read_parquet(PANEL_PATH)
    clipped = clip_to_study_end(panel, config.FOLLOW_ON_STUDY_END)

    assert clipped["date"].max() == pd.Timestamp("2026-04-30")


def test_prepare_event_study_panel_accepts_follow_on_window():
    from src.analysis.event_study import prepare_event_study_panel

    panel = pd.read_parquet(PANEL_PATH)
    prepared = prepare_event_study_panel(panel, config.FOLLOW_ON_STUDY_END)

    assert list(prepared.columns) == ["date", "country", "pb"]
    assert prepared["date"].max() == pd.Timestamp("2026-04-30")
