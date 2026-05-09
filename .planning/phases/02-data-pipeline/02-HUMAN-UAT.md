---
status: partial
phase: 02-data-pipeline
source: [02-VERIFICATION.md]
started: 2026-05-09T00:19:13Z
updated: 2026-05-09T00:19:13Z
---

## Current Test

[awaiting human testing]

## Tests

### 1. Full Pipeline Execution with Real Data

expected: |
  Run complete pipeline: (1) Hand-code data/raw/krx/compliance_coded.csv with all KOSPI firms,
  (2) python src/01c_dart_pull.py (internet + FSS_API_KEY), (3) python src/02_build_compliance.py,
  (4) python src/03_merge_covariates.py — compliance.csv has ~948 rows, events.csv has compliant
  firms only, sample.csv has 25 columns with real data
result: [pending]

### 2. DART API Execution

expected: |
  python src/01c_dart_pull.py with FSS_API_KEY in .env produces
  data/raw/dart/controlling_shareholder.csv with per-firm controlling shareholder percentages;
  corp_code_map.csv cached; no-DART-match firms printed to stdout
result: [pending]

### 3. Real Data Missingness Review

expected: |
  After full pipeline execution, review missingness report from 03_merge_covariates.py — most
  columns <10% missingness; note any columns with >20% missingness
result: [pending]

## Summary

total: 3
passed: 0
issues: 0
pending: 3
skipped: 0
blocked: 0

## Gaps