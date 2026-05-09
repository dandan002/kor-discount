"""
korea_japan_comparison_note.py - Standalone Phase 8 interpretation note generator.
"""
import logging
import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import config

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
    stream=sys.stdout,
)

REQUIRED_SPECS = {
    "narrow_2024_rollout",
    "narrow_2024_rollout_post12",
    "spaced_follow_through",
}


def _resolve_output_root(output_root: Path | None) -> Path:
    return config.OUTPUT_DIR if output_root is None else Path(output_root)


def _read_summary(output_root: Path) -> pd.DataFrame:
    summary_path = output_root / "tables" / "korea_event_study_robustness_summary.csv"
    summary = pd.read_csv(summary_path)
    summary_specs = set(summary["spec_name"])
    if summary_specs != REQUIRED_SPECS:
        raise ValueError(
            "Phase 8 summary contract requires exactly "
            f"{sorted(REQUIRED_SPECS)}; found {sorted(summary_specs)}"
        )
    return summary


def _read_car(path: Path) -> pd.DataFrame:
    return pd.read_csv(path)


def _max_rel_time(car: pd.DataFrame) -> int:
    return int(car["event_rel_time"].astype(int).max())


def _car_path(output_root: Path, relative_path: str) -> Path:
    return output_root / relative_path


def _load_japan_car(output_root: Path) -> pd.DataFrame:
    local_path = output_root / "tables" / "event_study_car.csv"
    repo_path = config.OUTPUT_DIR / "tables" / "event_study_car.csv"
    return _read_car(local_path if local_path.exists() else repo_path)


def _validate_summary_window(
    summary: pd.DataFrame,
    spec_name: str,
    observed_max_rel_time: int,
) -> None:
    matched = summary.loc[summary["spec_name"].eq(spec_name)]
    if matched.empty:
        raise ValueError(f"Missing required Phase 8 summary row: {spec_name}")
    expected = int(matched.iloc[0]["post_window_max"])
    if expected != observed_max_rel_time:
        raise ValueError(
            f"Summary drift for {spec_name}: expected {expected}, observed "
            f"{observed_max_rel_time}"
        )


def write_korea_japan_comparison_note(*, output_root: Path | None = None) -> Path:
    resolved_output_root = _resolve_output_root(output_root)
    summary = _read_summary(resolved_output_root)

    baseline_car = _read_car(
        _car_path(
            resolved_output_root,
            "tables/korea_event_study_robustness_narrow_2024_rollout_car.csv",
        )
    )
    sensitivity_car = _read_car(
        _car_path(
            resolved_output_root,
            "tables/korea_event_study_robustness_narrow_2024_rollout_post12_car.csv",
        )
    )
    japan_car = _load_japan_car(resolved_output_root)
    comparator_scope_note = (
        resolved_output_root / "tables" / "korea_event_study_comparator_scope_note.tex"
    ).read_text(encoding="utf-8")

    japan_max_rel_time = _max_rel_time(japan_car)
    baseline_max_rel_time = _max_rel_time(baseline_car)
    sensitivity_max_rel_time = _max_rel_time(sensitivity_car)

    _validate_summary_window(summary, "narrow_2024_rollout", baseline_max_rel_time)
    _validate_summary_window(
        summary,
        "narrow_2024_rollout_post12",
        sensitivity_max_rel_time,
    )
    _validate_summary_window(summary, "spaced_follow_through", 2)

    if "No Phase 8 change refactors src/analysis/event_study_core.py" not in comparator_scope_note:
        raise ValueError("Comparator scope note is missing the Phase 8 no-refactor caveat")

    note_lines = [
        "Japan is a historical policy benchmark, not a clean causal counterfactual for Korea.",
        "Korea evidence remains descriptive timing evidence.",
        "The Phase 8 baseline Korea specification is narrow_2024_rollout.",
        "The required narrow-window sensitivity is narrow_2024_rollout_post12.",
        "The spaced_follow_through specification is robustness-only and capped at max_post_months = 2.",
        "Comparator sensitivity remains in existing repo surfaces rather than a refactored event-study benchmark API.",
        (
            "Japan's shipped CAR window runs through event_rel_time = "
            f"{japan_max_rel_time}, while Korea's baseline and required sensitivity "
            f"run through event_rel_time = {baseline_max_rel_time} and "
            f"event_rel_time = {sensitivity_max_rel_time}, respectively."
        ),
        (
            "This mirrors the paper's Japan caveat that overlapping event windows "
            "and the saturated design support descriptive abnormal-movement evidence "
            "rather than a stand-alone country-level treatment effect."
        ),
    ]

    output_path = (
        resolved_output_root / "tables" / "korea_japan_event_study_interpretation_note.tex"
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(note_lines) + "\n", encoding="utf-8")
    logging.info("Saved %s", output_path)
    return output_path


def main() -> None:
    write_korea_japan_comparison_note()


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
