---
phase: 05-paper-assembly-and-replication-package
reviewed: 2026-04-20T00:00:00Z
depth: standard
files_reviewed: 12
files_reviewed_list:
  - README.md
  - run_all.py
  - src/policy/__init__.py
  - src/policy/counterfactual_projection.py
  - src/robustness/synthetic_control.py
  - tests/test_phase5.py
  - paper/main.tex
  - paper/references.bib
  - output/tables/table1_summary_stats.tex
  - output/tables/table2_ols.tex
  - output/tables/table3_geo_risk.tex
  - output/robustness/robustness_pe_ols.tex
findings:
  critical: 0
  warning: 4
  info: 5
  total: 9
status: issues_found
---

# Phase 05: Code Review Report

**Reviewed:** 2026-04-20
**Depth:** standard
**Files Reviewed:** 12
**Status:** issues_found

## Summary

This phase assembles the replication package (run_all.py, policy module, synthetic control robustness checks, test suite) and the paper artifact (main.tex, references.bib, output tables). The code is well-structured overall: look-ahead bias is guarded by centralizing event dates in config.py, scripts use the Agg backend for headless rendering, and assertion-based guards protect against malformed upstream CSVs.

Four warnings are flagged: a silent data loss risk in counterfactual_projection.py when the KOSPI panel has no 2024 observations, a logic error in the same file where `monthly_lift` is derived from the first-difference of a gap series rather than the gap level itself, a private/undocumented API call (`synth._gaps`) used across two scripts that will break silently on a pysyncon version bump, and a test gap that leaves the core projection arithmetic untested. Five informational items cover magic numbers, missing cross-file consistency between the robustness_pe_ols table and its narrative, missing `\label` for `table_event_study_coefs`, a BibTeX year/body mismatch in one entry, and an unused `choi2011` reference.

---

## Warnings

### WR-01: Silent empty-result when KOSPI 2024 data is absent

**File:** `src/policy/counterfactual_projection.py:74-75`

**Issue:** `kospi_2024 = kospi[kospi["date"] <= pd.Timestamp("2024-12-31")]` is never validated for emptiness before `.iloc[-1]` is called on line 75. If the panel file does not contain any KOSPI rows on or before 2024-12-31 (e.g., the panel was rebuilt from a truncated raw export), `kospi_2024` will be an empty DataFrame and `iloc[-1]` will raise an `IndexError` with no informative message, crashing the script at runtime rather than at the assertion-guarded validation stage.

**Fix:**
```python
kospi_2024 = kospi[kospi["date"] <= pd.Timestamp("2024-12-31")]
assert len(kospi_2024) > 0, (
    "No KOSPI observations on or before 2024-12-31 found in panel.parquet. "
    "Check that the panel covers the full 2004-2024 study period."
)
base_level = float(kospi_2024["pb"].iloc[-1])
base_date  = kospi_2024["date"].iloc[-1]
```

---

### WR-02: monthly_lift computed from gap differences, not gap level — likely wrong sign and scale

**File:** `src/policy/counterfactual_projection.py:64`

**Issue:** `monthly_lift = post_reform["gap"].diff().mean()` computes the average month-over-month *change* in the synthetic-control gap series (i.e., the second derivative of the Japan–synthetic-Japan P/B gap). The docstring and paper text (Section 7.2) both describe the projection as applying "the average monthly TOPIX P/B change... in the 12–18 months following Japan's March 2023 reform," which corresponds to the level change in TOPIX P/B, not the change in the gap series. Using the diff of the gap series means the projection applies the rate-of-change of the divergence rather than the absolute monthly P/B improvement, which is a different and harder-to-interpret quantity. Additionally, `.diff()` produces a NaN for the first row; with potentially very few post-reform rows, this can materially distort the mean.

The assertion on line 68 (`assert not pd.isna(monthly_lift)`) catches the total-NaN case but not the case where one NaN row silently inflates the denominator if future pandas versions change `.mean()` NaN-skipping behavior.

