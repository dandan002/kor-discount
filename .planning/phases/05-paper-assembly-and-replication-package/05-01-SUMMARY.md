---
phase: 05-paper-assembly-and-replication-package
plan: "01"
subsystem: replication-package
tags: [replication, policy, synthetic-control, counterfactual, run-all]
dependency_graph:
  requires:
    - output/robustness/synthetic_control_weights.csv
    - data/processed/panel.parquet
  provides:
    - output/robustness/synthetic_control_gap.csv
    - output/figures/figure4_counterfactual_projection.pdf
    - run_all.py
    - src/policy/__init__.py
    - src/policy/counterfactual_projection.py
    - tests/test_phase5.py
  affects:
    - src/robustness/synthetic_control.py
tech_stack:
  added:
    - src/policy (new Python package)
  patterns:
    - subprocess.run([sys.executable, path], check=True) for fail-fast script orchestration
    - Column validation + NaN guard before projection (T-05-02, T-05-03 mitigations)
key_files:
  created:
    - run_all.py
    - src/policy/__init__.py
    - src/policy/counterfactual_projection.py
    - tests/test_phase5.py
    - output/figures/figure4_counterfactual_projection.pdf
    - output/robustness/synthetic_control_gap.csv
  modified:
    - src/robustness/synthetic_control.py
decisions:
  - "RMSPE uncertainty band uses ±0.2893 (pre-treatment RMSPE from synthetic_control_weights.csv)"
  - "monthly_lift computed from month-over-month diff of gap series in 18 months post-TSE reform: 0.0186 P/B pts/month"
  - "Column assertion + NaN guard added to counterfactual_projection.py per threat model T-05-02/T-05-03"
metrics:
  duration_seconds: 155
  completed_date: "2026-04-21"
  tasks_completed: 3
  files_created: 6
  files_modified: 1
---

# Phase 05 Plan 01: Replication Foundation Summary

## One-liner

Replication entry point (run_all.py, 11 scripts), KOSPI P/B counterfactual projection figure (figure4), synthetic control gap CSV bridge, and Phase 5 test scaffold — all executed end-to-end with pytest gate passing.

## Tasks Completed

| Task | Name | Commit | Key Files |
|------|------|--------|-----------|
| 1 | Test scaffold + policy package + synthetic_control gap CSV write | 95589e4 | tests/test_phase5.py, src/policy/__init__.py, src/robustness/synthetic_control.py |
| 2 | counterfactual_projection.py + run_all.py | ad28893 | src/policy/counterfactual_projection.py, run_all.py |
| 3 | Run end-to-end and verify figure output | 1e266b5 | output/figures/figure4_counterfactual_projection.pdf, output/robustness/synthetic_control_gap.csv |

## Decisions Made

- RMSPE uncertainty band uses ±0.2893 (pre-treatment RMSPE from `synthetic_control_weights.csv`), consistent with Phase 4 accepted caveat.
- `monthly_lift` computed from month-over-month diff of post-reform gap series (months 1–18 after 2023-03-01): value = 0.0186 P/B pts/month.
- Column assertion `list(df.columns) == ["date", "gap"]` and NaN guard on `monthly_lift` added to `counterfactual_projection.py` per threat model T-05-02 and T-05-03.

## Key Results

- `output/robustness/synthetic_control_gap.csv`: 268 rows, columns [date, gap], written by updated `synthetic_control.py`
- `output/figures/figure4_counterfactual_projection.pdf`: 23,731 bytes, Japan-calibrated illustrative KOSPI P/B projection
- `run_all.py`: 11 scripts in dependency order, uses `sys.executable` and `check=True`, step banners, no `build_panel.py`
- `tests/test_phase5.py`: 9 test functions covering figure existence, gap CSV structure, run_all.py existence, paper/ directory, main.tex sections, references.bib

## Deviations from Plan

### Auto-added Missing Critical Functionality

**1. [Rule 2 - Security] Added column validation and NaN guard to counterfactual_projection.py**

- **Found during:** Task 2 (threat model review before implementation)
- **Issue:** Threat model T-05-02 requires validating synthetic_control_gap.csv columns; T-05-03 requires NaN guard on monthly_lift
- **Fix:** Added `assert list(gap_df.columns) == ["date", "gap"]` after CSV read; added `assert not pd.isna(monthly_lift)` before projection loop
- **Files modified:** src/policy/counterfactual_projection.py
- **Commit:** ad28893

## Known Stubs

None — all outputs are wired to real data sources and produce non-empty artifacts.

## Threat Flags

No new security-relevant surface introduced beyond what the plan's threat model already covers.

## Self-Check: PASSED

Files verified:
- run_all.py: FOUND
- src/policy/__init__.py: FOUND
- src/policy/counterfactual_projection.py: FOUND
- tests/test_phase5.py: FOUND
- output/figures/figure4_counterfactual_projection.pdf: FOUND (23731 bytes)
- output/robustness/synthetic_control_gap.csv: FOUND (268 rows)

Commits verified:
- 95589e4: FOUND (Task 1)
- ad28893: FOUND (Task 2)
- 1e266b5: FOUND (Task 3)

pytest gate: 3/3 tests passed
