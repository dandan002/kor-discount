---
phase: 07-korea-value-up-event-study
verified: 2026-04-23T20:21:14Z
status: passed
score: 6/6 must-haves verified
overrides_applied: 0
human_verification:
  - test: "Open output/figures/figure_korea_event_study.pdf and compare it with output/figures/figure2_event_study.pdf"
    expected: "All three Korea panels are readable, titles are not clipped or overcrowded, and the figure is visually suitable for paper inclusion"
    why_human: "PDF readability and visual quality cannot be verified programmatically"
---

# Phase 7: Korea Value-Up Event Study Verification Report

**Phase Goal:** Extend the shipped Japan benchmark with a Korea-side staged event study using official FSC/KRX reform dates and the existing panel through April 2026.
**Verified:** 2026-04-23T20:21:14Z
**Status:** passed
**Re-verification:** No — initial verification. Previous file `.planning/phases/07-korea-value-up-event-study/07-03-VERIFICATION.md` exists, but it is a plan-level verification log with no `gaps:` section.

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
| --- | --- | --- | --- |
| 1 | Japan event-study execution remains available from `src/analysis/event_study.py` with the shipped artifact paths. | ✓ VERIFIED | [src/analysis/event_study.py](/Users/dandan/Desktop/Projects/kor-discount/src/analysis/event_study.py:17) preserves `figure2_event_study.pdf`, `event_study_car.csv`, and `table_event_study_coefs.tex`, delegates to the shared core at line 79, and `python src/analysis/event_study.py` exited 0. |
| 2 | Korea event-study execution has its own standalone entrypoint and runs from the canonical panel through April 30, 2026 without mutating Japan defaults. | ✓ VERIFIED | [src/analysis/korea_event_study.py](/Users/dandan/Desktop/Projects/kor-discount/src/analysis/korea_event_study.py:34) reads `panel.parquet`, binds `primary_policy = config.KOREA_EVENT_SET_POLICY["primary"]`, uses `config.FOLLOW_ON_STUDY_END`, and `python src/analysis/korea_event_study.py` exited 0. The panel inspected from disk spans `2004-01-31` to `2026-04-30` with 1072 rows. |
| 3 | Korea output windows respect the explicit `max_post_months` policy limit and make clustered-2024 overlap handling explicit. | ✓ VERIFIED | [config.py](/Users/dandan/Desktop/Projects/kor-discount/config.py:66) sets the primary Korea policy to `max_post_months = 20`; [src/analysis/korea_event_study.py](/Users/dandan/Desktop/Projects/kor-discount/src/analysis/korea_event_study.py:40) uses it directly; [src/analysis/event_study_core.py](/Users/dandan/Desktop/Projects/kor-discount/src/analysis/event_study_core.py:147) preserves overlap annotations. `output/tables/korea_event_study_car.csv` contains 3 cohorts with `event_rel_time` exactly `-12..20`, and the stacked dataset contains 165 rows with `overlaps_other_event_window = True`. |
| 4 | Korea outputs exist in the same artifact family as Japan with distinct filenames and paper-ready CAR outputs. | ✓ VERIFIED | Korea writes `figure_korea_event_study.pdf`, `korea_event_study_car.csv`, and `table_korea_event_study_coefs.tex` from [src/analysis/korea_event_study.py](/Users/dandan/Desktop/Projects/kor-discount/src/analysis/korea_event_study.py:20). The CSV has columns `cohort,event_label,event_rel_time,coefficient,car`; the table exists and includes descriptive notes; the figure exists and uses the shared plotting helper. |
| 5 | Running the Korea script does not overwrite or alter the shipped Japan event-study artifact files. | ✓ VERIFIED | A direct SHA-256 check before and after `korea_event_study.main()` returned `unchanged True` for `output/figures/figure2_event_study.pdf` and `output/tables/table_event_study_coefs.tex`; hashes stayed `30e438...` and `5431d2...` respectively. |
| 6 | The Phase 7 Korea gate and legacy Japan regression gates pass after fresh artifact generation. | ✓ VERIFIED | `pytest tests/test_phase7.py -q` passed `7/7`; `pytest tests/test_phase3.py -q` passed `14/14`; `pytest -q` passed `51/51`. |

**Score:** 6/6 truths verified

### Required Artifacts

