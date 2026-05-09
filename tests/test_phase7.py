"""
tests/test_phase7.py - Contract tests for Phase 7 Korea event-study isolation.

Run: pytest tests/test_phase7.py --collect-only -q
"""
import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import config

OUTPUT_FIGURES = config.OUTPUT_DIR / "figures"
OUTPUT_TABLES = config.OUTPUT_DIR / "tables"
JAPAN_FIGURE = OUTPUT_FIGURES / "figure2_event_study.pdf"
JAPAN_TABLE = OUTPUT_TABLES / "table_event_study_coefs.tex"
KOREA_FIGURE = OUTPUT_FIGURES / "figure_korea_event_study.pdf"
KOREA_CAR = OUTPUT_TABLES / "korea_event_study_car.csv"
KOREA_TABLE = OUTPUT_TABLES / "table_korea_event_study_coefs.tex"
KOREA_SCRIPT = PROJECT_ROOT / "src" / "analysis" / "korea_event_study.py"
CORE_SCRIPT = PROJECT_ROOT / "src" / "analysis" / "event_study_core.py"


def _read_text(path: Path) -> str:
    assert path.exists(), f"Missing expected file: {path}"
    return path.read_text()


def _combined_source() -> str:
    parts: list[str] = []
    for path in (KOREA_SCRIPT, CORE_SCRIPT):
        if path.exists():
            parts.append(path.read_text())
    return "\n".join(parts)


def test_phase7_primary_policy_contract():
    primary = config.KOREA_EVENT_SET_POLICY["primary"]

    assert primary["dates"] is config.KOREA_VALUE_UP_NARROW_EVENT_DATES
    assert primary["labels"] is config.KOREA_VALUE_UP_NARROW_EVENT_LABELS
    assert isinstance(primary["max_post_months"], int)


def test_phase7_korea_script_exists():
    assert KOREA_SCRIPT.exists()


def test_phase7_output_paths_are_distinct():
    assert KOREA_FIGURE != JAPAN_FIGURE
    assert KOREA_CAR != OUTPUT_TABLES / "event_study_car.csv"
    assert KOREA_TABLE != JAPAN_TABLE


def test_phase7_korea_outputs_exist():
    for path in (KOREA_CAR, KOREA_TABLE, KOREA_FIGURE):
        assert path.exists(), f"Missing expected Korea artifact: {path}"
        assert path.stat().st_size > 0, f"Korea artifact is empty: {path}"


def test_phase7_korea_output_window_matches_policy():
    primary = config.KOREA_EVENT_SET_POLICY["primary"]
    car = pd.read_csv(KOREA_CAR)

    assert list(car.columns) == [
        "cohort",
        "event_label",
        "event_rel_time",
        "coefficient",
        "car",
    ]
    assert car["cohort"].nunique() == 3
    expected_window = set(range(-12, primary["max_post_months"] + 1))
    for cohort, group in car.groupby("cohort"):
        assert set(group["event_rel_time"]) == expected_window, cohort


def test_phase7_korea_source_mentions_overlap_handling():
    source = _combined_source()

    assert "overlap" in source.lower()
    assert (
        "KOREA_EVENT_SET_POLICY" in source
        or "max_post_months" in source
    )


def test_phase7_japan_artifacts_still_exist():
    for path in (JAPAN_FIGURE, JAPAN_TABLE):
        assert path.exists(), f"Missing expected Japan artifact: {path}"
        assert path.stat().st_size > 0, f"Japan artifact is empty: {path}"
