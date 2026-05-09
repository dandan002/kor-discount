"""
korea_asia_event_study_robustness.py - Korea-Asia robustness event-study runs.

Mirrors korea_event_study_robustness.py but uses KOSPI - MSCI EM Asia as the
spread instead of KOSPI - TOPIX. Runs all three spec variants (narrow_2024_rollout,
narrow_2024_rollout_post12, spaced_follow_through) with the Asia benchmark.
"""
import logging
import sys
from pathlib import Path
from typing import Sequence

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import config
from src.analysis import asia_panel, event_study_core, korea_asia_event_study

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
    stream=sys.stdout,
)

DEFAULT_SPEC_ORDER = [
    "narrow_2024_rollout",
    "narrow_2024_rollout_post12",
    "spaced_follow_through",
]

SUMMARY_COLUMNS = [
    "spec_name",
    "set_role",
    "study_end",
    "post_window_max",
    "cohort_count",
    "min_rel_time",
    "max_rel_time",
    "car_path",
    "table_path",
    "figure_dir",
]


def build_korea_asia_spec_catalog() -> dict[str, dict[str, object]]:
    return {
        "narrow_2024_rollout": {
            "policy_key": "primary",
            "base_policy_name": "narrow_2024_rollout",
            "set_role": "baseline",
            "figure_dir": Path(
                "figures/figure_korea_asia_event_study_robustness_narrow_2024_rollout"
            ),
            "car_path": Path(
                "tables/korea_asia_event_study_robustness_narrow_2024_rollout_car.csv"
            ),
            "table_path": Path(
                "tables/table_korea_asia_event_study_robustness_narrow_2024_rollout_coefs.tex"
            ),
            "max_post_months": 20,
        },
        "narrow_2024_rollout_post12": {
            "policy_key": "primary",
            "base_policy_name": "narrow_2024_rollout",
            "set_role": "window_sensitivity",
            "figure_dir": Path(
                "figures/figure_korea_asia_event_study_robustness_narrow_2024_rollout_post12"
            ),
            "car_path": Path(
                "tables/korea_asia_event_study_robustness_narrow_2024_rollout_post12_car.csv"
            ),
            "table_path": Path(
                "tables/table_korea_asia_event_study_robustness_narrow_2024_rollout_post12_coefs.tex"
            ),
            "max_post_months": 12,
        },
        "spaced_follow_through": {
            "policy_key": "robustness",
            "base_policy_name": "spaced_follow_through",
            "set_role": "robustness_only",
            "figure_dir": Path(
                "figures/figure_korea_asia_event_study_robustness_spaced_follow_through"
            ),
            "car_path": Path(
                "tables/korea_asia_event_study_robustness_spaced_follow_through_car.csv"
            ),
            "table_path": Path(
                "tables/table_korea_asia_event_study_robustness_spaced_follow_through_coefs.tex"
            ),
            "max_post_months": 2,
        },
    }


def _table_comment_lines(spec_name: str, max_post_months: int) -> list[str]:
    comments = [
        f"% spec_name={spec_name}",
        f"% study_end={config.FOLLOW_ON_STUDY_END.isoformat()}",
        f"% max_post_months={max_post_months}",
        "% Korea-Asia variant: spread is KOSPI - MSCI EM Asia P/B, not KOSPI - TOPIX P/B.",
        "% MSCI EM Asia includes Korea as a constituent.",
    ]
    if spec_name == "spaced_follow_through":
        comments.append(
            "% Robustness-only follow-through specification; do not treat as the baseline Korea design."
        )
    return comments


def _resolve_spec_names(
    catalog: dict[str, dict[str, object]],
    spec_names: Sequence[str] | None,
) -> list[str]:
    resolved_names = list(DEFAULT_SPEC_ORDER) if spec_names is None else list(spec_names)
    unknown_names = sorted(set(resolved_names) - set(catalog))
    if unknown_names:
        raise ValueError(f"Unknown Korea-Asia robustness spec(s): {unknown_names}")
    return resolved_names


