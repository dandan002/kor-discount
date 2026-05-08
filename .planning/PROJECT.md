# Korea Discount: Value-Up Compliance Study

## What This Is

A research pipeline and academic paper studying Korea's 2024 Corporate Value-Up program. The paper asks three questions: which KOSPI firms complied with the voluntary disclosure requirement (and why), whether compliant firms were substantively reforming or just signalling, and whether capital markets believed the disclosures. The output is a full empirical paper ready for independent submission.

## Core Value

A complete, reproducible analysis pipeline that produces all tables and figures from raw Bloomberg/KRX data — so the paper can be compiled and re-run with one command.

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] Project infrastructure: directory layout, virtual env, Makefile, requirements.txt, .env pattern
- [ ] Bloomberg utility: utils/bbg.py with BDP/BDH/BDS wrappers and graceful mock fallback
- [ ] Stats utility: utils/stats.py with shared regression helpers
- [ ] LaTeX utility: utils/latex_tables.py exporting DataFrames to .tex fragments
- [ ] Script 00: build_universe.py with --mock mode (synthetic KOSPI universe)
- [ ] Script 01: bloomberg_pull.py with --mock mode (synthetic snapshot, ROE panel, returns)
- [ ] Script 02: build_compliance.py — classify KRX disclosures (0/1/2) and extract event dates
- [ ] Script 03: merge_covariates.py — join Bloomberg + compliance + KFTC chaebol + DART ownership
- [ ] Script 04: descriptive.py — Table 1 summary stats, PBR distribution figure, compliance breakdown figure
- [ ] Script 05: logit_compliance.py — three-model logit with AMEs (Table 2), sector FE robustness
- [ ] Script 06: fundamentals_comparison.py — ROE trajectory, dividend growth, cash hoarding (Table 3, Figure 3)
- [ ] Script 07: event_study.py — market model, abnormal returns, power analysis, CAR plot (Table 4, Figure 4)
- [ ] LaTeX paper scaffold: main.tex, all 9 section files, style files, references.bib
- [ ] End-to-end mock run: all scripts pass with --mock and produce outputs/

### Out of Scope

- KOSDAQ firms — too illiquid for a clean event study; ROADMAP defers to appendix robustness
- KCGS governance scores — optional enhancement; not in v1
- Web scraping automation for KRX/DART — manual data collection is the planned approach
- Causal identification — paper is explicitly correlational (selection acknowledged)

## Context

- **Data dependency:** Bloomberg access (blpapi) required only for scripts 00 and 01. All other scripts read CSVs. Bloomberg session planned at a campus terminal before final data run.
- **Compliance coding:** Manual three-way classification (0=none, 1=vague, 2=quantitative) from KRX Value-Up portal. Inter-rater kappa check required (target κ > 0.75).
- **Chaebol data:** KFTC 2023 large business group list (manual download). Controlling shareholder % from DART OpenAPI or annual report scrape.
- **Papers in hand:** Literature already collected in /papers. Key refs: Lee (2025), Kang & Kim (2026), Yang et al. (2025), Kim et al. (2025).
- **LaTeX environment:** Requires full TeX Live / MiKTeX. Biblatex + biber. Custom paper.sty and econometrics.sty.

## Constraints

- **Timeline**: < 4 weeks to completion — prioritize pipeline completeness over polish
- **Bloomberg**: blpapi only installable at a Bloomberg terminal; all offline scripts must work without it
- **Tech stack**: Python 3, statsmodels for econometrics, stargazer for regression tables, matplotlib/seaborn for figures
- **Reproducibility**: Raw data files never modified; all outputs generated programmatically from data/
- **Offline-first**: Mock mode must produce the full outputs/ tree without Bloomberg or internet access

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| KOSPI only (no KOSDAQ) | KOSDAQ noise degrades event study; robustness check in appendix | — Pending |
| Three-way compliance coding (0/1/2) | Distinguishes signal quality (quantitative vs. vague) — central to Part A and B | — Pending |
| statsmodels over R | Python pipeline — keep everything in one language | — Pending |
| stargazer for tables | Publication-quality LaTeX regression tables from Python | — Pending |
| Mock mode for all Bloomberg scripts | Offline development without terminal access | — Pending |

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
*Last updated: 2026-05-08 after initialization*
