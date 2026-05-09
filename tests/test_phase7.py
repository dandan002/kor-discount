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
JAPAN_FIGURE = OUTPUT_FIGURES / "figure2_event_study"
JAPAN_TABLE = OUTPUT_TABLES / "table_event_study_coefs.tex"
KOREA_FIGURE = OUTPUT_FIGURES / "figure_korea_event_study"
KOREA_CAR = OUTPUT_TABLES / "korea_event_study_car.csv"
KOREA_TABLE = OUTPUT_TABLES / "table_korea_event_study_coefs.tex"
KOREA_SCRIPT = PROJECT_ROOT / "src" / "analysis" / "korea_event_study.py"
CORE_SCRIPT = PROJECT_ROOT / "src" / "analysis" / "event_study_core.py"
KOREA_ASIA_CAR = OUTPUT_TABLES / "korea_asia_event_study_car.csv"
KOREA_ASIA_TABLE = OUTPUT_TABLES / "table_korea_asia_event_study_coefs.tex"
KOREA_ASIA_FIGURE = OUTPUT_FIGURES / "figure_korea_asia_event_study"


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
    assert str(KOREA_FIGURE) != str(JAPAN_FIGURE)
    assert KOREA_CAR != OUTPUT_TABLES / "event_study_car.csv"
    assert KOREA_TABLE != JAPAN_TABLE


def test_phase7_korea_outputs_exist():
    assert KOREA_FIGURE.is_dir(), f"Missing Korea figure directory: {KOREA_FIGURE}"
    korea_pngs = list(KOREA_FIGURE.glob("*.png"))
    assert len(korea_pngs) >= 3, f"Expected >= 3 per-cohort plots, found {len(korea_pngs)}"
    for path in (KOREA_CAR, KOREA_TABLE):
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
    assert JAPAN_FIGURE.is_dir(), f"Missing Japan figure directory: {JAPAN_FIGURE}"
    for path in (JAPAN_TABLE,):
        assert path.exists(), f"Missing expected Japan artifact: {path}"
        assert path.stat().st_size > 0, f"Japan artifact is empty: {path}"


def test_phase7_korea_asia_outputs_exist():
    assert KOREA_ASIA_FIGURE.is_dir(), f"Missing Korea-Asia figure directory: {KOREA_ASIA_FIGURE}"
    korea_asia_pngs = list(KOREA_ASIA_FIGURE.glob("*.png"))
    assert len(korea_asia_pngs) >= 3, f"Expected >= 3 per-cohort plots, found {len(korea_asia_pngs)}"
    for path in (KOREA_ASIA_CAR, KOREA_ASIA_TABLE):
        assert path.exists(), f"Missing expected Korea-Asia artifact: {path}"
        assert path.stat().st_size > 0, f"Korea-Asia artifact is empty: {path}"


def test_phase7_korea_asia_car_has_three_cohorts():
    car = pd.read_csv(KOREA_ASIA_CAR)
    assert list(car.columns) == [
        "cohort",
        "event_label",
        "event_rel_time",
        "coefficient",
        "car",
    ]
    assert car["cohort"].nunique() == 3
    primary = config.KOREA_EVENT_SET_POLICY["primary"]
    expected_window = set(range(-12, int(primary["max_post_months"]) + 1))
    for cohort, group in car.groupby("cohort"):
        assert set(group["event_rel_time"]) == expected_window, cohort


def test_phase7_korea_asia_uses_msci_em_asia_spread():
    korea_asia_script = PROJECT_ROOT / "src" / "analysis" / "korea_asia_event_study.py"
    assert korea_asia_script.exists()
    source = korea_asia_script.read_text()
    assert "MSCI_EM_ASIA" in source
    assert "spread_denominator" in source


def test_phase7_korea_asia_table_mentions_asia():
    content = KOREA_ASIA_TABLE.read_text()
    assert "MSCI EM Asia" in content
    assert "CAR" in content
