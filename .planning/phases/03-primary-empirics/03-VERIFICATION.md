---
phase: 03-primary-empirics
verified: 2026-04-20T21:30:00Z
status: human_needed
score: 24/24 must-haves verified
overrides_applied: 0
re_verification:
  previous_status: gaps_found
  previous_score: 21/24
  gaps_closed:
    - "HC3 hollow inference claim removed from event-study script, CSV, and LaTeX table; output relabeled as descriptive CARs"
    - "Wild-bootstrap p-values now displayed in Table 2 cells for all three reform x Japan interaction terms"
  gaps_remaining: []
  regressions: []
human_verification:
  - test: "Open output/figures/figure2_event_study.pdf and inspect the three-panel event-study CAR figure"
    expected: "Three vertically stacked subplots (Stewardship Code 2014, CGC 2015, TSE P/B reform 2023), each showing a CAR path from month -12 to +24, vertical line at x=0, horizontal line at y=0, labeled axes, and readable cohort titles"
    why_human: "Figure layout, axis readability, legend clarity, and suitability for paper inclusion cannot be verified programmatically"
  - test: "Open output/figures/figure3_geo_risk.pdf and inspect the geopolitical risk overlay figure"
    expected: "Two-axis figure covering 2004-2024 with GPRC_KOR on left axis and KOSPI P/B / TOPIX P/B on right axis, shaded grey spans for escalation months, and the title 'Figure 3: Korea Geopolitical Risk and Valuation, 2004-2024'"
    why_human: "Visual quality, axis scaling, and shading readability cannot be verified programmatically"
---

# Phase 3: Primary Empirics Verification Report

**Phase Goal:** Event study, panel OLS, and geopolitical risk sub-analysis are fully estimated — results tables and figures exist and are ready for inclusion in the paper
**Verified:** 2026-04-20T21:30:00Z
**Status:** human_needed
**Re-verification:** Yes — after gap closure by Plan 03-06

## Re-verification Summary

Previous verification (2026-04-20T20:53:54Z) found two gaps:

1. EVNT-02: HC3 inference was hollow — the saturated event-study design produced null SE/t/p for all 108 non-baseline rows, but the table still claimed HC3.
2. OLS-03: Table 2 advertised wild-bootstrap p-values in its note but displayed only conventional SEs in the cells.

Plan 03-06 closed both gaps. This re-verification confirms both closures and performs a full check of all 24 must-haves.

## Goal Achievement

