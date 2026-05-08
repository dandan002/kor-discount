---
quick_id: 260508-hoc
slug: restructure-roadmap-phase-1-builds-acqui
description: Restructure roadmap — Phase 1 builds acquisition scripts, user runs at Bloomberg terminal, then analysis phases proceed from real data
date: 2026-05-08
must_haves:
  truths:
    - ROADMAP.md Phase 1 goal no longer references mock mode as success criterion
    - ROADMAP.md has a Bloomberg Terminal Checkpoint note between Phase 1 and Phase 2
    - Phase 2+ depends on real CSVs in data/raw/bloomberg/
    - REQUIREMENTS.md mock-mode requirements (DATA-02, DATA-04) moved to v2
    - INFR-03 no longer requires make mock target
    - E2E requirements updated to use real data pipeline
  artifacts:
    - .planning/ROADMAP.md
    - .planning/REQUIREMENTS.md
---

# Quick Task 260508-hoc: Restructure Roadmap (No Mock Mode)

## What

Restructure the project plan so that:
1. **Phase 1** builds acquisition scripts (real Bloomberg code) + infra + utilities
2. **User manually runs** at Bloomberg terminal after Phase 1 completes
3. **Phases 2–4** proceed assuming real data CSVs are already in `data/raw/bloomberg/`

Remove mock mode as a v1 requirement. Keep --mock as optional fallback (v2).

## Tasks

### Task 1: Update ROADMAP.md

- Change Phase 1 goal to: "All project infrastructure is in place and both Bloomberg acquisition scripts are complete and ready to run at a Bloomberg terminal"
- Replace mock-centric success criteria with: scripts exist with correct Bloomberg field calls, utils are importable, Makefile has standard targets
- Add Bloomberg Terminal Checkpoint note between Phase 1 and Phase 2
- Update Phase 2 to assume real data in data/raw/bloomberg/ (not mock)
- Update Phase 3 to run against real data
- Update Phase 4: remove `make mock && make analysis && make paper` from success criteria; replace with real data E2E

Files: `.planning/ROADMAP.md`

### Task 2: Update REQUIREMENTS.md

- Move DATA-02 (--mock for universe) to v2
- Move DATA-04 (--mock for bloomberg pull) to v2
- Update INFR-03: remove `make mock` from Makefile targets requirement
- Update E2E-01/02/03 to reference real data pipeline instead of mock
- Update traceability: Phase 1 now covers DATA-01, DATA-03, DATA-05 (not DATA-02, DATA-04)
- Decrement v1 count accordingly

Files: `.planning/REQUIREMENTS.md`
