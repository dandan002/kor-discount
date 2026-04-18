# Phase 3: Primary Empirics - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-17
**Phase:** 03-primary-empirics
**Areas discussed:** Event study window design, Geopolitical risk data source, NK escalation event definition, Results figure layout

---

## Event Study Window Design

| Option | Description | Selected |
|--------|-------------|----------|
| -36 months estimation window | Standard in governance event studies; 3 years before each reform date | ✓ |
| -24 months estimation window | Tighter; reduces confounders but may be too short | |
| -48 months estimation window | Longer but risks spanning prior events | |

**User's choice:** -36 months (3 years)

| Option | Description | Selected |
|--------|-------------|----------|
| -12 to +24 months event window | 1 year pre, 2 years post — standard for governance reform studies | ✓ |
| -6 to +12 months event window | Tighter; risks missing delayed effects | |
| -12 to +36 months event window | Longer post but 2023 TSE event has limited post-treatment data | |

**User's choice:** -12 to +24 months

| Option | Description | Selected |
|--------|-------------|----------|
| KOSPI minus TOPIX spread | Measures Korea Discount movement directly | ✓ |
| KOSPI P/B in levels (market model) | Standard form but loses discount framing | |
| KOSPI minus MSCI EM spread | EM peers baseline; MSCI EM partial contamination issue | |

**User's choice:** KOSPI minus TOPIX spread

---

## Geopolitical Risk Data Source

| Option | Description | Selected |
|--------|-------------|----------|
| Caldara-Iacoviello GPR index | Single CSV download; academic standard; country-level Korea series | ✓ |
| GDELT event database | BigQuery/file downloads; granular but overkill for monthly panel | |
| Hand-coded event list | High precision but small N; manual curation required | |

**User's choice:** Caldara-Iacoviello GPR index

| Option | Description | Selected |
|--------|-------------|----------|
| 75th percentile of Korea GPR | Data-driven; top quartile of geopolitical stress; documented in code | ✓ |
| Absolute threshold (GPR-Korea > 200) | Fixed level; harder to defend without calibration | |
| You decide | Leave to Claude | |

**User's choice:** 75th percentile of Korea GPR over the study period

---

## NK Escalation Event Definition

| Option | Description | Selected |
|--------|-------------|----------|
| OLS: KOSPI P/B ~ GPR_escalation_dummy + time FE + TOPIX P/B | Simple, defensible; same framework as panel OLS | ✓ |
| Event study around escalation months | Richer graphically but small N (~20-25 months) | |
| Correlation / descriptive only | Appropriate for partial-ID framing; less rigorous | |

**User's choice:** OLS regression

| Option | Description | Selected |
|--------|-------------|----------|
| Time FE + TOPIX P/B | Month FE absorbs macro; TOPIX controls for developed-market sentiment | ✓ |
| Time FE + SP500 P/B + MSCI EM P/B | Richer but risks multicollinearity; MSCI EM Korea contamination | |
| Just time FE | Minimal; acknowledged bias from global risk-off | |

**User's choice:** Time FE + TOPIX P/B

---

## Results Figure Layout

| Option | Description | Selected |
|--------|-------------|----------|
| One combined 3-panel figure | Single PDF, 3 subplots — paper-ready as Figure 2 | ✓ |
| Three separate figures | More flexible for appendix placement but clutters main text | |
| You decide | Leave to Claude | |

**User's choice:** One combined 3-panel figure (figure2_event_study.pdf)

| Option | Description | Selected |
|--------|-------------|----------|
| One combined table, columns = specifications | Standard econometrics format; easy comparison | ✓ |
| Separate tables per specification | Cleaner if specs differ greatly; unusual for panel OLS | |
| You decide | Leave to Claude | |

**User's choice:** One combined table with columns = specifications (table2_ols.tex)

---

## Claude's Discretion

- Wild-bootstrap iteration count (500 or 1000)
- Exact subplot layout for 3-panel event study figure
- Whether geopolitical regression results appear as standalone table or additional OLS column
- GPR raw data filename and storage path
- Companion diagnostic figures

## Deferred Ideas

- Synthetic control (Phase 4 robustness)
- Placebo/falsification tests (Phase 4 robustness)
- Alternative metric (P/E) robustness (Phase 4)
- Full channel decomposition (v2 requirements)
