# Project Retrospective

*A living document updated after each milestone. Lessons feed forward into future planning.*

---

## Milestone: v1.0 — Korea Discount Study MVP

**Shipped:** 2026-04-21
**Phases:** 5 | **Plans:** 24 | **Timeline:** 7 days (2026-04-14 → 2026-04-21)

### What Was Built

- 20-year monthly panel dataset (KOSPI/TOPIX/S&P500/MSCI EM P/B & P/E) from Bloomberg exports, built via `build_panel.py` into `panel.parquet`
- Full econometric suite: stacked event study (Cengiz 2019), panel OLS with wild-bootstrap inference, GPR geopolitical sub-analysis, synthetic control (ADH 2010), placebo falsification, P/E and alt-control robustness checks
- 48-page submission-ready LaTeX paper (`paper/main.pdf`, 370 KB) integrating all programmatic figures and tables; replication package with `run_all.py` orchestrating 11 scripts

### What Worked

- **Strict dependency ordering** — the 5-phase pipeline (data → descriptive → primary empirics → robustness → paper) prevented downstream rework; no phase had to reach back for missing upstream outputs
- **Event-date firewall in `config.py`** — locking treatment dates before data loading eliminated look-ahead bias risk entirely; zero instances of date-related confusion in any phase
- **Pytest gate at every phase** — incremental test coverage meant each phase started with confidence in prior outputs; 38/38 tests passing at close
- **Human UAT gates** — Figure 1 visual sign-off (Phase 2) and synthetic control sign-off (Phase 4) caught presentation issues before they propagated to paper prose
- **Worktree isolation for Phase 5 plans** — parallel plan execution in isolated git worktrees prevented mid-flight conflicts during prose writing

### What Was Inefficient

- **REQUIREMENTS.md traceability table fell out of sync** — requirements marked "Pending" in REQUIREMENTS.md while PROJECT.md correctly tracked them as validated; the two documents drifted and required reconciliation at milestone close
- **Phase 3 gap-closure plan (03-06)** — EVNT-02 and OLS-03 defects were found at verification that could have been caught at plan-writing time; required an extra plan and delayed Phase 4 start
- **Synthetic control RMSPE discovery late** — RMSPE=0.2893 was only measured after full estimation; earlier pre-flight check of donor pool quality could have flagged this sooner
- **LaTeX compilation errors in Phase 5** — several `\label` / `\ref` / undefined command issues required a dedicated fix pass; a compile-early-and-often discipline would have saved time

### Patterns Established

- **All three Japan reform dates as stacked treatment events** — this design pattern (Cengiz 2019) proved cleaner than a pooled regression and is directly citable; use for future multi-event natural experiments
- **`pysyncon==1.5.2` pinned for ADH synthetic control** — version pin prevents API drift; the `Synth` class interface is stable at this version
- **Abstract-ready LaTeX macros** — `discount_stats.py` writing `\newcommand{\KoreaDiscountVsTopix}` etc. means key numbers are single-sourced; use this pattern for all summary statistics in future papers
- **`run_all.py` orchestration** — explicit dependency-ordered script runner proved more reliable than a Makefile for a Python-only pipeline; reuse this pattern

### Key Lessons

1. **Keep requirement status in one place.** Having both REQUIREMENTS.md and PROJECT.md track validation status led to drift. In future milestones, PROJECT.md is the single source of truth; REQUIREMENTS.md is the definition document only.
2. **Compile LaTeX early and often.** Don't wait until the final integration plan to attempt `latexmk`. A compiling stub at the start of prose writing catches structural errors before they pile up.
3. **Pre-check donor pool quality before committing to synthetic control.** Compute preliminary RMSPE on a small pre-treatment window before running full estimation to flag fit problems early.
4. **Phase verification plans should include explicit diff checks.** "Full test suite green" is necessary but not sufficient — Phase 3 verification missed two output-content defects (blank HC3 claim, missing wild-bootstrap p-values) that required a gap-closure plan.

### Cost Observations

- Model: Claude Sonnet 4.6 (balanced profile throughout)
- Sessions: ~7 (one per phase approximately)
- Notable: Worktree isolation in Phase 5 enabled parallel plan execution without context bleed; recommend for any phase with 4+ independent plans

---

## Cross-Milestone Trends

### Process Evolution

| Milestone | Phases | Plans | Key Change |
|-----------|--------|-------|------------|
| v1.0 | 5 | 24 | Initial milestone — strict pipeline dependency order established |

### Cumulative Quality

| Milestone | Tests | Notes |
|-----------|-------|-------|
| v1.0 | 38/38 | Full suite passing at close; incremental coverage per phase |

### Top Lessons (Verified Across Milestones)

1. Single-source summary statistics as LaTeX macros — prevents key-number drift between analysis and prose
2. Human visual UAT gates at figure-producing phases catch presentation defects before paper integration