All automated gates pass. The phase goal is achieved on the code side. Two figures require human visual sign-off before the outputs are confirmed paper-ready.

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | Roadmap SC1: stacked event study estimates CARs for three Japan reform dates with heteroskedasticity-robust (or appropriately documented) standard errors | VERIFIED | `event_study_car.csv` has 111 rows across three cohorts, columns `{cohort, event_label, event_rel_time, coefficient, car}` only; `table_event_study_coefs.tex` caption reads "descriptive CAR estimates (no inference reported)" — HC3 claim removed; saturated-design justification documented in comment. |
| 2 | Roadmap SC2: PanelOLS estimates reform interactions and Table 2 presents country-clustered/wild-bootstrap inference | VERIFIED | `panel_ols.py` computes wild-bootstrap p-values for all three interaction terms (0.750, 0.375, 0.500); Table 2 cells show `0.09 [0.750]`, `-0.32 [0.375]`, `-0.24 [0.500]`; table note accurately describes bracketed values. |
| 3 | Roadmap SC3: GPR escalation indicator and KOSPI valuation response estimated with caveats | VERIFIED | `geo_risk.py` loads GPRC_KOR, computes 75th percentile threshold (0.37), escalation share 25%, estimates `kospi_pb ~ gpr_escalation_dummy + topix_pb + C(year)`, writes caveat to `table3_geo_risk.tex` and `geo_risk_results.csv`. |
| 4 | Roadmap SC4: analyses read canonical local inputs and analysis modules do not import one another | VERIFIED | All scripts read `config.PROCESSED_DIR / "panel.parquet"`; geo-risk also reads local `config.RAW_DIR / GPR_FILENAME`; isolation pytest passed. |
| 5 | Phase 3 tests are discoverable before implementation begins | VERIFIED | 14 tests collected and passing: `pytest tests/test_phase3.py -x -q` passes. |
| 6 | GPR source file exists locally and is documented | VERIFIED | `data/raw/data_gpr_export.xls` present; `data/raw/MANIFEST.md` contains exact Caldara-Iacoviello source URL. |
| 7 | `requirements.txt` pins `xlrd==2.0.1` | VERIFIED | Pin present; workbook read confirmed through geo-risk script execution. |
| 8 | `src/analysis` exists as a package | VERIFIED | `src/analysis/__init__.py` exists. |
| 9 | `python src/analysis/event_study.py` produces Figure 2 and event-study tables from `panel.parquet` | VERIFIED | Script exits 0; saves `figure2_event_study.pdf`, `event_study_car.csv`, and `table_event_study_coefs.tex`. |
| 10 | Event study uses reform dates from `config.py` and avoids hardcoded date literals | VERIFIED | `event_study.py` references `config.EVENT_DATES` and `config.EVENT_LABELS`. |
| 11 | Event-study windows and abnormal valuation construction are implemented | VERIFIED | `build_stacked_dataset()` returns three cohorts with -36..+24 rows, 36 pre-event months per cohort, and overlap annotations. |
| 12 | Stacked design preserves full windows, flags overlap, and documents saturated inference | VERIFIED | Window preservation and overlap flags verified; HC3 was removed and design saturation documented with comment referencing Cengiz et al. (2019). |
| 13 | `python src/analysis/panel_ols.py` estimates PanelOLS models with country and time fixed effects | VERIFIED | Script exits 0; source uses `PanelOLS(..., entity_effects=True, time_effects=True)`. |
| 14 | Panel OLS includes reform dummies interacted with Japan indicator | VERIFIED | Source constructs `stewardship_x_japan`, `cgc_x_japan`, `tse_pb_reform_x_japan`; CSV reports coefficients. |
| 15 | Wild-bootstrap inference is clustered by country with 999 Rademacher draws | VERIFIED | Source calls `wildboottest` with country cluster; CSV has three non-null wild p-values. |
| 16 | Table 2 displays wild-bootstrap p-values in brackets for interaction terms | VERIFIED | `table2_ols.tex` contains `0.09 [0.750]`, `-0.32 [0.375]`, `-0.24 [0.500]`; three bracket cells confirmed by regex. |
| 17 | `python src/analysis/geo_risk.py` constructs Korea GPR escalation dummy from 2004-2024 `GPRC_KOR` | VERIFIED | Script exits 0; threshold 0.37, share 0.250, N=252. |
| 18 | GPR escalation dummy equals 1 above the 75th percentile over 2004-2024 | VERIFIED | Source filters to STUDY_START/STUDY_END before `quantile(0.75)` and uses `>` threshold. |
| 19 | Geo-risk regression estimates KOSPI P/B on escalation dummy, year FE, and TOPIX P/B | VERIFIED | Formula `kospi_pb ~ gpr_escalation_dummy + topix_pb + C(year)` confirmed in source. |
| 20 | Geo-risk outputs include Figure 3 and caveated result artifacts | VERIFIED | `figure3_geo_risk.pdf`, `table3_geo_risk.tex`, `geo_risk_results.csv` all exist and non-empty; caveat text confirmed in `table3_geo_risk.tex`. |
| 21 | All Phase 3 scripts run from a clean command line without importing one another | VERIFIED | No cross-imports found; `pytest tests/test_phase3.py::test_analysis_modules_do_not_import_each_other` passed. |
| 22 | `pytest tests/test_phase3.py -x -q` passes after outputs exist | VERIFIED | 14 passed. |
| 23 | `pytest tests/ -x -q` passes after Phase 3 outputs are generated | VERIFIED | 21 passed. |
| 24 | All required Phase 3 paper artifacts exist under `output/figures` and `output/tables` | VERIFIED | Figure 2, Figure 3, Table 2, event-study coefficient table, Table 3, geo-risk CSV, and OLS CSV all non-empty. |

