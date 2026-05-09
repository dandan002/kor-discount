# Korea Discount: Value-Up Compliance Study
# Usage:
#   make acquire   - Run Refinitiv acquisition scripts (Eikon terminal + REFINITIV_APP_KEY required)
#   make analysis  - Run all offline analysis scripts (requires data/raw/bloomberg/*.csv)
#   make paper     - Compile LaTeX paper to outputs/paper.pdf
#   make all       - Full pipeline: acquire + analysis + paper

.PHONY: acquire analysis paper all

SNAPSHOT = data/raw/bloomberg/snapshot_2023.csv
ROE_PANEL = data/raw/bloomberg/roe_panel.csv
RETURNS_PANEL = data/raw/bloomberg/returns_panel.csv

# --- Refinitiv acquisition (Eikon terminal + REFINITIV_APP_KEY required) ---
acquire:
	@if [ -f "$(SNAPSHOT)" ] && [ -f "$(ROE_PANEL)" ] && [ -f "$(RETURNS_PANEL)" ]; then \
		echo "CSVs already present. Delete data/raw/bloomberg/ to re-run."; \
	else \
		echo "Running Refinitiv acquisition scripts..."; \
		python src/00_build_universe.py && python src/01_bloomberg_pull.py; \
	fi

# --- Offline analysis pipeline ---
analysis:
	python src/02_build_compliance.py
	python src/03_merge_covariates.py
	python src/04_descriptive.py
	python src/05_logit_compliance.py
	python src/06_fundamentals_comparison.py
	python src/07_event_study.py

# --- LaTeX paper compilation ---
paper:
	cd paper && pdflatex main.tex && biber main && pdflatex main.tex && pdflatex main.tex
	cp paper/main.pdf outputs/paper.pdf

# --- Full pipeline ---
all: acquire analysis paper
