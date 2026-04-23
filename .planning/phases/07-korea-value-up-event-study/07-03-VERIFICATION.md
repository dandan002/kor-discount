---
phase: 07-korea-value-up-event-study
plan: 03
updated: 2026-04-23T20:09:13Z
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
