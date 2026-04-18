# Phase 3: Primary Empirics - Context

**Gathered:** 2026-04-17
**Status:** Ready for planning

<domain>
## Phase Boundary

Estimate three analyses from `data/processed/panel.parquet` and write all results to `output/` — (1) stacked event study of cumulative abnormal valuation changes around each Japan reform date, (2) panel OLS with two-way country + time fixed effects and reform-interaction dummies, and (3) geopolitical risk sub-analysis estimating KOSPI response to North Korea escalation months. All output must be paper-ready: CAR figures, coefficient tables, and regression tables in LaTeX.

New analyses (synthetic control, robustness/placebo tests, policy projections) belong in later phases. This phase is primary empirics only.

</domain>

<decisions>
## Implementation Decisions

### Event Study Design
- **D-01:** Pre-event estimation window: **-36 months** (3 years before each reform date). Used to fit the counterfactual trend in the KOSPI–TOPIX spread. Applies to all three Japan reform events.
- **D-02:** Event window shown in CAR figure: **-12 to +24 months** relative to event date (t=0). One year of pre-event and two years of post-event are plotted per event.
- **D-03:** The "abnormal" valuation change is measured as **KOSPI P/B minus TOPIX P/B spread**. The counterfactual is the expected spread implied by the pre-estimation-window trend. CAR = cumulative deviation of the spread from its pre-event trajectory. This directly tests whether Japan's governance reforms compressed the Korea Discount.
- **D-04:** Stacked design (Cengiz et al. 2019): stack the three event-date cohorts and run a single regression with cohort × time-relative-to-event interactions. Heteroskedasticity-robust standard errors throughout.

### Panel OLS
- **D-05:** Estimator: `linearmodels.PanelOLS` (not `statsmodels.OLS`). Two-way country + time fixed effects.
- **D-06:** Reform dummies interacted with the Japan indicator. Coefficients interpreted in P/B points.
- **D-07:** Standard errors: wild-bootstrap clustered by country (with 4 clusters, traditional cluster-SE is unreliable; wild bootstrap is the appropriate correction). Bootstrap iterations: Claude's discretion (500–1000 is standard).
- **D-08:** Output: one combined LaTeX regression table (`output/tables/table2_ols.tex`), columns = specifications (baseline two-way FE, + reform dummies, + reform × Japan interactions). Booktabs style, 2 decimal places — same convention as Phase 2 Table 1.

### Geopolitical Risk Sub-Analysis
- **D-09:** Data source: **Caldara-Iacoviello Geopolitical Risk (GPR) index** — single downloadable CSV from the authors' site. Use the country-level GPR series for South Korea. No API required.
- **D-10:** Escalation indicator: binary dummy = 1 if GPR-Korea in month t exceeds the **75th percentile of GPR-Korea over the full study period** (2004–2024). This threshold is computed once and stored as a constant in the analysis script (documented, not hardcoded as a magic number).
- **D-11:** Estimand: OLS regression — `KOSPI P/B ~ GPR_escalation_dummy + time_FE + TOPIX P/B`. Time fixed effects absorb global macro trends; TOPIX P/B controls for Japan/developed-market valuation sentiment. Isolates Korea-specific geopolitical response.
- **D-12:** Results written with explicit partial-identification caveats — the coefficient measures association, not pure causal effect of NK escalation, because GPR-Korea may be contaminated by global risk-off episodes.

### Output Organization
- **D-13:** Event study CAR figures: **one combined 3-panel figure** with one subplot per Japan reform date. Saved to `output/figures/figure2_event_study.pdf`. Publication-plain style consistent with Figure 1.
- **D-14:** A separate geopolitical results figure (time series of GPR-Korea with escalation months shaded + KOSPI P/B overlay, or regression coefficient plot) saved to `output/figures/figure3_geo_risk.pdf`. Structure at Claude's discretion.
- **D-15:** Each analysis module writes its own outputs; no analysis module imports from another analysis module (`panel.parquet` is the sole shared input).

