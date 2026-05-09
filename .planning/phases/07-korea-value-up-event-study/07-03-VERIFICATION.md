---
phase: 07-korea-value-up-event-study
plan: 03
updated: 2026-04-23T20:10:39Z
---

# 07-03 Verification Log

## Task 1: Regenerate Japan and Korea event-study artifacts and prove they coexist

Completed at `2026-04-23T20:09:13Z`.

Command order executed exactly as specified:

1. `python src/analysis/event_study.py`
2. `shasum -a 256 output/figures/figure2_event_study.pdf output/tables/table_event_study_coefs.tex > /tmp/phase7-japan-before.sha`
3. `python src/analysis/korea_event_study.py`
4. `shasum -a 256 output/figures/figure2_event_study.pdf output/tables/table_event_study_coefs.tex > /tmp/phase7-japan-after.sha`
5. `diff -u /tmp/phase7-japan-before.sha /tmp/phase7-japan-after.sha`
6. `test -s output/figures/figure2_event_study.pdf`
7. `test -s output/tables/table_event_study_coefs.tex`
8. `test -s output/figures/figure_korea_event_study.pdf`
9. `test -s output/tables/korea_event_study_car.csv`
10. `test -s output/tables/table_korea_event_study_coefs.tex`

Observed results:

- Japan regeneration exited `0`.
- Korea regeneration exited `0`.
- `diff -u /tmp/phase7-japan-before.sha /tmp/phase7-japan-after.sha` exited `0`, so the Korea run did not alter the Japan figure or Japan table hashes.
- Japan figure/table and Korea figure/CAR/table all existed and were non-empty after regeneration.

## Task 2: Run targeted and full-suite regression gates

Completed at `2026-04-23T20:10:39Z`.

Commands executed:

1. `pytest tests/test_phase7.py -q`
2. `pytest tests/test_phase3.py -q`
3. `pytest -q`
4. `python -c "import pandas as pd; df = pd.read_csv('output/tables/korea_event_study_car.csv'); assert df['cohort'].nunique() == 3; print('phase7-verify-ok')"`

Observed results:

- `pytest tests/test_phase7.py -q` exited `0` with `7 passed in 0.58s`.
- `pytest tests/test_phase3.py -q` exited `0` with `14 passed in 14.62s`.
- `pytest -q` exited `0` with `51 passed in 14.64s`.
- The Korea CAR cohort-count verification printed `phase7-verify-ok`.

## Manual Follow-Up

- Review `output/figures/figure_korea_event_study.pdf` for readability, especially the clustered 2024 cohort titles/panels. This remains a human-only paper-quality check after the automated gates passed.
