---
phase: 3
slug: primary-empirics
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-04-17
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
| 3-W0-01 | W0 | 0 | EVNT-01..04, OLS-01..03, GEO-01..03 | — | N/A | infra | `pytest tests/test_phase3.py -x -q` | ❌ W0 | ⬜ pending |
| 3-01-01 | 01 | 1 | EVNT-01, EVNT-03 | — | N/A | unit | `pytest tests/test_phase3.py::test_three_cohorts -x` | ❌ W0 | ⬜ pending |
| 3-01-02 | 01 | 1 | EVNT-02, EVNT-04 | — | N/A | smoke | `pytest tests/test_phase3.py::test_figure2_exists tests/test_phase3.py::test_figure2_panels tests/test_phase3.py::test_event_study_coefs -x` | ❌ W0 | ⬜ pending |
| 3-02-01 | 02 | 2 | OLS-01, OLS-02, OLS-03 | — | N/A | smoke+content | `pytest tests/test_phase3.py::test_table2_exists tests/test_phase3.py::test_table2_reform_dummies tests/test_phase3.py::test_table2_booktabs -x` | ❌ W0 | ⬜ pending |
| 3-03-01 | 03 | 3 | GEO-01, GEO-02, GEO-03 | — | N/A | unit+smoke+content | `pytest tests/test_phase3.py::test_gpr_threshold tests/test_phase3.py::test_figure3_exists tests/test_phase3.py::test_geo_caveats -x` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_phase3.py` — stubs for EVNT-01 through GEO-03
- [ ] `src/analysis/__init__.py` — empty package init
- [ ] Download `data/raw/data_gpr_export.xls` from `https://www.matteoiacoviello.com/gpr_files/data_gpr_export.xls`
- [ ] Add MANIFEST.md entry for `data_gpr_export.xls`

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| 2014-cohort post-period truncation flagged in paper | EVNT-03 | Requires human review of written methodology text | Check that event_study.py comment documents t=+1..+15 truncation for 2014 cohort; verify paper draft acknowledges this limitation |
| Partial-identification caveats are substantive | GEO-03 | Automated test checks presence of keywords, not quality of argument | Review geo_risk.py script docstring and output .tex fragment to confirm caveats explain endogeneity limitations |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 30s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
