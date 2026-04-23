---
phase: 06-korea-reform-date-locking-and-sample-horizon
plan: "02"
tags: [config, event-study, tests, horizon]
key_files:
  created:
    - src/analysis/study_window.py
    - tests/test_phase6.py
  modified:
    - config.py
    - src/analysis/event_study.py
---

# Phase 06 Plan 02 Summary

## One-liner

Added separate Japan and Korea event-date surfaces, a machine-readable Korea event policy, a shared study-end clip helper, and an event-study preparation path wired to the paper default horizon.

## Results

- Preserved backwards-compatible Japan aliases through `EVENT_DATES = JAPAN_EVENT_DATES` and `EVENT_LABELS = JAPAN_EVENT_LABELS`
- Added Korea narrow and spaced date sets plus labels and `KOREA_EVENT_SET_POLICY`
- Added `PAPER_STUDY_END` (`2024-12-31`) and `FOLLOW_ON_STUDY_END` (`2026-04-30`)
- Added `clip_to_study_end()` in `src/analysis/study_window.py`
- Added `prepare_event_study_panel()` and routed `build_stacked_dataset()` through the centralized paper horizon path
- Added six Phase 6 regression tests covering config separation and the follow-on horizon

## Verification

- `pytest tests/test_phase6.py -q` passed
- `python -c "import config; assert config.EVENT_DATES == config.JAPAN_EVENT_DATES; assert config.KOREA_EVENT_SET_POLICY['primary']['set_name']; assert config.FOLLOW_ON_STUDY_END.isoformat() == '2026-04-30'; print('phase6-config-ok')"` printed `phase6-config-ok`
