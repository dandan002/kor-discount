---
phase: 04-synthetic-control-and-robustness
verified: 2026-04-21T00:11:14Z
status: passed
score: 12/12 must-haves verified
overrides_applied: 0
---

# Phase 4: Synthetic Control and Robustness Verification Report

**Phase Goal:** The synthetic control for the 2023 TSE reform is estimated and all planned robustness checks pass -- the primary result is confirmed robust to alternative specifications  
**Verified:** 2026-04-21T00:11:14Z  
**Status:** passed  
**Re-verification:** No -- initial verification

## Goal Achievement

Phase 4 achieved the goal. All four robustness scripts regenerate their outputs from real source data, all expected artifacts exist and are substantive, the Phase 4 and full test suites pass, and the human checkpoint response `rmspe-high` is treated as accepted with a Phase 5 paper-text caveat rather than a blocker.

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | Phase 4 test scaffold exists and covers all required checks | VERIFIED | `tests/test_phase4.py` defines 8 tests covering synthetic weights, outputs, SUTVA, placebo outputs, P/E outputs, alt-control outputs, ROBUST-04 figures, and module isolation. |
| 2 | `src/robustness/` is a package and `pysyncon==1.5.2` is pinned/importable | VERIFIED | `src/robustness/__init__.py` exists; `requirements.txt` contains `pysyncon==1.5.2`; `importlib.metadata.version("pysyncon")` returned `1.5.2`. |
| 3 | Synthetic control runs using ADH/pysyncon for the 2023 TSE P/B reform | VERIFIED | `python src/robustness/synthetic_control.py` exited 0; `run_synth()` uses `Dataprep`/`Synth` with TOPIX treated and five donors. |
| 4 | Synthetic control reports weights, positive RMSPE, and pre/post fit chart | VERIFIED | `synthetic_control_weights.csv` has donor/weight/pre_rmspe; weights sum to `1.0`; RMSPE is `0.2892855456344879`; `figure_synth_gap.pdf` is a valid non-empty PDF. |
| 5 | Donor pool and SUTVA justification are documented | VERIFIED | `synthetic_control.py` includes the SUTVA block with donor pool, KOSPI exclusion, and governance-contagion rationale. One comment sentence is stale about India/Taiwan placebo markets; treated as warning, not blocker. |
| 6 | ROBUST-04 in-time and in-space synthetic-control placebos run and save outputs | VERIFIED | `synthetic_control.py` regenerated `figure_placebo_intime.pdf` and `figure_placebo_inspace.pdf`; both are valid non-empty PDFs. |
| 7 | ROBUST-01 placebo falsification tests run on Taiwan and Indonesia | VERIFIED | `robustness_placebo.py` regenerated Taiwan/Indonesia CAR CSVs and falsification PDF; all post-event placebo CIs include zero (`25/25` for each market). |
| 8 | ROBUST-02 P/E robustness replicates Phase 3 event study, PanelOLS, and GPR flow | VERIFIED | `robustness_pe.py` regenerates `robustness_pe_event_coefs.tex` and `robustness_pe_ols.tex`; GPR sub-analysis runs and logs coefficient/p-value. |
| 9 | ROBUST-02 drops P/E nulls before analysis | VERIFIED | `load_panel_pe()` calls `panel.dropna(subset=["pe"])`; verification saw 4 P/E nulls in `panel.parquet` and script logged 1068 rows after dropping them. |
| 10 | ROBUST-03 alternative controls run for EM Asia and EM ex-China | VERIFIED | `robustness_alt_control.py` regenerated both LaTeX outputs; uses `CHINA_WEIGHT_APPROX = 0.30` with an approximation comment and real MSCI EM/China raw CSV inputs. |
| 11 | Robustness modules are standalone | VERIFIED | Manual AST import scan found no imports from `src.analysis`, `src.robustness`, `analysis`, or `robustness` in the four robustness scripts. |
| 12 | Full verification gate passes, including human checkpoint | VERIFIED | Regenerated all four robustness outputs, then `python -m pytest tests/test_phase4.py -q` passed `8 passed`; `python -m pytest tests/ -q` passed `29 passed`; checkpoint response `rmspe-high` accepted with caveat. |

