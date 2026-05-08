---
phase: 01-foundation
fixed_at: 2026-05-08T18:55:23Z
review_path: .planning/phases/01-foundation/01-REVIEW.md
iteration: 1
findings_in_scope: 4
fixed: 4
skipped: 0
status: all_fixed
---

# Phase 01: Code Review Fix Report

**Fixed at:** 2026-05-08T18:55:23Z
**Source review:** .planning/phases/01-foundation/01-REVIEW.md
**Iteration:** 1

**Summary:**
- Findings in scope: 4 (4 Warning, 0 Critical — IN-01 excluded as Info)
- Fixed: 4
- Skipped: 0

## Fixed Issues

### WR-01: Partial Bloomberg outputs treated as completed acquisition

**Files modified:** `Makefile`
**Commit:** ce1d6cf
**Applied fix:** The `acquire` target now checks all three required CSVs (`snapshot_2023.csv`, `roe_panel.csv`, `returns_panel.csv`) instead of only `snapshot_2023.csv`. Two new variables `ROE_PANEL` and `RETURNS_PANEL` were added, and the `if` condition uses `&&` to require all three files to exist before skipping acquisition. Removed the redundant second echo line that only repeated the file path.

### WR-02: LaTeX export disables escaping for normal table data

**Files modified:** `utils/latex_tables.py`
**Commit:** 671f622
**Applied fix:** Changed `df.to_latex(escape=False)` to default `escape=True` via a new `escape` parameter on `df_to_latex()`. Added a `raw_latex=False` opt-in parameter that, when set to `True`, disables escaping for trusted preformatted tables. The function signature is now `df_to_latex(df, caption, label, footnote=None, float_format="%.3f", escape=True, raw_latex=False)`. Internally, `raw_latex=True` maps to `escape=False` in the `to_latex` call; otherwise escaping is on by default.

### WR-03: Footnotes generate tablenotes outside a threeparttable

**Files modified:** `utils/latex_tables.py`
**Commit:** a61d861
**Applied fix:** Restructured the generated LaTeX to wrap the table content in a `threeparttable` environment. The output now includes `\begin{threeparttable}` after `\centering` and `\end{threeparttable}` before `\end{table}`. The `tablenotes` environment is now properly nested inside `threeparttable`. Also cleaned up the footnote line generation to use `lines.extend()` with a list instead of string concatenation with embedded newlines.

### WR-04: Bloomberg API errors not surfaced before writing outputs

**Files modified:** `utils/bbg.py`
**Commit:** f933b9a
**Applied fix:** Added `_raise_bbg_errors(msg, security_data=None)` helper function after `_get_session()` that checks for `responseError` on the message level, and `securityError` and `fieldExceptions` on the per-security element level, raising `RuntimeError` with descriptive messages for each. Called this helper in all three Bloomberg message-processing loops: `bdp()` (checks both message-level and per-security), `_bdh_batch()` (checks both message-level and per-security), and `bds()` (checks both message-level and per-security). This ensures Bloomberg API errors are surfaced immediately rather than silently producing incomplete CSVs.

## Skipped Issues

None — all in-scope findings were successfully fixed.

---

_Fixed: 2026-05-08T18:55:23Z_
_Fixer: the agent (gsd-code-fixer)_
_Iteration: 1_