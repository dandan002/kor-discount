# Phase 4: Synthetic Control and Robustness - Context

**Gathered:** 2026-04-20
**Status:** Ready for planning

<domain>
## Phase Boundary

Stress-test Phase 3 results: (1) estimate a synthetic control for the 2023 TSE P/B reform using the ADH (2010) method, with in-space and in-time placebo tests; (2) run four robustness checks (P/E replication of full Phase 3, alt EM benchmark, placebo falsification markets, synthetic control placebos). All outputs land in `output/robustness/` (new directory) and `output/figures/`. No new primary estimates — this phase confirms the Phase 3 results hold under alternative specifications.

</domain>

<decisions>
## Implementation Decisions

### Synthetic Control Library
- **D-01:** Use **`pysyncon`** (Python port of Stata `synth`, ADH 2010) for the synthetic control estimator. Add to `requirements.txt` with a pinned version. Do NOT use `mlsynth` or manual `scipy.optimize` implementation.
- **D-02:** Treated unit: **Japan (TOPIX P/B)**. Treatment date: 2023-03-01 (locked in `config.py` as `TSE_PB_REFORM_DATE`).
- **D-03:** Outcome variable for synthetic control: **P/B** (same metric as primary analyses). P/E robustness handled separately in ROBUST-02.

### Donor Pool Composition
- **D-04:** Donor pool = **STOXX600, FTSE100, HSI (MSCI HK), MSCI Taiwan, SP500**. Rationale: mix of low-growth developed markets (STOXX600, FTSE100) with governance-discount Asia-Pacific markets (HSI, MSCI Taiwan) and a high-P/B anchor (SP500) to span the pre-treatment P/B range.
- **D-05:** **Korea (KOSPI) is excluded** from the donor pool. Reason: Korea is the primary comparison market for the Korea Discount argument; including it in "synthetic Japan" would conflate the estimand and invite reviewer circularity questions.
- **D-06:** India and Indonesia are excluded from the synthetic control donor pool (high-growth premium distorts P/B trajectory; their pysyncon weights would naturally converge to near-zero anyway). They are used in ROBUST-01 placebo tests instead.
- **D-07:** SUTVA justification must be documented in a comment in the synthetic control script: STOXX600/FTSE100 governance reforms in this period did not involve TSE-style P/B mandates; HSI and MSCI Taiwan are Hong Kong and Taiwan markets with no equivalent reform event in 2023.
- **D-08:** Pre-treatment period for synthetic control: **2004-01-01 to 2023-02-01** (full available history up to one month before treatment). Pre-treatment RMSPE must be reported in the output and in the figure caption.

### Robustness Tests Structure
- **D-09:** One standalone Python module per robustness check, mirroring Phase 3 pattern. Each script is independently executable and writes to `output/robustness/`. Scripts:
  - `src/robustness/synthetic_control.py` — SYNTH-01 through SYNTH-03 + ROBUST-04
  - `src/robustness/robustness_pe.py` — ROBUST-02 (full P/E replication)
  - `src/robustness/robustness_alt_control.py` — ROBUST-03 (alt EM benchmarks)
  - `src/robustness/robustness_placebo.py` — ROBUST-01 (placebo falsification markets)

### P/E Robustness (ROBUST-02)
- **D-10:** Full Phase 3 re-run using **P/E instead of P/B** — event study (Figure equivalent), panel OLS with reform-interaction dummies, and geopolitical risk sub-analysis. All three analyses replicated. Results saved to `output/robustness/` with clear `_pe` suffix on filenames.
- **D-11:** Use the same estimation windows, fixed effects, and standard error methods as Phase 3 (carry forward D-01 through D-15 from `03-CONTEXT.md`). No methodological changes — metric swap only.

### Alternative Control Group (ROBUST-03)
- **D-12:** Run **both** alternative EM benchmark substitutions:
  - **MSCI EM ex-Korea proxy**: Use **MSCI EM Asia** (already in `data/raw/`) as the closest available proxy for EM ex-Korea. Document this substitution explicitly.
  - **MSCI EM ex-China**: Use a EM benchmark that downweights or excludes China — given available data, this requires constructing a proxy or using a subset. Claude's discretion on implementation; document the approach.
- **D-13:** Each alt-control variant produces its own regression table (LaTeX fragment) saved to `output/robustness/`.

### Placebo Falsification (ROBUST-01)
- **D-14:** Falsification markets: **MSCI Taiwan** and **MSCI Indonesia** — neither had a P/B governance reform event over the 2014–2023 event windows. Run the Phase 3 event study design on each market (treating it as a pseudo-Japan and applying the same reform date windows). Expected result: null or negligible effects.
- **D-15:** Placebo results saved alongside primary results in `output/robustness/placebo_*.csv` and a combined placebo figure showing null effects vs. primary Japan effect.

### Synthetic Control Placebo Tests (ROBUST-04)
- **D-16:** Two placebo test types:
  - **In-time placebo**: Re-run synthetic control with a fake treatment date (e.g., 2019-01-01, pre-COVID) to verify no spurious gap appears.
  - **In-space placebo**: Run synthetic control treating each donor pool country as the treated unit in turn; plot the distribution of placebo gaps alongside Japan's gap to show Japan's post-2023 gap is unusually large.
- **D-17:** In-space and in-time placebo outputs saved to `output/robustness/` as CSV + PDF figure.

### Output Organization
- **D-18:** New directory `output/robustness/` created by the first script that runs. Structure:
  - `synthetic_control_weights.csv` — donor weights + pre-treatment RMSPE
  - `figure_synth_gap.pdf` — pre/post gap plot (primary synthetic control figure)
  - `figure_placebo_intime.pdf`, `figure_placebo_inspace.pdf` — ROBUST-04 placebo figures
  - `placebo_taiwan_*.csv`, `placebo_indonesia_*.csv` — ROBUST-01 results
  - `robustness_pe_ols.tex`, `robustness_pe_event_coefs.tex` — ROBUST-02 tables
  - `robustness_alt_control_em_asia.tex`, `robustness_alt_control_em_exchina.tex` — ROBUST-03 tables