**Score:** 12/12 truths verified

### Required Artifacts

| Artifact | Expected | Status | Details |
|---|---|---|---|
| `tests/test_phase4.py` | Phase 4 smoke/unit tests | VERIFIED | 8 test functions defined; imports config and checks output artifacts. |
| `src/robustness/__init__.py` | Package marker | VERIFIED | Exists and importable. |
| `requirements.txt` | Pinned synthetic-control dependency | VERIFIED | Contains `pysyncon==1.5.2`; metadata version check returned `1.5.2`. |
| `src/robustness/synthetic_control.py` | ADH synthetic control + ROBUST-04 placebos | VERIFIED | Runs successfully and writes weights plus three PDFs. |
| `output/robustness/synthetic_control_weights.csv` | Donor weights + RMSPE | VERIFIED | 186 bytes; columns `donor,weight,pre_rmspe`; weights sum to `1.0`; RMSPE positive. |
| `output/figures/figure_synth_gap.pdf` | Primary synthetic-control gap plot | VERIFIED | 19028 bytes; PDF header present. |
| `output/robustness/figure_placebo_intime.pdf` | In-time placebo figure | VERIFIED | 19595 bytes; PDF header present. |
| `output/robustness/figure_placebo_inspace.pdf` | In-space placebo figure | VERIFIED | 30403 bytes; PDF header present. |
| `src/robustness/robustness_placebo.py` | Taiwan/Indonesia placebo event study | VERIFIED | Runs successfully and writes CAR CSVs plus falsification PDF. |
| `output/robustness/placebo_taiwan_car.csv` | Taiwan placebo CAR estimates | VERIFIED | 25 rows; columns include `event_rel_time`, `car`, `ci_lo`, `ci_hi`. |
| `output/robustness/placebo_indonesia_car.csv` | Indonesia placebo CAR estimates | VERIFIED | 25 rows; columns include `event_rel_time`, `car`, `ci_lo`, `ci_hi`. |
| `output/robustness/figure_placebo_falsification.pdf` | Combined placebo falsification figure | VERIFIED | 16211 bytes; PDF header present. |
| `src/robustness/robustness_pe.py` | Full P/E robustness script | VERIFIED | Runs successfully; event-study and PanelOLS outputs saved; GPR result logged. |
| `output/robustness/robustness_pe_ols.tex` | P/E PanelOLS table | VERIFIED | 961 bytes; contains P/E caption and wild-bootstrap p-values. |
| `output/robustness/robustness_pe_event_coefs.tex` | P/E event-study table | VERIFIED | 7190 bytes; contains P/E CAR rows. |
| `src/robustness/robustness_alt_control.py` | Alternative-control robustness script | VERIFIED | Runs successfully for EM Asia and EM ex-China. |
| `output/robustness/robustness_alt_control_em_asia.tex` | EM Asia alt-control table | VERIFIED | 825 bytes; non-empty LaTeX table. |
| `output/robustness/robustness_alt_control_em_exchina.tex` | EM ex-China alt-control table | VERIFIED | 830 bytes; non-empty LaTeX table. |

### Key Link Verification

