---
phase: 07-korea-value-up-event-study
reviewed: 2026-04-23T20:17:00Z
depth: standard
files_reviewed: 4
files_reviewed_list:
  - src/analysis/event_study_core.py
  - src/analysis/event_study.py
  - src/analysis/korea_event_study.py
  - tests/test_phase7.py
findings:
  critical: 0
  warning: 2
  info: 1
  total: 3
status: issues_found
advisory_only: true
---

# Phase 07: Code Review Report

**Reviewed:** 2026-04-23T20:17:00Z
**Depth:** standard
**Files Reviewed:** 4
**Status:** issues_found

## Summary

Reviewed the Phase 07 source/test changes in `src/analysis/` and `tests/test_phase7.py`, using the Phase 07 summaries and `.planning/REQUIREMENTS.md` for scope/context only. No implementation-breaking defects or security issues were found in the Python analysis code, and both `pytest tests/test_phase7.py -q` and `pytest tests/test_phase3.py -q` pass in the current worktree.

The material risk is in the new test gate: it does not exercise the Korea generation path or automate the Japan non-overwrite guarantee that Phase 07 claims to preserve. That leaves room for stale artifacts or future wiring regressions to pass unnoticed.

## Warnings

### WR-01: Phase 7 Tests Pass Against Pre-Existing Artifacts Instead of Executing Korea Generation

**File:** `tests/test_phase7.py:59-79`
**Issue:** The main Korea assertions only verify that `output/tables/korea_event_study_car.csv`, `output/tables/table_korea_event_study_coefs.tex`, and `output/figures/figure_korea_event_study.pdf` already exist and that the committed CSV has the expected shape. The test never calls `src.analysis.korea_event_study.main()` or `event_study_core.run_event_study()`. A broken entrypoint, wrong output wiring, or lost table-comment plumbing could still pass as long as old artifacts remain in `output/`.
**Fix:**
```python
from src.analysis import korea_event_study

def test_phase7_korea_generation_smoke(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "OUTPUT_DIR", tmp_path)
    monkeypatch.setattr(
        korea_event_study, "KOREA_FIGURE_OUTPUT_PATH", tmp_path / "figures" / "figure_korea_event_study.pdf"
    )
    monkeypatch.setattr(
        korea_event_study, "KOREA_CAR_OUTPUT_PATH", tmp_path / "tables" / "korea_event_study_car.csv"
    )
    monkeypatch.setattr(
        korea_event_study, "KOREA_TABLE_OUTPUT_PATH", tmp_path / "tables" / "table_korea_event_study_coefs.tex"
    )

    korea_event_study.main()

    assert (tmp_path / "tables" / "korea_event_study_car.csv").exists()
    assert (tmp_path / "tables" / "table_korea_event_study_coefs.tex").read_text().find("max_post_months=") != -1
```

### WR-02: The Japan Non-Overwrite Contract Is Not Enforced by an Automated Regression Test

**File:** `tests/test_phase7.py:92-95`
**Issue:** `test_phase7_japan_artifacts_still_exist()` only checks that the Japan figure/table are present and non-empty. It does not verify the Phase 07 requirement that Korea generation leaves shipped Japan artifacts unchanged. A regression that accidentally rewrites `figure2_event_study.pdf` or `table_event_study_coefs.tex` would still pass if the files continue to exist.
**Fix:**
```python
import hashlib
from src.analysis import korea_event_study

def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def test_phase7_korea_run_does_not_modify_japan_artifacts():
    before = {path: _sha256(path) for path in (JAPAN_FIGURE, JAPAN_TABLE)}
    korea_event_study.main()
    after = {path: _sha256(path) for path in (JAPAN_FIGURE, JAPAN_TABLE)}
    assert after == before
```

## Info

### IN-01: Overlap Handling Is Checked Via a Source String Match, Not Observed Behavior

**File:** `tests/test_phase7.py:82-89`
**Issue:** The overlap requirement is currently satisfied by asserting that the combined source contains the word `"overlap"` and either `KOREA_EVENT_SET_POLICY` or `max_post_months`. That is brittle and can pass even if the generated dataset stops carrying `overlaps_other_event_window` / `overlap_event_labels` or if the Korea LaTeX comments stop disclosing the overlap/window notes.
**Fix:** Replace the source-string assertion with a behavioral check against generated outputs or a constructed stacked dataset, for example by asserting that the Korea LaTeX header contains the two note lines and that `build_stacked_dataset(...)` yields overlap columns with at least one `True` value for the primary Korea policy.

---

_Reviewed: 2026-04-23T20:17:00Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
