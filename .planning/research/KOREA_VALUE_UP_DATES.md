# Korea Value-Up Reform Date Research

**Project:** Korea Discount Study  
**Milestone:** v1.1 Korea Value-Up Reform Event Study  
**Researched:** 2026-04-23

## Purpose

Collect the official Korea-side reform dates that can support a staged event study analogous to the shipped Japan analysis.

## Current Data Constraint

- `data/processed/panel.parquet` currently spans **2004-01-31 through 2026-04-30**
- This means:
  - 2024 reform events can support roughly 20-26 post-treatment months
  - 2025 reforms have materially shorter post windows
  - 2026 reforms are too recent for long-window inference and are better treated as robustness or follow-through dates for now

## Narrow Value-Up Rollout Set

Use when prioritizing direct policy purity around the 2024 FSC/KRX Value-Up program itself.

| Date | Source | Why it matters |
|------|--------|----------------|
| 2024-02-26 | FSC press release: "Active Support to be Provided to Promote Voluntary Efforts of Listed Companies in Enhancing Their Value" | First formal seminar introducing the Corporate Value-up Program framework and disclosure support pillars |
| 2024-05-02 | FSC press release: "Guidelines on Corporate Value-up Plan Unveiled to Support Listed Companies' Voluntary Efforts to Boost Corporate Value" | Draft guidelines/manual unveiled; this is the clearest disclosure-framework milestone |
| 2024-08-12 | FSC press release: "FSC Chairman Holds Meeting with Listed Companies to Boost Corporate Value-up Efforts" | Implementation push after initial disclosures; explicitly reiterates September 2024 value-up index and Q4 ETF rollout |

## Spaced Shareholder-Value Follow-Through Set

Use when prioritizing cleaner temporal spacing over narrow program purity.

| Date | Source | Why it matters |
|------|--------|----------------|
| 2024-02-26 | FSC program-launch press release | Start of the Korea Value-Up agenda |
| 2025-07-09 | FSC press release: "All KOSPI-listed Firms to be Subject to Mandatory Corporate Governance Disclosure Duty from 2026" | Governance disclosure broadened to all KOSPI firms; not the original program launch, but directly aligned with the shareholder-value reform track |
| 2026-02-24 | FSC press release: "Revised Rule to Require High Dividend Companies to Disclose Their Qualifications through Corporate Value-up Plans" | Tax-linked disclosure requirement tied explicitly to corporate value-up plans |

## Excluded but Relevant Milestones

| Date | Source | Note |
|------|--------|------|
| 2024-04-02 | FSC press release: "FSC Introduces New Incentive Programs for Corporate Value-up Program" | Strong candidate event, but tightly clustered with the February and May milestones; likely better as a sensitivity or substitute date |
| 2024-12-24 | FSC press release: "Rule Changes on Treasury Stocks of Listed Companies Scheduled to Take Effect from December 31" | Shareholder-value relevant and clearly official, but only four post-treatment months exist through 2026-04-30 |

## Recommendation

Phase 6 should keep both date sets alive until the code-level event-window choice is finalized:

1. **Primary candidate:** narrow 2024 rollout set for the closest "same format as Japan" policy narrative
2. **Robustness candidate:** spaced 2024-2026 follow-through set for cleaner separation between events

## Sources

- FSC, 2024-02-26: https://www.fsc.go.kr/eng/pr010101/81778
- FSC, 2024-04-02: https://www.fsc.go.kr/eng/pr010101/82032
- FSC, 2024-05-02: https://www.fsc.go.kr/eng/pr010101/82213
- FSC, 2024-08-12: https://www.fsc.go.kr/eng/pr010101/82875
- FSC, 2025-07-09: https://www.fsc.go.kr/eng/pr010101/84905
- FSC, 2026-02-24: https://www.fsc.go.kr/eng/pr010101/86320%3FsrchCtgry%3D%26curPage%3D%26srchKey%3D%26srchText%3D%26srchBeginDt%3D%26srchEndDt%3D
