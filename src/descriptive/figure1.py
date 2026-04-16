"""
figure1.py - Generate Figure 1: KOSPI P/B vs benchmark indices, 2004-2024.

Outputs:
  output/figures/figure1_pb_comparison.pdf - publication-quality PDF, 300 DPI
"""
import logging
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # headless backend - must come before pyplot import
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import config

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
    stream=sys.stdout,
)


def main() -> None:
    """Generate Figure 1 from the canonical processed panel."""
    df = pd.read_parquet(config.PROCESSED_DIR / "panel.parquet")
    df = df[df["date"] <= pd.Timestamp("2024-12-31")].copy()

    sns.set_theme(style="whitegrid")
    fig, ax = plt.subplots(figsize=(10, 5))

    colors = {
        "KOSPI": "#1f77b4",
        "TOPIX": "#ff7f0e",
        "SP500": "#2ca02c",
        "MSCI_EM": "#d62728",
    }
    labels = {
        "KOSPI": "KOSPI",
        "TOPIX": "TOPIX",
        "SP500": "S&P 500",
        "MSCI_EM": "MSCI EM",
    }

    for country in config.COUNTRIES:
        sub = df[df["country"] == country].sort_values("date")
        ax.plot(
            sub["date"],
            sub["pb"],
            label=labels[country],
            color=colors[country],
            linewidth=1.5,
        )

    ax.set_xlabel("Date")
    ax.set_ylabel("Price-to-Book Ratio (P/B)")
    ax.set_title("Figure 1: Index-Level P/B Ratios, 2004-2024", fontsize=11)
    ax.legend(loc="upper left", frameon=True)
    ax.xaxis.set_major_locator(mdates.YearLocator(4))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))

    for event_date, event_label in config.EVENT_LABELS.items():
        ax.axvline(
            pd.Timestamp(event_date),
            color="grey",
            linestyle="--",
            linewidth=0.8,
            alpha=0.7,
        )
        ax.text(
            pd.Timestamp(event_date),
            1.0,
            event_label,
            transform=ax.get_xaxis_transform(),
            rotation=90,
            verticalalignment="top",
            fontsize=7,
            color="grey",
        )

    output_path = config.OUTPUT_DIR / "figures" / "figure1_pb_comparison.pdf"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(
        output_path,
        dpi=300,
        bbox_inches="tight",
        format="pdf",
        metadata={"CreationDate": None, "ModDate": None},
    )
    plt.close(fig)
    logging.info("Saved Figure 1 to %s", output_path)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
