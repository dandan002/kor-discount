---
phase: 06-korea-reform-date-locking-and-sample-horizon
plan: "01"
tags: [dates, documentation, korea-value-up]
key_files:
  created:
    - .planning/phases/06-korea-reform-date-locking-and-sample-horizon/06-DATE-LOCK.md
---

# Phase 06 Plan 01 Summary

## One-liner

Created the phase-local Korea reform date lock memo with official-source rules, primary and robustness date sets, excluded dates, and the `2026-04-30` window constraint for later phases.

## Results

- Locked the primary 2024 rollout set: `2024-02-26`, `2024-05-02`, `2024-08-12`
- Locked the robustness follow-through set: `2024-02-26`, `2025-07-09`, `2026-02-24`
- Documented why `2024-04-02` and `2024-12-24` are excluded from the primary specification
- Recorded the hand-off rule that Phase 7 should default to the narrow 2024 set and treat the spaced set as robustness

## Verification

- The required sections exist in `06-DATE-LOCK.md`
- All required dates are present in the memo
- The memo states the `20-26 post-treatment months` constraint from the `2026-04-30` endpoint
