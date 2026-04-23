# Phase 6 Research — Korea Reform Date Locking and Sample Horizon

**Phase:** 6  
**Date:** 2026-04-23  
**Status:** Ready for planning

## Research Question

What needs to be true for Phase 6 to lock Korea reform dates and extend the study horizon through `2026-04-30` without regressing the shipped Japan-based v1.0 paper?

## Executive Summary

Phase 6 should be treated as an enabling phase, not an analysis-rewrite phase. The codebase already has the necessary raw and processed data through `2026-04-30`, and the official Korea Value-Up timeline has already been sourced into `.planning/research/KOREA_VALUE_UP_DATES.md`. The real planning risk is architectural: Japan reform dates are globally hard-wired in `config.py`, and many downstream scripts independently hard-cap their sample at `2024-12-31`. If Phase 6 changes those defaults indiscriminately, it will silently rewrite the shipped v1.0 paper outputs instead of preparing a clean Korea follow-on path.

The safest Phase 6 outcome is therefore:

1. add a structurally separate Korea reform-date config surface,
2. centralize study-horizon constants so code can opt into `2026-04-30` deliberately,
3. document the primary-vs-robustness Korea date sets in a phase memo,
4. add targeted tests/verification that prove the new controls exist and that existing Japan outputs remain reproducible under their current defaults.

Phase 6 should not try to update every descriptive, policy, and paper artifact to the 2026 horizon. That broader rewrite belongs to later phases if explicitly planned. For this phase, the main deliverable is safe infrastructure for Phase 7.

## What The Codebase Already Gives You

### 1. Data horizon is not the blocker

- `data/processed/panel.parquet` spans `2004-01-31` through `2026-04-30`
- `src/data/verify_panel.py` already accepts any panel whose max date is `>= 2024-12-31`, so current data verification is permissive enough for extension
- Raw manifest filenames and raw Bloomberg exports already run through `2004_2026`

Implication: Phase 6 does **not** need a new data-ingestion project. It needs code-level horizon controls.

### 2. Official Korea reform dates are already sourced

`.planning/research/KOREA_VALUE_UP_DATES.md` provides two viable date sets:

- Narrow rollout set:
  - `2024-02-26`
  - `2024-05-02`
  - `2024-08-12`
- Spaced follow-through set:
  - `2024-02-26`
  - `2025-07-09`
  - `2026-02-24`

Implication: Phase 6 should lock the config and rationale, not re-do internet research.

## Current Hard-Coded Risks

### 1. Japan events are globally modeled as the only event set

`config.py` currently exposes:

- `STEWARDSHIP_CODE_DATE`
- `CGC_DATE`
- `TSE_PB_REFORM_DATE`
- `EVENT_DATES`
- `EVENT_LABELS`

These are Japan-specific names, but the generic containers `EVENT_DATES` and `EVENT_LABELS` are consumed directly by:

- `src/analysis/event_study.py`
- `src/robustness/robustness_placebo.py`
- `src/robustness/robustness_pe.py`
- `src/descriptive/figure1.py`

Implication: if Korea dates are dropped into `EVENT_DATES`, existing Japan scripts will silently change behavior. Phase 6 must create **separate** Korea date/label structures rather than mutating the current Japan ones.

### 2. Study-end logic is duplicated across modules

The following currently hard-cap at `2024-12-31`:

- `src/analysis/panel_ols.py`
- `src/analysis/geo_risk.py`
- `src/robustness/robustness_alt_control.py`
- `src/robustness/robustness_pe.py`
- `src/descriptive/figure1.py`
- `src/descriptive/table1.py`
- `src/descriptive/discount_stats.py`
- `src/policy/counterfactual_projection.py`
- paper text in `paper/main.tex`

Implication: Phase 6 should centralize or parameterize horizon selection where needed for the Korea follow-on path, but it should **not** automatically widen every v1.0 output to 2026.

### 3. Event-study logic is reusable, but only after config isolation

`src/analysis/event_study.py` is already close to reusable for Korea because it:

