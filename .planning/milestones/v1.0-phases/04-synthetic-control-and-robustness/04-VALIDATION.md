---
phase: 4
slug: synthetic-control-and-robustness
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-04-20
---

# Phase 4 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 8.3.4 |
| **Config file** | none (direct invocation) |
| **Quick run command** | `pytest tests/test_phase4.py -x -q` |
| **Full suite command** | `pytest tests/ -q` |
| **Estimated runtime** | ~30 seconds |

---

## Sampling Rate

- **After every task commit:** Run `pytest tests/test_phase4.py -x -q`
- **After every plan wave:** Run `pytest tests/ -q`
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 30 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 4-W0-01 | W0 | 0 | SYNTH-01 | — | N/A | unit | `pytest tests/test_phase4.py::test_synth_weights_sum_to_one -x` | ❌ Wave 0 | ⬜ pending |
| 4-W0-02 | W0 | 0 | SYNTH-02 | — | N/A | smoke | `pytest tests/test_phase4.py::test_synth_outputs_exist -x` | ❌ Wave 0 | ⬜ pending |
| 4-W0-03 | W0 | 0 | SYNTH-03 | — | N/A | static | `pytest tests/test_phase4.py::test_sutva_comment_present -x` | ❌ Wave 0 | ⬜ pending |
| 4-W0-04 | W0 | 0 | ROBUST-01 | — | N/A | smoke | `pytest tests/test_phase4.py::test_placebo_outputs_exist -x` | ❌ Wave 0 | ⬜ pending |
| 4-W0-05 | W0 | 0 | ROBUST-02 | — | N/A | smoke | `pytest tests/test_phase4.py::test_robust02_outputs_exist -x` | ❌ Wave 0 | ⬜ pending |
| 4-W0-06 | W0 | 0 | ROBUST-03 | — | N/A | smoke | `pytest tests/test_phase4.py::test_robust03_outputs_exist -x` | ❌ Wave 0 | ⬜ pending |
| 4-W0-07 | W0 | 0 | ROBUST-04 | — | N/A | smoke | `pytest tests/test_phase4.py::test_robust04_outputs_exist -x` | ❌ Wave 0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_phase4.py` — stubs for SYNTH-01 through ROBUST-04 smoke tests
- [ ] `src/robustness/__init__.py` — empty package init
- [ ] `pysyncon==1.5.2` added to `requirements.txt` and installed
- [ ] `output/robustness/` directory pre-created

*All Wave 0 items must be green before Wave 1 execution begins.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Pre-treatment fit visual check | SYNTH-02 | Gap plot requires human judgment on fit quality | Open `output/figures/figure_synth_gap.pdf`; confirm pre-2023 synthetic Japan tracks actual Japan closely; RMSPE should be < 0.15 P/B points |
| In-space placebo distribution figure | ROBUST-04 | Outlier judgment requires human review | Open `output/robustness/figure_placebo_inspace.pdf`; confirm Japan's post-2023 gap is a visible outlier vs. donor pool placebos |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 30s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
