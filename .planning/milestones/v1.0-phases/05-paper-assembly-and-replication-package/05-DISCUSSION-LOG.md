# Phase 5: Paper Assembly and Replication Package - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-20
**Phase:** 05-paper-assembly-and-replication-package
**Areas discussed:** Prose authorship model, LaTeX template & structure, run_all.py scope & design, Counterfactual projection (POLICY-02)

---

## Prose Authorship Model

| Option | Description | Selected |
|--------|-------------|----------|
| Full prose | Claude writes complete publication-quality text for every section | ✓ |
| Skeleton + outlines | LaTeX structure + bullet-point outlines per section; user writes prose | |
| Hybrid: some full, some outlines | Full prose for mechanical sections; outlines for judgment-heavy sections | |

**User's choice:** Full prose
**Notes:** Claude reads actual numbers from output/ and embeds them verbatim.

---

## Number Embedding Strategy

| Option | Description | Selected |
|--------|-------------|----------|
| Embed numbers directly | Read CSVs/LaTeX fragments and write values into prose verbatim | ✓ |
| LaTeX newcommand macros | Separate macros.tex with \KoreaDiscountTopix etc.; prose uses macros | |

**User's choice:** Embed numbers directly
**Notes:** Simpler, no macro infrastructure needed for v1.

---

## LaTeX Template

| Option | Description | Selected |
|--------|-------------|----------|
| article class, NBER-style | \documentclass{article}, 1-inch margins, Times, 12pt, double-spaced | ✓ |
| Target journal template | Specific journal .cls or .sty file | |
| Minimal article, no styling | Plain article, no custom geometry | |

**User's choice:** article class, NBER-style

---

## Bibliography Management

| Option | Description | Selected |
|--------|-------------|----------|
| Claude creates references.bib from scratch | Full BibTeX with ~30-50 entries for all citations | ✓ |
| Skeleton .bib with placeholders | Structure with TODO entries; user fills in | |
| I'll provide a .bib file | User has existing bibliography | |

**User's choice:** Claude creates from scratch

---

## run_all.py Scope

| Option | Description | Selected |
|--------|-------------|----------|
| Figures + tables only | Reruns analysis scripts from panel.parquet; raw data must be present | ✓ |
| Full end-to-end incl. build_panel.py | Also rebuilds panel.parquet from raw data | |

**User's choice:** Figures + tables only

---

## run_all.py Failure Handling

| Option | Description | Selected |
|--------|-------------|----------|
| Fail fast | Any non-zero exit stops run_all.py immediately with clear error | ✓ |
| Continue and summarize | Runs all scripts regardless of failures; summary at end | |

**User's choice:** Fail fast

---

## Counterfactual Projection Method

| Option | Description | Selected |
|--------|-------------|----------|
| Apply Japan's observed lift to Korea | Measure post-2023 TSE reform TOPIX P/B lift; project same onto KOSPI | ✓ |
| Scale by governance gap | Scale Japan's lift by governance index proxy for Korea's deficit | |

**User's choice:** Apply Japan's observed lift directly

---

## Counterfactual Projection Presentation

| Option | Description | Selected |
|--------|-------------|----------|
| Figure: Korea P/B + projected dashed path | Programmatic figure4_counterfactual_projection.pdf | ✓ |
| Text only, no figure | Projection magnitude stated in prose only | |

**User's choice:** Figure with dashed projection path

---

## Claude's Discretion

- Section lengths and subsection structure
- BibTeX key naming convention
- Results section structure (standalone vs. folded)
- Uncertainty band width for projection figure

## Deferred Ideas

- LaTeX macro infrastructure (\newcommand) — v2
- DVC pipeline — v2 requirement REP-V2-01
- Full end-to-end run_all.py including build_panel.py
