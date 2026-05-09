---
phase: 04-synthetic-control-and-robustness
reviewed: 2026-04-21T00:06:09Z
depth: standard
files_reviewed: 7
files_reviewed_list:
  - requirements.txt
  - tests/test_phase4.py
  - src/robustness/__init__.py
  - src/robustness/synthetic_control.py
  - src/robustness/robustness_placebo.py
  - src/robustness/robustness_pe.py
  - src/robustness/robustness_alt_control.py
findings:
  critical: 0
  warning: 3
  info: 2
  total: 5
status: issues_found
---

# Phase 04: Code Review Report

**Reviewed:** 2026-04-21T00:06:09Z
**Depth:** standard
**Files Reviewed:** 7
**Status:** issues_found

## Summary

Reviewed the Phase 4 robustness modules, dependency pin, and smoke tests at standard depth. No critical security issues were found. The main risks are incomplete machine-readable outputs for robustness analyses and tests that can pass against stale generated artifacts even when the scripts regress.

## Warnings

### WR-01: P/E GPR Robustness Result Is Only Logged

**File:** `src/robustness/robustness_pe.py:630`
**Issue:** `run_pe_geo_risk()` performs the P/E GPR sub-analysis, but lines 638-650 only log the threshold, coefficients, and p-values. The module docstring promises a full Phase 3 P/E replication with outputs under `output/robustness/`, so this result is lost unless stdout logs are preserved.
**Fix:**
```python
def run_pe_geo_risk(panel_pe: pd.DataFrame) -> pd.DataFrame:
    """Run the Phase 3 GPR sub-analysis with P/E and persist the key coefficients."""
    gpr, threshold = load_gpr_korea()
    reg_df = build_geo_regression_data(panel_pe, gpr)
    result = estimate_geo_model(reg_df)
    names = result.model.exog_names

    rows = []
    for term in ("gpr_escalation_dummy", "topix_pe"):
        idx = names.index(term)
        rows.append(
            {
                "term": term,
                "estimate": float(result.params[idx]),
                "std_error": float(result.bse[idx]),
                "p_value": float(result.pvalues[idx]),
                "threshold": threshold if term == "gpr_escalation_dummy" else pd.NA,
                "nobs": len(reg_df),
            }
        )

    out = pd.DataFrame(rows)
    out.to_csv(ROBUSTNESS_DIR / "robustness_pe_gpr_results.csv", index=False)
    return out
```

### WR-02: Synthetic Placebo Gap Series Are Not Persisted

**File:** `src/robustness/synthetic_control.py:181`
**Issue:** `run_intime_placebo()` and `run_inspace_placebo()` compute gap series and save PDF figures, but neither writes the underlying placebo gaps to CSV. That makes the ROBUST-04 evidence hard to audit or reuse downstream, and the returned data disappears when the script is run from the CLI.
**Fix:**
```python
gap_it.rename("gap").reset_index(names="date").to_csv(
    ROBUSTNESS_DIR / "placebo_intime_gap.csv",
    index=False,
)

pd.concat(
    [
        gap.rename("gap")
        .reset_index(names="date")
        .assign(placebo_unit=placebo_unit)
        for placebo_unit, gap in placebo_gaps.items()
    ],
    ignore_index=True,
).to_csv(ROBUSTNESS_DIR / "placebo_inspace_gaps.csv", index=False)
```

### WR-03: Phase 4 Tests Can Pass Against Stale Artifacts

**File:** `tests/test_phase4.py:25`
**Issue:** The tests only assert that generated output files already exist and contain minimal columns/content. A broken `synthetic_control.py`, `robustness_pe.py`, or `robustness_alt_control.py` can still pass if the old files remain in `output/robustness/`.
**Fix:**
```python
import subprocess

def test_phase4_scripts_regenerate_outputs():
    for script in (
        "src/robustness/synthetic_control.py",
        "src/robustness/robustness_placebo.py",
        "src/robustness/robustness_pe.py",
        "src/robustness/robustness_alt_control.py",
    ):
        subprocess.run(
            [sys.executable, str(PROJECT_ROOT / script)],
            cwd=PROJECT_ROOT,
            check=True,
        )
```

## Info

### IN-01: Cross-Import Test Misses Plain Imports And Analysis Imports

**File:** `tests/test_phase4.py:105`
**Issue:** The standalone-module guard only inspects `ast.ImportFrom` nodes and only checks `src.robustness` / `robustness` prefixes. A plain `import src.robustness.robustness_pe` or any `src.analysis` import would bypass the test even though the phase requires standalone scripts.
**Fix:** Extend the AST walk to inspect `ast.Import` aliases as well, and reject `src.analysis`, `analysis`, `src.robustness`, and `robustness` module prefixes.

### IN-02: SUTVA Comment Does Not Match The Implemented Falsification Markets

**File:** `src/robustness/synthetic_control.py:34`
**Issue:** The SUTVA block says India and Indonesia are used in ROBUST-01 placebo tests, but `robustness_placebo.py` uses Taiwan and Indonesia (`src/robustness/robustness_placebo.py:32`). The code follows the implemented placebo-market set, but the comment is stale/misleading.
**Fix:** Update the comment to state that India is excluded from the donor pool, Indonesia is used as a placebo market, and Taiwan is both a donor-market input and an explicit falsification market per ROBUST-01.

---

_Reviewed: 2026-04-21T00:06:09Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
