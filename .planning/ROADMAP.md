# Roadmap: Korea Discount Study

## Milestones

- ✅ **v1.0 Korea Discount Study MVP** — Phases 1–5 (shipped 2026-04-21)
- 🚧 **v1.1 Korea Value-Up Reform Event Study** — Phases 6–9 (planned 2026-04-23)

## Phases

### Phase 6: Korea Reform Date Locking and Sample Horizon

**Goal**: Official Korea reform dates are locked, the study horizon is extended through `2026-04-30`, and the project has a documented primary-vs-robustness date strategy before any new estimation
**Depends on**: Phase 5 / shipped v1.0 baseline
**Plans**: 3 plans

Plans:
- [x] 06-01-PLAN.md — Research memo: official FSC/KRX date lock, narrow vs extended date sets, and overlap/post-window rationale
- [x] 06-02-PLAN.md — Plumbing: `config.py`, shared study horizon controls, and tests for Korea reform dates without breaking Japan outputs
- [x] 06-03-PLAN.md — Verification: confirm panel coverage through 2026-04, artifact paths, and backwards compatibility with v1.0 outputs

### Phase 7: Korea Value-Up Event Study

**Goal**: A Korea-side staged event study exists in the same artifact format as the current Japan analysis, with CAR outputs ready for paper inclusion
**Depends on**: Phase 6
**Plans**: 3 plans

Plans:
- [x] 07-01-PLAN.md — Foundation: Korea event-study module scaffold, tests, and shared helpers factored from the Japan implementation where appropriate
- [x] 07-02-PLAN.md — Estimation: Korea reform CAR calculations plus figure/table outputs in `output/`
- [x] 07-03-PLAN.md — Verification: regenerate Korea and Japan event-study artifacts and confirm the comparison-ready output contract

### Phase 8: Robustness and Comparative Interpretation

**Goal**: The Korea follow-on result is stress-tested across date sets and event windows, and the Japan-versus-Korea interpretation is written with appropriate caveats
**Depends on**: Phase 7
**Plans**: 3 plans

Plans:
- [ ] 08-01-PLAN.md — Date-set robustness: narrow 2024 rollout versus spaced 2024-2026 reform sequence
- [ ] 08-02-PLAN.md — Window/comparator sensitivity: shorter post windows and comparator checks justified by the 2026-04 endpoint
- [ ] 08-03-PLAN.md — Interpretation: comparison note and limitations text distinguishing descriptive policy timing from stronger causal inference

### Phase 9: Paper and Replication Integration

**Goal**: The paper, run orchestration, README, and verification paths incorporate the Korea follow-on study without regressing the shipped milestone
**Depends on**: Phase 8
**Plans**: 3 plans

Plans:
- [ ] 09-01-PLAN.md — Paper integration: background/method/results updates and new figure/table references
- [ ] 09-02-PLAN.md — Replication workflow: `run_all.py`, README, and artifact inventory updates
- [ ] 09-03-PLAN.md — Final verification: targeted tests plus full reproducibility pass for Japan and Korea event-study outputs

<details>
<summary>✅ v1.0 Korea Discount Study MVP (Phases 1–5) — SHIPPED 2026-04-21</summary>

- [x] Phase 1: Repo Setup and Data Pipeline (3/3 plans) — completed 2026-04-16
- [x] Phase 2: Descriptive Analysis (4/4 plans) — completed 2026-04-17
- [x] Phase 3: Primary Empirics (6/6 plans) — completed 2026-04-20
- [x] Phase 4: Synthetic Control and Robustness (6/6 plans) — completed 2026-04-21
- [x] Phase 5: Paper Assembly and Replication Package (5/5 plans) — completed 2026-04-21

Full details: `.planning/milestones/v1.0-ROADMAP.md`

</details>

## Progress

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 1. Repo Setup and Data Pipeline | v1.0 | 3/3 | Complete | 2026-04-16 |
| 2. Descriptive Analysis | v1.0 | 4/4 | Complete | 2026-04-17 |
| 3. Primary Empirics | v1.0 | 6/6 | Complete | 2026-04-20 |
| 4. Synthetic Control and Robustness | v1.0 | 6/6 | Complete | 2026-04-21 |
| 5. Paper Assembly and Replication Package | v1.0 | 5/5 | Complete | 2026-04-21 |
| 6. Korea Reform Date Locking and Sample Horizon | v1.1 | 3/3 | Complete | 2026-04-23 |
| 7. Korea Value-Up Event Study | v1.1 | 3/3 | Complete | 2026-04-23 |
| 8. Robustness and Comparative Interpretation | v1.1 | 0/3 | Pending | — |
| 9. Paper and Replication Integration | v1.1 | 0/3 | Pending | — |
