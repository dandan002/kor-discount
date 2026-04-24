"""
korea_event_study_robustness.py - Policy-driven Korea robustness event-study runs.
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
from src.analysis import event_study_core, korea_event_study

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
    stream=sys.stdout,
)


def build_phase8_spec_catalog() -> dict[str, dict[str, object]]:
    return {
        "narrow_2024_rollout": {
            "policy_key": "primary",
            "figure_path": Path(
                "figures/figure_korea_event_study_robustness_narrow_2024_rollout.pdf"
            ),
            "car_path": Path(
                "tables/korea_event_study_robustness_narrow_2024_rollout_car.csv"
            ),
            "table_path": Path(
                "tables/table_korea_event_study_robustness_narrow_2024_rollout_coefs.tex"
            ),
            "max_post_months": 20,
        },
        "spaced_follow_through": {
            "policy_key": "robustness",
            "figure_path": Path(
                "figures/figure_korea_event_study_robustness_spaced_follow_through.pdf"
            ),
            "car_path": Path(
                "tables/korea_event_study_robustness_spaced_follow_through_car.csv"
            ),
            "table_path": Path(
                "tables/table_korea_event_study_robustness_spaced_follow_through_coefs.tex"
            ),
            # This robustness-only spec is fixed at max_post_months=2 through
            # the 2026-04-30 study endpoint.
            "max_post_months": 2,
        },
    }


def _table_comment_lines(spec_name: str, max_post_months: int) -> list[str]:
    comments = [
        f"% spec_name={spec_name}",
        f"% study_end={config.FOLLOW_ON_STUDY_END.isoformat()}",
        f"% max_post_months={max_post_months}",
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
    resolved_names = list(catalog) if spec_names is None else list(spec_names)
    unknown_names = sorted(set(resolved_names) - set(catalog))
    if unknown_names:
        raise ValueError(f"Unknown Phase 8 robustness spec(s): {unknown_names}")
    return resolved_names


def run_korea_robustness_specs(
    *,
    output_root: Path | None = None,
    spec_names: Sequence[str] | None = None,
) -> dict[str, pd.DataFrame]:
    catalog = build_phase8_spec_catalog()
    selected_names = _resolve_spec_names(catalog, spec_names)
    resolved_output_root = config.OUTPUT_DIR if output_root is None else Path(output_root)
    panel = pd.read_parquet(config.PROCESSED_DIR / "panel.parquet")
    results: dict[str, pd.DataFrame] = {}

    for spec_name in selected_names:
        spec = catalog[spec_name]
        policy_key = str(spec["policy_key"])
        policy = config.KOREA_EVENT_SET_POLICY[policy_key]
        policy_name = str(policy["set_name"])
        max_post_months = int(spec["max_post_months"])
        policy_post_months = int(policy["max_post_months"])
        if policy_name != spec_name or policy_post_months != max_post_months:
            raise ValueError(
                "Phase 8 robustness spec catalog drifted from config.KOREA_EVENT_SET_POLICY: "
                f"spec={spec_name}, policy_name={policy_name}, "
                f"spec_max_post_months={max_post_months}, "
                f"policy_max_post_months={policy_post_months}"
            )

        results[spec_name] = event_study_core.run_event_study(
            panel,
            event_dates=policy["dates"],
            event_labels=policy["labels"],
            study_end=config.FOLLOW_ON_STUDY_END,
            stack_window_min=korea_event_study.KOREA_STACK_WINDOW_MIN,
            stack_window_max=max_post_months,
            event_window_min=korea_event_study.KOREA_EVENT_WINDOW_MIN,
            event_window_max=max_post_months,
            figure_title=(
                "Korea Value-Up Robustness Event-Study CAR: "
                f"{spec_name.replace('_', ' ')}"
            ),
            figure_output_path=resolved_output_root / Path(str(spec["figure_path"])),
            car_output_path=resolved_output_root / Path(str(spec["car_path"])),
            table_output_path=resolved_output_root / Path(str(spec["table_path"])),
            table_comment_lines=_table_comment_lines(spec_name, max_post_months),
        )

    return results


def main() -> None:
    results = run_korea_robustness_specs()
    logging.info("Saved Korea robustness specs: %s", ", ".join(results))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
