# Data Sourcing Guide: Phase 1

Instructions for downloading 20-year index valuation data (P/B, P/E) for KOSPI, TOPIX, S&P 500, and MSCI EM from LSEG Workspace.

---

## What You Need

A Workspace web login at `workspace.refinitiv.com`. You need **Datastream** access — check with your institution's library if you're at a university (many subscribe as a separate add-on from base Workspace).

---

## Method 1: Datastream Web (Recommended)

Datastream is the correct tool for long historical time series of index-level P/B and P/E.

**Step 1 — Open Datastream**

In Workspace, search for `Datastream` in the app bar and open it. Select **Time Series Request**.

**Step 2 — Enter the series**

One download per series/metric combination. Use these mnemonics and field codes:

| Index | Datastream Mnemonic | P/B Field | P/E Field |
|-------|-------------------|-----------|-----------|
| KOSPI | `KOSPICP` | `PBSG` | `PESG` |
| TOPIX | `TOKYOSE` | `PBSG` | `PESG` |
| S&P 500 | `S&PCOMP` | `PBSG` | `PESG` |
| MSCI EM | `MSEMKF$` | `PBSG` | `PESG` |

> If `PBSG` / `PESG` don't resolve, try `PBR` and `PE` — Datastream uses aliases. Use the Datastream search tool to look up valid field codes for each mnemonic.

**Step 3 — Set date range**

- Start: `01/01/2004`
- End: today
- Frequency: `Monthly`

**Step 4 — Export**

Click **Download** → **CSV**. Repeat for each series/metric combination (8 downloads total: 4 indices × 2 metrics).

---

## Method 2: Chart App → Export (Fallback)

If Datastream is not accessible:

1. In Workspace web, search for the index (e.g. `KOSPI`) → open the index page
2. Go to the **Chart** tab
3. Add a study: search `Price/Book` or `P/B Ratio`
4. Extend the time range to 20 years
5. Click the **download icon** (top right of chart) → **Export Data** → CSV

Repeat for TOPIX, S&P 500, MSCI EM.

---

## File Naming Convention

Save all raw files to `data/raw/` without modification:

```
data/raw/
  kospi_pb_2004_2024.csv
  kospi_pe_2004_2024.csv
  topix_pb_2004_2024.csv
  topix_pe_2004_2024.csv
  sp500_pb_2004_2024.csv
  sp500_pe_2004_2024.csv
  msci_em_pb_2004_2024.csv
  msci_em_pe_2004_2024.csv
```

`src/data/build_panel.py` will merge and reshape these into `data/processed/panel.parquet`.

---

## If Datastream Is Not Available

Many university subscriptions include Workspace but not Datastream. If unavailable, use these public fallbacks:

| Index | Source | Notes |
|-------|--------|-------|
| KOSPI | [KRX Statistics](http://data.krx.co.kr) | Historical P/B published in annual data downloads; navigate to Market Data → Indices |
| TOPIX | [JPX Data](https://www.jpx.co.jp/english/markets/statistics-equities/misc/index.html) | P/B and P/E historical data available as Excel downloads |
| S&P 500 | [Shiller Data (Yale)](http://www.econ.yale.edu/~shiller/data.htm) or [FRED](https://fred.stlouisfed.org) | Shiller CAPE series; FRED has S&P 500 P/E via MULTPL |
| MSCI EM | [MSCI Factsheets](https://www.msci.com/our-solutions/indexes/emerging-markets) | Monthly factsheets include P/B; requires manual PDF extraction or direct download where available |

> **Critical (DATA-04):** Document survivorship bias limitations for whichever source you use. Free sources (Yahoo Finance, Macrotrends) almost certainly do not provide point-in-time constituent data — flag this explicitly in the data section of the paper.

---

## Provenance Manifest

After downloading, create `data/raw/MANIFEST.md` with an entry for each file:

```markdown
| File | Source | Series | Field | Vintage Date | Download Method |
|------|--------|--------|-------|-------------|-----------------|
| kospi_pb_2004_2024.csv | LSEG Datastream | KOSPICP | PBSG | YYYY-MM-DD | Manual web export |
| ... | | | | | |
```

This satisfies DATA-03 (provenance documentation) and is required for the replication package (OUTPUT-03).

---

## Event Date Reference (config.py)

Per DATA-02 and the look-ahead bias firewall, lock these dates in `config.py` **before** loading any data:

```python
EVENT_DATES = {
    "stewardship_code":       "2014-02-01",  # Japan FSA Stewardship Code announced
    "corporate_governance_code": "2015-06-01",  # Japan CGC effective date
    "tse_pb_reform":          "2023-03-01",  # TSE P/B > 1 reform announcement
}
```

Sources for official dates:
- FSA Stewardship Code: Japan FSA press release, February 2014
- Corporate Governance Code: TSE effective date, June 2015
- TSE P/B reform: TSE announcement, March 2023

---

*Created: 2026-04-14 | Phase 1 reference*