**Score:** 24/24 truths verified

### Deferred Items

| # | Item | Addressed In | Evidence |
|---|------|--------------|----------|
| 1 | GEO-03 final integration into the paper's causal mechanism section | Phase 5 | Phase 5 goal covers a complete LaTeX paper integrating generated figures and tables; PAPER-06 covers causal mechanism prose. |

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `tests/test_phase3.py` | Phase 3 Nyquist tests | VERIFIED | 14 collected/passing tests including new inference-presentation assertions. |
| `data/raw/data_gpr_export.xls` | Caldara-Iacoviello GPR workbook | VERIFIED | Present; readable via xlrd. |
| `data/raw/MANIFEST.md` | Raw-data provenance | VERIFIED | Contains `data_gpr_export.xls` and exact Caldara-Iacoviello source URL. |
| `requirements.txt` | `xlrd==2.0.1` pin | VERIFIED | Pin present. |
| `src/analysis/__init__.py` | Package marker | VERIFIED | Present. |
| `src/analysis/event_study.py` | Standalone event-study script | VERIFIED | HC3 removed; output relabeled as descriptive CARs; plain OLS used. |
| `output/figures/figure2_event_study.pdf` | Three-panel event-study figure | VERIFIED | Non-empty PDF. Requires human visual sign-off. |
| `output/tables/event_study_car.csv` | CAR output without hollow inference | VERIFIED | Columns `{cohort, event_label, event_rel_time, coefficient, car}` only — no hc3_se/t_stat/p_value. |
| `output/tables/table_event_study_coefs.tex` | Descriptive CAR table | VERIFIED | HC3 absent; caption says "descriptive CAR estimates (no inference reported)"; CAR column present. |
| `src/analysis/panel_ols.py` | Standalone PanelOLS script | VERIFIED | Wild-bootstrap p-values displayed in Table 2 for interaction terms. |
| `output/tables/panel_ols_results.csv` | Machine-readable PanelOLS output | VERIFIED | Contains reform-interaction coefficients and non-null wild p-values. |
| `output/tables/table2_ols.tex` | Panel OLS paper table with wild-p | VERIFIED | Three bracket cells `coef [wild_p]` for interaction terms; accurate note; old misleading note absent. |
| `src/analysis/geo_risk.py` | Standalone geo-risk script | VERIFIED | Substantive and wired. |
| `output/figures/figure3_geo_risk.pdf` | Geo-risk figure | VERIFIED | Non-empty PDF. Requires human visual sign-off. |
| `output/tables/table3_geo_risk.tex` | Geo-risk regression table | VERIFIED | Booktabs rules and partial-identification caveat confirmed. |
| `output/tables/geo_risk_results.csv` | Geo-risk machine-readable output | VERIFIED | Contains threshold, escalation coefficient, TOPIX control, and caveat note. |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `tests/test_phase3.py` | `config.OUTPUT_DIR` | Output constants | WIRED | Derives figures/tables from `config.OUTPUT_DIR`. |
| `tests/test_phase3.py` | GPR raw file | `GPR_PATH = config.RAW_DIR / "data_gpr_export.xls"` | WIRED | Uses local raw-data path. |
| `data/raw/MANIFEST.md` | Caldara-Iacoviello source | Source URL row | WIRED | Contains exact source URL. |
| `src/analysis/event_study.py` | `config.EVENT_DATES` | Event loop and cohort labels | WIRED | References `config.EVENT_DATES` and `config.EVENT_LABELS`. |
| `src/analysis/event_study.py` | `data/processed/panel.parquet` | `pd.read_parquet` | WIRED | Reads canonical panel. |
| `src/analysis/event_study.py` | descriptive CARs output | `ols_result = sm.OLS(y, x).fit()` | WIRED | HC3 removed; plain OLS coefficients flow to CSV and LaTeX. |
| `src/analysis/panel_ols.py` | `linearmodels.PanelOLS` | Two-way FE model | WIRED | `entity_effects=True, time_effects=True`. |
| `src/analysis/panel_ols.py` | wild bootstrap p-values in Table 2 | `_format_table_cell` + `INTERACTIONS_SPEC` branch | WIRED | Interaction terms formatted as `coef [wild_p]` in table cells. |
| `src/analysis/panel_ols.py` | Table 2 output | `output_path.write_text` | WIRED | Writes `table2_ols.tex` with correct inference display. |
| `src/analysis/geo_risk.py` | GPR workbook | `pd.read_excel(config.RAW_DIR / GPR_FILENAME, engine="xlrd")` | WIRED | Reads fixed local workbook. |
| `src/analysis/geo_risk.py` | `data/processed/panel.parquet` | `pd.read_parquet` | WIRED | Reads canonical panel. |
| `src/analysis/geo_risk.py` | partial-identification caveat | LaTeX and CSV notes | WIRED | Caveat confirmed in `table3_geo_risk.tex` and `geo_risk_results.csv`. |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
|----------|---------------|--------|--------------------|--------|
| `event_study.py` | `panel`, `stacked`, `car` | `data/processed/panel.parquet` via `pd.read_parquet` | Yes — 111 CAR rows for three cohorts | VERIFIED |
| `event_study_car.csv` | `coefficient`, `car` | Plain OLS on stacked panel | Yes — no hollow inference columns remain | VERIFIED |
| `panel_ols.py` | `results_df`, `wild_p_value` in table cells | `panel.parquet`, PanelOLS, wildboottest | Yes — 3 bracket cells in Table 2 | VERIFIED |
| `geo_risk.py` | `gpr_escalation_dummy`, `reg_df`, HC3 result | Local GPR workbook + `panel.parquet` | Yes | VERIFIED |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Phase 3 tests | `pytest tests/test_phase3.py -x -q` | 14 passed | PASS |
| Full test suite | `pytest tests/ -x -q` | 21 passed | PASS |
| Analysis module isolation | `pytest tests/test_phase3.py::test_analysis_modules_do_not_import_each_other -x -q` | 1 passed | PASS |
| Event-study CSV columns | `pd.read_csv(...).columns` | `{cohort, event_label, event_rel_time, coefficient, car}` — no inference columns | PASS |
| HC3 absent from event study table | `grep -q "HC3" table_event_study_coefs.tex` | Exit non-zero | PASS |
| Wild-p brackets in Table 2 | `re.findall(r'-?\d+\.\d{2} \[\d+\.\d{3}\]', table2_ols.tex)` | 3 cells: `0.09 [0.750]`, `-0.32 [0.375]`, `-0.24 [0.500]` | PASS |
| Old misleading Table 2 note absent | grep for old note string | Absent | PASS |
| New accurate Table 2 note present | grep for "bracketed values are" | Present | PASS |
| All output files non-empty | `test -s` for 8 output files | All 8 pass | PASS |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|-------------|--------|----------|
| EVNT-01 | 03-01, 03-02, 03-05 | Run event study around three Japan reform dates | SATISFIED | Script produces three cohorts for 2014, 2015, and 2023. |
| EVNT-02 | 03-01, 03-02, 03-06 | Event study uses heteroskedasticity-robust standard errors (or appropriate documented alternative) | SATISFIED | HC3 removed because saturated cohort x relative-time design makes sandwich estimates undefined; output relabeled as descriptive CARs with rationale documented; this is the methodologically correct resolution. |
| EVNT-03 | 03-01, 03-02, 03-05 | Stacked event-study design across treatment dates | SATISFIED | `build_stacked_dataset()` returns three -36..+24 cohorts with overlap annotations citing Cengiz et al. (2019). |
| EVNT-04 | 03-01, 03-02, 03-05 | CAR figures and coefficient tables for paper inclusion | SATISFIED | Figure 2 (PDF) and `table_event_study_coefs.tex` exist; table labels clearly as descriptive CARs. |
| OLS-01 | 03-01, 03-03, 03-05 | Two-way country + time FE using `linearmodels.PanelOLS` | SATISFIED | Source imports and uses PanelOLS with entity/time effects. |
| OLS-02 | 03-01, 03-03, 03-05 | Reform dummies interacted with Japan indicator | SATISFIED | Three interaction terms constructed; CSV reports coefficients. |
| OLS-03 | 03-01, 03-03, 03-06 | Standard errors clustered by country; regression table presented | SATISFIED | Wild-bootstrap p-values (clustered by country) now displayed inline in Table 2 for all three interaction terms. |
| GEO-01 | 03-01, 03-04, 03-05 | Construct North Korea escalation indicator from GPR | SATISFIED | GPRC_KOR loaded from local workbook; 75th percentile dummy constructed. |
| GEO-02 | 03-01, 03-04, 03-05 | Estimate KOSPI valuation response to escalation events | SATISFIED | HC3 geo-risk regression output in CSV and LaTeX. |
| GEO-03 | 03-01, 03-04, 03-05 | Results integrated with caveats about partial identification | SATISFIED FOR PHASE 3 / PAPER INTEGRATION DEFERRED | Caveat text present in table and CSV; narrative integration deferred to Phase 5. |