| From | To | Via | Status | Details |
|---|---|---|---|---|
| `tests/test_phase4.py` | `config.py` | PROJECT_ROOT injection + `import config` | WIRED | Lines 12-20 inject project root and define output paths from config. |
| `tests/test_phase4.py` | `output/robustness/` | `ROBUSTNESS_DIR` assertions | WIRED | Tests assert on every Phase 4 robustness artifact. |
| `synthetic_control.py` | raw donor CSVs | `config.RAW_DIR / filename` | WIRED | Loads TOPIX plus STOXX600, FTSE100, MSCI_HK, MSCI_TAIWAN, SP500; validates `pb` non-null. |
| `synthetic_control.py` | `config.TSE_PB_REFORM_DATE` | reform marker in plots | WIRED | Actual reform date used in primary and in-time placebo plots. |
| `synthetic_control.py` | `output/robustness/`, `output/figures/` | `mkdir` + `to_csv`/`savefig` | WIRED | `main()` creates directories and writes all synthetic-control outputs. |
| `robustness_placebo.py` | `panel.parquet` + raw placebo CSVs | TOPIX baseline + Taiwan/Indonesia raw P/B | WIRED | Loads TOPIX from `config.PROCESSED_DIR / "panel.parquet"` and raw placebo files from `config.RAW_DIR`. |
| `robustness_placebo.py` | `output/robustness/` | `to_csv` + `savefig` | WIRED | CAR CSVs and combined falsification PDF regenerated. |
| `robustness_pe.py` | `panel.parquet` + GPR raw XLS | `read_parquet`, `dropna`, `read_excel` | WIRED | P/E panel, PanelOLS, event study, and GPR sub-analysis run from real local data. |
| `robustness_pe.py` | `output/robustness/` | `write_text` LaTeX outputs | WIRED | Writes event-study and PanelOLS P/E tables. |
| `robustness_alt_control.py` | `panel.parquet` + raw EM CSVs | base panel plus substituted benchmarks | WIRED | Loads base KOSPI/TOPIX/SP500 panel and raw EM Asia, EM, China P/B files. |
| `robustness_alt_control.py` | `output/robustness/` | variant-specific LaTeX writes | WIRED | Writes `robustness_alt_control_em_asia.tex` and `robustness_alt_control_em_exchina.tex`. |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
|---|---|---|---|---|
| `synthetic_control_weights.csv` | `weights_df`, `pre_rmspe` | Raw P/B CSVs -> `Dataprep` -> `Synth.fit()` -> `synth.weights()`/`synth.mspe()` | Yes | FLOWING |
| `figure_synth_gap.pdf` | `ts_gap` | `dataprep.make_outcome_mats()` -> `synth._gaps()` | Yes | FLOWING |
| `figure_placebo_intime.pdf` | `gap_it` | Same donor panel, fake 2019 treatment date, `Synth.fit()` | Yes | FLOWING |
| `figure_placebo_inspace.pdf` | `placebo_gaps` | Donor-as-treated loop over five donors with real panel data | Yes | FLOWING |
| `placebo_taiwan_car.csv` / `placebo_indonesia_car.csv` | `car_df` | Raw placebo market P/B + TOPIX from `panel.parquet` -> stacked event study | Yes | FLOWING |
| `robustness_pe_event_coefs.tex` | `car` | `panel.parquet` P/E after null drop -> stacked event-study CARs | Yes | FLOWING |
| `robustness_pe_ols.tex` | `results_df` | `panel.parquet` P/E -> two-way FE PanelOLS + wild bootstrap | Yes | FLOWING |
| `robustness_alt_control_*.tex` | `results_df` | `panel.parquet` base rows + real raw EM benchmark substitutions -> PanelOLS | Yes | FLOWING |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|---|---|---|---|
| Regenerate synthetic-control outputs | `python src/robustness/synthetic_control.py` | Exited 0; RMSPE `0.2893`; outputs saved | PASS |
| Regenerate placebo falsification outputs | `python src/robustness/robustness_placebo.py` | Exited 0; Taiwan and Indonesia CAR CSVs plus figure saved | PASS |
| Regenerate P/E robustness outputs | `python src/robustness/robustness_pe.py` | Exited 0; event-study and PanelOLS LaTeX saved; GPR logged | PASS |
| Regenerate alternative-control outputs | `python src/robustness/robustness_alt_control.py` | Exited 0; both LaTeX tables saved | PASS |
| Phase 4 test suite | `python -m pytest tests/test_phase4.py -q` | `8 passed in 0.40s` | PASS |
| Full project test suite | `python -m pytest tests/ -q` | `29 passed in 2.18s` | PASS |
| Placebo null evidence | Python read of CAR CSVs | Taiwan and Indonesia post-event CIs include zero for all `25/25` post rows | PASS |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|---|---|---|---|---|
| SYNTH-01 | 04-01, 04-02, 04-06 | Estimate ADH synthetic control for Japan 2023 TSE P/B reform | SATISFIED | `synthetic_control.py` runs with `pysyncon.Dataprep`/`Synth` and TOPIX treated unit. |
| SYNTH-02 | 04-01, 04-02, 04-06 | Report pre-treatment RMSPE, donor weights, and fit chart | SATISFIED | Weights CSV reports RMSPE `0.2892855456344879`, weights sum `1.0`, and `figure_synth_gap.pdf` exists. |
| SYNTH-03 | 04-01, 04-02, 04-06 | Document donor pool and SUTVA concerns | SATISFIED | SUTVA comment documents donor pool, KOSPI exclusion, and governance-contagion rationale. Stale India/Taiwan wording noted as warning. |
| ROBUST-01 | 04-01, 04-03, 04-06 | Placebo/falsification tests on non-reform markets | SATISFIED | Taiwan and Indonesia placebo event studies regenerate CAR CSVs; all post-event CIs include zero. |
| ROBUST-02 | 04-01, 04-04, 04-06 | Replicate primary results using P/E instead of P/B | SATISFIED | P/E event-study, PanelOLS, and GPR flows run from `panel.parquet`; required LaTeX outputs exist. |
| ROBUST-03 | 04-01, 04-05, 04-06 | Alternative control group robustness | SATISFIED | EM Asia and EM ex-China variants run and save LaTeX tables. |
| ROBUST-04 | 04-01, 04-02, 04-06 | In-time and in-space synthetic-control placebos | SATISFIED | In-time and in-space placebo figures regenerated and saved under `output/robustness/`. |

