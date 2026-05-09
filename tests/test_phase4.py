"""
tests/test_phase4.py - Smoke and unit tests for Phase 4 robustness outputs.

Run: pytest tests/test_phase4.py -x -q
"""
import ast
import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import config

ROBUSTNESS_DIR = config.OUTPUT_DIR / "robustness"
FIGURES_DIR = config.OUTPUT_DIR / "figures"
PANEL_PATH = config.PROCESSED_DIR / "panel.parquet"


def test_synth_weights_sum_to_one():
    """SYNTH-01: Donor weights must sum to 1.0 (convexity constraint)."""
    path = ROBUSTNESS_DIR / "synthetic_control_weights.csv"
    assert path.exists(), f"Run synthetic_control.py first: {path}"
    df = pd.read_csv(path)
    total = df["weight"].sum()
    assert abs(total - 1.0) < 1e-3, f"Weights sum to {total:.6f}, expected 1.0"


def test_synth_outputs_exist():
    """SYNTH-02: synthetic_control_weights.csv must exist with positive RMSPE."""
    path = ROBUSTNESS_DIR / "synthetic_control_weights.csv"
    assert path.exists(), f"Missing: {path}"
    assert path.stat().st_size > 0
    df = pd.read_csv(path)
    assert "donor" in df.columns
    assert "weight" in df.columns
    assert "pre_rmspe" in df.columns
    assert (df["pre_rmspe"] > 0).all()


def test_sutva_comment_present():
    """SYNTH-03: SUTVA justification comment must appear in synthetic_control.py."""
    source = PROJECT_ROOT / "src" / "robustness" / "synthetic_control.py"
    content = source.read_text()
    assert "SUTVA" in content, "SUTVA justification comment missing from synthetic_control.py"
    assert "STOXX600" in content
    assert "KOSPI" in content


def test_placebo_outputs_exist():
    """ROBUST-01: placebo CSV files must exist with expected columns."""
    for market in ("taiwan", "indonesia"):
        path = ROBUSTNESS_DIR / f"placebo_{market}_car.csv"
        assert path.exists(), f"Missing: {path}"
        df = pd.read_csv(path)
        assert "event_rel_time" in df.columns
        assert "car" in df.columns


def test_robust02_outputs_exist():
    """ROBUST-02: P/E robustness LaTeX files must exist and contain P/E header."""
    for fname in ("robustness_pe_ols.tex", "robustness_pe_event_coefs.tex"):
        path = ROBUSTNESS_DIR / fname
        assert path.exists(), f"Missing: {path}"
        assert path.stat().st_size > 0
        content = path.read_text()
        assert any(token in content.lower() for token in ("p/e", "price-to-earnings", "pe"))


def test_robust03_outputs_exist():
    """ROBUST-03: alt-control LaTeX files must exist."""
    for fname in (
        "robustness_alt_control_em_asia.tex",
        "robustness_alt_control_em_exchina.tex",
    ):
        path = ROBUSTNESS_DIR / fname
        assert path.exists(), f"Missing: {path}"
        assert path.stat().st_size > 0


def test_robust04_outputs_exist():
    """ROBUST-04: in-time and in-space placebo figures must exist."""
    for fname in ("figure_placebo_intime.pdf", "figure_placebo_inspace.pdf"):
        path = ROBUSTNESS_DIR / fname
        assert path.exists(), f"Missing: {path}"
        assert path.stat().st_size > 0


def test_robustness_modules_do_not_import_each_other():
    """Robustness scripts must be standalone - no cross-imports within src/robustness/."""
    robustness_modules = {
        "synthetic_control",
        "robustness_pe",
        "robustness_alt_control",
        "robustness_placebo",
    }
    for module_name in robustness_modules:
        path = PROJECT_ROOT / "src" / "robustness" / f"{module_name}.py"
        if not path.exists():
            continue
        tree = ast.parse(path.read_text(), filename=str(path))
        for node in ast.walk(tree):
            if not isinstance(node, ast.ImportFrom) or node.module is None:
                continue
            module = node.module
            if module.startswith(("src.robustness.", "robustness.")):
                imported = module.rsplit(".", maxsplit=1)[-1]
                assert imported not in robustness_modules - {module_name}, (
                    f"{path} imports another robustness module: {module}"
                )
