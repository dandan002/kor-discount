"""
tests/test_descriptive.py - Smoke and unit tests for Phase 2 descriptive outputs.

Run: pytest tests/test_descriptive.py -x -q
"""
import sys
from pathlib import Path

import pandas as pd
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import config

OUTPUT_FIGURES = config.OUTPUT_DIR / "figures"
OUTPUT_TABLES  = config.OUTPUT_DIR / "tables"


# DESC-01 checks
def test_figure1_pdf_exists():
    assert (OUTPUT_FIGURES / "figure1_pb_comparison.pdf").exists()

def test_figure1_pdf_nonempty():
    path = OUTPUT_FIGURES / "figure1_pb_comparison.pdf"
    assert path.stat().st_size > 0

# DESC-02 checks
def test_table1_tex_exists():
    assert (OUTPUT_TABLES / "table1_summary_stats.tex").exists()

def test_table1_booktabs():
    content = (OUTPUT_TABLES / "table1_summary_stats.tex").read_text()
    assert "\\toprule" in content

# DESC-03 checks
def test_discount_csv_exists():
    path = OUTPUT_TABLES / "discount_stats.csv"
    assert path.exists()
    df = pd.read_csv(path)
    assert "TOPIX" in df["benchmark"].values
    assert "MSCI_EM" in df["benchmark"].values

def test_discount_topix_negative():
    df = pd.read_csv(OUTPUT_TABLES / "discount_stats.csv")
    topix_mean = df[df["benchmark"] == "TOPIX"]["mean"].iloc[0]
    assert topix_mean < 0

def test_discount_tstat_significant():
    df = pd.read_csv(OUTPUT_TABLES / "discount_stats.csv")
    for _, row in df.iterrows():
        assert abs(row["t_stat"]) > 2.0, (
            f"t-stat for {row['benchmark']} = {row['t_stat']:.2f}, expected |t| > 2.0"
        )
