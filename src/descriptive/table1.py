"""
table1.py - Generate Table 1: P/B summary statistics by country and sub-period.

Sub-periods (D-09, theoretically motivated by Japan reform dates):
  Full (2004--2024)        : full study period
  Pre-reform (2004--2013)  : before Japan Stewardship Code
  Reform era (2014--2022)  : Stewardship Code through TSE P/B reform
  Post-TSE (2023--2024)    : after TSE P/B reform request

Outputs:
  output/tables/table1_summary_stats.tex - booktabs LaTeX fragment
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

SUB_PERIODS = {
    "Full (2004--2024)": ("2004-01-01", "2024-12-31"),
    "Pre-reform (2004--2013)": ("2004-01-01", "2013-12-31"),
    "Reform era (2014--2022)": ("2014-01-01", "2022-12-31"),
    "Post-TSE (2023--2024)": ("2023-01-01", "2024-12-31"),
}


def main() -> None:
    """Generate Table 1 from the canonical processed panel."""
    df = pd.read_parquet(config.PROCESSED_DIR / "panel.parquet")
    df = df[df["date"] <= pd.Timestamp("2024-12-31")].copy()

    frames = []
    for period_name, (start, end) in SUB_PERIODS.items():
        subset = df[(df["date"] >= start) & (df["date"] <= end)]
        stats = (
            subset.groupby("country")["pb"]
            .agg(
                mean="mean",
                median="median",
                std="std",
                min="min",
                max="max",
            )
            .round(3)
        )
        stats.insert(0, "Period", period_name)
        frames.append(stats)

    table1 = pd.concat(frames)

    latex_str = table1.style.format(precision=2).to_latex(
        hrules=True,
        caption="Summary statistics of index-level P/B ratios by country and sub-period.",
        label="tab:summary_stats",
    )

    output_path = config.OUTPUT_DIR / "tables" / "table1_summary_stats.tex"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(latex_str, encoding="utf-8")
    logging.info("Saved Table 1 to %s", output_path)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
