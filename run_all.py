#!/usr/bin/env python3
"""
run_all.py - Replication entry point for the Korea Discount study.

Regenerates all figures and tables from data/processed/panel.parquet
(and data/raw/ for GPR series). Does NOT regenerate panel.parquet itself.

Usage:
    pip install -r requirements.txt
    python run_all.py

Requirements:
    data/processed/panel.parquet must exist (run src/data/build_panel.py once)
    All data/raw/ CSV files must be present
"""
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent

SCRIPTS = [
    ("descriptive analysis — Figure 1", "src/descriptive/figure1.py"),
    ("descriptive analysis — Table 1", "src/descriptive/table1.py"),
    ("discount statistics", "src/descriptive/discount_stats.py"),
    ("event study", "src/analysis/event_study.py"),
    ("panel OLS", "src/analysis/panel_ols.py"),
    ("geopolitical risk", "src/analysis/geo_risk.py"),
    ("synthetic control", "src/robustness/synthetic_control.py"),
    ("placebo falsification", "src/robustness/robustness_placebo.py"),
    ("P/E robustness", "src/robustness/robustness_pe.py"),
    ("alternative control robustness", "src/robustness/robustness_alt_control.py"),
    ("counterfactual projection", "src/policy/counterfactual_projection.py"),
]


def main() -> None:
    n = len(SCRIPTS)
    for i, (label, script_rel) in enumerate(SCRIPTS, 1):
        script_path = PROJECT_ROOT / script_rel
        print(f"\n=== [{i}/{n}] Running {label} ===")
        subprocess.run([sys.executable, str(script_path)], check=True)
    print("\nAll outputs regenerated successfully.")


if __name__ == "__main__":
    main()
