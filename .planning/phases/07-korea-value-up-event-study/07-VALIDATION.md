---
phase: 7
slug: korea-value-up-event-study
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-04-23
---

# Phase 7 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest |
| **Config file** | `pytest.ini` / repo-default pytest discovery |
| **Quick run command** | `pytest tests/test_phase7.py -q` |
| **Full suite command** | `pytest -q` |
| **Estimated runtime** | ~10-20 seconds |

---

## Sampling Rate

- **After every task commit:** Run `pytest tests/test_phase7.py -q`
- **After every plan wave:** Run `pytest -q`
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 20 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 07-01-01 | 01 | 1 | KEVNT-04 | — | Japan event-study entrypoint remains intact while Korea logic moves behind explicit parameters or a separate entrypoint | collect/unit | `pytest tests/test_phase7.py --collect-only -q` | ❌ W0 | ⬜ pending |
| 07-01-02 | 01 | 1 | KEVNT-03 | — | Korea overlap handling is explicit in code and test contracts | unit | `pytest tests/test_phase7.py -q` | ❌ W0 | ⬜ pending |
| 07-02-01 | 02 | 1 | KEVNT-01, KEVNT-02 | — | Korea event-study script writes CSV, LaTeX, and PDF outputs under Korea-specific paths | smoke | `python src/analysis/korea_event_study.py && pytest tests/test_phase7.py -q` | ❌ W0 | ⬜ pending |
| 07-02-02 | 02 | 1 | KEVNT-03 | — | Korea CAR outputs cover the configured plotted window and preserve overlap annotations for clustered dates | unit+content | `python src/analysis/korea_event_study.py && pytest tests/test_phase7.py -q` | ❌ W0 | ⬜ pending |
| 07-03-01 | 03 | 2 | KEVNT-04 | — | Japan and Korea artifact paths coexist without silent overwrites | integration | `python src/analysis/event_study.py && python src/analysis/korea_event_study.py && pytest tests/test_phase7.py -q` | ✅ | ⬜ pending |
| 07-03-02 | 03 | 2 | KEVNT-01..04 | — | Full project regression gate passes after Korea event-study additions | integration | `pytest -q` | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_phase7.py` — Korea event-study contract coverage for KEVNT-01 through KEVNT-04

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Review `output/figures/figure_korea_event_study.pdf` for readable titles, axes, and overlap-heavy cohort panels | KEVNT-02, KEVNT-03 | Figure readability and paper suitability cannot be verified programmatically | Open the PDF and confirm the Korea panels are readable, use the same visual language as the Japan figure, and do not become visually ambiguous because of clustered 2024 reform dates |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 20s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
