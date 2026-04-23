# Phase 7 Research — Korea Value-Up Event Study

**Phase:** 7  
**Date:** 2026-04-23  
**Status:** Ready for planning

## Research Question

What needs to be true for Phase 7 to add a Korea-side staged event study in the same style as the shipped Japan analysis without overwriting or regressing the Japan artifact contract?

## Executive Summary

Phase 7 should be treated as a reuse-and-isolate phase, not a rewrite of the shipped Japan event study. Phase 6 already created the essential prerequisites: Korea event-date collections in `config.py`, a documented primary-versus-robustness date policy, and a follow-on study horizon through `2026-04-30`. The remaining risk is structural. The current Japan script, `src/analysis/event_study.py`, is still a Japan-specific entrypoint tied to `config.EVENT_DATES`, `config.EVENT_LABELS`, and fixed Japan artifact paths. If Phase 7 mutates those globals or reuses the same output filenames, the shipped Japan outputs will silently change.

The safest Phase 7 architecture is:

1. keep `src/analysis/event_study.py` as the Japan entrypoint and preserve its current output filenames,
2. factor reusable cohort-building, CAR estimation, and table/figure writing helpers into a shared event-study core,
3. add a Korea-specific standalone entrypoint that passes Korea dates, Korea labels, the follow-on study end, and Korea-specific output paths explicitly,
4. use the narrow 2024 Korea rollout set as the primary Phase 7 specification and defer the spaced 2025-2026 sequence to Phase 8 robustness,
5. add dedicated Phase 7 tests that prove the Korea outputs exist, the Korea design handles overlap explicitly, and the Japan outputs are still reproducible and unchanged.

This phase should not yet touch `run_all.py`, README workflow, or paper numbering. Those belong to Phase 9.

## What Phase 6 Already Solved

### 1. Korea dates and horizon are locked

`config.py` now exposes:

- `KOREA_VALUE_UP_NARROW_EVENT_DATES`
- `KOREA_VALUE_UP_NARROW_EVENT_LABELS`
- `KOREA_VALUE_UP_SPACED_EVENT_DATES`
- `KOREA_VALUE_UP_SPACED_EVENT_LABELS`
- `KOREA_EVENT_SET_POLICY`
- `FOLLOW_ON_STUDY_END = 2026-04-30`

`06-DATE-LOCK.md`, `06-RESEARCH.md`, and `06-VERIFICATION.md` establish that:

- the narrow 2024 rollout set is the primary narrative candidate,
- the spaced 2025-2026 sequence is a robustness candidate,
- the common post window for the primary 2024 set is capped below Japan's +24 months because the panel ends at `2026-04-30`.

Implication: Phase 7 does not need to re-decide the Korea date policy. It needs to operationalize the primary set cleanly.

### 2. The current event-study pipeline is already close to reusable

`src/analysis/event_study.py` already contains the key reusable logic:

- `prepare_event_study_panel()`
- `build_stacked_dataset()`
- `estimate_event_study()`
- `_write_latex_table()`
- `plot_event_study()`

It already:

- builds stacked cohorts,
- preserves overlapping windows with explicit annotations,
- computes descriptive CAR paths,
- writes machine-readable CSV and LaTeX outputs,
- renders a publication-style multi-panel PDF.

Implication: Phase 7 should reuse these mechanics, not re-implement the estimator from scratch.

## Current Structural Risks

### 1. Japan remains the default global event-study surface

`src/analysis/event_study.py` still reads:

- `config.EVENT_DATES`
- `config.EVENT_LABELS`
- `config.PAPER_STUDY_END`

and still writes:

- `output/figures/figure2_event_study.pdf`
- `output/tables/event_study_car.csv`
- `output/tables/table_event_study_coefs.tex`

Implication: changing `config.EVENT_DATES` globally, or widening the current script in place without explicit parameterization, risks violating `KEVNT-04` by rewriting shipped Japan artifacts.

### 2. Korea overlap is more severe than Japan overlap

