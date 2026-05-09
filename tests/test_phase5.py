"""
tests/test_phase5.py - Smoke and existence tests for Phase 5 outputs.

Run: pytest tests/test_phase5.py -x -q
"""
import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import config

FIGURES_DIR = config.OUTPUT_DIR / "figures"
TABLES_DIR = config.OUTPUT_DIR / "tables"
ROBUSTNESS_DIR = config.OUTPUT_DIR / "robustness"
PAPER_DIR = PROJECT_ROOT / "paper"


def test_counterfactual_figure_exists():
    """POLICY-02: figure4_counterfactual_projection.pdf must exist and be non-empty."""
    p = FIGURES_DIR / "figure4_counterfactual_projection.pdf"
    assert p.exists(), f"Missing: {p}"
    assert p.stat().st_size > 0, f"Empty file: {p}"


def test_all_figures_exist():
    """OUTPUT-01: All main figures must exist in output/figures/."""
    required = [
        "figure1_pb_comparison.pdf",
        "figure2_event_study.pdf",
        "figure3_geo_risk.pdf",
        "figure_synth_gap.pdf",
        "figure4_counterfactual_projection.pdf",
    ]
    for fname in required:
        p = FIGURES_DIR / fname
        assert p.exists(), f"Missing figure: {p}"
        assert p.stat().st_size > 0, f"Empty figure: {p}"


def test_synthetic_control_gap_csv_exists():
    """SYNTH-GAP: synthetic_control_gap.csv must exist and be non-empty."""
    p = ROBUSTNESS_DIR / "synthetic_control_gap.csv"
    assert p.exists(), f"Missing: {p}"
    assert p.stat().st_size > 0, f"Empty file: {p}"


def test_gap_csv_columns():
    """SYNTH-GAP: synthetic_control_gap.csv must have exactly columns [date, gap]."""
    p = ROBUSTNESS_DIR / "synthetic_control_gap.csv"
    assert p.exists(), f"Run synthetic_control.py first: {p}"
    df = pd.read_csv(p)
    assert list(df.columns) == ["date", "gap"], (
        f"Expected columns ['date', 'gap'], got {df.columns.tolist()}"
    )
    assert len(df) >= 100, f"Expected >= 100 rows, got {len(df)}"


def test_run_all_exists():
    """OUTPUT-03: run_all.py must exist at the repo root."""
    p = PROJECT_ROOT / "run_all.py"
    assert p.exists(), f"Missing: {p}"


def test_paper_dir_exists():
    """OUTPUT-01: paper/ directory must exist at repo root."""
    assert PAPER_DIR.exists(), f"Missing directory: {PAPER_DIR}"
    assert PAPER_DIR.is_dir(), f"Not a directory: {PAPER_DIR}"


def test_main_tex_exists():
    """OUTPUT-01: paper/main.tex must exist."""
    p = PAPER_DIR / "main.tex"
    assert p.exists(), f"Missing: {p}"
    assert p.stat().st_size > 0, f"Empty file: {p}"


def test_required_sections_present():
    """OUTPUT-01: paper/main.tex must contain all required section headings."""
    p = PAPER_DIR / "main.tex"
    assert p.exists(), f"Run paper assembly first: {p}"
    content = p.read_text(encoding="utf-8")
    required_sections = [
        r"\section{Introduction}",
        r"\section{Institutional Background}",
        r"\section{Literature Review}",
        r"\section{Data}",
        r"\section{Causal Mechanisms}",
        r"\section{Empirical Strategy}",
        r"\section{Results}",
        r"\section{Discussion",
        r"\section{Conclusion}",
        r"\section{Policy Recommendations}",
    ]
    for section in required_sections:
        assert section in content, f"Missing section in main.tex: {section}"


def test_references_bib_exists():
    """OUTPUT-01: paper/references.bib must exist."""
    p = PAPER_DIR / "references.bib"
    assert p.exists(), f"Missing: {p}"
    assert p.stat().st_size > 0, f"Empty file: {p}"
