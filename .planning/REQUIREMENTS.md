# Requirements: Korea Discount Study

**Defined:** 2026-04-23
**Core Value:** A rigorous, reproducible empirical argument that the Korea Discount is structural and addressable — with credible causal evidence from Japan that reform works.

## v1.1 Requirements

### Reform Dates and Sample

- [ ] **DATES-01**: Researcher can trace every Korea reform event used in the new study to an official FSC or KRX source with an exact announcement or effective date recorded in project docs
- [ ] **DATES-02**: `config.py` contains a locked Korea reform date set and labels that are structurally separate from the shipped Japan event dates
- [ ] **SAMPLE-01**: The analysis pipeline can consume the existing panel through at least `2026-04-30` without regressing the shipped Japan outputs
- [ ] **SAMPLE-02**: The Korea study documents and enforces an event-window choice consistent with the available post-treatment months for the selected reform dates

### Korea Event Study

- [x] **KEVNT-01**: Researcher can run a Korea-side staged event study, analogous to the current Japan design, on an official Korea reform sequence tied to the Value-Up agenda
- [x] **KEVNT-02**: The Korea event study writes machine-readable CAR outputs and a paper-ready figure/table in the same style as the Japan event-study artifacts
- [x] **KEVNT-03**: The design explicitly handles closely clustered Korea reform announcements by documented date selection, overlap annotation, or shorter windows rather than silent contamination
- [x] **KEVNT-04**: The shipped Japan event-study outputs remain reproducible and unchanged unless a comparison artifact is intentionally versioned

### Robustness and Interpretation

- [ ] **KROB-01**: Researcher can evaluate at least two Korea reform-date specifications: a narrow 2024 Value-Up rollout set and a more spaced shareholder-value follow-through set
- [ ] **KROB-02**: Researcher can rerun the Korea event study under at least one alternative event-window sensitivity justified by the `2026-04-30` data endpoint
- [ ] **KROB-03**: Results include a direct Japan-versus-Korea interpretation note that separates descriptive policy timing evidence from stronger causal claims

### Paper and Reproducibility

- [ ] **KPAPER-01**: Paper background and methods text are updated to describe the Korea Value-Up reform dates and the Korea-side event-study design
- [ ] **KPAPER-02**: `run_all.py` and README documentation regenerate the Korea event-study artifacts alongside the existing Japan analysis
- [ ] **KPAPER-03**: Tests or verification scripts cover the Korea date config, sample horizon, and expected artifact paths

## v1.2 Requirements (Deferred)

### Extended Korea Reform Inference

- **KEXT-01**: Korea-side panel OLS or local-projection designs quantify the valuation effect of the Korea reform sequence once enough post-reform months exist for defensible inference
- **KEXT-02**: A Korea-specific synthetic control or donor-based counterfactual is attempted only after the reform window is long enough to evaluate pre-fit and post-treatment separation credibly

### Broader Governance Reform Coverage

- **KEXT-03**: Treasury-stock rule changes and Commercial Act follow-through are integrated into a later, fuller shareholder-protection reform chapter

## Out of Scope

| Feature | Reason |
|---------|--------|
| Rebuilding the entire paper around Korea reforms only | v1.1 is a follow-on milestone that extends, not replaces, the shipped Japan benchmark |
| Full firm-level Value-Up plan disclosure dataset | High scope increase; current study remains index-level |
| Formal causal claims on 2025-2026 Korea reforms | Too little post-treatment time is available as of 2026-04-23 |
| Intraday or daily announcement-return analysis | Existing codebase and paper are monthly valuation based |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| DATES-01 | Phase 6 | Complete |
| DATES-02 | Phase 6 | Complete |
| SAMPLE-01 | Phase 6 | Complete |
| SAMPLE-02 | Phase 6 | Complete |
| KEVNT-01 | Phase 7 | Complete |
| KEVNT-02 | Phase 7 | Complete |
| KEVNT-03 | Phase 7 | Complete |
| KEVNT-04 | Phase 7 | Complete |
| KROB-01 | Phase 8 | Pending |
| KROB-02 | Phase 8 | Pending |
| KROB-03 | Phase 8 | Pending |
| KPAPER-01 | Phase 9 | Pending |
| KPAPER-02 | Phase 9 | Pending |
| KPAPER-03 | Phase 9 | Pending |

**Coverage:**
- v1.1 requirements: 14 total
- Mapped to phases: 14
- Unmapped: 0

---
*Requirements defined: 2026-04-23*
*Last updated: 2026-04-23 after milestone v1.1 kickoff*