- derives cohorts from a date list,
- computes overlap annotations,
- builds trend-based abnormal spreads, and
- writes stable machine-readable outputs.

But it assumes:

- exactly one global event set in `config.EVENT_DATES`
- labels from `config.EVENT_LABELS`
- a fixed TOPIX/KOSPI spread framing

Implication: Phase 6 does not need to rewrite the event-study estimator. It needs to prepare clean config and horizon plumbing so Phase 7 can either:

- generalize the module to accept an explicit event set, or
- create a Korea-specific wrapper that reuses the same internals.

## Recommended Planning Boundaries

### Plan 06-01 should be documentation-first and locked

Deliver a phase memo that:

- records the official source for each Korea reform date,
- explains why the narrow rollout set is the default narrative candidate,
- explains why the spaced follow-through set is the robustness candidate,
- states the maximum defensible post window for each date given the `2026-04-30` endpoint,
- identifies excluded-but-relevant dates such as `2024-04-02` and `2024-12-24`.

This should produce a durable source-of-truth file under the phase directory, not rely only on milestone-level notes.

### Plan 06-02 should isolate config and horizon controls

The safe implementation path is:

- preserve all existing Japan constants for backwards compatibility,
- add Korea-specific constants and grouped collections,
- add explicit study-end constants instead of scattered literals,
- update only the modules necessary to prove the new controls exist.

Concrete design preference:

- keep Japan defaults intact for shipped scripts,
- add opt-in controls for Korea/extended horizon work,
- avoid changing paper-generation scripts in Phase 6 unless required for compatibility tests.

### Plan 06-03 should verify backward compatibility explicitly

Verification should focus on proving:

- the panel reaches `2026-04-30`,
- config contains separate Japan and Korea event collections,
- scripts that rely on Japan defaults still point at the Japan event set,
- the new horizon controls are importable and test-covered,
- no existing event-study artifact path is overwritten by the config refactor alone.

## Suggested File Targets

### Likely to modify in this phase

- `config.py`
- one or more shared analysis helpers if created
- targeted tests, likely a new phase-6 test file or additions to import/config tests
- phase docs:
  - `06-RESEARCH.md`
  - `06-VALIDATION.md`
  - phase memo for locked date strategy if separate from research

### Likely not to modify yet

- `paper/main.tex`
- `run_all.py`
- `src/analysis/event_study.py` logic beyond minimal compatibility preparation
- descriptive scripts whose 2024 framing belongs to the shipped paper

Those belong to later phases unless a minimal compatibility change is unavoidable.

## Testing and Verification Gaps

Current test coverage is heavy on Phase 3 outputs but light on the specific risks introduced by Phase 6.

Add tests for:

- existence and type of new Korea date constants
- separation between Japan and Korea event collections
- explicit extended-horizon constants or helpers
- smoke assertions that old Japan config names still resolve
- a panel-date assertion for `2026-04-30` if not already present in a dedicated phase-6 test

Avoid tests that regenerate the entire paper in this phase. The point is to verify the plumbing layer, not to absorb all later integration cost early.

## Planner Guidance

The planner should optimize for a low-blast-radius phase:

- Plan 1: phase-local locked memo for dates and windows
- Plan 2: config/horizon plumbing plus focused tests
- Plan 3: verification-only pass proving safety and compatibility

The planner should **not** bundle future Korea event-study implementation into this phase. That would violate the roadmap split and make verification too broad.

## Validation Architecture

Phase 6 is a configuration-and-contract phase. Validation should rely on:

- fast pytest coverage for config and horizon helpers,
- targeted CLI verification of panel max date,
- grep/read verification of new config keys and separated event collections,
- explicit non-regression checks that Japan default paths remain intact.

This phase does not need expensive end-to-end regeneration on every task commit. Quick feedback is sufficient if the tests directly cover the config surface.

## Research Conclusion

Phase 6 is straightforward if it stays narrow:

- lock and document Korea dates,
- isolate event-set configuration,
- centralize study-end controls,
- verify compatibility.

It becomes risky only if it tries to update all 2024-framed outputs at once. The planner should enforce that boundary.
