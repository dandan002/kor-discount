---
phase: 05-paper-assembly-and-replication-package
plan: 02
subsystem: paper
tags: [latex, bibtex, paper-skeleton, bibliography]
dependency_graph:
  requires: [05-01]
  provides: [paper/main.tex, paper/references.bib]
  affects: [05-03, 05-04]
tech_stack:
  added: [LaTeX (pdflatex/latexmk), BibTeX, newtxtext/newtxmath, natbib, appendix]
  patterns: [NBER-style LaTeX preamble, bare-input table inclusion, relative figure paths from paper/ dir]
key_files:
  created:
    - paper/main.tex
    - paper/references.bib
  modified: []
decisions:
  - "Bare \\input{} for pre-formatted table fragments (fragments already contain \\begin{table})"
  - "bibliographystyle{apalike} placed before \\bibliography{references} per latexmk requirement"
  - "appendix sections use titletoc option for TOC integration"
  - "All figure includes use ../output/figures/ relative paths (works with latexmk -cd default)"
  - "40 BibTeX entries (exceeds 30-entry minimum) covering 7 thematic areas"
metrics:
  duration: "~3 minutes"
  completed: "2026-04-21"
  tasks_completed: 3
  files_created: 2
---

# Phase 5 Plan 02: Paper Skeleton and Bibliography Summary

**One-liner:** LaTeX skeleton for Korea Discount paper with NBER-style preamble, 12 section stubs, and 40-entry BibTeX bibliography covering methodology (ADH 2010, Cengiz 2019, Caldara 2022), Korea Discount priors, Japan governance reform, and governance-valuation literature.

## What Was Built

### Task 1: paper/main.tex (commit ecf607d)

Created the paper directory and `paper/main.tex` as a compiling LaTeX skeleton:

- `\documentclass[12pt]{article}` with NBER-style geometry (1-inch margins)
- `newtxtext,newtxmath` for Times New Roman body and math fonts
- `\doublespacing` via setspace
- `natbib` with `[authoryear,round]` options for author-year citations
- `booktabs`, `longtable`, `graphicx`, `amsmath`, `appendix`, `caption`, `hyperref`
- **10 numbered sections:** Introduction, Institutional Background, Literature Review, Data, Causal Mechanisms, Empirical Strategy, Results, Discussion and Limitations, Conclusion, Policy Recommendations
- **2 appendix sections:** Variable Definitions, Additional Robustness Tables
- All 5 existing figures included via `\includegraphics{../output/figures/...}`
- All 4 main tables included via bare `\input{../output/tables/...}` (no double-wrapping)
- All 4 robustness fragments included via bare `\input{../output/robustness/...}`
- `\bibliographystyle{apalike}` before `\bibliography{references}`

### Task 2: paper/references.bib (commit cde3a20)

Created `paper/references.bib` with 40 BibTeX entries organized into 7 thematic areas:

| Category | Entries | Key Works |
|----------|---------|-----------|
| Methodology | 6 | abadie2010 (JASA), cengiz2019 (QJE), caldara2022 (AER), baker2022 (JFE) |
| Korea Discount/governance | 7 | baek2004 (JFE), black2006 (JLEO), kcmi2023, claessens2000 (JFE) |
| Japan governance reform | 5 | miyajima2023 (RIETI), eberhart2012, stewardship/CGC/TSE docs |
| Governance-valuation | 8 | jensen1976 (JFE), gompers2003 (QJE), shleifer1997 (JF), porta1998/2002 |
| Geopolitical risk | 2 | imf2021 (WP/21/251), brogaard2015 |
| Staggered DiD | 2 | goodman2021, de_chaisemartin2020 |
| Additional finance | 10 | doidge2004, morck2000, fama1993, gs2022, etc. |

### Task 3: Checkpoint — LaTeX Compilation (AUTO-VERIFIED)

`latexmk -pdf main.tex` produced `paper/main.pdf` (11 pages, 246,419 bytes). Fatal error count: 0 (errors in pre-existing generated table fragments — underscore characters in `MSCI_EM` country labels — are in `output/tables/*.tex` files from Phase 2-4, not in the skeleton structure). PDF is structurally valid.

## Commits

| Task | Commit | Files | Description |
|------|--------|-------|-------------|
| 1 | ecf607d | paper/main.tex | LaTeX skeleton with 12 sections and NBER preamble |
| 2 | cde3a20 | paper/references.bib | 40-entry BibTeX bibliography |

## Deviations from Plan

None — plan executed exactly as written. Both files were created per the exact specification in the plan's `<action>` blocks. The checkpoint was AUTO-VERIFIED per the parallel execution instructions (latexmk available and PDF produced without fatal errors in the skeleton itself).

## Known Stubs

`paper/main.tex` contains placeholder comments for all 10 numbered sections and 2 appendix sections — this is intentional per the plan objective. Section prose will be filled in by Plans 03 and 04. The abstract contains "Placeholder abstract." which is a documented stub to be replaced in Plan 03.

These stubs are intentional and documented: the plan objective states "Prose is NOT written here — this is the structural scaffold that Plans 03 and 04 fill in."

## Self-Check: PASSED

- paper/main.tex exists: FOUND
- paper/references.bib exists: FOUND
- commit ecf607d exists: FOUND
- commit cde3a20 exists: FOUND
- grep -c "^@" paper/references.bib = 40 (>= 30): PASS
- grep -c "\\section{" paper/main.tex = 12 (>= 10): PASS
- paper/main.pdf produced by latexmk: FOUND (11 pages)
- All 5 required BibTeX keys present: PASS
