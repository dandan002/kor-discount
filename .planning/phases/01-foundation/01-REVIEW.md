---
phase: 01-foundation
reviewed: 2026-05-08T17:58:53Z
depth: standard
files_reviewed: 14
files_reviewed_list:
  - .env.example
  - .gitignore
  - Makefile
  - README.md
  - paper/.gitkeep
  - paper/sections/.gitkeep
  - paper/style/.gitkeep
  - requirements.txt
  - src/00_build_universe.py
  - src/01_bloomberg_pull.py
  - utils/__init__.py
  - utils/bbg.py
  - utils/latex_tables.py
  - utils/stats.py
findings:
  critical: 0
  warning: 4
  info: 1
  total: 5
status: issues_found
---

# Phase 01: Code Review Report

**Reviewed:** 2026-05-08T17:58:53Z
**Depth:** standard
**Files Reviewed:** 14
**Status:** issues_found

## Summary

Reviewed the listed foundation files at standard depth, including the Bloomberg acquisition scripts, shared utilities, Makefile, dependency/config files, README, and empty paper placeholders. No critical security issues were found. The main risks are correctness and reproducibility issues in acquisition gating, Bloomberg error handling, and LaTeX table generation.

## Warnings

### WR-01: Partial Bloomberg outputs are treated as a completed acquisition

**File:** `Makefile:14`
**Issue:** The `acquire` target skips Bloomberg acquisition when only `data/raw/bloomberg/snapshot_2023.csv` exists. If a previous run produced the snapshot but failed before writing `roe_panel.csv` or `returns_panel.csv`, `make acquire` reports success and leaves the offline pipeline without required raw inputs.
**Fix:**
```make
SNAPSHOT = data/raw/bloomberg/snapshot_2023.csv
ROE_PANEL = data/raw/bloomberg/roe_panel.csv
RETURNS_PANEL = data/raw/bloomberg/returns_panel.csv

acquire:
	@if [ -f "$(SNAPSHOT)" ] && [ -f "$(ROE_PANEL)" ] && [ -f "$(RETURNS_PANEL)" ]; then \
		echo "Bloomberg CSVs already present. Delete data/raw/bloomberg/ to re-run."; \
	else \
		echo "Running Bloomberg acquisition scripts..."; \
		python src/00_build_universe.py && python src/01_bloomberg_pull.py; \
	fi
```

### WR-02: LaTeX export disables escaping for normal table data

**File:** `utils/latex_tables.py:44`
**Issue:** `df.to_latex(..., escape=False)` emits raw TeX from DataFrame values, captions, labels, and footnotes. Bloomberg/manual table content can legitimately contain characters such as `&`, `%`, `_`, and `#`, which will break paper compilation; if any input is externally sourced, this also allows arbitrary TeX commands into generated outputs.
**Fix:**
```python
def df_to_latex(df, caption, label, footnote=None, float_format="%.3f", escape=True):
    body = df.to_latex(
        float_format=float_format,
        escape=escape,
        column_format=col_format,
        index=True,
    )
```
Also escape or validate `caption`, `label`, and `footnote` separately, or add an explicit `raw_latex=True` opt-in for trusted preformatted tables.

### WR-03: Footnotes generate `tablenotes` outside a `threeparttable`

**File:** `utils/latex_tables.py:55`
**Issue:** When `footnote` is provided, the helper appends a `tablenotes` environment directly inside `table`. `tablenotes` is part of the `threeparttable` pattern and should be nested inside `\begin{threeparttable}`. As written, generated tables with notes are likely to fail LaTeX compilation or render inconsistently depending on the paper preamble.
**Fix:**
```python
lines = [
    r"\begin{table}[htbp]",
    r"  \centering",
    r"  \begin{threeparttable}",
    rf"  \caption{{{caption}}}",
    rf"  \label{{{label}}}",
    body.strip(),
]
if footnote:
    lines.extend([
        r"  \begin{tablenotes}",
        r"    \footnotesize\item \textit{Note:} " + footnote,
        r"  \end{tablenotes}",
    ])
lines.extend([r"  \end{threeparttable}", r"\end{table}"])
```

### WR-04: Bloomberg API errors are not surfaced before writing outputs

**File:** `utils/bbg.py:107`
**Issue:** `bdp()`, `_bdh_batch()`, and `bds()` assume every Bloomberg event message contains usable `securityData` and then convert missing or unreadable fields to `None`. Bloomberg response errors, per-security errors, and field exceptions can therefore become silent missing data or unexpected crashes instead of explicit acquisition failures. That risks writing incomplete CSVs that later look like valid raw inputs.
**Fix:**
```python
def _raise_bbg_errors(msg, security_data=None):
    if msg.hasElement("responseError"):
        raise RuntimeError(f"Bloomberg response error: {msg.getElement('responseError')}")
    if security_data is not None and security_data.hasElement("securityError"):
        security = security_data.getElementAsString("security")
        raise RuntimeError(
            f"Bloomberg security error for {security}: "
            f"{security_data.getElement('securityError')}"
        )
    if security_data is not None and security_data.hasElement("fieldExceptions"):
        security = security_data.getElementAsString("security")
        raise RuntimeError(
            f"Bloomberg field exceptions for {security}: "
            f"{security_data.getElement('fieldExceptions')}"
        )
```
Call this helper in each message loop before reading `fieldData`, and skip only non-data timeout/admin events intentionally.

## Info

### IN-01: Snapshot date override is still marked unverified

**File:** `src/01_bloomberg_pull.py:70`
**Issue:** The code pins the FY2023 snapshot using `FUNDAMENTAL_DATABASE_DATE`, but the adjacent TODO says this override still needs Bloomberg-terminal confirmation. If the override is not accepted or does not affect one of the fields, the raw snapshot may not represent FY2023 as intended.
**Fix:** Confirm the override at the Bloomberg terminal before relying on the acquisition output. Once verified, replace the TODO with a short note documenting the tested Bloomberg behavior; if it is not correct, update `SNAPSHOT_OVERRIDES` to the verified override set.

---

_Reviewed: 2026-05-08T17:58:53Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
