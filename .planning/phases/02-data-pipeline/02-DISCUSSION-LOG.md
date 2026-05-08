# Phase 2: Data Pipeline - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-05-08
**Phase:** 2-Data Pipeline
**Areas discussed:** compliance_coded.csv format, Chaebol + controlling shareholder data, sample.csv column set, Missing data handling

---

## compliance_coded.csv Format

| Option | Description | Selected |
|--------|-------------|----------|
| data/raw/krx/ with ticker + code + date | Minimum 3 columns: ticker, compliance_code, disclosure_date | ✓ |
| data/raw/krx/ with extra metadata cols | Add company_name and disclosure_url for audit trail | |
| project root or data/raw/ top level | More prominent location for the critical input file | |

**User's choice:** `data/raw/krx/compliance_coded.csv` with ticker + code + date.

---

| Option | Description | Selected |
|--------|-------------|----------|
| Leave blank / NaN | Code 0 = no event; events.csv only covers codes 1 and 2 | ✓ |
| Sentinel date (9999-12-31) | Explicit placeholder, less error-prone | |
| Require date for all rows | Even code 0 firms get a deadline date | |

**User's choice:** Leave blank/NaN for code 0 firms.

---

| Option | Description | Selected |
|--------|-------------|----------|
| Inline check with warning | If compliance_coded_r2.csv present, compute kappa and print; skip if absent | ✓ |
| Separate script or notebook | Kappa check outside 02_build_compliance.py | |
| Skip — single rater for now | No kappa check in Phase 2 | |

**User's choice:** Inline check with warning — non-blocking.

---

## Chaebol + Controlling Shareholder Data

| Option | Description | Selected |
|--------|-------------|----------|
| Hand-coded chaebol_tickers.csv | User manually maps ticker → chaebol_group | |
| Name-prefix match (Recommended) | Strip Korean suffixes, match firm names to KFTC group names; print unmatched | ✓ |
| Cross_Shareholding_Restricted = Yes only | Filter to the 61 major chaebol groups before name match | |

**User's choice:** Name-prefix match with stdout report.
**Notes:** User initially indicated "Pull it using the openapi" — clarified that the KFTC list doesn't have an API; the KFTC CSV was then manually added to `data/raw/kftc/`. File confirmed: `KFTC_large_business_groups_2026.csv`, 102 groups, group-level (no individual firm tickers).

---

| Option | Description | Selected |
|--------|-------------|----------|
| Defer to later | Add controlling_pct as NaN placeholder | |
| Include it — data available now | Populate data/raw/dart/ before Phase 2 | |
| Pull from FSS DART OpenAPI | Use FSS_API_KEY already in .env | ✓ |

**User's choice:** Pull from FSS OpenAPI via new `src/01c_dart_pull.py`.

---

| Option | Description | Selected |
|--------|-------------|----------|
| Separate script: src/01c_dart_pull.py | Same pattern as src/00 and src/01; merge script reads CSV | ✓ |
| Inline in 03_merge_covariates.py | DART call embedded in merge; simpler but mixes concerns | |

**User's choice:** Separate script following the existing acquisition pattern.

---

| Option | Description | Selected |
|--------|-------------|----------|
| Largest shareholder % only | 최대주주 단독 (single largest holder) | |
| Controlling family/related-party % only | 조직도 (insider group total) | |
| Both columns | Pull both; analyst chooses in regression | ✓ |

**User's choice:** Both `controlling_pct_largest` and `controlling_pct_group`.

---

## sample.csv Column Set

| Option | Description | Selected |
|--------|-------------|----------|
| Proposed column set | ticker, name, sector + Bloomberg financials + ROE panel + chaebol + DART + compliance | ✓ |
| Rename Bloomberg fields | Map raw mnemonics to readable names (already included in Recommended) | |
| Add/remove something | Other columns needed | |

**User's choice:** Column set as proposed — all Bloomberg mnemonics renamed to human-readable names.

---

| Option | Description | Selected |
|--------|-------------|----------|
| Wide format: roe_2019 … roe_2023 | One row per firm, five ROE columns | ✓ |
| Keep separate from sample.csv | Panel scripts read roe_panel.csv directly | |

**User's choice:** Wide format merged into sample.csv.

---

## Missing Data Handling

| Option | Description | Selected |
|--------|-------------|----------|
| Keep with NaN + print report | Left-join; NaN for missing Bloomberg; missingness report to stdout | ✓ |
| Drop and warn | Remove firms missing Bloomberg data from sample.csv | |

**User's choice:** Keep with NaN + print missingness report.

---

| Option | Description | Selected |
|--------|-------------|----------|
| All continuous Bloomberg financials | All 12 snapshot fields + 5 ROE panel columns | ✓ |
| Only regression covariates | Subset used in the logit only | |
| All numeric except identifiers | Broadest possible winsorization | |

**User's choice:** All continuous Bloomberg financials + ROE panel columns at 1st/99th percentiles.

---

## Claude's Discretion

- DART corp_code lookup implementation (API vs. pre-cached mapping)
- Rate limiting and retry logic for DART API calls
- Exact Korean suffix list for KFTC name-prefix matching

## Deferred Ideas

None — discussion stayed within phase scope.
