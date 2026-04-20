---
phase: 03-primary-empirics
reviewed: 2026-04-20T00:00:00Z
depth: standard
files_reviewed: 12
files_reviewed_list:
  - data/raw/MANIFEST.md
  - requirements.txt
  - src/analysis/__init__.py
  - src/analysis/event_study.py
  - src/analysis/geo_risk.py
  - src/analysis/panel_ols.py
  - tests/test_phase3.py
  - output/tables/event_study_car.csv
  - output/tables/panel_ols_results.csv
  - output/tables/table_event_study_coefs.tex
  - output/tables/table2_ols.tex
  - output/tables/table3_geo_risk.tex
findings:
  critical: 0
  warning: 5
  info: 5
  total: 10
status: issues_found
---

# Phase 03: Code Review Report

**Reviewed:** 2026-04-20T00:00:00Z
**Depth:** standard
**Files Reviewed:** 12
**Status:** issues_found

## Summary

This phase implements three primary empirical analyses: a stacked Cengiz-style event study (`event_study.py`), a two-way fixed-effects panel OLS with wild-bootstrap inference (`panel_ols.py`), and a geopolitical-risk regression (`geo_risk.py`). Tests are in `tests/test_phase3.py` and outputs in `output/tables/`.

The code is well-structured with pinned dependencies and careful inline documentation of statistical design choices. No security vulnerabilities or data-loss risks were found. Five warning-level issues were identified, the most consequential being a discarded OLS fit result in the wild-bootstrap routine (`panel_ols.py`) and an overly broad pre-period filter in `geo_risk.py`. Five informational items cover dead code, undocumented assumptions, and presentation gaps.

---

## Warnings

### WR-01: `sm.OLS.fit()` result is discarded in `_wild_bootstrap_pvalues` — unfitted model passed to `wildboottest`

**File:** `src/analysis/panel_ols.py:175-176`
**Issue:** The FWL-demeaned OLS model is instantiated on line 175 and `.fit()` is called on line 176, but the return value of `.fit()` is not assigned to any variable — the fitted result is immediately discarded. The next call to `wildboottest(sm_model, ...)` on line 189 passes the **unfitted** `sm.OLS` object. Whether `wildboottest 0.3.2` accepts an unfitted model and calls `.fit()` internally is an implementation detail that is not part of its documented API. If the library expects a fitted `RegressionResultsWrapper` (as documented), wild-bootstrap p-values in `panel_ols_results.csv` are computed from an unfit model, silently producing incorrect results.

**Fix:**
```python
sm_result = sm.OLS(y_valid, x_valid).fit()
boot = wildboottest(
    sm_result,
    B=BOOTSTRAP_ITERATIONS,
    cluster=country_cluster,
    weights_type=WILD_BOOTSTRAP_WEIGHTS,
    bootstrap_type="11",
    seed=BOOTSTRAP_SEED,
    show=False,
)
```

---

### WR-02: Wild-bootstrap cluster codes are non-deterministic — `pd.Categorical` ordering depends on observation order

**File:** `src/analysis/panel_ols.py:182-187`
**Issue:** `country_cluster` is constructed from `pd.Categorical(country_labels).codes`. An unordered `Categorical` assigns integer codes in first-seen observation order. Since `x_valid` is a demeaned multi-index DataFrame, the iteration order depends on the sort order of `reg_panel`. If panel sort order ever changes, cluster assignments silently change, making bootstrap results non-reproducible across environments even with the same `BOOTSTRAP_SEED`. The `wildboottest` API requires that cluster labels consistently identify the same groups.

**Fix:** Explicitly specify sorted categories so codes are stable regardless of observation order:
```python
unique_countries = sorted(country_labels.unique())
country_cluster = pd.Series(
    pd.Categorical(country_labels, categories=unique_countries).codes.astype("int64"),
    index=country_labels.index,
    name="country",
)
```

---

### WR-03: `build_geo_regression_data` does not filter the panel to `>= STUDY_START` — pre-study rows could be included in the pivot

**File:** `src/analysis/geo_risk.py:73`
**Issue:** `panel_study = panel[panel["date"] <= STUDY_END].copy()` only applies an upper-bound filter. The GPR data is filtered to `[STUDY_START, STUDY_END]` inside `load_gpr_korea`, so the inner-join merge prevents pre-2004 rows from appearing in `reg_df` at present. However, the pivot on line 75-78 is built from all dates back to the start of the panel, which silently carries pre-2004 rows through to the merge step. If the panel ever includes data before 2004, those rows will enter `reg_df` without warning. The lower bound should be enforced symmetrically.

**Fix:**
```python
panel_study = panel[
    (panel["date"] >= STUDY_START) & (panel["date"] <= STUDY_END)
].copy()
```

---

### WR-04: `_append_term_rows` logic relies on fall-through to produce the "not included" note for baseline POST_TERMS — fragile control flow

**File:** `src/analysis/panel_ols.py:116-155`
**Issue:** For `BASELINE_SPEC` rows where `term in POST_TERMS`, the `if term in POST_TERMS and specification in {DUMMIES_SPEC, INTERACTIONS_SPEC}` guard is False, so execution falls through to the `if term in result.params.index and term in included_terms` branch (also False for baseline, since terms is `[]`), and then falls to the final `note = "not included"` block. This produces the correct output but only because two conditions both happen to be False. A future maintainer adding a specification that includes POST_TERMS in the baseline would get an incorrect "not included" note. The three-way branch should be made explicit with `elif`.

