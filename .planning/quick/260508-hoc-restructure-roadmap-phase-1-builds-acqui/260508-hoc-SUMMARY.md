---
quick_id: 260508-hoc
status: complete
date: 2026-05-08
---

# Quick Task 260508-hoc: Restructure Roadmap (No Mock Mode)

## What Changed

Restructured the project plan so the workflow is:
1. **Phase 1** builds all infra + utils + real Bloomberg acquisition scripts
2. **Bloomberg Terminal Checkpoint** — user runs scripts, real CSVs land in `data/raw/bloomberg/`
3. **Phases 2–4** proceed from real data

## Files Modified

- `.planning/ROADMAP.md` — Phase 1 goal rewritten; Bloomberg Terminal Checkpoint added; Phase 3/4 updated to reference real data
- `.planning/REQUIREMENTS.md` — DATA-02 and DATA-04 (--mock mode) moved to v2; INFR-03 updated (`make mock` → `make acquire`); E2E requirements reference real data; v1 count updated to 41
- `.planning/STATE.md` — Decision and blocker notes updated

## Key Decisions

- Mock mode removed from v1 scope — not needed since user will run Bloomberg scripts before analysis
- `make acquire` replaces `make mock` as the Phase 1 terminal target
- Phase 1 success criteria are now "scripts are correct and runnable" (not "produces mock CSVs")
- Bloomberg Terminal Checkpoint is a natural handoff point baked into the roadmap