### Claude's Discretion
- Wild-bootstrap iteration count (500 or 1000 — whichever is practical)
- Exact subplot layout for the 3-panel event study figure (vertical stack vs. 1×3 horizontal)
- Whether to produce a standalone geopolitical regression table or fold the coefficient into the OLS table as an additional column
- GPR data download filename and storage location within `data/raw/`
- Any companion diagnostic figures (pre-trend tests, residual plots)

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Configuration and Data
- `config.py` — Event dates firewall; Japan reform dates locked here (2014-02-01, 2015-06-01, 2023-03-01). All analysis scripts MUST read dates from this file, never hardcode them.
- `data/processed/panel.parquet` — Canonical panel: columns (date, country, pb, pe), monthly frequency, countries: KOSPI, TOPIX, SP500, MSCI_EM, 2004–2024. All three analyses read exclusively from this file.
- `data/raw/MANIFEST.md` — Data provenance documentation; GPR index CSV should be added here as a new entry.

### Code Patterns (read for style)
- `src/data/build_panel.py` — Panel schema and `pd.read_parquet` loading pattern.
- `src/descriptive/figure1.py` — Established figure script pattern: PROJECT_ROOT resolution, output directory creation, PDF export, publication-plain style.
- `src/descriptive/discount_stats.py` — Pattern for writing machine-readable output artifacts alongside prose-ready fragments.

### Requirements
- `.planning/REQUIREMENTS.md` §Event Study — EVNT-01, EVNT-02, EVNT-03, EVNT-04
- `.planning/REQUIREMENTS.md` §Panel OLS — OLS-01, OLS-02, OLS-03
- `.planning/REQUIREMENTS.md` §Geopolitical Risk Sub-Analysis — GEO-01, GEO-02, GEO-03

### External Data
- Caldara-Iacoviello GPR index (country-level CSV): https://www.matteoiacoviello.com/gpr.htm — download and add to `data/raw/`; document in MANIFEST.md

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `config.py`: `EVENT_DATES`, `EVENT_LABELS`, `STEWARDSHIP_CODE_DATE`, `CGC_DATE`, `TSE_PB_REFORM_DATE` — import for all event study date logic.
- `config.py`: `RAW_DIR`, `PROCESSED_DIR` — use for path resolution throughout.
- `requirements.txt`: `linearmodels` must be added if not already pinned (check before planning — Phase 2 only used statsmodels + matplotlib/seaborn).
- `src/descriptive/figure1.py`: `PROJECT_ROOT = Path(__file__).resolve().parents[N]` + sys.path pattern; matplotlib publication-plain style; PDF output via `savefig`.

### Established Patterns
- All scripts are standalone and executable directly (`python src/analysis/event_study.py`).
- Logging via `logging.basicConfig` to stdout.
- Output directories created with `Path.mkdir(parents=True, exist_ok=True)`.
- Newey-West lag = 12 months established in Phase 2 as the project convention for HAC errors.

### Integration Points
- Phase 3 scripts read from `data/processed/panel.parquet` (Phase 1 output) and GPR CSV (new raw file).
- Phase 3 outputs land in `output/figures/` and `output/tables/` — reuse directories already created by Phase 2.
- Phase 4 (paper assembly) will `\input{}` the `.tex` fragments produced here — use consistent file naming.

</code_context>

<specifics>
## Specific Ideas

- GPR threshold (75th percentile) must be computed from the data and stored as a named constant in the geopolitical script — not hardcoded as a number. Makes it auditable and reproducible.
- The stacked event study regression should cite Cengiz et al. (2019) in a comment noting the design rationale.
- Wild-bootstrap SE for OLS: use `wildboottest` library or equivalent; document the weight distribution used (Rademacher or Mammen) in a script comment for referee transparency.

</specifics>

<deferred>
## Deferred Ideas

- Synthetic control (SYNTH-01 to SYNTH-03) — belongs in Phase 4 robustness
- Placebo / falsification tests (ROBUST-01 to ROBUST-04) — Phase 4 robustness
- Alternative metric (P/E) robustness — Phase 4
- Full channel decomposition (GEO-V2-01) — v2 requirements

</deferred>

---

*Phase: 03-primary-empirics*
*Context gathered: 2026-04-17*
