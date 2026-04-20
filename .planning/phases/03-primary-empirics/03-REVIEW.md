---
phase: 03-primary-empirics
reviewed: 2026-04-20T20:48:05Z
depth: standard
files_reviewed: 16
files_reviewed_list:
  - data/raw/MANIFEST.md
  - data/raw/data_gpr_export.xls
  - output/figures/figure2_event_study.pdf
  - output/figures/figure3_geo_risk.pdf
  - output/tables/event_study_car.csv
  - output/tables/geo_risk_results.csv
  - output/tables/panel_ols_results.csv
  - output/tables/table2_ols.tex
  - output/tables/table3_geo_risk.tex
  - output/tables/table_event_study_coefs.tex
  - requirements.txt
  - src/analysis/__init__.py
  - src/analysis/event_study.py
  - src/analysis/geo_risk.py
  - src/analysis/panel_ols.py
  - tests/test_phase3.py
findings:
  critical: 0
  warning: 2
  info: 1
  total: 3
status: issues_found
---

# Phase 3: Code Review Report

**Reviewed:** 2026-04-20T20:48:05Z
**Depth:** standard
**Files Reviewed:** 16
**Status:** issues_found

## Summary

Reviewed the Phase 3 empirics code, generated tables/figures, raw GPR workbook, dependency pins, and test coverage. The main risk is inference correctness: the event-study code writes HC3 standard-error columns, but every non-baseline event-study row in `output/tables/event_study_car.csv` has blank `hc3_se`, `t_stat`, and `p_value` values. The PanelOLS table also references wild-bootstrap p-values without actually displaying them.

## Warnings

### WR-01: Event-study HC3 inference is undefined for non-baseline event months

**File:** `src/analysis/event_study.py:198`
**Issue:** `estimate_event_study()` creates one dummy column for each cohort/event-month cell, then fits OLS with no pooled residual variation for those cells. With one observation per non-baseline dummy, the model exactly fits those rows and HC3 leverage reaches the undefined case, so `robust.bse`, `robust.tvalues`, and `robust.pvalues` become `NaN`. This is visible in the generated artifact: all 108 non-baseline rows in `output/tables/event_study_car.csv` have blank `hc3_se`, `t_stat`, and `p_value` values, while `table_event_study_coefs.tex` still labels them as HC3 results.
**Fix:** Either make the event-study table explicitly descriptive and remove the HC3/t-stat/p-value columns, or change the model so inference is estimable with residual degrees of freedom. For example, pool relative-time effects across cohorts and include cohort fixed effects:

```python
y = windowed["abnormal_spread"].astype(float)
rel = pd.Categorical(windowed["event_rel_time"], categories=expected_times)
rel_dummies = pd.get_dummies(rel, prefix="rel").drop(
    columns=[f"rel_{BASE_PERIOD}"]
)
cohort_fe = pd.get_dummies(windowed["cohort"], prefix="cohort", drop_first=True)
x = pd.concat([rel_dummies, cohort_fe], axis=1).astype(float)
x = sm.add_constant(x, has_constant="add")
robust = sm.OLS(y, x).fit().get_robustcov_results(cov_type="HC3")
```

If cohort-specific CARs must remain the primary output, compute them as descriptive series and do not present missing HC3 inference as estimated statistics.

### WR-02: PanelOLS table note advertises wild-bootstrap p-values that are not shown

**File:** `src/analysis/panel_ols.py:240`
**Issue:** `_format_table_cell()` formats each coefficient cell as only `coef (std_error)`, while `write_latex_table()` appends a note saying wild-bootstrap p-values use 999 Rademacher draws. The CSV contains `wild_p_value`, but the paper-ready LaTeX table omits those p-values entirely. This can mislead readers into thinking the displayed inference reflects the bootstrap values.
**Fix:** Include the wild p-value in each interaction cell, or remove/reword the note when the table intentionally omits p-values. One direct fix:

```python
wild_p = row.get("wild_p_value")
wild_suffix = "" if pd.isna(wild_p) else f"; wild p={float(wild_p):.3f}"
return f"{coef:.2f} ({std_error:.2f}{wild_suffix})"
```

## Info

### IN-01: Tests allow the event-study inference columns to be entirely blank

**File:** `tests/test_phase3.py:71`
**Issue:** `test_event_study_coefs()` only checks that the LaTeX output contains the strings `HC3` and `CAR`. It does not verify that the machine-readable event-study artifact contains non-null standard errors, t-statistics, or p-values. As a result, the current all-blank HC3 inference columns pass the test suite.
**Fix:** Add an assertion against `event_study_car.csv` that matches the intended contract. If HC3 inference is required:

```python
car = pd.read_csv(OUTPUT_TABLES / "event_study_car.csv")
non_base = car[car["event_rel_time"] != -1]
assert non_base[["hc3_se", "t_stat", "p_value"]].notna().all().all()
```

If the event study is intentionally descriptive, assert that the output/table no longer claims to provide HC3 inference.

---

_Reviewed: 2026-04-20T20:48:05Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