The Japan design preserves overlap between 2014 and 2015 and annotates it. Korea's primary 2024 dates are closer:

- `2024-02-26`
- `2024-05-02`
- `2024-08-12`

With a Japan-style plotted window, these cohorts overlap heavily. Phase 7 therefore cannot rely on silent reuse. It must make the overlap strategy visible in code and outputs.

Implication: explicit overlap annotation remains mandatory, and the Korea window length must be driven by the Phase 6 policy rather than blindly reusing Japan's full +24 window.

### 3. Paper-facing numbering should remain deferred

The shipped Japan paper contract already treats:

- `figure2_event_study.pdf` as Figure 2,
- `table_event_study_coefs.tex` as the paper-ready event-study table.

Implication: Phase 7 should create comparison-ready Korea artifacts with unique names, not renumber figures or rewrite paper includes. Paper integration belongs to Phase 9.

## Recommended Architecture

### Preferred module split

Use a two-entrypoint architecture:

- Keep `src/analysis/event_study.py` as the Japan script.
- Add a new Korea entrypoint, preferably `src/analysis/korea_event_study.py`.
- Factor reusable logic into a shared helper module such as `src/analysis/event_study_core.py` or equivalent.

The shared layer should accept explicit inputs for:

- `event_dates`
- `event_labels`
- `study_end`
- stack window bounds
- plotted event window bounds
- figure title
- output paths

The entrypoint scripts should own only:

- config selection,
- artifact naming,
- title/label strings,
- script-level `main()` orchestration.

Why this is safer than mutating `event_study.py` in place:

- Japan remains reproducible through the original CLI path.
- Korea can use different window bounds without branching on globals.
- Phase 9 can later integrate both entrypoints into `run_all.py` deliberately.

### Recommended Korea specification for Phase 7

Use the primary Korea set only:

- `config.KOREA_EVENT_SET_POLICY["primary"]`

Do not use the spaced 2025-2026 set in the Phase 7 mainline implementation. It only has two common post months as of `2026-04-30`, so it is better treated as a Phase 8 robustness specification.

For the Korea mainline window:

- retain the Japan-style stacked-cohort mechanics and artifact style,
- keep the pre-period long enough to mirror the Japan design where feasible,
- cap the Korea post window at the policy-supported common horizon rather than forcing +24.

The planner should encode the exact Korea window values explicitly in the plan text. The safest default is to derive them from `KOREA_EVENT_SET_POLICY["primary"]["max_post_months"]` rather than hard-coding them in multiple places.

### Recommended artifact names

To satisfy "same artifact format" without overwriting Japan outputs, use Korea-specific filenames under the same directories:

- `output/tables/korea_event_study_car.csv`
- `output/tables/table_korea_event_study_coefs.tex`
- `output/figures/figure_korea_event_study.pdf`

These names:

- keep the artifact style parallel to Japan,
- avoid collisions with shipped paper assets,
- leave Phase 9 free to decide final figure/table numbering.

## Recommended Plan Boundaries

### Plan 07-01 should be foundation and test-first

This plan should:

- introduce the shared event-study core abstraction,
- preserve the Japan entrypoint behavior and filenames,
- add the Korea entrypoint scaffold,
- add `tests/test_phase7.py` with output-contract and overlap-policy checks,
- encode the Korea event-set selection through explicit config access rather than global reassignment.

This plan should not yet regenerate final Korea artifacts for paper use beyond scaffold-level smoke expectations.

### Plan 07-02 should be Korea estimation and artifact generation

This plan should:

- wire the Korea entrypoint to the primary Korea event set,
- run the Korea stacked event study against the follow-on panel horizon,
- write the Korea CSV, LaTeX, and PDF outputs,
- ensure the Korea figure/table style mirrors the Japan event-study presentation,
- surface overlap annotations or related explanatory fields in machine-readable outputs if not already exposed.

This plan should explicitly satisfy:

- `KEVNT-01`
- `KEVNT-02`
- `KEVNT-03`

