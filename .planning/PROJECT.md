# Korea Discount Study

## What This Is

An academic research paper and reproducible Python codebase investigating the persistent valuation discount of South Korean equities ("Korea Discount") relative to developed-market peers. The paper quantifies the discount across a 20-year panel of KOSPI, TOPIX, S&P 500, and MSCI EM valuation data, diagnoses its compounded causes, and derives policy recommendations using Japan's corporate governance reforms as a natural experiment.

## Core Value

Explores whether the Korea Discount is structural and addressable — with causal evidence from Japan.

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] 20-year panel dataset of KOSPI, TOPIX, S&P 500, and MSCI EM valuation metrics (P/B, P/E, EV/EBITDA or equivalent) sourced and cleaned
- [ ] Quantitative analysis of the Korea Discount magnitude over time with descriptive statistics and visualizations
- [ ] Causal mechanism section covering three drivers: chaebol cross-shareholding opacity, weak minority-shareholder regulatory recourse, and North Korea geopolitical risk premium
- [ ] Natural experiment analysis using Japan's staggered governance reforms (Stewardship Code 2014, Corporate Governance Code 2015, TSE P/B reform 2023) as treatment events
- [ ] Event study: cumulative abnormal valuation changes around each Japanese reform date
- [ ] Panel OLS with country/time fixed effects and reform-interaction dummies
- [ ] Synthetic control robustness check for at least the 2023 TSE reform
- [ ] Near- and long-term policy recommendations for Korea (FSC, KRX, regulatory levers)
- [ ] Final paper document (LaTeX or similar) integrating prose, figures, and tables from the analysis
- [ ] Reproducible repo: clean notebooks or scripts, requirements file, data pipeline from raw sources to figures

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
- **Data not yet sourced** — will need to identify and pull 20-year valuation index data; options include FRED, Yahoo Finance, OECD, Bloomberg exports, or World Bank

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
*Last updated: 2026-04-14 after initialization*