### Anti-Patterns Found

No new blockers or warnings. Previous blockers from the initial verification have been resolved:

- `event_study.py`: HC3 suppress-warning pattern removed; plain OLS used with documented rationale.
- `event_study_car.csv`: Hollow inference columns removed.
- `panel_ols.py`: `_format_table_cell` now branches on interaction terms to display `coef [wild_p]`.
- `table2_ols.tex`: Displays wild-bootstrap p-values in cells for interaction terms; note accurately describes bracketed values.

### Human Verification Required

#### 1. Figure 2 Visual Quality

**Test:** Open `output/figures/figure2_event_study.pdf` and review the three-panel event-study CAR figure.
**Expected:** Three vertically stacked subplots (one per reform event: Stewardship Code 2014, CGC 2015, TSE P/B reform 2023), each showing a CAR path from month -12 to +24, a vertical dashed line at x=0, a horizontal line at y=0, labeled axes ("Months relative to reform" and "CAR: KOSPI - TOPIX P/B"), and readable panel titles.
**Why human:** Figure layout, axis readability, legend clarity, and suitability for paper inclusion cannot be verified programmatically.

#### 2. Figure 3 Visual Quality

**Test:** Open `output/figures/figure3_geo_risk.pdf` and review the geopolitical risk and valuation overlay figure.
**Expected:** Two-axis figure covering 2004-2024 with GPRC_KOR on the left y-axis and KOSPI P/B / TOPIX P/B on the right y-axis, light grey vertical spans for escalation months where `gpr_escalation_dummy == 1`, and the title "Figure 3: Korea Geopolitical Risk and Valuation, 2004-2024".
**Why human:** Visual quality, axis scaling, shading readability, and suitability for paper inclusion cannot be verified programmatically.

### Gaps Summary

No automated gaps remain. Both gaps from the initial verification were closed by Plan 03-06:

1. EVNT-02 closed: event-study HC3 removed; output correctly labeled as descriptive CARs; plain OLS used; saturation documented.
2. OLS-03 closed: Table 2 now displays wild-bootstrap p-values in brackets for all three reform x Japan interaction terms.

Phase goal is achieved subject to human sign-off on figure visual quality.

---

_Verified: 2026-04-20T21:30:00Z_
_Verifier: Claude (gsd-verifier)_