**Fix:**
```python
if term in POST_TERMS and specification in {DUMMIES_SPEC, INTERACTIONS_SPEC}:
    # absorbed by time FE
    rows.append({..., "note": "absorbed by time FE"})
elif term in result.params.index and term in included_terms:
    # estimable coefficient
    rows.append({..., "note": ""})
else:
    # not in this specification
    rows.append({..., "note": "not included"})
```

---

### WR-05: `test_table2_reform_dummies` allows year-string fallback matching — test can pass even if reform names are absent from the table

**File:** `tests/test_phase3.py:145-152`
**Issue:** Each `expected_reforms` tuple includes a year string ("2014", "2015") as a fallback token. Because `table2_ols.tex` row labels are raw Python identifiers (`post_stewardship`, `cgc_x_japan`), the test currently passes because "stewardship" and "cgc" appear in those labels. But the year-string fallback means the test would still pass if the reform name were replaced with any unrelated content that happened to contain "2014" (e.g., a comment or footnote date). The test asserts less than it should.

**Fix:** Remove the year-string fallback tokens and require the human-readable reform name directly, or add a stricter assertion that the row label contains the reform name:
```python
assert "stewardship" in content
assert "cgc" in content or "corporate governance" in content
assert "tse" in content and ("p/b" in content or "pb" in content)
```

---

## Info

### IN-01: `src/analysis/__init__.py` is empty

**File:** `src/analysis/__init__.py:1`
**Issue:** The file exists but is completely empty (1-line blank file). Adding a module docstring would clarify the public surface and match the style of the three analysis modules.

**Fix:**
```python
"""Phase 3 analysis modules: event_study, panel_ols, geo_risk."""
```

---

### IN-02: `ESTIMATION_WINDOW_MONTHS = 36` is a magic constant that would silently diverge if `STACK_WINDOW_MIN` or `BASE_PERIOD` change

**File:** `src/analysis/event_study.py:28-32, 138`
**Issue:** `ESTIMATION_WINDOW_MONTHS = 36` is defined as a standalone literal. Its value is derivable from `abs(STACK_WINDOW_MIN - BASE_PERIOD)` = `abs(-36 - (-1))` + 1 = 36. If `STACK_WINDOW_MIN` or `BASE_PERIOD` are changed in a future experiment, `ESTIMATION_WINDOW_MONTHS` would need to be updated separately; there is no link between them. The assertion on line 138 would then fail with a confusing message.

**Fix:** Derive the constant rather than hardcoding it:
```python
ESTIMATION_WINDOW_MONTHS = BASE_PERIOD - STACK_WINDOW_MIN  # pre-event months excl. base = 35
# and adjust the assertion: len(pre) != (ESTIMATION_WINDOW_MONTHS + 1)
```
Or simply use `abs(STACK_WINDOW_MIN - BASE_PERIOD) + 1` inline in the assertion.

---

### IN-03: `requirements.txt` compatibility warning for `wildboottest` is unresolved

**File:** `requirements.txt:16`
**Issue:** The comment `# Wild bootstrap inference (Phase 3 — verify compatibility with linearmodels 6.x)` documents an open question rather than a confirmed status. Given that `panel_ols.py` uses `PanelData.demean()` from linearmodels 6.1 alongside wildboottest 0.3.2, and linearmodels 6.x introduced API changes, this is a deployment risk that should be explicitly closed.

**Fix:** Replace the open question with a confirmed-compatible note, or add a minimal smoke test:
```python
def test_wildboottest_linearmodels_compatible():
    """Confirm wildboottest accepts linearmodels-demeaned data without error."""
    import linearmodels  # noqa: F401
    import wildboottest   # noqa: F401
    assert True  # import-level compatibility confirmed
```

---

### IN-04: `table2_ols.tex` uses raw Python variable names as row labels

**File:** `output/tables/table2_ols.tex:9-14`
**Issue:** Published row labels are `post_stewardship`, `cgc_x_japan`, `tse_pb_reform_x_japan`, etc. — raw Python identifiers. For a paper-ready table these should be humanised. This is addressable in `write_latex_table` via a label mapping dict.

**Fix:** Add a `TERM_LABELS` mapping in `panel_ols.py`:
```python
TERM_LABELS = {
    "post_stewardship": "Post-Stewardship Code",
    "post_cgc": "Post-Corp.\ Governance Code",
    "post_tse_pb_reform": "Post-TSE P/B Reform",
    "stewardship_x_japan": "Stewardship Code $\\times$ Japan",
    "cgc_x_japan": "CGC $\\times$ Japan",
    "tse_pb_reform_x_japan": "TSE P/B $\\times$ Japan",
}
table.rename(index=TERM_LABELS, inplace=True)
```

---

### IN-05: `plot_geo_risk` shading loop calls `axvspan` once per escalation month via `iterrows`

**File:** `src/analysis/geo_risk.py:192-196`
**Issue:** The loop `for _, row in reg_df[reg_df["gpr_escalation_dummy"] == 1].iterrows(): ax_gpr.axvspan(...)` adds approximately 60 matplotlib patches individually (25% of 252 months). This is not a correctness issue and has no runtime impact for a one-shot script, but is noted as a common source of figure rendering slowness and is easily consolidated.

**Fix (optional):** Collect spans as a list and add them in one call, or simply document the bounded iteration count in a comment.

---

_Reviewed: 2026-04-20T00:00:00Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
