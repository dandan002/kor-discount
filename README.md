# The Korea Discount, Corporate Governance, and Lessons from Reforms

This repository contains the replication package for the paper "Corporate Governance Reform and the Korea Discount: Evidence from Japan's Natural Experiment."

## Reproduction

To regenerate all figures and tables from raw data:

```bash
pip install -r requirements.txt
python run_all.py
```

Then compile the paper:

```bash
cd paper && latexmk -pdf main.tex
```

**Requirements:**
- `data/processed/panel.parquet` must exist (run `python src/data/build_panel.py` once with raw data)
- All `data/raw/` CSV files must be present (see `data/raw/MANIFEST.md`)
- TeX Live 2024 (latexmk, pdflatex) must be installed

The `run_all.py` script regenerates all outputs in dependency order and will fail fast (non-zero exit) if any script fails, naming the failed script. This regenerates all 11 analysis outputs including figures, tables, and robustness checks.
