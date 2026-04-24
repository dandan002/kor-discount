---
phase: 8
slug: robustness-and-comparative-interpretation
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-04-24
---

# Phase 8 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest |
| **Config file** | `pytest.ini` / repo-default pytest discovery |
| **Quick run command** | `pytest tests/test_phase8.py -q` |
| **Full suite command** | `pytest -q` |
| **Estimated runtime** | ~15-25 seconds |

---

## Sampling Rate

- **After every task commit:** Run `pytest tests/test_phase8.py -q`
- **After every plan wave:** Run `pytest tests/test_phase6.py tests/test_phase7.py tests/test_phase8.py -q`
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 25 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 08-01-01 | 01 | 1 | KROB-01 | T-08-01 / — | Narrow and spaced Korea date specs rerun under explicit named policies and write distinct robustness artifact paths | unit+integration | `pytest tests/test_phase8.py::test_korea_robustness_date_specs_generate_expected_windows -q` | ❌ W0 | ⬜ pending |
| 08-01-02 | 01 | 1 | KROB-01 | T-08-02 / — | The spaced follow-through specification does not silently overstate the available post-treatment horizon | content | `python src/analysis/korea_event_study_robustness.py && pytest tests/test_phase8.py::test_spaced_follow_through_window_is_capped_at_two_months -q` | ❌ W0 | ⬜ pending |
| 08-02-01 | 02 | 2 | KROB-02 | T-08-03 / — | Alternative narrow-window sensitivity reruns from fresh code paths rather than passing against stale artifacts | smoke | `python src/analysis/korea_event_study_robustness.py && pytest tests/test_phase8.py::test_narrow_window_sensitivity_reruns_cleanly -q` | ❌ W0 | ⬜ pending |
| 08-02-02 | 02 | 2 | KROB-02 | T-08-04 / — | Comparator sensitivity stays within existing repo surfaces and does not mutate the shipped TOPIX-based event-study core | unit+content | `pytest tests/test_phase8.py::test_phase8_does_not_refactor_event_study_core_comparator_contract -q` | ❌ W0 | ⬜ pending |
| 08-03-01 | 03 | 3 | KROB-03 | T-08-05 / — | Japan-versus-Korea note states descriptive timing evidence only and rejects stronger causal language | content | `pytest tests/test_phase8.py::test_korea_japan_note_contains_causal_caveats -q` | ❌ W0 | ⬜ pending |
| 08-03-02 | 03 | 3 | KROB-01..03 | T-08-01..05 / — | Phase 8 robustness outputs and interpretation note coexist with prior milestone artifacts and do not regress Phase 6/7 contracts | integration | `pytest tests/test_phase6.py tests/test_phase7.py tests/test_phase8.py -q && pytest -q` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_phase8.py` — robustness and interpretation gate for KROB-01 through KROB-03
- [ ] Fresh-output smoke coverage — Phase 8 tests must execute the robustness runner or equivalent fresh generation path rather than checking pre-existing files only
- [ ] Interpretation-note contract checks — pytest coverage for descriptive-only Japan-versus-Korea wording

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Review Phase 8 robustness figure/table naming and note phrasing for paper-readiness | KROB-01, KROB-03 | The final wording and presentation suitability of comparison-ready artifacts cannot be fully validated programmatically | Open the generated Phase 8 robustness artifacts and confirm the spec names, shortened-window disclosures, and Japan-versus-Korea caveat note are readable and publication-appropriate |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 25s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