def _validate_spec_against_policy(spec_name: str, spec: dict[str, object]) -> dict[str, object]:
    policy_key = str(spec["policy_key"])
    policy = config.KOREA_EVENT_SET_POLICY[policy_key]
    base_policy_name = str(spec["base_policy_name"])
    set_role = str(spec["set_role"])
    max_post_months = int(spec["max_post_months"])
    policy_name = str(policy["set_name"])
    policy_post_months = int(policy["max_post_months"])

    if policy_name != base_policy_name:
        raise ValueError(
            "Korea-Asia spec catalog drifted from config.KOREA_EVENT_SET_POLICY: "
            f"spec={spec_name}, policy_name={policy_name}, "
            f"base_policy_name={base_policy_name}"
        )

    if set_role == "window_sensitivity":
        if max_post_months >= policy_post_months:
            raise ValueError(
                "Korea-Asia narrow sensitivity must stay shorter than the baseline policy "
                f"window: spec={spec_name}, max_post_months={max_post_months}, "
                f"policy_max_post_months={policy_post_months}"
            )
    elif policy_post_months != max_post_months:
        raise ValueError(
            "Korea-Asia spec catalog drifted from config.KOREA_EVENT_SET_POLICY: "
            f"spec={spec_name}, policy_name={policy_name}, "
            f"spec_max_post_months={max_post_months}, "
            f"policy_max_post_months={policy_post_months}"
        )

    return policy


def _build_summary_row(
    spec_name: str,
    spec: dict[str, object],
    car_df: pd.DataFrame,
) -> dict[str, object]:
    rel_times = car_df["event_rel_time"].astype(int)
    return {
        "spec_name": spec_name,
        "set_role": str(spec["set_role"]),
        "study_end": config.FOLLOW_ON_STUDY_END.isoformat(),
        "post_window_max": int(rel_times.max()),
        "cohort_count": int(car_df["cohort"].nunique()),
        "min_rel_time": int(rel_times.min()),
        "max_rel_time": int(rel_times.max()),
        "car_path": str(spec["car_path"]),
        "table_path": str(spec["table_path"]),
        "figure_dir": str(spec["figure_dir"]),
    }


def _write_summary(
    output_root: Path,
    summary_rows: list[dict[str, object]],
) -> Path:
    summary_path = output_root / "tables" / "korea_asia_event_study_robustness_summary.csv"
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(summary_rows, columns=SUMMARY_COLUMNS).to_csv(summary_path, index=False)
    logging.info("Saved %s", summary_path)
    return summary_path


def run_korea_asia_robustness_specs(
    *,
    output_root: Path | None = None,
    spec_names: Sequence[str] | None = None,
) -> dict[str, pd.DataFrame]:
    catalog = build_korea_asia_spec_catalog()
    selected_names = _resolve_spec_names(catalog, spec_names)
    resolved_output_root = config.OUTPUT_DIR if output_root is None else Path(output_root)
    panel = asia_panel.load_panel_with_em_asia()
    results: dict[str, pd.DataFrame] = {}
    summary_rows: list[dict[str, object]] = []

    for spec_name in selected_names:
        spec = catalog[spec_name]
        policy = _validate_spec_against_policy(spec_name, spec)
        max_post_months = int(spec["max_post_months"])

        results[spec_name] = event_study_core.run_event_study(
            panel,
            event_dates=policy["dates"],
            event_labels=policy["labels"],
            study_end=config.FOLLOW_ON_STUDY_END,
            stack_window_min=korea_asia_event_study.KOREA_STACK_WINDOW_MIN,
            stack_window_max=max_post_months,
            event_window_min=korea_asia_event_study.KOREA_EVENT_WINDOW_MIN,
            event_window_max=max_post_months,
            figure_title=(
                "Korea-Asia Value-Up Robustness Event-Study CAR: "
                f"{spec_name.replace('_', ' ')}"
            ),
            figure_output_dir=resolved_output_root / Path(str(spec["figure_dir"])),
            car_output_path=resolved_output_root / Path(str(spec["car_path"])),
            table_output_path=resolved_output_root / Path(str(spec["table_path"])),
            spread_numerator="KOSPI",
            spread_denominator=asia_panel.MSCI_EM_ASIA_COUNTRY,
            spread_label="KOSPI - MSCI EM Asia P/B",
            spread_description="KOSPI-MSCI EM Asia P/B",
            table_comment_lines=_table_comment_lines(spec_name, max_post_months),
        )
        summary_rows.append(_build_summary_row(spec_name, spec, results[spec_name]))

    _write_summary(resolved_output_root, summary_rows)

    return results


def main() -> None:
    results = run_korea_asia_robustness_specs(spec_names=DEFAULT_SPEC_ORDER)
    logging.info("Saved Korea-Asia robustness specs: %s", ", ".join(results))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)