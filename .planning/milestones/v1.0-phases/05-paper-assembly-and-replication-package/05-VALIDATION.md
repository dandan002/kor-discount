---
phase: 5
slug: paper-assembly-and-replication-package
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-04-20
---

# Phase 5 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 7.x |
| **Config file** | `pytest.ini` (existing) |
| **Quick run command** | `python -c "import subprocess; subprocess.run(['python', 'run_all.py'], check=True)"` |
| **Full suite command** | `pytest tests/ -v && latexmk -pdf paper/main.tex && echo "PDF compiled"` |
| **Estimated runtime** | ~120 seconds |

---

## Sampling Rate

- **After every task commit:** Run `pytest tests/ -v -x`
- **After every plan wave:** Run full suite (run_all.py + latexmk compile)
- **Before `/gsd-verify-work`:** Full suite must be green; PDF must compile
- **Max feedback latency:** 120 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 05-01-01 | 01 | 1 | OUTPUT-03 | — | N/A | integration | `python run_all.py` | ✅ | ⬜ pending |
| 05-01-02 | 01 | 1 | OUTPUT-03 | — | N/A | integration | `python run_all.py && echo OK` | ❌ W0 | ⬜ pending |
| 05-02-01 | 02 | 1 | POLICY-02 | — | N/A | integration | `python src/policy/counterfactual_projection.py && test -f output/figures/figure4_counterfactual_projection.pdf` | ❌ W0 | ⬜ pending |
| 05-03-01 | 03 | 2 | PAPER-01..10 | — | N/A | compile | `latexmk -pdf paper/main.tex && test -f paper/main.pdf` | ❌ W0 | ⬜ pending |
| 05-04-01 | 04 | 3 | OUTPUT-01,02 | — | N/A | compile | `latexmk -pdf paper/main.tex 2>&1 | grep -v "Warning"` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `src/policy/__init__.py` — policy package init
- [ ] `paper/` directory exists

*Note: pytest test suite from Phases 1–4 continues to run; no new test file required for prose/LaTeX tasks. Wave 0 creates the package and directory scaffolds.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| PDF is ~35–50 pages with all 10 sections | PAPER-01..10 | Page count and prose quality require human review | Open `paper/main.pdf`, check section headings and page count |
| Figures render correctly in PDF | OUTPUT-01 | Visual layout cannot be verified programmatically | Inspect Figures 1–4 in the compiled PDF |
| Counterfactual projection clearly labeled illustrative | POLICY-02 | Text label requires human confirmation | Check Figure 4 caption in compiled PDF |
| Policy recommendations tied to FSC/KRX/stewardship levers | POLICY-01 | Content quality requires human review | Read policy section in compiled PDF |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 120s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