### Plan 07-03 should be verification and non-regression only

This plan should:

- regenerate Japan and Korea event-study outputs intentionally,
- verify the Korea artifacts exist and are non-empty,
- verify the Japan artifact paths still exist and are unchanged unless a versioned comparison output is intentionally added,
- run the targeted Phase 7 pytest gate and the full pytest suite,
- document remaining manual figure-review needs.

This plan is where `KEVNT-04` should be proven.

## Suggested File Targets

### Likely to modify

- `src/analysis/event_study.py`
- new shared helper module for event-study core logic
- new `src/analysis/korea_event_study.py`
- `tests/test_phase7.py`

### Likely to generate

- `output/tables/korea_event_study_car.csv`
- `output/tables/table_korea_event_study_coefs.tex`
- `output/figures/figure_korea_event_study.pdf`

### Likely not to modify yet

- `run_all.py`
- `README.md`
- `paper/main.tex`

Those belong to Phase 9 integration work.

## Testing and Verification Gaps

The current repo has strong adjacent coverage in:

- `tests/test_phase3.py` for the Japan event-study contract,
- `tests/test_phase6.py` for Korea date config and follow-on horizon plumbing.

What is missing for Phase 7 is a Korea-specific verification surface. Add `tests/test_phase7.py` for:

- Korea entrypoint existence and importability,
- Korea output filenames and non-empty artifacts,
- Korea CAR CSV column contract,
- Korea cohort count and complete plotted-window coverage,
- overlap annotation behavior for clustered 2024 dates,
- non-regression assertion that Japan artifact paths still exist after Korea generation.

Avoid using only `tests/test_phase3.py` as the Korea gate. That would blur Japan and Korea responsibilities and make regressions harder to localize.

## Planner Guidance

The planner should optimize for explicit isolation:

- separate Japan and Korea entrypoints,
- shared reusable core,
- Korea-specific outputs,
- dedicated Korea tests,
- verification that Japan artifacts are preserved.

The planner should avoid:

- reassigning `config.EVENT_DATES` globally for Korea,
- overwriting `figure2_event_study.pdf` or `table_event_study_coefs.tex`,
- expanding scope into paper or replication workflow integration,
- treating the spaced 2025-2026 set as the primary Phase 7 implementation.

## Validation Architecture

Phase 7 is a mixed refactor-plus-new-artifact phase. Validation should rely on:

- a new fast Phase 7 pytest file for Korea-specific contracts,
- targeted script execution for both Japan and Korea entrypoints,
- output-file existence checks for both Korea and Japan artifact paths,
- a final full-suite pytest pass for non-regression.

Recommended validation contract:

- Quick run command: `pytest tests/test_phase7.py -q`
- Full suite command: `pytest -q`
- Per-task feedback should stay under ~20 seconds where possible

Key checks the plans should include:

- `pytest tests/test_phase7.py --collect-only -q`
- `python src/analysis/korea_event_study.py`
- `test -s output/figures/figure_korea_event_study.pdf`
- `test -s output/tables/korea_event_study_car.csv`
- `test -s output/tables/table_korea_event_study_coefs.tex`
- `test -s output/figures/figure2_event_study.pdf`
- `test -s output/tables/table_event_study_coefs.tex`
- `pytest tests/test_phase7.py -q`
- `pytest -q`

Manual verification should remain for:

- visual review of the Korea event-study figure,
- confirmation that overlap titles/labels remain readable with the clustered Korea dates.

## Research Conclusion

Phase 7 is well-bounded if it stays disciplined:

- reuse the shipped Japan event-study mechanics,
- isolate Korea behind its own entrypoint and filenames,
- use the narrow 2024 date set as the primary implementation,
- reserve the spaced 2025-2026 sequence for Phase 8 robustness,
- prove Japan non-regression explicitly.

The implementation becomes risky only if Korea is introduced by mutating the current Japan defaults. The planner should enforce separation at the module, config, and artifact-path levels.