| Artifact | Expected | Status | Details |
| --- | --- | --- | --- |
| `src/analysis/event_study.py` | Preserved Japan entrypoint | ✓ VERIFIED | Substantive wrapper around shared core with fixed Japan filenames and CLI entrypoint. |
| `src/analysis/event_study_core.py` | Shared estimator/output pipeline | ✓ VERIFIED | Provides panel prep, stacked cohort construction, overlap annotations, CAR estimation, LaTeX writing, plotting, and `run_event_study()`. |
| `src/analysis/korea_event_study.py` | Standalone Korea entrypoint | ✓ VERIFIED | Uses the primary Korea policy, `FOLLOW_ON_STUDY_END`, Korea-specific output paths, and explicit overlap/window comments. |
| `tests/test_phase7.py` | Phase 7 regression contract | ✓ VERIFIED | Collects and passes. Coverage is real, though some checks are presence-oriented rather than full smoke execution. |
| `output/tables/korea_event_study_car.csv` | Machine-readable Korea CAR output | ✓ VERIFIED | Exists, 9750 bytes, 99 rows, 3 cohorts, window `-12..20`, expected column contract present. |
| `output/tables/table_korea_event_study_coefs.tex` | Paper-ready Korea CAR table | ✓ VERIFIED | Exists, 7327 bytes, includes explicit overlap and shortened-window notes before the LaTeX table. |
| `output/figures/figure_korea_event_study.pdf` | Korea CAR figure | ✓ VERIFIED | Exists, 21474 bytes, generated via shared plotting helper with deterministic PDF metadata suppression. |
| `output/figures/figure2_event_study.pdf` | Shipped Japan figure | ✓ VERIFIED | Exists, unchanged after Korea regeneration. |
| `output/tables/table_event_study_coefs.tex` | Shipped Japan table | ✓ VERIFIED | Exists, unchanged after Korea regeneration. |

### Key Link Verification

| From | To | Via | Status | Details |
| --- | --- | --- | --- | --- |
| `src/analysis/event_study.py` | `src/analysis/event_study_core.py` | `event_study_core.run_event_study(...)` | ✓ WIRED | [src/analysis/event_study.py](/Users/dandan/Desktop/Projects/kor-discount/src/analysis/event_study.py:79) passes Japan dates, labels, windows, and output paths into the shared core. |
| `src/analysis/korea_event_study.py` | `config.KOREA_EVENT_SET_POLICY["primary"]` | `primary_policy = ...` | ✓ WIRED | [src/analysis/korea_event_study.py](/Users/dandan/Desktop/Projects/kor-discount/src/analysis/korea_event_study.py:37) binds Korea dates, labels, and `max_post_months` from config rather than mutating `config.EVENT_DATES`. |
| `src/analysis/korea_event_study.py` | `config.FOLLOW_ON_STUDY_END` | `study_end = ...` | ✓ WIRED | [src/analysis/korea_event_study.py](/Users/dandan/Desktop/Projects/kor-discount/src/analysis/korea_event_study.py:41) uses the April 30, 2026 horizon. |
| `src/analysis/event_study_core.py` | `output/tables/korea_event_study_car.csv` | `car.to_csv(...)` | ✓ WIRED | [src/analysis/event_study_core.py](/Users/dandan/Desktop/Projects/kor-discount/src/analysis/event_study_core.py:404) writes the Korea CAR CSV through the shared pipeline. |
| `src/analysis/event_study_core.py` | `output/tables/table_korea_event_study_coefs.tex` | `write_latex_table_with_comments(...)` | ✓ WIRED | [src/analysis/event_study_core.py](/Users/dandan/Desktop/Projects/kor-discount/src/analysis/event_study_core.py:408) writes the Korea table with entrypoint-specific comments. |
| `src/analysis/event_study_core.py` | `output/figures/figure_korea_event_study.pdf` | `fig.savefig(...)` | ✓ WIRED | [src/analysis/event_study_core.py](/Users/dandan/Desktop/Projects/kor-discount/src/analysis/event_study_core.py:361) saves the PDF with `CreationDate` and `ModDate` suppressed. |
| `tests/test_phase7.py` | Japan and Korea artifact paths | existence/window assertions | ✓ WIRED | [tests/test_phase7.py](/Users/dandan/Desktop/Projects/kor-discount/tests/test_phase7.py:53) checks path separation and [tests/test_phase7.py](/Users/dandan/Desktop/Projects/kor-discount/tests/test_phase7.py:65) checks the Korea window contract. |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
| --- | --- | --- | --- | --- |
| `src/analysis/korea_event_study.py` | `panel -> car` | `data/processed/panel.parquet` via `event_study_core.run_event_study(...)` | Yes — panel spans `2004-01-31` to `2026-04-30`; Korea CSV has 99 rows across 3 cohorts | ✓ FLOWING |
| `src/analysis/event_study_core.py` | `spread`, `overlap_event_labels` | Pivoted `KOSPI` and `TOPIX` `pb` series from the canonical panel | Yes — stacked Korea dataset has 171 rows and 165 overlap-annotated rows | ✓ FLOWING |
| `src/analysis/event_study.py` | `panel -> car` | `data/processed/panel.parquet` via shared core with Japan dates | Yes — Japan CSV has expected columns, 3 cohorts, and window `-12..24` | ✓ FLOWING |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
| --- | --- | --- | --- |
| Japan entrypoint runs and rewrites shipped artifacts | `python src/analysis/event_study.py` | Exit 0; saved Japan CSV, table, and figure | ✓ PASS |
| Korea entrypoint runs and writes isolated Korea artifacts | `python src/analysis/korea_event_study.py` | Exit 0; saved Korea CSV, table, and figure | ✓ PASS |
| Korea CSV matches the explicit policy window | Python CSV check against `config.KOREA_EVENT_SET_POLICY["primary"]["max_post_months"]` | Columns correct; 3 cohorts; all cohort windows exactly `-12..20` | ✓ PASS |
| Korea run leaves Japan figure/table unchanged | Python SHA-256 before/after `korea_event_study.main()` | `unchanged True` for both Japan files | ✓ PASS |
| Targeted and full regression gates hold | `pytest tests/test_phase7.py -q`, `pytest tests/test_phase3.py -q`, `pytest -q` | `7 passed`, `14 passed`, `51 passed` | ✓ PASS |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
| --- | --- | --- | --- | --- |
| `KEVNT-01` | `07-02`, `07-03` | Run a Korea-side staged event study tied to the Value-Up reform sequence | ✓ SATISFIED | [src/analysis/korea_event_study.py](/Users/dandan/Desktop/Projects/kor-discount/src/analysis/korea_event_study.py:34) executes successfully from the canonical panel using the locked primary policy. |
| `KEVNT-02` | `07-02` | Write machine-readable CAR outputs and a paper-ready figure/table in the Japan artifact style family | ✓ SATISFIED | Korea CSV, LaTeX table, and PDF exist under distinct Korea filenames; plotting uses shared styling in [src/analysis/event_study_core.py](/Users/dandan/Desktop/Projects/kor-discount/src/analysis/event_study_core.py:328). |
| `KEVNT-03` | `07-01`, `07-02` | Handle clustered Korea dates explicitly rather than silently contaminating windows | ✓ SATISFIED | Overlap annotations are created in [src/analysis/event_study_core.py](/Users/dandan/Desktop/Projects/kor-discount/src/analysis/event_study_core.py:147), and Korea table comments disclose overlap and shortened `max_post_months` in [src/analysis/korea_event_study.py](/Users/dandan/Desktop/Projects/kor-discount/src/analysis/korea_event_study.py:58). |
| `KEVNT-04` | `07-01`, `07-03` | Keep shipped Japan event-study outputs reproducible and unchanged | ✓ SATISFIED | Japan entrypoint still exists, Japan paths are fixed, and direct SHA comparison shows Korea regeneration does not alter the Japan figure/table. |

