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
NARROW_POST12_CAR = "tables/korea_event_study_robustness_narrow_2024_rollout_post12_car.csv"
SPACED_CAR = "tables/korea_event_study_robustness_spaced_follow_through_car.csv"
SPACED_TABLE = "tables/table_korea_event_study_robustness_spaced_follow_through_coefs.tex"
SUMMARY_CSV = "tables/korea_event_study_robustness_summary.csv"
COMPARATOR_NOTE = "tables/korea_event_study_comparator_scope_note.tex"
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


def test_narrow_window_sensitivity_reruns_cleanly(tmp_path):
    _run_phase8_specs(tmp_path, spec_names=["narrow_2024_rollout_post12"])

    narrow_post12 = pd.read_csv(tmp_path / NARROW_POST12_CAR)
    assert list(narrow_post12.columns) == EXPECTED_COLUMNS

    for cohort, group in narrow_post12.groupby("cohort"):
        assert set(group["event_rel_time"]) == set(range(-12, 13)), cohort

    summary = pd.read_csv(tmp_path / SUMMARY_CSV)
    matched = summary.loc[
        summary["spec_name"].eq("narrow_2024_rollout_post12")
        & summary["post_window_max"].eq(12)
    ]
    assert not matched.empty


def test_phase8_does_not_refactor_event_study_core_comparator_contract(tmp_path):
    event_study_core_source = (
        PROJECT_ROOT / "src" / "analysis" / "event_study_core.py"
    ).read_text(encoding="utf-8")
    assert 'for country in ("KOSPI", "TOPIX")' in event_study_core_source
    assert 'pivot["KOSPI"] - pivot["TOPIX"]' in event_study_core_source

    signature_block = event_study_core_source.split("def run_event_study(", 1)[1].split(
        ") -> pd.DataFrame:",
        1,
    )[0]
    assert "comparator=" not in signature_block
    assert "benchmark=" not in signature_block

    _run_phase8_specs(tmp_path, spec_names=["narrow_2024_rollout"])
    note = (tmp_path / COMPARATOR_NOTE).read_text(encoding="utf-8")
    assert "output/tables/discount_stats.csv" in note
    assert "output/robustness/robustness_alt_control_em_asia.tex" in note
    assert "output/robustness/robustness_alt_control_em_exchina.tex" in note
    assert "output/robustness/figure_placebo_falsification.pdf" in note


def test_korea_japan_note_contains_causal_caveats(tmp_path):
    module = importlib.import_module("src.analysis.korea_event_study_robustness")
    module.run_korea_robustness_specs(output_root=tmp_path)

    note_module = importlib.import_module("src.analysis.korea_japan_comparison_note")
    note_module.write_korea_japan_comparison_note(output_root=tmp_path)

    note = (
        tmp_path / "tables" / "korea_japan_event_study_interpretation_note.tex"
    ).read_text(encoding="utf-8")

    assert (
        "Japan is a historical policy benchmark, not a clean causal counterfactual for Korea."
        in note
    )
    assert "Korea evidence remains descriptive timing evidence." in note
    assert "narrow_2024_rollout" in note
    assert "narrow_2024_rollout_post12" in note
    assert "spaced_follow_through" in note
    assert "max_post_months = 2" in note
    assert (
        "Japan's shipped CAR window runs through event_rel_time = 24, while Korea's "
        "baseline and required sensitivity run through event_rel_time = 20 and "
        "event_rel_time = 12, respectively."
        in note
    )

    assert "Korea proves" not in note
    assert "Korea causal effect" not in note
    assert "Korea treatment effect" not in note
