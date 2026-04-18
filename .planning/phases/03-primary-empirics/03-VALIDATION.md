---
phase: 3
slug: primary-empirics
status: ready_for_execution
nyquist_compliant: true
wave_0_complete: false
created: 2026-04-17
updated: 2026-04-18
---

# Phase 3 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 8.3.4 |
| **Config file** | none — implicit discovery |
| **Quick run command** | `pytest tests/test_phase3.py -x -q` |
| **Full suite command** | `pytest tests/ -x -q` |
| **Estimated runtime** | ~30 seconds |

`wave_0_complete: false` is intentional and truthful at plan time: the Wave 0/test-foundation work is planned in `03-01-PLAN.md` but has not been executed yet. `nyquist_compliant: true` means every planned implementation task has an automated verification path, and the required test/data foundation is explicitly scheduled before dependent Wave 2 analysis plans.

---

## Sampling Rate

- **After every task commit:** Run `pytest tests/test_phase3.py -x -q`
- **After every plan wave:** Run `pytest tests/ -x -q`
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 30 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 3-01-01 | 01 | 1 | EVNT-01..04, OLS-01..03, GEO-01..03 | T-03-01-01..05 | Test/data foundation is created before dependent analysis plans | infra | `pytest tests/test_phase3.py --collect-only -q` | planned in 03-01 | ⬜ pending |
| 3-01-02 | 01 | 1 | GEO-01 | T-03-01-01, T-03-01-03 | GPR source is local, provenance-tracked, and readable with xlrd | data smoke | `python -c "import pandas as pd; df = pd.read_excel('data/raw/data_gpr_export.xls', usecols=['month','GPRC_KOR'], engine='xlrd'); assert len(df) > 0; print('GPR XLS OK')"` | planned in 03-01 | ⬜ pending |
| 3-02-01 | 02 | 2 | EVNT-01, EVNT-02, EVNT-03 | T-03-02-01..04 | Event dates come from config, full D-01/D-02 windows are preserved, overlaps are annotated, HC3 SEs are used | unit+content | `pytest tests/test_phase3.py::test_three_cohorts tests/test_phase3.py::test_event_study_coefs -x` | after 03-02 | ⬜ pending |
| 3-02-02 | 02 | 2 | EVNT-04 | T-03-02-01..04 | Figure 2 is generated from complete -12..+24 CAR output for all cohorts | smoke | `pytest tests/test_phase3.py::test_figure2_exists tests/test_phase3.py::test_figure2_panels -x` | after 03-02 | ⬜ pending |
| 3-03-01 | 03 | 2 | OLS-01, OLS-02, OLS-03 | T-03-03-01..05 | PanelOLS two-way FE and country-clustered wild bootstrap are used | smoke+content | `pytest tests/test_phase3.py::test_table2_exists tests/test_phase3.py::test_table2_reform_dummies tests/test_phase3.py::test_table2_booktabs -x` | after 03-03 | ⬜ pending |
| 3-04-01 | 04 | 2 | GEO-01, GEO-03 | T-03-04-01..05 | GPR threshold is computed on 2004-2024 local data and caveats are emitted | unit+content | `pytest tests/test_phase3.py::test_gpr_threshold tests/test_phase3.py::test_geo_caveats -x` | after 03-04 | ⬜ pending |
| 3-04-02 | 04 | 2 | GEO-02 | T-03-04-01..05 | Figure 3 is generated from local panel and GPR inputs | smoke | `pytest tests/test_phase3.py::test_figure3_exists -x` | after 03-04 | ⬜ pending |
| 3-05-01 | 05 | 3 | EVNT-01..04, OLS-01..03, GEO-01..03 | T-03-05-01..05 | All outputs regenerate from canonical inputs | integration | `python src/analysis/event_study.py && python src/analysis/panel_ols.py && python src/analysis/geo_risk.py` | after 03-02..04 | ⬜ pending |
| 3-05-02 | 05 | 3 | EVNT-01..04, OLS-01..03, GEO-01..03 | T-03-05-01..05 | Full Phase 3 and project test gates pass | integration | `pytest tests/test_phase3.py -x -q && pytest tests/ -x -q` | after 03-05-01 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 / Test Foundation Requirements

- [ ] `tests/test_phase3.py` — stubs for EVNT-01 through GEO-03, including per-cohort pre-period coverage and plotted -12..+24 CAR coverage checks
- [ ] `src/analysis/__init__.py` — empty package init
- [ ] Download `data/raw/data_gpr_export.xls` from `https://www.matteoiacoviello.com/gpr_files/data_gpr_export.xls`
- [ ] Add MANIFEST.md entry for `data_gpr_export.xls`

These items are scheduled as Plan 03-01, Wave 1. They are not complete until `03-01-PLAN.md` executes and `pytest tests/test_phase3.py --collect-only -q` exits 0.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| 2014/2015 event-window overlap flagged in paper | EVNT-03 | Requires human review of written methodology text | Check that event_study.py comment and table notes document that both windows are preserved and overlapping months are annotated; verify paper draft acknowledges this limitation |
| Partial-identification caveats are substantive | GEO-03 | Automated test checks presence of keywords, not quality of argument | Review geo_risk.py script docstring and output .tex fragment to confirm caveats explain endogeneity limitations |

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or depend on Plan 03-01 test/data foundation
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Plan 03-01 covers all MISSING test/data foundation references before Wave 2
- [x] No watch-mode flags
- [x] Feedback latency < 30s
- [x] `nyquist_compliant: true` set in frontmatter for the plan-time validation contract
- [ ] `wave_0_complete: true` set after Plan 03-01 actually executes and its automated checks pass

**Approval:** ready for execution; Wave 0/test foundation not yet executed
