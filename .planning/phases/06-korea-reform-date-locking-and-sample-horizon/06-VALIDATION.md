---
phase: 6
slug: korea-reform-date-locking-and-sample-horizon
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-04-23
---

# Phase 6 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest |
| **Config file** | `pytest.ini` / repo-default pytest discovery |
| **Quick run command** | `pytest tests/test_phase6.py -q` |
| **Full suite command** | `pytest -q` |
| **Estimated runtime** | ~10-20 seconds |

---

## Sampling Rate

- **After every task commit:** Run `pytest tests/test_phase6.py -q`
- **After every plan wave:** Run `pytest -q`
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 20 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 06-01-01 | 01 | 1 | DATES-01 | — | Locked dates are documented from official sources only | doc check | `rg -n "2024-02-26|2024-05-02|2024-08-12|2025-07-09|2026-02-24" .planning/phases/06-korea-reform-date-locking-and-sample-horizon` | ✅ | ⬜ pending |
| 06-02-01 | 02 | 1 | DATES-02 | — | `config.py` exposes separate Japan and Korea event collections | unit | `pytest tests/test_phase6.py -q` | ❌ W0 | ⬜ pending |
| 06-02-02 | 02 | 1 | SAMPLE-01 | — | Extended sample horizon is represented in shared constants/helpers without breaking Japan defaults | unit | `pytest tests/test_phase6.py -q` | ❌ W0 | ⬜ pending |
| 06-03-01 | 03 | 2 | SAMPLE-02 | — | Verification confirms panel max date and non-regression paths | integration | `pytest -q` | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_phase6.py` — config/date/horizon regression coverage for DATES-02, SAMPLE-01, SAMPLE-02

*If none: "Existing infrastructure covers all phase requirements."*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Review the phase date memo for source fidelity and narrative choice | DATES-01 | Official-source correctness and primary-vs-robustness framing are judgment calls | Open the phase memo and confirm every event date maps to an FSC/KRX source and that the narrow vs spaced date-set rationale is explicit |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 20s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