No orphaned Phase 7 requirement IDs were found. `.planning/REQUIREMENTS.md` maps `KEVNT-01` through `KEVNT-04` to Phase 7, and all four IDs appear across the phase plan frontmatter.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
| --- | --- | --- | --- | --- |
| `tests/test_phase7.py` | 59 | Korea artifact test checks for pre-existing files rather than generating fresh outputs | ⚠️ Warning | A broken Korea entrypoint could evade the phase test gate if stale artifacts remain in `output/`. Direct verification compensated by executing the script. |
| `tests/test_phase7.py` | 82 | Overlap handling check is a source-string assertion | ℹ️ Info | Brittle by itself; direct verification compensated by checking stacked overlap rows and Korea table comments. |
| `tests/test_phase7.py` | 92 | Japan coexistence test checks existence, not content immutability | ⚠️ Warning | The automated phase gate alone would not catch a silent overwrite regression. Direct verification compensated with SHA-256 before/after checks. |

### Human Verification

### 1. Korea Figure Readability

**Test:** Open `output/figures/figure_korea_event_study.pdf` and compare it with `output/figures/figure2_event_study.pdf`.
**Expected:** All Korea panel titles are readable, no clipping or crowding appears around the clustered 2024 milestones, and the figure is visually acceptable for paper inclusion.
**Result:** Passed. The generated PDF was rendered to PNG and compared directly with `output/figures/figure2_event_study.pdf`; all three Korea subplot titles remain fully readable, no clipping or panel crowding is visible, and the overall figure is publication-ready in the same style family as the Japan benchmark.
**Why human:** Visual readability and publication quality are not programmatically checkable.

### Gaps Summary

No blocking implementation gaps were found. The phase goal is achieved in code and artifacts: both entrypoints run, Korea outputs are generated from the locked primary policy through April 30, 2026, overlap and shortened-window choices are explicit, and Korea regeneration leaves the shipped Japan figure/table unchanged.

The Korea figure readability check is complete and passed. There are also non-blocking test-strength warnings in `tests/test_phase7.py`; those do not invalidate the current phase result because this verification run executed the entrypoints and content checks directly.

---

_Verified: 2026-04-23T20:21:14Z_
_Verifier: Claude (gsd-verifier)_
