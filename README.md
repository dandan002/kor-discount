# Korea Discount: Value-Up Compliance Study

Reproducible empirical pipeline studying KOSPI firms' compliance with Korea's 2024 Corporate Value-Up program.

## Setup

```bash
python -m venv venv
source venv/bin/activate          # macOS/Linux
# venv\Scripts\activate           # Windows
pip install -r requirements.txt
cp .env.example .env
# Edit .env if Bloomberg host/port differ from defaults
```

## IMPORTANT: Always run from project root

All scripts must be run from the project root directory so that the `utils/` package is importable:

```bash
# CORRECT
python src/00_build_universe.py
python src/01_bloomberg_pull.py

# WRONG - will raise ModuleNotFoundError for utils
cd src && python 00_build_universe.py
```

## Bloomberg terminal session (one-time)

At a Bloomberg terminal:

```bash
pip install blpapi
python utils/bbg.py --test            # verify connection
python src/00_build_universe.py       # -> data/raw/universe_raw.csv
python src/01_bloomberg_pull.py       # -> data/raw/bloomberg/*.csv
ls -lh data/raw/bloomberg/            # confirm three non-empty CSVs
```

Once `data/raw/bloomberg/` contains `snapshot_2023.csv`, `roe_panel.csv`, and `returns_panel.csv`, all remaining work is offline.

## Pipeline

```bash
make acquire    # Bloomberg terminal only - pulls raw CSVs
make analysis   # Offline - builds compliance dataset, runs all analyses
make paper      # Offline - compiles LaTeX paper to outputs/paper.pdf
make all        # acquire + analysis + paper
```

## Directory layout

```text
src/             analysis scripts (00_build_universe.py through 07_event_study.py)
utils/           shared Python package (bbg, stats, latex_tables)
data/raw/        Bloomberg CSVs and manual data (never modified)
data/processed/  pipeline outputs (sample.csv, compliance.csv, etc.)
outputs/         tables (.tex), figures (.pdf), logs
paper/           LaTeX paper scaffold
```
