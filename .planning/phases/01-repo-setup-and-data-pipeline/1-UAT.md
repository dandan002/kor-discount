---
status: testing
phase: 01-repo-setup-and-data-pipeline
source: [ROADMAP.md success criteria]
started: 2026-04-16T00:00:00Z
updated: 2026-04-16T00:00:00Z
---

## Current Test

<!-- OVERWRITE each test - shows where we are -->

number: 1
name: Dependencies Install Clean
expected: |
  Running `pip install -r requirements.txt` in a fresh environment installs all pinned dependencies without error.
awaiting: user response

## Tests

### 1. Dependencies Install Clean
expected: Running `pip install -r requirements.txt` in a fresh environment installs all pinned dependencies without error.
result: [pending]

### 2. Event Dates Locked in config.py
expected: `config.py` exists at the repo root (or `src/`) with event dates locked to official policy records — 2014-02-01, 2015-06-01, 2023-03-01 — before any data is loaded.
result: [pending]

### 3. Raw Data Manifest
expected: `data/raw/` contains source files with a MANIFEST documenting source URL, vintage date, and download method for each series. No undocumented files.
result: [pending]

### 4. build_panel.py Produces panel.parquet
expected: Running `python src/data/build_panel.py` produces `data/processed/panel.parquet` with schema (date, country, pb, pe) covering ~2004-2024 at monthly frequency for at least KOSPI, TOPIX, SP500, MSCI_EM — with no undocumented missing observations.
result: [pending]

### 5. GFC Compression Visible (no survivorship bias)
expected: The 2008-2009 global financial crisis period shows a sharp P/B compression for all markets in the panel, confirming absence of survivorship bias (i.e., data includes the crash, not just the recovery).
result: [pending]

## Summary

total: 5
passed: 0
issues: 0
pending: 5
skipped: 0

## Gaps

[none yet]
