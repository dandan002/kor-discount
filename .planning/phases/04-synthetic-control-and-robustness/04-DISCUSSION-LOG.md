# Phase 4: Synthetic Control and Robustness - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-20
**Phase:** 04-synthetic-control-and-robustness
**Areas discussed:** Synthetic control library, Donor pool composition, Robustness scope, Placebo market selection

---

## Synthetic Control Library

| Option | Description | Selected |
|--------|-------------|----------|
| pysyncon | Faithful ADH (2010) implementation, well-documented, plots + weights out-of-the-box | ✓ |
| mlsynth | Newer library with ADH + augmented variants; overkill for standard replication paper | |
| Manual scipy | Implement weight quadratic program directly; ~150 lines, harder to audit | |

**User's choice:** pysyncon
**Notes:** Add to requirements.txt (not a separate optional requirements file). Single pinned dependency keeps replication package one-command reproducible.

---

## Donor Pool Composition

| Option | Description | Selected |
|--------|-------------|----------|
| Korea excluded | Korea is primary comparison market; including it conflates the estimand | ✓ |
| Korea included | Technically valid donor but weakens narrative clarity | |

| Option | Description | Selected |
|--------|-------------|----------|
| Developed + governance-discount | STOXX600, FTSE100, HSI, MSCI Taiwan, SP500 | ✓ |
| Developed only | STOXX600, FTSE100, SP500, DJI — stricter SUTVA but likely poorer pre-treatment fit | |
| All available markets | Full set; risks overfitting and complicates SUTVA narrative | |

**User's choice:** Developed + governance-discount pool; Korea excluded
**Notes:** User raised a substantive question about whether Japan's 20-30 year stagnation period makes synthetic control valid. Conclusion: stagnation is baked into the pre-treatment period (2004–2022 P/B trajectory to match on) and does not invalidate the method. Japan's low P/B is structurally similar to HSI and MSCI Taiwan (governance discount markets), making them natural donor candidates. RMSPE diagnostic will surface any poor pre-treatment fit.

---

## Robustness Scope

| Option | Description | Selected |
|--------|-------------|----------|
| P/E headline only | Re-run OLS + synthetic control gap only | |
| Full Phase 3 P/E re-run | Event study + OLS + geo analysis all using P/E | ✓ |

| Option | Description | Selected |
|--------|-------------|----------|
| MSCI EM ex-Korea only | Use MSCI EM Asia as proxy | |
| MSCI EM ex-China only | Test sensitivity to China weight | |
| Both | Ex-Korea (MSCI EM Asia proxy) + ex-China | ✓ |

| Option | Description | Selected |
|--------|-------------|----------|
| One module per check | Mirrors Phase 3 standalone script pattern | ✓ |
| Single orchestrator | Easier E2E run but violates Phase 3 pattern | |

**User's choice:** Full Phase 3 re-run for P/E; both alt EM benchmarks; one module per check
**Notes:** User opted for thoroughness on both P/E scope and EM benchmark variants. Script structure keeps Phase 3 pattern intact.

---

## Placebo Market Selection

| Option | Description | Selected |
|--------|-------------|----------|
| MSCI Taiwan | No governance reform, Asia-Pacific, null effect expected | ✓ |
| MSCI Indonesia | EM Asia, no reform event | ✓ |
| MSCI India | Third EM Asia market; India had own reform signals in period | |

**User's choice:** MSCI Taiwan + MSCI Indonesia
**Notes:** Both markets have data in data/raw/. India excluded due to own market reform signals in the event window period.

---

## Claude's Discretion

- Exact pysyncon API calls and solver kwargs
- Whether to use TOPIX or MSCI Japan as treated unit P/B series
- MSCI EM ex-China proxy construction method
- In-time placebo date selection
- In-space placebo distribution figure layout

## Deferred Ideas

- Full channel decomposition (GEO-V2-01) — v2 requirements
- DVC pipeline — REP-V2-01, future milestone
- Formally constructed MSCI EM ex-China index vs. proxy — v1 proxy acceptable
