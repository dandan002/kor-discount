---
phase: 2
slug: descriptive-analysis
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-04-16
---

# Phase 2 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest |
| **Config file** | none — Wave 0 installs |
| **Quick run command** | `pytest tests/ -x -q` |
| **Full suite command** | `pytest tests/ -q` |
| **Estimated runtime** | ~10 seconds |

---

## Sampling Rate

- **After every task commit:** Run `pytest tests/ -x -q`
- **After every plan wave:** Run `pytest tests/ -q`
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** ~10 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 02-01-T1 | 02-01 | 1 | DESC-01, DESC-02, DESC-03 | — | N/A | scaffold | `python -c "import pytest; print('ok')"` | ❌ W0 | ⬜ pending |
| 02-01-T2 | 02-01 | 1 | DESC-01, DESC-02, DESC-03 | — | N/A | unit | `pytest tests/test_descriptive.py -x -q` | ❌ W0 | ⬜ pending |
| 02-02-T1 | 02-02 | 2 | DESC-01 | — | N/A | smoke | `pytest tests/test_descriptive.py::test_figure1_pdf_exists tests/test_descriptive.py::test_figure1_pdf_nonempty -x` | ❌ W0 | ⬜ pending |
| 02-02-T2 | 02-02 | 2 | DESC-02 | — | N/A | unit | `pytest tests/test_descriptive.py::test_table1_tex_exists tests/test_descriptive.py::test_table1_booktabs -x` | ❌ W0 | ⬜ pending |
| 02-03-T1 | 02-03 | 2 | DESC-03 | — | N/A | unit | `pytest tests/test_descriptive.py::test_discount_csv_exists tests/test_descriptive.py::test_discount_topix_negative tests/test_descriptive.py::test_discount_tstat_significant -x` | ❌ W0 | ⬜ pending |
| 02-04-T1 | 02-04 | 3 | DESC-01, DESC-02, DESC-03 | — | N/A | smoke | `pytest tests/ -q` | ❌ W0 | ⬜ pending |
| 02-04-T2 | 02-04 | 3 | DESC-01 | — | N/A | manual | Visual review of figure1_pb_comparison.pdf | N/A | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/__init__.py` — empty file for pytest discovery
- [ ] `tests/test_descriptive.py` — smoke + unit tests covering DESC-01, DESC-02, DESC-03
- [ ] `pip install pytest` — not in requirements.txt; needed for test runner
- [ ] `pip install -r requirements.txt` — pins scipy==1.13.1 (resolves statsmodels import error)

---

## Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command |
|--------|----------|-----------|-------------------|
| DESC-01 | `figure1_pb_comparison.pdf` exists in `output/figures/` after running `figure1.py` | smoke | `pytest tests/test_descriptive.py::test_figure1_pdf_exists -x` |
| DESC-01 | PDF file size > 0 bytes | smoke | `pytest tests/test_descriptive.py::test_figure1_pdf_nonempty -x` |
| DESC-02 | `table1_summary_stats.tex` exists in `output/tables/` | smoke | `pytest tests/test_descriptive.py::test_table1_tex_exists -x` |
| DESC-02 | `.tex` file contains `\toprule` (booktabs) | unit | `pytest tests/test_descriptive.py::test_table1_booktabs -x` |
| DESC-03 | `discount_stats.csv` exists and has TOPIX and MSCI_EM rows | unit | `pytest tests/test_descriptive.py::test_discount_csv_exists -x` |
| DESC-03 | KOSPI−TOPIX mean spread is negative (< 0) | unit | `pytest tests/test_descriptive.py::test_discount_topix_negative -x` |
| DESC-03 | t-statistic absolute value > 2.0 (statistically significant) | unit | `pytest tests/test_descriptive.py::test_discount_tstat_significant -x` |

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Figure 1 visual quality (line clarity, annotation placement, publication-plain style) | DESC-01 | Aesthetic judgment cannot be automated | Open `output/figures/figure1_pb_comparison.pdf`, verify: 4 labeled lines (KOSPI, TOPIX, SP500, MSCI_EM), 3 vertical dashed annotation lines with labels (2014-02-01, 2015-06-01, 2023-03-01), no PE series plotted, whitegrid style |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 10s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
