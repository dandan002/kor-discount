# Korea Discount Study

## What This Is

An academic research paper and reproducible Python codebase investigating the persistent valuation discount of South Korean equities ("Korea Discount") relative to developed-market peers. The paper quantifies the discount across a 20-year panel of KOSPI, TOPIX, S&P 500, and MSCI EM valuation data, diagnoses its compounded causes, and derives policy recommendations using Japan's corporate governance reforms as a natural experiment.

## Core Value

Explores whether the Korea Discount is structural and addressable — with causal evidence from Japan.

## Requirements

### Validated

- [Phase 1, 2026-04-16] 20-year monthly panel dataset for KOSPI, TOPIX, S&P 500, and MSCI EM P/B and P/E is sourced, documented in `data/raw/MANIFEST.md`, and transformed into `data/processed/panel.parquet`.
- [Phase 1, 2026-04-16] Reproducible repo foundation exists: locked Japan reform dates in `config.py`, pinned Python dependencies in `requirements.txt`, and raw-to-processed cleaning logic in `src/data/build_panel.py`.
- [Phase 2, 2026-04-17] Descriptive outputs are generated and verified: Figure 1 PDF, Table 1 LaTeX summary statistics, and Korea Discount HAC estimates (`-0.177x` vs TOPIX; `-0.601x` vs MSCI EM).

### Validated

- [Phase 3, 2026-04-20] Event study: cumulative abnormal valuation changes around each Japanese reform date — stacked cohort design, descriptive CARs (HC3 removed; saturated design), figures and coefficient tables in `output/`. Validated in Phase 3.
- [Phase 3, 2026-04-20] Panel OLS with country/time fixed effects and reform-interaction dummies — wild-bootstrap p-values displayed in Table 2 for three reform×Japan terms. Validated in Phase 3.
- [Phase 3, 2026-04-20] Geopolitical risk sub-analysis: GPR overlay figure and Table 3 estimating GPR premium on Korea Discount. Validated in Phase 3.
- [Phase 4, 2026-04-21] Synthetic control robustness for the 2023 TSE P/B reform using `pysyncon`, including donor weights, RMSPE, gap plot, and in-time/in-space placebo figures. Validated in Phase 4.
- [Phase 4, 2026-04-21] Robustness suite covering Taiwan/Indonesia placebo falsification, P/E replications, and alternative EM control groups. Validated in Phase 4.

### Active

- [ ] Causal mechanism section covering three drivers: chaebol cross-shareholding opacity, weak minority-shareholder regulatory recourse, and North Korea geopolitical risk premium
- [ ] Natural experiment analysis using Japan's staggered governance reforms (Stewardship Code 2014, Corporate Governance Code 2015, TSE P/B reform 2023) as treatment events
- [ ] Near- and long-term policy recommendations for Korea (FSC, KRX, regulatory levers)
- [ ] Final paper document (LaTeX or similar) integrating prose, figures, and tables from the analysis
- [ ] Reproducible repo: downstream analysis scripts, figure/table generation, and final replication entrypoint from the validated panel

### Out of Scope

- Real-time or live market data infrastructure — this is a retrospective study, not a dashboard
- Non-equity asset classes (bonds, FX, real estate) — discount is equity-specific
- Company-level microstructure analysis — paper operates at index/market level
- Causal claims beyond what the natural experiment design supports — descriptive and event-study framing for DiD limitations acknowledged

## Context

- **Domain**: Equity valuation, corporate governance, emerging market finance, comparative political economy
- **Korea Discount drivers (thesis)**: Three compounding factors — (1) chaebol cross-shareholding networks creating opacity and minority-shareholder suppression, (2) regulatory environment affording limited recourse to outside investors, (3) geopolitical risk premium from North Korean brinkmanship
- **Japan comparison**: Japan faced an analogous "Japan Discount" through the 2010s; its staged governance reforms provide three clean treatment dates for natural experiment identification
- **Empirical strategy**: Staggered event study (primary) + panel OLS with fixed effects (primary) + synthetic control (robustness). Honest about not claiming full causal ID for single-country comparison.
- **Data sourced for Phase 1** — Bloomberg raw CSV exports and `data/raw/MANIFEST.md` are checked in; `src/data/build_panel.py` produces the canonical monthly P/B and P/E panel for KOSPI, TOPIX, S&P 500, and MSCI EM.
- **Descriptive outputs from Phase 2** — `src/descriptive/figure1.py`, `table1.py`, and `discount_stats.py` generate the verified Figure 1 PDF, Table 1 LaTeX fragment, discount statistics CSV, and abstract-ready LaTeX macros.
- **Primary empirics from Phase 3 complete** — Event study (Figure 2, descriptive CARs), panel OLS (Table 2 with wild-bootstrap p-values), and geopolitical risk sub-analysis (Figure 3, Table 3) are all estimated and in `output/`.
- **Robustness checks from Phase 4 complete** — Synthetic control, placebo falsification, P/E replication, and alternative-control checks are implemented in `src/robustness/` with outputs in `output/robustness/` and `output/figures/`. Synthetic-control RMSPE is high (`0.2893`) and should be framed as a caveat in the paper.

## Constraints

- **Tech Stack**: Python — pandas, statsmodels, matplotlib/seaborn; no R
- **Audience**: Academic submission (peer-reviewed journal or conference)
- **Reproducibility**: All figures and tables must be generated from code; no manual chart creation
- **Data**: Must use publicly accessible or already-licensed sources; data pipeline must be documented

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Python over R | User preference | — Pending |
| Staggered event study + panel OLS as primary methods | Credible for single-country natural experiment; honest about causal limits; mirrors Miyajima et al. and recent governance literature | — Pending |
| Synthetic control as robustness (not primary) | Compelling for causal claim but adds complexity; use for 2023 TSE reform where pre-treatment data is cleanest | — Pending |
| All three Japan reform dates as treatment events | Stacked identification gives three bites; richer than single-event study | — Pending |
| Bloomberg raw valuation exports for Phase 1 panel | Free public point-in-time valuation data was low-confidence; checked-in Bloomberg extracts provide reproducible raw snapshots with a manifest | Validated in Phase 1 |
| Event-date firewall in `config.py` | Treatment dates must be locked before data loading to prevent look-ahead bias | Validated in Phase 1 |
| Korea Discount units reported in P/B points | DESC-03 allows bps or ratio; Phase 2 research selected ratio-style P/B multiple units for direct interpretation | Validated in Phase 2 |
| `pysyncon` for synthetic control | Phase 4 resolved the `pysyncon` vs `mlsynth` choice in favor of a pinned `pysyncon==1.5.2` ADH implementation | Validated in Phase 4 |
| High synthetic-control RMSPE accepted as caveat | Human checkpoint response `rmspe-high` approved proceeding with `0.2893` RMSPE as paper-text caveat rather than blocker | Validated in Phase 4 |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-04-21 after Phase 4 completion*