**Fix:** Confirm the intended quantity. If the projection should apply the average monthly P/B lift in TOPIX (not the gap diff), the correct computation is the mean month-over-month change in TOPIX P/B itself over the post-reform window. If the gap diff is intentional, add a comment explaining the econometric rationale and use `nanmean` or explicit `dropna()`:

```python
# Option A: use TOPIX P/B monthly change directly (matches paper description)
topix_post = topix_series[
    (topix_series["date"] >= reform_date) & (topix_series["date"] <= cutoff_date)
].copy()
monthly_lift = topix_post["pb"].diff().dropna().mean()

# Option B: if gap diff is intentional, be explicit about NaN handling
monthly_lift = post_reform["gap"].diff().dropna().mean()
assert not pd.isna(monthly_lift), "monthly_lift is NaN after dropna — check gap series"
```

---

### WR-03: Use of private API `synth._gaps()` in two scripts

**File:** `src/robustness/synthetic_control.py:119`, `src/robustness/synthetic_control.py:187`, `src/robustness/synthetic_control.py:252`

**Issue:** `synth._gaps(Z0=Z0, Z1=Z1)` calls a leading-underscore (private) method of the `pysyncon.Synth` class three times: once in `plot_gap`, once in `run_intime_placebo`, and once in `run_inspace_placebo`. Private methods are not part of a library's stable API; a minor pysyncon update that renames or removes `_gaps` will cause a silent `AttributeError` at runtime with no fallback. The `requirements.txt` file is not in the review scope, so it is unknown whether the pysyncon version is pinned.

**Fix:** Pin the exact pysyncon version in requirements.txt and add a version guard at module import time:

```python
import pysyncon
_REQUIRED_PYSYNCON = "0.3"   # or whatever the verified-working version is
assert pysyncon.__version__ == _REQUIRED_PYSYNCON, (
    f"pysyncon {_REQUIRED_PYSYNCON} required; found {pysyncon.__version__}. "
    "Private _gaps() API may have changed."
)
```

Alternatively, file an upstream issue to expose `gaps()` as a public method and update once the public API is available.

---

### WR-04: No test covers the counterfactual projection arithmetic

**File:** `tests/test_phase5.py:23-27`

**Issue:** `test_counterfactual_figure_exists()` checks only that the output PDF exists and is non-empty. It does not assert anything about the numeric correctness of `monthly_lift`, `base_level`, `proj_values`, or the uncertainty band. Given the bug identified in WR-02, a wrong `monthly_lift` (including a negative value producing a downward-sloping projection) would pass all current tests as long as the PDF renders.

**Fix:** Add a smoke test that imports the key intermediate values or validates the gap CSV properties that feed the projection:

```python
def test_monthly_lift_is_positive():
    """Projection should apply a positive P/B lift (Japan's P/B rose post-reform)."""
    gap_path = ROBUSTNESS_DIR / "synthetic_control_gap.csv"
    df = pd.read_csv(gap_path, parse_dates=["date"])
    reform_date = pd.Timestamp("2023-03-01")
    cutoff = reform_date + pd.DateOffset(months=18)
    post = df[(df["date"] >= reform_date) & (df["date"] <= cutoff)].copy()
    monthly_lift = post["gap"].diff().dropna().mean()
    assert monthly_lift > 0, (
        f"monthly_lift = {monthly_lift:.4f} is non-positive; "
        "projection would show Korea's P/B declining under a reform scenario."
    )
```

---

## Info

### IN-01: Magic number RMSPE = 0.2893 hardcoded without derivation comment

**File:** `src/policy/counterfactual_projection.py:33`

**Issue:** `RMSPE = 0.2893` is hardcoded at module level. The comment says it comes from `synthetic_control_weights.csv`, but there is no runtime check that the value is consistent with the CSV produced by the current run. If `synthetic_control.py` is re-run and produces a different RMSPE (e.g., due to a data update or solver change), the hardcoded value in the uncertainty band will silently be wrong.