No orphaned Phase 4 requirements found. `.planning/REQUIREMENTS.md` maps exactly SYNTH-01, SYNTH-02, SYNTH-03, ROBUST-01, ROBUST-02, ROBUST-03, and ROBUST-04 to Phase 4, and all are claimed by Phase 4 plans.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|---|---:|---|---|---|
| `src/robustness/robustness_pe.py` | 630 | P/E GPR result is logged only | Warning | Advisory review risk: no machine-readable GPR robustness CSV. Not a blocker because 04-04 explicitly required no separate GPR table. |
| `src/robustness/synthetic_control.py` | 181, 248 | Placebo gap series are returned/plotted but not persisted as CSV | Warning | Auditability risk for ROBUST-04 underlying gaps; figures satisfy current plan/roadmap artifact contract. |
| `tests/test_phase4.py` | 23 | Tests can pass against stale outputs | Warning | Mitigated in this verification by regenerating all four scripts before running tests; worth strengthening later. |
| `tests/test_phase4.py` | 105 | Import isolation test only inspects `ast.ImportFrom` and only robustness prefixes | Info | Manual AST scan checked plain imports and `src.analysis` too; no current violation. |
| `src/robustness/synthetic_control.py` | 34 | SUTVA comment says India/Indonesia are used in ROBUST-01, but code uses Taiwan/Indonesia | Info | Documentation precision issue for Phase 5; does not invalidate the donor-pool SUTVA justification. |

Accumulator initializations such as `rows = []`, `cohorts = []`, and `placebo_gaps = {}` were scanned and are normal computation buffers, not stubs.

### Human Verification Required

None remaining. The plan's human checkpoint was answered `rmspe-high`; per the provided instruction and 04-06 summary, the high synthetic-control RMSPE is accepted as a paper-text caveat. Phase 5 should state that synthetic control is supportive robustness evidence with imperfect pre-treatment fit.

### Gaps Summary

No blocking gaps found. The phase goal is achieved. Residual risks are advisory and should be carried into Phase 5 prose/auditability work:

- Synthetic-control RMSPE is high (`0.2893`), accepted as a caveat rather than a failure.
- P/E robustness is mixed/volatile in interpretation, but the planned P/E replication was implemented and generated.
- Underlying ROBUST-04 placebo gap CSVs and P/E GPR CSV would improve downstream auditability but were not required by Phase 4's contract.

---

_Verified: 2026-04-21T00:11:14Z_  
_Verifier: Claude (gsd-verifier)_