### Claude's Discretion
- Exact `pysyncon` API calls (solver kwargs, predictor variable selection)
- Whether to use TOPIX or MSCI Japan series as the treated unit P/B input (check data coverage and pick the longer/cleaner series)
- Construction method for MSCI EM ex-China proxy given available raw data
- In-time placebo date selection (pick a clean pre-treatment year with no major confounds)
- Exact matplotlib layout for the in-space placebo distribution figure

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Configuration and Data
- `config.py` — Event dates firewall; `TSE_PB_REFORM_DATE = 2023-03-01` is the synthetic control treatment date. All scripts MUST read this, never hardcode.
- `data/processed/panel.parquet` — Canonical panel (date, country, pb, pe). All robustness scripts read exclusively from this file plus the raw CSVs for donor pool markets.
- `data/raw/MANIFEST.md` — Data provenance; verify donor pool markets are documented here.

### Phase 3 Context (carry-forward decisions)
- `.planning/phases/03-primary-empirics/03-CONTEXT.md` — All Phase 3 implementation decisions apply to the P/E robustness re-run (D-10, D-11). Read before implementing `robustness_pe.py`.

### Code Patterns (read for style)
- `src/descriptive/figure1.py` — Established figure script pattern: PROJECT_ROOT resolution, output dir creation, PDF export, publication-plain style.
- `src/analysis/event_study.py` — Stacked Cengiz-style event study implementation to be adapted for P/E robustness and placebo falsification.
- `src/analysis/panel_ols.py` — Panel OLS pattern to be adapted for P/E and alt-control robustness.
- `src/analysis/geo_risk.py` — GPR analysis pattern to be adapted for P/E robustness.

### Requirements
- `.planning/REQUIREMENTS.md` §Synthetic Control — SYNTH-01, SYNTH-02, SYNTH-03
- `.planning/REQUIREMENTS.md` §Robustness & Validation — ROBUST-01, ROBUST-02, ROBUST-03, ROBUST-04

### External
- pysyncon documentation: https://pysyncon.readthedocs.io — verify API before planning; confirm it supports predictor-variable weighting (V matrix) as in ADH 2010.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `src/analysis/event_study.py` — Full stacked event study implementation; adapt for P/E swap (change `pb` → `pe` column) and for placebo market runs (change treated unit from Japan to Taiwan/Indonesia).
- `src/analysis/panel_ols.py` — Panel OLS with wild-bootstrap; adapt metric column and control group for ROBUST-02 and ROBUST-03.
- `src/analysis/geo_risk.py` — GPR analysis; adapt metric column for ROBUST-02.
- `config.py` — `EVENT_DATES`, `EVENT_LABELS`, `RAW_DIR`, `PROCESSED_DIR` — import throughout.

### Donor Pool Raw Data Available
The following CSVs are already present in `data/raw/` for the donor pool:
- `stoxx600_pb_2004_2026.csv`, `stoxx600_pe_2004_2026.csv`
- `ftse100_pb_2004_2026.csv`, `ftse100_pe_2004_2026.csv`
- `msci_hk_pb_2004_2026.csv`, `msci_hk_pe_2004_2026.csv` (HSI proxy)
- `msci_taiwan_pb_2004_2026.csv`, `msci_taiwan_pe_2004_2026.csv`
- `sp500_pb_2004_2026.csv`, `sp500_pe_2004_2026.csv`
- `msci_em_asia_pb_2004_2026.csv` (MSCI EM ex-Korea proxy for ROBUST-03)
- `msci_indonesia_pb_2004_2026.csv`, `msci_taiwan_pb_2004_2026.csv` (ROBUST-01 placebo)

### Established Patterns
- All scripts standalone, executable directly (`python src/robustness/synthetic_control.py`)
- Logging via `logging.basicConfig` to stdout
- `Path.mkdir(parents=True, exist_ok=True)` for output directories
- Booktabs style LaTeX tables, 2 decimal places

### Integration Points
- `output/robustness/` is a new directory — first script must create it
- Phase 5 (paper assembly) will `\input{}` the robustness `.tex` fragments — maintain consistent naming convention

</code_context>

<specifics>
## Specific Ideas

- SUTVA justification: the donor pool narrative should note that the 2021–2022 period includes global ESG/governance trends that affected all markets; the synthetic control pre-treatment period is long enough (19 years) that this noise is averaged out, and the RMSPE diagnostic will flag any poor fit.
- pysyncon pre-treatment fit should be assessed using both RMSPE and a visual pre-trend check in the gap plot. If RMSPE > 0.15 P/B points, note in the paper that the synthetic control should be interpreted cautiously.
- The in-space placebo distribution plot is the most compelling visual for synthetic control validity — Japan's post-2023 gap should be an outlier relative to the donor pool placebos.

</specifics>

<deferred>
## Deferred Ideas

- Full channel decomposition (GEO-V2-01) — v2 requirements, not this phase
- Callaway-Sant'Anna staggered DiD — explicitly out of scope (wrong estimator for N=1 treated unit; see REQUIREMENTS.md Out of Scope)
- DVC pipeline for data versioning — REP-V2-01, future milestone
- MSCI EM ex-China using a formally constructed index vs. a proxy approximation — acceptable to use a proxy in v1; note limitation in paper

</deferred>

---

*Phase: 04-synthetic-control-and-robustness*
*Context gathered: 2026-04-20*