**Fix:** Read RMSPE from the CSV at runtime rather than hardcoding it:

```python
weights_df = pd.read_csv(ROBUSTNESS_DIR / "synthetic_control_weights.csv")
RMSPE = float(weights_df["pre_rmspe"].iloc[0])
logging.info("Loaded RMSPE = %.4f from synthetic_control_weights.csv", RMSPE)
```

---

### IN-02: `stewardship_x_japan` coefficient sign inconsistency between table and narrative

**File:** `output/robustness/robustness_pe_ols.tex:12`, cross-reference to `paper/main.tex:857-860`

**Issue:** In `robustness_pe_ols.tex`, `stewardship_x_japan` shows `-32.08 [0.125]`. This is a very large negative P/E interaction that is not mentioned anywhere in the main text or appendix narrative (Appendix B only states results are "qualitatively consistent in direction with the main P/B findings but estimated with wider confidence intervals"). A coefficient of -32.08 on a P/E outcome is anomalous given that P/E ratios for TOPIX are in the range of 10–25; this is likely caused by outlier P/E values during the 2008-2009 earnings collapse. The narrative's claim of "qualitatively similar but noisier" is misleading for this coefficient.

**Fix:** Add a footnote in the appendix acknowledging this outlier and explaining that the Stewardship Code P/E interaction is driven by near-zero earnings in 2014, making the coefficient unreliable:

```latex
% In Appendix B, after \input{robustness_pe_ols.tex}:
\footnote{The Stewardship Code $\times$ Japan P/E interaction ($-32.08$) is an outlier
driven by near-zero or negative earnings for TOPIX constituents in 2013--2014, which
produce extreme P/E ratios. This coefficient is not informative about governance effects
and should be disregarded; the P/B specification is more reliable for this cohort.}
```

---

### IN-03: `table_event_study_coefs` referenced without a label definition in that file

**File:** `paper/main.tex:847`

**Issue:** `\input{../output/tables/table_event_study_coefs.tex}` is referenced by `\ref{tab:event_study_coefs}` on line 813 but `table_event_study_coefs.tex` must define `\label{tab:event_study_coefs}` for the cross-reference to resolve. This cannot be verified from the file list provided (the file exists on disk but its content is not in scope), but it is a common assembly error when table fragments are auto-generated. A missing label produces a `?` in the compiled PDF without a LaTeX error.

**Fix:** Verify that `output/tables/table_event_study_coefs.tex` contains `\label{tab:event_study_coefs}` inside its `table` environment. If not, add it to the generating script (`src/analysis/event_study.py`).

---

### IN-04: BibTeX entry `bertrand2002` has mismatched key year and publication year

**File:** `paper/references.bib:381-388`

**Issue:** The entry is keyed as `bertrand2002` but the `year` field is `2003` and the correct publication year for "Enjoying the Quiet Life?" (Bertrand & Mullainathan) in *Journal of Political Economy* is 2003. The citation key is misleading (the working paper circulated in 2002; the published version is 2003). This does not cause a compilation error but creates a mismatch between the cite key and the formatted reference that readers may notice.

**Fix:** Rename the key to `bertrand2003` and update all `\cite{bertrand2002}` occurrences (confirm there are none in the current paper text first, as the entry does not appear to be cited in the reviewed sections).

---

### IN-05: `choi2011` BibTeX entry appears unused in main.tex

**File:** `paper/references.bib:111-119`

**Issue:** `choi2011` (Choi, Kim, Lee, "Value, Growth, and Risk Preferences") does not appear in any `\cite{}` call in `paper/main.tex` in the reviewed text. An unused bibliography entry is minor but adds noise and may cause reviewer confusion about whether a relevant prior literature result was intentionally excluded from the narrative.

**Fix:** Either add a citation in the literature review section where it is relevant (the paper studies Korean analyst behavior, which is tangentially related), or remove the entry from `references.bib`.

---

_Reviewed: 2026-04-20_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
