# Phase 2: Descriptive Analysis - Context

**Gathered:** 2026-04-16
**Status:** Ready for planning

<domain>
## Phase Boundary

Generate Figure 1 (20-year KOSPI P/B vs benchmark time series), Table 1 (summary statistics by country and sub-period), and compute the Korea Discount magnitude as a time-averaged P/B spread with statistical significance — ready for verbatim use in the abstract and introduction.

New analyses (event study, OLS, geopolitical) belong in Phase 3. This phase is validation and documentation only.

</domain>

<decisions>
## Implementation Decisions

### Figure 1 Design
- **D-01:** Figure 1 shows P/B only — one series per market (KOSPI, TOPIX, SP500, MSCI EM). PE is excluded from the headline figure; KOSPI PE gaps are too prominent.
- **D-02:** Annotate all three Japan reform dates as vertical dashed lines with text labels: 2014-02-01 (Stewardship Code), 2015-06-01 (CGC), 2023-03-01 (TSE P/B reform). Dates are already locked in `config.py` — read from there.
- **D-03:** Visual style: publication-plain — seaborn whitegrid or matplotlib default, no decorative elements. Matches most journal submission guidelines.

### Discount Quantification
- **D-04:** Compute the Korea Discount as a spread against two benchmarks: TOPIX (developed peer, core thesis) and MSCI EM (EM peer). SP500 appears as a context line in Figure 1 but is not used for the headline discount metric.
- **D-05:** Units: P/B points (e.g., "KOSPI trades at a −0.45x P/B discount to TOPIX"). Direct and intuitive for valuation multiples. Do not convert to basis points.
- **D-06:** Statistical test: paired t-test on (KOSPI PB − benchmark PB) with Newey-West standard errors to correct for autocorrelation in monthly valuation data. Use `statsmodels.stats.sandwich_covariance` or `sm.OLS` with HAC errors. Report t-statistic and 95% CI alongside the mean spread.

### Output Formatting
- **D-07:** No specific journal target yet. Use sensible defaults: 300 DPI, PDF format for figures, saved to `output/figures/`. Easy to adjust when a journal is targeted.
- **D-08:** LaTeX tables: booktabs style, 2 decimal places, saved as `.tex` fragments to `output/tables/`. Use `pandas.to_latex()` with `booktabs=True`.
- **D-09:** Table 1 sub-periods aligned with Japan reform dates: full period (2004–2024), Pre-reform (2004–2013), Reform era (2014–2022), Post-TSE (2023–2024). This is theoretically motivated and directly previews the natural experiment design.

### Claude's Discretion
- Legend placement, exact line colors within the publication-plain style, figure aspect ratio, and whether to include a secondary axis or annotation box — all open to Claude's judgment.
- Whether to output a companion PE figure to `output/figures/` (not for Figure 1 numbering, but as supplementary) is at Claude's discretion.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Configuration and Data
- `src/data/config.py` — Event dates firewall; Japan reform dates locked here (2014-02-01, 2015-06-01, 2023-03-01). All analysis scripts must read dates from this file, never hardcode them.
- `src/data/build_panel.py` — Panel schema and construction logic reference.
- `src/data/verify_panel.py` — Verification patterns and expected panel structure.

### Data
- `data/processed/panel.parquet` — Canonical panel: columns (date, country, pb, pe), monthly frequency, countries: KOSPI, TOPIX, SP500, MSCI_EM, 2004–2024.
- `data/raw/MANIFEST.md` — Data provenance documentation.

### Requirements
- `.planning/REQUIREMENTS.md` §Descriptive Analysis — DESC-01, DESC-02, DESC-03 are the acceptance criteria for this phase.

No external journal style guides or ADRs referenced.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `src/data/config.py`: `RAW_DIR`, `PROCESSED_DIR`, `EVENT_DATES` — import these rather than hardcoding paths or dates in Phase 2 scripts.
- `requirements.txt`: matplotlib 3.9.2 and seaborn 0.13.2 already pinned — no new visualization dependencies needed.
- `src/data/build_panel.py`: Pattern for loading `panel.parquet` via `pd.read_parquet(config.PROCESSED_DIR / "panel.parquet")` — follow this pattern in descriptive scripts.

### Established Patterns
- All scripts use `PROJECT_ROOT = Path(__file__).resolve().parents[N]` and add to `sys.path` before importing `config` — follow this pattern.
- Scripts are standalone and executable directly (`python src/descriptive/figure1.py`) — new Phase 2 scripts should follow the same convention.
- Logging via `logging.basicConfig` to stdout.

### Integration Points
- Phase 2 scripts read from `data/processed/panel.parquet` (produced by Phase 1).
- Phase 2 outputs land in `output/figures/` and `output/tables/` — these directories need to be created if absent (use `mkdir -p` or `Path.mkdir(parents=True, exist_ok=True)`).
- Phase 3 will consume the discount magnitude number directly — write it as a machine-readable artifact (e.g., `output/tables/discount_stats.csv`) in addition to the prose-ready LaTeX fragment.

</code_context>

<specifics>
## Specific Ideas

- The three Japan reform vertical markers should use dates from `config.EVENT_DATES` (or equivalent attribute name in config.py) — no hardcoded date strings in figure scripts.
- Newey-West lag selection: use automatic lag selection (`sm.stats.sandwich_covariance.cov_hac`) or set lags = 12 (one year of monthly data) as a convention for this paper.

</specifics>

<deferred>
## Deferred Ideas

- PE figure / appendix table — mentioned implicitly; deferred to Phase 5 appendix assembly.
- Sub-period breakdown of the discount magnitude (pre/post reform) — useful but belongs in the Phase 3 OLS results, not the descriptive phase.

</deferred>

---

*Phase: 02-descriptive-analysis*
*Context gathered: 2026-04-16*
