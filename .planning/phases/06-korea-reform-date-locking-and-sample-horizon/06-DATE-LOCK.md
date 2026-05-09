# Phase 6 Date Lock

## Official Source Rule

Only official Financial Services Commission (`FSC`) or Korea Exchange (`KRX`) announcements can define Korea reform event dates for the follow-on Korea Value-Up study. Phase 7 and later phases should treat this file as the operational date-lock memo and the milestone research note `KOREA_VALUE_UP_DATES` as the upstream evidence log.

## Primary Candidate: Narrow 2024 Rollout Set

| Date | Official Source Body | Why it matters |
|------|----------------------|----------------|
| 2024-02-26 | FSC | First formal launch point for the Korea Corporate Value-up Program and its disclosure-support framework. |
| 2024-05-02 | FSC | The Value-up guidelines/manual were unveiled, making this the clearest disclosure-framework milestone. |
| 2024-08-12 | FSC | Follow-through implementation push that explicitly tied the program to the September 2024 index and Q4 ETF rollout. |

## Robustness Candidate: Spaced Follow-Through Set

| Date | Official Source Body | Why it matters |
|------|----------------------|----------------|
| 2024-02-26 | FSC | Start of the Korea Value-Up policy agenda. |
| 2025-07-09 | FSC | Governance disclosure was broadened to all KOSPI firms from 2026, extending the shareholder-value reform track. |
| 2026-02-24 | FSC | Tax-linked disclosure requirements were tied directly to corporate value-up plans, making it a clean follow-through reform date. |

## Excluded But Relevant Dates

- `2024-04-02` remains relevant because the FSC announced new incentive programs for the Value-Up agenda, but it is excluded from the primary specification because it is too tightly clustered between the February 26 and May 2 milestones.
- `2024-12-24` remains relevant because the FSC finalized treasury-stock rule changes tied to shareholder-value reforms, but it is excluded from the primary specification because the `2026-04-30` data endpoint leaves only a very short post-treatment window.

## Window Constraint from 2026-04-30 Endpoint

The canonical panel currently ends on `2026-04-30`, which means:

- 2024 events have roughly `20-26 post-treatment months`, enough for the narrow rollout narrative.
- 2025 events have materially shorter post windows, so they are better suited to robustness or follow-through interpretation than main-specification inference.
- 2026 events are too recent for long-window inference and should be treated as follow-through or robustness dates only.

## Phase 7 Hand-off

Phase 7 should treat the narrow 2024 rollout set as the default narrative candidate. The spaced 2024-2026 set is reserved for robustness unless later evidence or implementation constraints justify changing that choice.

## Source Pointers

- `2024-02-26`: FSC press release on active support for listed companies' voluntary value-up efforts
- `2024-05-02`: FSC press release unveiling the Value-up Plan guidelines
- `2024-08-12`: FSC chairman meeting with listed companies to boost Value-up efforts
- `2025-07-09`: FSC press release extending mandatory governance disclosure to all KOSPI firms from 2026
- `2026-02-24`: FSC press release requiring high-dividend companies to disclose qualifications through value-up plans
- `2024-04-02`: FSC press release introducing new Value-up incentive programs
- `2024-12-24`: FSC press release on treasury-stock rule changes taking effect December 31
