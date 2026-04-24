"""
tests/test_phase8.py - Fresh-output regression coverage for Phase 8 robustness specs.

Run: pytest tests/test_phase8.py --collect-only -q
"""
import importlib
import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

ROBUSTNESS_SCRIPT = PROJECT_ROOT / "src" / "analysis" / "korea_event_study_robustness.py"
NARROW_CAR = "tables/korea_event_study_robustness_narrow_2024_rollout_car.csv"
SPACED_CAR = "tables/korea_event_study_robustness_spaced_follow_through_car.csv"
SPACED_TABLE = "tables/table_korea_event_study_robustness_spaced_follow_through_coefs.tex"
EXPECTED_COLUMNS = [
    "cohort",
    "event_label",
    "event_rel_time",
    "coefficient",
    "car",
]


def _run_phase8_specs(tmp_path: Path, spec_names: list[str]) -> None:
    module = importlib.import_module("src.analysis.korea_event_study_robustness")
    module.run_korea_robustness_specs(output_root=tmp_path, spec_names=spec_names)


def test_korea_robustness_date_specs_generate_expected_windows(tmp_path):
    _run_phase8_specs(
        tmp_path,
        spec_names=["narrow_2024_rollout", "spaced_follow_through"],
    )

    narrow = pd.read_csv(tmp_path / NARROW_CAR)
    spaced = pd.read_csv(tmp_path / SPACED_CAR)

    assert list(narrow.columns) == EXPECTED_COLUMNS
    assert list(spaced.columns) == EXPECTED_COLUMNS
    assert narrow["cohort"].nunique() == 3
    assert spaced["cohort"].nunique() == 3

    for cohort, group in narrow.groupby("cohort"):
        assert set(group["event_rel_time"]) == set(range(-12, 21)), cohort

    for cohort, group in spaced.groupby("cohort"):
        assert set(group["event_rel_time"]) == set(range(-12, 3)), cohort


def test_spaced_follow_through_window_is_capped_at_two_months(tmp_path):
    _run_phase8_specs(tmp_path, spec_names=["spaced_follow_through"])

    table = (tmp_path / SPACED_TABLE).read_text(encoding="utf-8")

    assert "spaced_follow_through" in table
    assert "max_post_months=2" in table
    assert "2026-04-30" in table
