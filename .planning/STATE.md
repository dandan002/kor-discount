# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-04-14)

**Core value:** A rigorous, reproducible empirical argument that the Korea Discount is structural and addressable — with credible causal evidence from Japan that reform works.
**Current focus:** Phase 1 — Repo Setup and Data Pipeline

## Current Position

Phase: 1 of 5 (Repo Setup and Data Pipeline)
Plan: 0 of TBD in current phase
Status: Ready to plan
Last activity: 2026-04-14 — Roadmap created

Progress: [░░░░░░░░░░] 0%

## Performance Metrics

**Velocity:**
- Total plans completed: 0
- Average duration: —
- Total execution time: 0 hours

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| - | - | - | - |

**Recent Trend:**
- Last 5 plans: —
- Trend: —

*Updated after each plan completion*

## Accumulated Context

### Decisions

Decisions are logged in PROJECT.md Key Decisions table.
Recent decisions affecting current work:

- [Init]: Python over R — user preference
- [Init]: Staggered event study + panel OLS as primary methods; synthetic control as robustness
- [Init]: All three Japan reform dates as treatment events (2014, 2015, 2023)
- [Init]: Use `linearmodels.PanelOLS` not `statsmodels.OLS` for panel FE regressions
- [Init]: Event dates must be locked in config.py before any data is loaded (look-ahead bias firewall)

### Pending Todos

None yet.

### Blockers/Concerns

- [Phase 1]: KOSPI point-in-time P/B availability from free public sources is LOW confidence — confirm KRX portal export capabilities before committing to data strategy. Bloomberg/Refinitiv may be required.
- [Phase 3]: Stacked event study (Cengiz et al. 2019) requires manual Python construction — no mature library exists. Plan a focused pre-implementation research step.
- [Phase 3]: Verify `wildboottest` package exists and is compatible with `linearmodels` 6.x before committing to this inference approach.
- [Phase 4]: Resolve `pysyncon` vs `mlsynth` before Phase 4 implementation.

## Session Continuity

Last session: 2026-04-14
Stopped at: Roadmap created, STATE.md initialized — ready to plan Phase 1
Resume file: None
