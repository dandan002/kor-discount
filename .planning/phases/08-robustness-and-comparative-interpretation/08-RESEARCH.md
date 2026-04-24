# Phase 8: Robustness and Comparative Interpretation - Research

**Researched:** 2026-04-24  
**Domain:** Korea follow-on event-study robustness, comparator sensitivity, and Japan-versus-Korea interpretation boundaries  
**Confidence:** HIGH

## User Constraints

- No phase-local `08-CONTEXT.md` exists, so the operative constraints come from the direct user prompt plus current project state. [VERIFIED: `node "/Users/dandan/.codex/get-shit-done/bin/gsd-tools.cjs" init phase-op 8`, `.planning/STATE.md`]
- Phase 8 must address `KROB-01`, `KROB-02`, and `KROB-03`. [VERIFIED: `.planning/REQUIREMENTS.md`]
- Phase 7 already shipped a primary Korea event study driven by `config.KOREA_EVENT_SET_POLICY["primary"]` and `config.FOLLOW_ON_STUDY_END`. [VERIFIED: `.planning/STATE.md`, `config.py`, `src/analysis/korea_event_study.py`, `.planning/phases/07-korea-value-up-event-study/07-VERIFICATION.md`]
- The canonical panel currently ends on `2026-04-30`. [VERIFIED: `config.py`, local `panel.parquet` audit on 2026-04-24]
- This phase stops at robustness outputs and interpretation-ready artifacts or text inputs; it is not paper integration work. [VERIFIED: user prompt, `.planning/ROADMAP.md`]
- Security enforcement is enabled, so downstream plans should include `<threat_model>` blocks. [VERIFIED: user prompt]

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| KROB-01 | Evaluate at least two Korea reform-date specifications: a narrow 2024 Value-Up rollout set and a more spaced shareholder-value follow-through set | The repo already locks both date sets in `config.py`, Phase 6 documents why both exist, and official FSC pages confirm the relevant milestones. [VERIFIED: `config.py`, `.planning/phases/06-korea-reform-date-locking-and-sample-horizon/06-DATE-LOCK.md`][CITED: https://www.fsc.go.kr/eng/pr010101/81778][CITED: https://www.fsc.go.kr/eng/pr010101/82213][CITED: https://www.fsc.go.kr/eng/pr010101/82875][CITED: https://www.fsc.go.kr/eng/pr010101/84905][CITED: https://www.fsc.go.kr/eng/pr010101/86320%3FsrchCtgry%3D%26curPage%3D%26srchKey%3D%26srchText%3D%26srchBeginDt%3D%26srchEndDt%3D] |
| KROB-02 | Rerun the Korea event study under at least one alternative event-window sensitivity justified by the `2026-04-30` endpoint | The shared core already accepts alternate `stack_window_max` and `event_window_max` values, and direct feasibility checks show the narrow set runs cleanly at `+12` and `+8`, while the spaced set only supports `+2` if all three cohorts are retained. [VERIFIED: `src/analysis/event_study_core.py`, `src/analysis/korea_event_study.py`, local feasibility audit on 2026-04-24] |
| KROB-03 | Include a Japan-versus-Korea interpretation note that separates descriptive policy timing evidence from stronger causal claims | The current paper already treats Japan event windows as descriptive rather than clean causal estimates, and Korea has even shorter and more overlapped post-treatment evidence than Japan. [VERIFIED: `paper/main_v2.tex`, `.planning/PROJECT.md`, `.planning/phases/06-korea-reform-date-locking-and-sample-horizon/06-DATE-LOCK.md`, `.planning/phases/07-korea-value-up-event-study/07-VERIFICATION.md`][CITED: https://www.fsc.go.kr/eng/pr010101/81778][CITED: https://www.fsc.go.kr/eng/pr010101/82213][CITED: https://www.fsc.go.kr/eng/pr010101/82875][CITED: https://www.fsc.go.kr/eng/pr010101/84905][CITED: https://www.fsc.go.kr/eng/pr010101/86320%3FsrchCtgry%3D%26curPage%3D%26srchKey%3D%26srchText%3D%26srchBeginDt%3D%26srchEndDt%3D] |
</phase_requirements>

## Summary

Phase 8 should keep the shipped narrow 2024 Korea rollout set as the baseline, add one shorter narrow-window rerun as the required event-window sensitivity, and treat the spaced 2024/2025/2026 follow-through set as a separate robustness specification capped at `+2` post months. The reason is mechanical, not stylistic: with a panel ending on `2026-04-30`, the narrow dates have 26, 23, and 20 post months available, while the spaced dates have 26, 9, and only 2 post months available; direct local reruns confirm the spaced set works at `+2` and fails at `+3` because the February 24, 2026 cohort lacks a third post month. [VERIFIED: `config.py`, `.planning/phases/06-korea-reform-date-locking-and-sample-horizon/06-DATE-LOCK.md`, local month-count audit on 2026-04-24, local `event_study_core.build_stacked_dataset()` feasibility audit on 2026-04-24][CITED: https://www.fsc.go.kr/eng/pr010101/81778][CITED: https://www.fsc.go.kr/eng/pr010101/84905][CITED: https://www.fsc.go.kr/eng/pr010101/86320%3FsrchCtgry%3D%26curPage%3D%26srchKey%3D%26srchText%3D%26srchBeginDt%3D%26srchEndDt%3D]

Do not plan a full comparator refactor inside the Phase 8 event-study codepath. The shared event-study core currently constructs `spread = KOSPI - TOPIX`, validates only `KOSPI` and `TOPIX` in the pivoted panel, and labels the figure axis as `CAR: KOSPI - TOPIX P/B`; existing non-TOPIX sensitivity already lives elsewhere in the codebase through descriptive benchmark checks (`TOPIX`, `MSCI_EM`), alternative EM control-group panel OLS (`MSCI_EM_ASIA`, approximate `MSCI_EM_EX_CHINA`), and placebo market event studies (`MSCI_TAIWAN`, `MSCI_INDONESIA`). [VERIFIED: `src/analysis/event_study_core.py`, `src/descriptive/discount_stats.py`, `src/robustness/robustness_alt_control.py`, `src/robustness/robustness_placebo.py`, `paper/main_v2.tex`]

The Japan-versus-Korea comparison note should stop at descriptive timing interpretation. The existing paper already says the Japan event windows are descriptive abnormal movements rather than clean country-level treatment effects, flags overlap between the 2014 and 2015 Japan windows, and adds Abenomics and synthetic-control caveats; Korea is a weaker identification setting still because the 2024 milestones are clustered and the 2025/2026 follow-through events have short post horizons. [VERIFIED: `paper/main_v2.tex`, `.planning/PROJECT.md`, `.planning/phases/07-korea-value-up-event-study/07-VERIFICATION.md`][CITED: https://www.fsc.go.kr/eng/pr010101/81778][CITED: https://www.fsc.go.kr/eng/pr010101/82213][CITED: https://www.fsc.go.kr/eng/pr010101/82875][CITED: https://www.fsc.go.kr/eng/pr010101/84905][CITED: https://www.fsc.go.kr/eng/pr010101/86320%3FsrchCtgry%3D%26curPage%3D%26srchKey%3D%26srchText%3D%26srchBeginDt%3D%26srchEndDt%3D]

**Primary recommendation:** Keep `narrow_2024_rollout` as the baseline, add a `+12` narrow-window sensitivity, run `spaced_follow_through` only at `+2`, keep `TOPIX` fixed inside the event-study core, and generate a standalone interpretation note artifact that explicitly says Japan is a policy benchmark and Korea is descriptive follow-on evidence, not a new causal estimate. [VERIFIED: `config.py`, `src/analysis/korea_event_study.py`, `src/analysis/event_study_core.py`, `paper/main_v2.tex`, local feasibility audit on 2026-04-24]

## Standard Stack

Versions below were verified locally on 2026-04-24 unless otherwise noted. [VERIFIED: `python3 --version`, `pytest --version`, direct local imports, `requirements.txt`]

### Core

| Library | Version | Purpose | Why Standard | Source |
|---------|---------|---------|--------------|--------|
| Python | 3.12.2 | Runtime for all analysis and validation commands | The repo is a Python-only empirical workflow and all phase entrypoints are Python scripts | [VERIFIED: `python3 --version`, `.planning/PROJECT.md`] |
| pandas | 2.2.3 | Panel loading, reshaping, CSV/LaTeX output | Every existing analysis path reads `panel.parquet` and writes tabular artifacts with pandas | [VERIFIED: direct local import, `requirements.txt`, `src/analysis/event_study_core.py`] |
| statsmodels | 0.14.4 | Pre-trend OLS and descriptive event-study estimation | The shared event-study core and other analysis modules already depend on it | [VERIFIED: direct local import, `requirements.txt`, `src/analysis/event_study_core.py`] |
| matplotlib | 3.9.2 | PDF figure generation | Current Japan and Korea CAR figures are generated through matplotlib | [VERIFIED: direct local import, `requirements.txt`, `src/analysis/event_study_core.py`] |
| seaborn | 0.13.2 | Figure styling | The shared plotting helper calls `sns.set_theme(style="whitegrid")` | [VERIFIED: direct local import, `requirements.txt`, `src/analysis/event_study_core.py`] |
| pytest | 8.3.4 | Phase-gate validation | Every milestone phase uses pytest-based regression gates | [VERIFIED: `pytest --version`, direct local import, `tests/test_phase6.py`, `tests/test_phase7.py`] |

### Supporting

| Library | Version | Purpose | When to Use | Source |
|---------|---------|---------|-------------|--------|
| linearmodels | 6.1 | Alternative-control PanelOLS robustness checks | Use only if Phase 8 surfaces existing comparator sensitivity via the shipped panel-OLS robustness path | [VERIFIED: direct local import, `requirements.txt`, `src/robustness/robustness_alt_control.py`, `src/analysis/panel_ols.py`] |
| pyarrow | 15.0.2 | `panel.parquet` I/O | Needed whenever Phase 8 reruns load the canonical panel from disk | [VERIFIED: direct local import, `requirements.txt`, local `panel.parquet` audit on 2026-04-24] |

### Alternatives Considered

| Instead of | Could Use | Tradeoff | Source |
|------------|-----------|----------|--------|
| Reusing `event_study_core.run_event_study()` | A bespoke Korea robustness estimator | Higher regression risk and duplicate logic for the same CAR contract | [VERIFIED: `src/analysis/event_study_core.py`, `src/analysis/korea_event_study.py`] |
| Keeping `TOPIX` fixed for event-study robustness | Refactoring the core to accept arbitrary comparators in Phase 8 | The current core hard-codes the KOSPI-TOPIX spread, axis label, and country validation, so comparator refactor is a scope expansion rather than a simple robustness rerun | [VERIFIED: `src/analysis/event_study_core.py`] |
| Using the spaced follow-through set only as `+2` robustness | Extending it to a longer post window | Fails against the actual `2026-04-30` endpoint because the February 24, 2026 event has only two post months available | [VERIFIED: `config.py`, local month-count audit on 2026-04-24, local feasibility audit on 2026-04-24] |

**Installation:**
```bash
pip install -r requirements.txt
```

**Version verification:** Local runtime verification matched the repo pins for `pandas`, `statsmodels`, `matplotlib`, `seaborn`, `pyarrow`, `pytest`, and `linearmodels`. [VERIFIED: direct local imports, `requirements.txt`]

## Architecture Patterns

### Recommended Project Structure

Keep Phase 8 additions inside the same surfaces Phase 7 already established: analysis runners in `src/analysis/`, phase-gate tests in `tests/`, and spec-specific artifacts in `output/figures/` and `output/tables/`. That matches the current Japan/Korea event-study layout and preserves the shipped artifact contract. [VERIFIED: `src/analysis/event_study.py`, `src/analysis/korea_event_study.py`, `tests/test_phase7.py`, `.planning/phases/07-korea-value-up-event-study/07-VERIFICATION.md`]

```text
src/
├── analysis/
│   ├── event_study_core.py          # Shared estimator/output core (reuse)
│   ├── korea_event_study.py         # Shipped primary Korea wrapper
│   └── ...Phase 8 robustness runner # New wrapper or loop, not a new estimator
tests/
├── test_phase8.py                   # Fresh-output robustness and note assertions
output/
├── figures/                         # Spec-specific Korea robustness PDFs
└── tables/                          # CAR CSVs, LaTeX tables, interpretation note fragment
```

### Pattern 1: Policy-Driven Wrapper over the Shared Core

**What:** Implement Phase 8 as additional wrappers or loops over `event_study_core.run_event_study()` using explicit date/label/window policies; do not fork the estimator math. [VERIFIED: `src/analysis/korea_event_study.py`, `src/analysis/event_study_core.py`, `config.py`]

**When to use:** Any robustness run where the only changes are event dates, labels, post-window length, titles, or output names. [VERIFIED: `src/analysis/korea_event_study.py`, `config.py`]

**Example:**
```python
# Source: src/analysis/korea_event_study.py
primary_policy = config.KOREA_EVENT_SET_POLICY["primary"]
event_study_core.run_event_study(
    panel,
    event_dates=primary_policy["dates"],
    event_labels=primary_policy["labels"],
    study_end=config.FOLLOW_ON_STUDY_END,
    stack_window_min=-36,
    stack_window_max=int(primary_policy["max_post_months"]),
    event_window_min=-12,
    event_window_max=int(primary_policy["max_post_months"]),
    figure_output_path=...,
    car_output_path=...,
    table_output_path=...,
)
```

### Pattern 2: Window Sensitivity by Synchronous Truncation

**What:** Keep `stack_window_max` and `event_window_max` synchronized for each specification, exactly as the shipped Korea wrapper does today. [VERIFIED: `src/analysis/korea_event_study.py`]  
**Why:** The shared core requires a complete event window for every cohort, so the post horizon must be chosen by the most recent event retained in the specification. [VERIFIED: `src/analysis/event_study_core.py`, local feasibility audit on 2026-04-24]

**Feasible Phase 8 windows:**

- `narrow_2024_rollout`: shipped `+20` already works, and direct reruns confirm `+12` and `+8` also work cleanly for all three cohorts. [VERIFIED: `config.py`, local feasibility audit on 2026-04-24]
- `spaced_follow_through`: `+2` works for all three cohorts, but `+3` fails because the February 24, 2026 event has no third post month through April 2026. [VERIFIED: `config.py`, local month-count audit on 2026-04-24, local feasibility audit on 2026-04-24]

**Recommendation:** Use `+12` as the required alternative window for `KROB-02` because it preserves a full one-year post-treatment view for the narrow 2024 rollout while materially reducing overlap relative to the shipped `+20` design. Keep `+8` optional and do not require it unless reviewers or the user explicitly want a second narrow-window cut. [VERIFIED: local feasibility audit on 2026-04-24, `.planning/phases/07-korea-value-up-event-study/07-VERIFICATION.md`]

### Pattern 3: Comparator Sensitivity at the Codebase Boundary

**What:** Treat `TOPIX` as the fixed event-study comparator in Phase 8, and express comparator sensitivity through existing non-event-study robustness surfaces instead of refactoring `event_study_core` mid-phase. [VERIFIED: `src/analysis/event_study_core.py`, `src/descriptive/discount_stats.py`, `src/robustness/robustness_alt_control.py`, `src/robustness/robustness_placebo.py`]

**When to use:** When the planner needs comparator sensitivity without turning Phase 8 into a core-estimator redesign. [VERIFIED: `.planning/ROADMAP.md`, `src/analysis/event_study_core.py`]

**Comparator choices that already exist in the repo:**

- `TOPIX` is the event-study spread benchmark and the paper’s primary comparative market for event-window interpretation. [VERIFIED: `src/analysis/event_study_core.py`, `paper/main_v2.tex`]
- `MSCI_EM` is the shipped descriptive benchmark for headline discount magnitude. [VERIFIED: `src/descriptive/discount_stats.py`, `tests/test_descriptive.py`]
- `MSCI_EM_ASIA` and approximate `MSCI_EM_EX_CHINA` already exist as alternative control-group checks in the panel-OLS robustness path. [VERIFIED: `src/robustness/robustness_alt_control.py`, `paper/main_v2.tex`]
- `MSCI_TAIWAN` and `MSCI_INDONESIA` already exist as placebo event-study markets. [VERIFIED: `src/robustness/robustness_placebo.py`, `tests/test_phase4.py`]

### Pattern 4: Standalone Interpretation Note Artifact

**What:** Generate one interpretation-ready text fragment rather than editing the paper in Phase 8. A `.tex` fragment under `output/tables/` is the lowest-friction choice because the current paper already consumes generated LaTeX fragments from that directory. [VERIFIED: user prompt, `.planning/ROADMAP.md`, `paper/main_v2.tex`, `output/tables/*.tex`]

**What it should say:** Japan remains the policy benchmark and institutional analogue; Korea Phase 8 adds descriptive timing evidence around Korea’s own reforms; neither the Japan event windows nor the Korea follow-on windows justify a strong new causal claim in this phase. [VERIFIED: `paper/main_v2.tex`, `.planning/PROJECT.md`, `.planning/phases/06-korea-reform-date-locking-and-sample-horizon/06-DATE-LOCK.md`][CITED: https://www.fsc.go.kr/eng/pr010101/81778][CITED: https://www.fsc.go.kr/eng/pr010101/82213][CITED: https://www.fsc.go.kr/eng/pr010101/82875][CITED: https://www.fsc.go.kr/eng/pr010101/84905][CITED: https://www.fsc.go.kr/eng/pr010101/86320%3FsrchCtgry%3D%26curPage%3D%26srchKey%3D%26srchText%3D%26srchBeginDt%3D%26srchEndDt%3D]

### Anti-Patterns to Avoid

- **Do not silently mutate `config.KOREA_EVENT_SET_POLICY["primary"]`:** robustness runs should be explicit named specs with their own output paths. [VERIFIED: `config.py`, `src/analysis/korea_event_study.py`]
- **Do not extend the spaced follow-through set beyond `+2`:** the core will reject incomplete windows, and a manual workaround would misstate the actual evidence horizon. [VERIFIED: `src/analysis/event_study_core.py`, local feasibility audit on 2026-04-24]
- **Do not sell comparator sensitivity as an event-study benchmark swap unless the core is intentionally refactored:** current comparator flexibility exists in descriptive, panel-OLS, and placebo modules, not in `event_study_core`. [VERIFIED: `src/analysis/event_study_core.py`, `src/descriptive/discount_stats.py`, `src/robustness/robustness_alt_control.py`, `src/robustness/robustness_placebo.py`]
- **Do not turn Phase 8 into paper integration:** the roadmap and prompt reserve that for Phase 9. [VERIFIED: user prompt, `.planning/ROADMAP.md`]

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why | Source |
|---------|-------------|-------------|-----|--------|
| Korea robustness CAR estimation | A second event-study estimator | `src/analysis/event_study_core.py` via a thin wrapper | The shared core already handles panel prep, cohort building, CAR construction, comments, CSV, LaTeX, and PDF output | [VERIFIED: `src/analysis/event_study_core.py`, `src/analysis/korea_event_study.py`] |
| Korea reform-date sourcing | New ad hoc media dates | Locked Phase 6 date memo plus official FSC pages already referenced there | The repo already established an official-source rule and date-set split | [VERIFIED: `.planning/research/KOREA_VALUE_UP_DATES.md`, `.planning/phases/06-korea-reform-date-locking-and-sample-horizon/06-DATE-LOCK.md`][CITED: https://www.fsc.go.kr/eng/pr010101/81778][CITED: https://www.fsc.go.kr/eng/pr010101/82213][CITED: https://www.fsc.go.kr/eng/pr010101/82875][CITED: https://www.fsc.go.kr/eng/pr010101/84905][CITED: https://www.fsc.go.kr/eng/pr010101/86320%3FsrchCtgry%3D%26curPage%3D%26srchKey%3D%26srchText%3D%26srchBeginDt%3D%26srchEndDt%3D] |
| Comparator sensitivity | A new arbitrary-benchmark event-study framework inside Phase 8 | Existing repo surfaces: `discount_stats.py`, `robustness_alt_control.py`, `robustness_placebo.py` | Comparator robustness already exists elsewhere; refactoring the event-study core would be a separate engineering task | [VERIFIED: `src/descriptive/discount_stats.py`, `src/robustness/robustness_alt_control.py`, `src/robustness/robustness_placebo.py`, `src/analysis/event_study_core.py`] |
| Interpretation prose | Paper edits in Phase 8 | A standalone note fragment under `output/tables/` | It keeps Phase 8 within scope and leaves actual manuscript wiring to Phase 9 | [VERIFIED: user prompt, `.planning/ROADMAP.md`, `paper/main_v2.tex`] |

**Key insight:** Phase 8 is mostly a specification-and-output phase, not a new-estimator phase. The highest-value work is choosing defensible windows and caveats that the current core already supports. [VERIFIED: `src/analysis/event_study_core.py`, `.planning/ROADMAP.md`, `.planning/REQUIREMENTS.md`]

## Common Pitfalls

### Pitfall 1: Treating the Spaced 2024-2026 Set as a Long-Window Design

**What goes wrong:** The planner picks the spaced follow-through dates and keeps a long post window out of habit. [VERIFIED: `config.py`, `.planning/phases/06-korea-reform-date-locking-and-sample-horizon/06-DATE-LOCK.md`]  
**Why it happens:** The 2024 event in that set has plenty of runway, which hides the fact that the February 24, 2026 event only has two post months. [VERIFIED: local month-count audit on 2026-04-24][CITED: https://www.fsc.go.kr/eng/pr010101/86320%3FsrchCtgry%3D%26curPage%3D%26srchKey%3D%26srchText%3D%26srchBeginDt%3D%26srchEndDt%3D]  
**How to avoid:** Lock the spaced set at `max_post_months = 2` unless the panel endpoint moves beyond April 2026. [VERIFIED: `config.py`, local feasibility audit on 2026-04-24]  
**Warning signs:** `build_stacked_dataset()` raises a complete-window `ValueError`, or the planner proposes a shared post window longer than two months for the spaced set. [VERIFIED: `src/analysis/event_study_core.py`, local feasibility audit on 2026-04-24]

### Pitfall 2: Over-Interpreting Magnitude Comparisons Across Japan and Korea

**What goes wrong:** The note treats Korea CAR magnitudes as if they are directly comparable to Japan CAR magnitudes in a causal or policy-payoff sense. [VERIFIED: `paper/main_v2.tex`, `.planning/REQUIREMENTS.md`]  
**Why it happens:** Both studies share the same output family, which makes visual comparability stronger than identification comparability. [VERIFIED: `src/analysis/event_study.py`, `src/analysis/korea_event_study.py`, `.planning/phases/07-korea-value-up-event-study/07-VERIFICATION.md`]  
**How to avoid:** State explicitly that Japan is the historical policy benchmark, Korea is descriptive follow-on evidence, and the studies have different overlap and horizon constraints. [VERIFIED: `paper/main_v2.tex`, `.planning/phases/06-korea-reform-date-locking-and-sample-horizon/06-DATE-LOCK.md`][CITED: https://www.fsc.go.kr/eng/pr010101/81778][CITED: https://www.fsc.go.kr/eng/pr010101/84905][CITED: https://www.fsc.go.kr/eng/pr010101/86320%3FsrchCtgry%3D%26curPage%3D%26srchKey%3D%26srchText%3D%26srchBeginDt%3D%26srchEndDt%3D]  
**Warning signs:** Language such as “Korea proves,” “Korea causes,” or “Japan predicts the Korea treatment effect” appears in a Phase 8 note. [VERIFIED: `paper/main_v2.tex`, user prompt]

### Pitfall 3: Smuggling a Comparator Refactor into a Robustness Phase

**What goes wrong:** Phase 8 starts rewriting the core estimator around arbitrary comparators to satisfy the word “comparator.” [VERIFIED: `.planning/ROADMAP.md`, `src/analysis/event_study_core.py`]  
**Why it happens:** The codebase has comparator sensitivity elsewhere, so it is easy to assume the event-study core is equally flexible. [VERIFIED: `src/descriptive/discount_stats.py`, `src/robustness/robustness_alt_control.py`, `src/robustness/robustness_placebo.py`, `src/analysis/event_study_core.py`]  
**How to avoid:** Keep the Korea event-study comparator fixed at TOPIX for Phase 8 and surface alternative comparator evidence through already-shipped modules or narrative notes. [VERIFIED: `src/analysis/event_study_core.py`, `paper/main_v2.tex`]  
**Warning signs:** New API proposals mention arbitrary benchmark names, extra spread formulas, or new figure-axis semantics inside the shared core. [VERIFIED: `src/analysis/event_study_core.py`]

### Pitfall 4: Letting Stale Artifacts Masquerade as Passing Robustness

**What goes wrong:** Tests only assert that files exist, so an old robustness output can mask a broken script. [VERIFIED: `tests/test_phase4.py`, `tests/test_phase7.py`, `.planning/phases/07-korea-value-up-event-study/07-VERIFICATION.md`]  
**Why it happens:** Several existing tests are presence-oriented rather than fresh-generation smoke tests. [VERIFIED: `tests/test_phase4.py`, `tests/test_phase7.py`, `.planning/phases/07-korea-value-up-event-study/07-VERIFICATION.md`]  
**How to avoid:** Phase 8 tests should either generate fresh outputs into temporary paths or verify the script’s runtime behavior directly before asserting on files. [VERIFIED: `.planning/phases/07-korea-value-up-event-study/07-VERIFICATION.md`, `.planning/phases/06-korea-reform-date-locking-and-sample-horizon/06-VERIFICATION.md`]  
**Warning signs:** A test passes without executing a Phase 8 script, or it reads only pre-existing files under `output/`. [VERIFIED: `tests/test_phase4.py`, `tests/test_phase7.py`]

## Code Examples

Verified patterns from current project code:

### Existing Korea Wrapper Pattern
```python
# Source: src/analysis/korea_event_study.py
primary_policy = config.KOREA_EVENT_SET_POLICY["primary"]
event_dates = primary_policy["dates"]
event_labels = primary_policy["labels"]
max_post_months = int(primary_policy["max_post_months"])
study_end = config.FOLLOW_ON_STUDY_END
```

### Current Hard-Wired Event-Study Comparator
```python
# Source: src/analysis/event_study_core.py
for country in ("KOSPI", "TOPIX"):
    if country not in pivot.columns:
        raise ValueError(f"Panel is missing required country: {country}")

spread = (pivot["KOSPI"] - pivot["TOPIX"]).rename("spread").dropna().to_frame()
```

### Current Output-Contract Pattern
```python
# Source: src/analysis/event_study_core.py
car.to_csv(car_output_path, index=False)
write_latex_table_with_comments(
    car,
    table_output_path,
    leading_comments=table_comment_lines,
)
plot_event_study(
    car,
    event_dates=event_dates,
    event_labels=event_labels,
    figure_title=figure_title,
    figure_output_path=figure_output_path,
)
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact | Source |
|--------------|------------------|--------------|--------|--------|
| One Korea primary specification only | Locked primary and robustness date sets in `config.KOREA_EVENT_SET_POLICY` | Phase 6 on 2026-04-23 | Phase 8 can rerun robustness without changing Japan defaults | [VERIFIED: `config.py`, `.planning/phases/06-korea-reform-date-locking-and-sample-horizon/06-VERIFICATION.md`] |
| Treating recent reforms as if long windows are always available | Choosing post windows from the actual `2026-04-30` endpoint and most recent event in each set | Phase 6 onward | Prevents infeasible or misleading long-window Korea follow-through claims | [VERIFIED: `.planning/phases/06-korea-reform-date-locking-and-sample-horizon/06-DATE-LOCK.md`, local month-count audit on 2026-04-24] |
| Event-study results described as if they support formal inference | Descriptive CARs only, with no standard errors reported from the saturated design | Phase 3 onward | Phase 8 interpretation must stay descriptive on both Japan and Korea sides | [VERIFIED: `src/analysis/event_study_core.py`, `paper/main_v2.tex`] |

**Deprecated/outdated:**

- Treating the 2025 and 2026 Korea dates as main-spec long-window evidence is outdated under the current `2026-04-30` panel endpoint; they belong in robustness or follow-through interpretation only. [VERIFIED: `.planning/phases/06-korea-reform-date-locking-and-sample-horizon/06-DATE-LOCK.md`, local month-count audit on 2026-04-24][CITED: https://www.fsc.go.kr/eng/pr010101/84905][CITED: https://www.fsc.go.kr/eng/pr010101/86320%3FsrchCtgry%3D%26curPage%3D%26srchKey%3D%26srchText%3D%26srchBeginDt%3D%26srchEndDt%3D] |
- Treating the Japan event-study figures as clean governance-only causal experiments is already rejected by the shipped paper and should not be revived in the Phase 8 comparison note. [VERIFIED: `paper/main_v2.tex`] |

## Assumptions Log

All core factual claims in this research were verified against the current codebase, local environment, local dataset, or official FSC press-release pages. No unverified implementation-critical assumptions remain. [VERIFIED: sources listed below]

## Open Questions (RESOLVED)

1. **Should Phase 8 ship only one shorter narrow-window sensitivity, or two?**
   - What we know: `+12` and `+8` both execute cleanly for the narrow 2024 set, and `KROB-02` requires at least one alternative window. [VERIFIED: local feasibility audit on 2026-04-24]
   - Resolution: Phase 8 will ship exactly one required shorter narrow-window sensitivity, `narrow_2024_rollout_post12`, because it satisfies `KROB-02` while preserving a full one-year post-treatment window and avoids generating extra low-value artifacts. [VERIFIED: `.planning/REQUIREMENTS.md`, `.planning/ROADMAP.md`, local feasibility audit on 2026-04-24]
   - Deferred choice: leave `+8` out of scope for this phase unless a later reviewer-driven change explicitly asks for a second sensitivity. [VERIFIED: `.planning/ROADMAP.md`]

2. **How much comparator sensitivity should Phase 8 expose directly in Korea robustness outputs?**
   - What we know: the event-study core is TOPIX-specific, while alternative comparator robustness already exists elsewhere in the repo. [VERIFIED: `src/analysis/event_study_core.py`, `src/descriptive/discount_stats.py`, `src/robustness/robustness_alt_control.py`, `src/robustness/robustness_placebo.py`]
   - Resolution: Phase 8 will keep the event-study spread fixed at `KOSPI - TOPIX` inside `src/analysis/event_study_core.py` and surface comparator sensitivity only through existing descriptive, panel-robustness, and placebo outputs plus a Phase 8 scope note. [VERIFIED: `.planning/ROADMAP.md`, `src/analysis/event_study_core.py`, `src/descriptive/discount_stats.py`, `src/robustness/robustness_alt_control.py`, `src/robustness/robustness_placebo.py`]
   - Out of scope: a true event-study comparator refactor or new benchmark API remains deferred unless a later phase explicitly reopens the shared-core contract. [VERIFIED: `.planning/ROADMAP.md`, `src/analysis/event_study_core.py`]

## Environment Availability

| Dependency | Required By | Available | Version | Fallback | Source |
|------------|------------|-----------|---------|----------|--------|
| Python | All analysis scripts | ✓ | 3.12.2 | — | [VERIFIED: `python3 --version`] |
| pytest | Phase validation | ✓ | 8.3.4 | — | [VERIFIED: `pytest --version`] |
| pandas / statsmodels / matplotlib / seaborn / pyarrow | Korea robustness reruns and artifact generation | ✓ | `2.2.3 / 0.14.4 / 3.9.2 / 0.13.2 / 15.0.2` | — | [VERIFIED: direct local imports, `requirements.txt`] |
| linearmodels | Existing comparator-sensitivity OLS path | ✓ | 6.1 | Skip OLS comparator reruns if not needed | [VERIFIED: direct local import, `requirements.txt`] |
| `data/processed/panel.parquet` | All Korea reruns | ✓ | 1,072 rows; max date `2026-04-30` | None | [VERIFIED: local panel audit on 2026-04-24] |

**Missing dependencies with no fallback:** None. [VERIFIED: local environment audit on 2026-04-24]

**Missing dependencies with fallback:** None. [VERIFIED: local environment audit on 2026-04-24]

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | `pytest 8.3.4` [VERIFIED: `pytest --version`] |
| Config file | `none — pytest is invoked directly from repo root` [VERIFIED: repo file scan on 2026-04-24] |
| Quick run command | `pytest tests/test_phase8.py -q` [VERIFIED: project phase-test pattern in `tests/test_phase6.py`, `tests/test_phase7.py`] |
| Full suite command | `pytest -q` [VERIFIED: `.planning/phases/06-korea-reform-date-locking-and-sample-horizon/06-VERIFICATION.md`, `.planning/phases/07-korea-value-up-event-study/07-VERIFICATION.md`] |

### Phase Requirements -> Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| KROB-01 | Narrow and spaced Korea date specs both generate the expected cohort windows and distinct artifact names | integration | `pytest tests/test_phase8.py::test_korea_robustness_date_specs_generate_expected_windows -q` | ❌ Wave 0 |
| KROB-02 | The chosen alternative narrow window reruns cleanly and the spaced set is capped at `+2` | unit + integration | `pytest tests/test_phase8.py::test_korea_window_sensitivity_respects_endpoint -q` | ❌ Wave 0 |
| KROB-03 | The interpretation note explicitly separates descriptive timing evidence from stronger causal claims | unit / content | `pytest tests/test_phase8.py::test_korea_japan_note_contains_causal_caveats -q` | ❌ Wave 0 |

### Sampling Rate

- **Per task commit:** `pytest tests/test_phase8.py -q` [VERIFIED: existing phase-test pattern in `tests/test_phase6.py`, `tests/test_phase7.py`]
- **Per wave merge:** `pytest tests/test_phase6.py tests/test_phase7.py tests/test_phase8.py -q` [VERIFIED: current milestone dependency chain in `.planning/ROADMAP.md`]
- **Phase gate:** `pytest -q` plus direct rerun of the Phase 8 robustness entrypoint(s) to avoid stale-artifact false positives. [VERIFIED: `.planning/phases/07-korea-value-up-event-study/07-VERIFICATION.md`, `tests/test_phase4.py`, `tests/test_phase7.py`]

### Wave 0 Gaps

- [ ] `tests/test_phase8.py` — missing phase gate for `KROB-01` through `KROB-03`. [VERIFIED: repo file scan on 2026-04-24]
- [ ] Fresh-output smoke coverage — Phase 8 should execute its robustness runner into temporary paths or otherwise prove regeneration, not just inspect existing files. [VERIFIED: `tests/test_phase4.py`, `tests/test_phase7.py`, `.planning/phases/07-korea-value-up-event-study/07-VERIFICATION.md`]
- [ ] Interpretation-note contract test — no current test asserts caveated Japan-versus-Korea wording because the artifact does not exist yet. [VERIFIED: repo file scan on 2026-04-24]

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control | Source |
|---------------|---------|------------------|--------|
| V2 Authentication | no | Not applicable for offline analysis scripts | [VERIFIED: current repo architecture in `.planning/PROJECT.md`, `src/analysis/*.py`] |
| V3 Session Management | no | Not applicable for offline analysis scripts | [VERIFIED: current repo architecture in `.planning/PROJECT.md`, `src/analysis/*.py`] |
| V4 Access Control | no | Not applicable for local batch analysis | [VERIFIED: current repo architecture in `.planning/PROJECT.md`, `src/analysis/*.py`] |
| V5 Input Validation | yes | Keep column checks, event-window completeness checks, and locked date policies; fail fast on missing countries or malformed panels | [VERIFIED: `src/analysis/event_study_core.py`, `config.py`, `tests/test_phase6.py`] |
| V6 Cryptography | no | Not applicable for this phase | [VERIFIED: current repo architecture in `.planning/PROJECT.md`, `src/analysis/*.py`] |

### Known Threat Patterns for This Stack

| Pattern | STRIDE | Standard Mitigation | Source |
|---------|--------|---------------------|--------|
| Unverified event-date substitution | Tampering | Only use the Phase 6 locked date sets backed by official FSC sources | [VERIFIED: `.planning/phases/06-korea-reform-date-locking-and-sample-horizon/06-DATE-LOCK.md`, `config.py`][CITED: https://www.fsc.go.kr/eng/pr010101/81778][CITED: https://www.fsc.go.kr/eng/pr010101/82213][CITED: https://www.fsc.go.kr/eng/pr010101/82875][CITED: https://www.fsc.go.kr/eng/pr010101/84905][CITED: https://www.fsc.go.kr/eng/pr010101/86320%3FsrchCtgry%3D%26curPage%3D%26srchKey%3D%26srchText%3D%26srchBeginDt%3D%26srchEndDt%3D] |
| Overwriting shipped Japan artifacts during Korea robustness runs | Tampering | Preserve Korea-specific filenames and keep explicit Japan/Korea path separation | [VERIFIED: `src/analysis/event_study.py`, `src/analysis/korea_event_study.py`, `.planning/phases/07-korea-value-up-event-study/07-VERIFICATION.md`] |
| Accepting stale outputs as proof of a passing rerun | Repudiation / Tampering | Execute Phase 8 scripts in verification and prefer fresh-output tests over existence-only assertions | [VERIFIED: `tests/test_phase4.py`, `tests/test_phase7.py`, `.planning/phases/07-korea-value-up-event-study/07-VERIFICATION.md`] |
| Extending windows beyond the true sample endpoint | Tampering / DoS | Let `build_stacked_dataset()` fail on incomplete windows and encode maximum post months explicitly per spec | [VERIFIED: `src/analysis/event_study_core.py`, `config.py`, local feasibility audit on 2026-04-24] |

## Sources

### Primary (HIGH confidence)

- `config.py` - locked Korea narrow/spaced date sets, `KOREA_EVENT_SET_POLICY`, `FOLLOW_ON_STUDY_END`
- `src/analysis/event_study_core.py` - shared estimator, hard-wired KOSPI-TOPIX spread, complete-window enforcement, output contract
- `src/analysis/korea_event_study.py` - shipped Korea wrapper and current `max_post_months` usage
- `src/descriptive/discount_stats.py` - shipped descriptive comparator surfaces (`TOPIX`, `MSCI_EM`)
- `src/robustness/robustness_alt_control.py` - existing alternative comparator checks (`MSCI_EM_ASIA`, approximate `MSCI_EM_EX_CHINA`)
- `src/robustness/robustness_placebo.py` - existing placebo event-study markets (`MSCI_TAIWAN`, `MSCI_INDONESIA`)
- `.planning/phases/06-korea-reform-date-locking-and-sample-horizon/06-DATE-LOCK.md` - rationale for narrow vs spaced date sets and endpoint constraint
- `.planning/phases/06-korea-reform-date-locking-and-sample-horizon/06-VERIFICATION.md` - proof that follow-on horizon and policy dict shipped cleanly
- `.planning/phases/07-korea-value-up-event-study/07-VERIFICATION.md` - proof that the Korea event study runs, respects `max_post_months`, and leaves Japan outputs unchanged
- `paper/main_v2.tex` - current causal-limit language for Japan event-study interpretation
- FSC official press releases:
  - https://www.fsc.go.kr/eng/pr010101/81778
  - https://www.fsc.go.kr/eng/pr010101/82213
  - https://www.fsc.go.kr/eng/pr010101/82875
  - https://www.fsc.go.kr/eng/pr010101/84905
  - https://www.fsc.go.kr/eng/pr010101/86320%3FsrchCtgry%3D%26curPage%3D%26srchKey%3D%26srchText%3D%26srchBeginDt%3D%26srchEndDt%3D
- Local environment audits on 2026-04-24:
  - `python3 --version`
  - `pytest --version`
  - direct import/version checks for `pandas`, `statsmodels`, `matplotlib`, `seaborn`, `pyarrow`, `pytest`, `linearmodels`
  - direct `panel.parquet` audit
  - direct feasibility reruns for narrow `+12`, narrow `+8`, spaced `+2`, and spaced `+3`

### Secondary (MEDIUM confidence)

- None. [VERIFIED: source audit on 2026-04-24]

### Tertiary (LOW confidence)

- None. [VERIFIED: source audit on 2026-04-24]

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - all versions and dependencies were verified locally against the current environment and repo pins. [VERIFIED: local environment audit on 2026-04-24, `requirements.txt`]
- Architecture: HIGH - recommendations align directly with the shipped Phase 6 and Phase 7 code and verification artifacts. [VERIFIED: `config.py`, `src/analysis/event_study_core.py`, `src/analysis/korea_event_study.py`, phase verification docs]
- Pitfalls: HIGH - the major failure modes are already visible in current code constraints, Phase 4/7 test-strength warnings, and the actual date-window math. [VERIFIED: `src/analysis/event_study_core.py`, `tests/test_phase4.py`, `tests/test_phase7.py`, local feasibility audit on 2026-04-24]

**Research date:** 2026-04-24  
**Valid until:** 2026-05-24 for repo-structure findings; sooner only if the panel endpoint or Korea date policy changes. [VERIFIED: `config.py`, local panel audit on 2026-04-24]
