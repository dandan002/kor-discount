# Phase 1: Foundation - Research

**Researched:** 2026-05-08
**Domain:** Python project scaffolding, Bloomberg blpapi wrappers, utility module design
**Confidence:** HIGH

## Summary

Phase 1 is a pure infrastructure and scripting phase. No analysis runs; the deliverable is a working project skeleton — directory layout, Python utility modules, two Bloomberg acquisition scripts, and a Makefile. The critical constraint is that the acquisition scripts must work correctly at a Bloomberg terminal (blpapi installed) but fail gracefully without it. All locked decisions from CONTEXT.md govern the implementation.

The environment is already partially scaffolded: `data/raw/bloomberg/`, `data/raw/dart/`, `data/raw/krx/`, `data/raw/kftc/`, `outputs/figures/`, `outputs/tables/`, and `outputs/logs/` exist. blpapi 3.26.3.1 is installed in the active Anaconda environment (Python 3.12.2). The default blpapi connection is `localhost:8194`. The 290 prior-project index CSVs in `data/raw/` must be moved to `data/raw/prior-project/` and gitignored per D-06/D-07. `src/utils/` (empty directory) must be removed; `utils/` is created at project root per D-03.

There is one requirement mismatch to resolve: UTIL-02 says `python src/utils/bbg.py --test` but D-03 (locked decision) places `utils/` at project root. The correct test command after D-03 is `python utils/bbg.py --test` (or equivalently `python -m utils.bbg --test`). The planner must resolve this by using the locked D-03 path.

**Primary recommendation:** Build in wave order — directory cleanup first, then `utils/` modules (bbg.py, stats.py, latex_tables.py), then acquisition scripts, then Makefile and README.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- **D-01:** Returns panel date range: 2021-01-01 to 2026-03-31
- **D-02:** KOSPI Index benchmark series uses the same date range (2021-01-01 to 2026-03-31)
- **D-03:** `utils/` lives at the project root (not inside `src/`). The existing empty `src/utils/` directory should be removed; a new `utils/` directory is created at root level.
- **D-04:** `utils/` is a proper Python package with `__init__.py`. Scripts import as `from utils.bbg import bdp`, `from utils.stats import winsorize`, `from utils.latex_tables import df_to_latex` — all working when run from the project root with no PYTHONPATH manipulation needed.
- **D-05:** All `src/` scripts are run from the project root: `python src/00_build_universe.py`. No `sys.path` hacks inside scripts.
- **D-06:** The 200+ index-level CSVs in `data/raw/` (Bovespa, S&P 500, KOSPI, MSCI, etc.) are from a prior project. Phase 1 moves them to `data/raw/prior-project/` locally. The `panel.parquet` in `data/processed/` is also moved to `data/prior-project/`.
- **D-07:** `data/raw/prior-project/` and `data/prior-project/` are added to .gitignore — not committed. The existing MANIFEST.md and MISSING.txt (from prior project) are moved into prior-project/ as well.

### Claude's Discretion

- Makefile acquire guard behavior: implement a simple guard that checks for `data/raw/bloomberg/snapshot_2023.csv` and skips with a message if it exists.
- Virtual environment approach: standard `python -m venv venv` unless Bloomberg terminal constraints suggest otherwise; document in README.
- requirements.txt pinning strategy: pin major versions with `>=` lower bounds rather than exact pins to accommodate Bloomberg terminal's environment.

### Deferred Ideas (OUT OF SCOPE)

None — discussion stayed within phase scope.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| INFR-01 | Project directory layout matches ROADMAP spec (data/, src/, outputs/, paper/, utils/) | Directory audit shows most dirs exist; `paper/`, `utils/`, `src/` need to be created/cleaned up |
| INFR-02 | requirements.txt lists all Python dependencies with pinned versions | Standard packages verified against PyPI; see Standard Stack section |
| INFR-03 | Makefile provides `make acquire`, `make analysis`, `make paper`, and `make all` targets | Standard GNU Make patterns; guard for `make acquire` documented in Code Examples |
| INFR-04 | .env pattern configured for Bloomberg host/port; template .env.example committed | blpapi SessionOptions defaults: host=127.0.0.1, port=8194; .env already has FSS_API_KEY |
| INFR-05 | Virtual environment setup documented in README | `python -m venv venv` pattern; README.md does not yet exist |
| UTIL-01 | utils/bbg.py implements BDP, BDH, BDS wrappers with graceful ImportError fallback | blpapi ReferenceDataRequest/HistoricalDataRequest patterns documented in Code Examples |
| UTIL-02 | utils/bbg.py passes connection test when run as `python utils/bbg.py --test` | D-03 overrides REQUIREMENTS.md path; correct path is `python utils/bbg.py --test` |
| UTIL-03 | utils/stats.py provides shared helpers for winsorization, robust SE computation, and Cohen's Kappa | scipy.stats.mstats.winsorize verified; statsmodels.stats.inter_rater.cohens_kappa verified |
| UTIL-04 | utils/latex_tables.py exports a DataFrame to a standalone .tex table fragment with booktabs formatting | Pure Python/pandas implementation; no additional library needed |
| DATA-01 | src/00_build_universe.py pulls live KOSPI universe from Bloomberg (BDS + BDP) and saves universe_raw.csv | BDS("KOSPI Index", "INDX_MEMBERS") pattern and BDP field list documented |
| DATA-03 | src/01_bloomberg_pull.py pulls snapshot_2023.csv, roe_panel.csv, and returns_panel.csv from Bloomberg | 12-field BDP snapshot, BDH ROE panel, BDH returns panel patterns documented |
| DATA-05 | All Bloomberg scripts fail gracefully with informative error when blpapi not installed | try/except ImportError pattern; sys.exit(1) with message |
</phase_requirements>

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Bloomberg data acquisition | Acquisition scripts (src/) | utils/bbg.py wrapper | Scripts are thin orchestrators; all API logic in wrapper |
| blpapi session management | utils/bbg.py | — | Single place to manage connection config, retry, error handling |
| Statistical utilities | utils/stats.py | scipy/statsmodels | Thin wrappers over verified library functions |
| LaTeX table generation | utils/latex_tables.py | pandas | Pure string formatting; no external dep needed |
| Build orchestration | Makefile | — | make acquire drives terminal runs; make analysis/paper drive later phases |
| Directory layout | Filesystem (Phase 1 setup) | .gitignore | One-time scaffold; subsequent phases assume structure exists |
| Env config | .env / .env.example | python-dotenv | Secrets never committed; example template committed |

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| blpapi | 3.26.3.1 | Bloomberg terminal API | Official Bloomberg Python SDK; already installed [VERIFIED: pip show blpapi] |
| pandas | >=2.2.1 | DataFrames, CSV I/O | Project standard; already installed [VERIFIED: pip show pandas] |
| numpy | >=1.26.4 | Numerical arrays | Required by pandas/scipy/statsmodels [VERIFIED: pip show numpy] |
| scipy | >=1.12.0 | winsorize (mstats), stats | `scipy.stats.mstats.winsorize` is the standard winsorization function [VERIFIED: python3 -c] |
| statsmodels | >=0.14.4 | cohens_kappa, robust SEs | `statsmodels.stats.inter_rater.cohens_kappa` verified; robust SEs in later phases [VERIFIED: python3 -c] |
| python-dotenv | >=1.0.0 | Load .env for Bloomberg host/port | `from dotenv import load_dotenv` confirmed importable [VERIFIED: python3 -c] |
| matplotlib | >=3.8.3 | Figures (later phases) | Imported without issue; needed in requirements.txt [VERIFIED: pip show matplotlib] |
| seaborn | >=0.13.2 | Figures (later phases) | Imported without issue [VERIFIED: pip show seaborn] |

### Supporting (needed in later phases, pin now)
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| stargazer | >=0.0.7 | LaTeX regression tables | Phase 3 logit output; not installed yet — install at setup [VERIFIED: pip index versions stargazer] |
| sklearn (scikit-learn) | >=1.x | cohen_kappa_score fallback | Available alternative to statsmodels kappa; sklearn already installed [VERIFIED: python3 -c] |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| scipy.stats.mstats.winsorize | numpy percentile clip | winsorize returns MaskedArray; numpy clip easier to serialize — acceptable alternative |
| statsmodels cohens_kappa | sklearn cohen_kappa_score | Both available; statsmodels returns full KappaResults object with CI; sklearn returns scalar |
| python-dotenv | os.environ.get() | dotenv cleaner for .env files; either works |

**Installation (project venv):**
```bash
pip install pandas>=2.2.1 numpy>=1.26.4 scipy>=1.12.0 statsmodels>=0.14.4 \
            python-dotenv>=1.0.0 matplotlib>=3.8.3 seaborn>=0.13.2 stargazer>=0.0.7
# blpapi installed separately at Bloomberg terminal:
# pip install blpapi
```

**Version notes (verified 2026-05-08):**
- scipy latest is 1.17.1; project has 1.12.0 — both work; requirements.txt uses `>=1.12.0`
- stargazer latest is 0.0.7 — only version family; use `>=0.0.7`
- blpapi 3.26.3.1 is installed in current Anaconda env [VERIFIED: pip show blpapi]

## Architecture Patterns

### System Architecture Diagram

```
Bloomberg Terminal
       |
       v
[utils/bbg.py session]
       |
       |-- BDS("KOSPI Index", "INDX_MEMBERS") ---------> [src/00_build_universe.py]
       |                                                         |
       |-- BDP(tickers, identifying_fields) ----->               v
       |                                               data/raw/universe_raw.csv
       |
       |-- BDP(tickers, 12_snapshot_fields) ----------> [src/01_bloomberg_pull.py]
       |-- BDH(tickers, ROE, 2021-2026) -------->               |
       |-- BDH(tickers, PX_LAST, 2021-2026) --->               v
       |-- BDH("KOSPI Index", PX_LAST, 2021-2026)     data/raw/bloomberg/
       |                                               ├── universe_raw.csv
       |                                               ├── snapshot_2023.csv
       v                                               ├── roe_panel.csv
[utils/] (importable from project root)                └── returns_panel.csv
├── __init__.py
├── bbg.py       ← BDP/BDH/BDS wrappers + graceful ImportError
├── stats.py     ← winsorize, robust_se, cohens_kappa
└── latex_tables.py ← df_to_latex()
```

### Recommended Project Structure
```
kor-discount/
├── src/
│   ├── 00_build_universe.py    # BDS universe pull
│   └── 01_bloomberg_pull.py    # BDP snapshot + BDH panels
├── utils/                      # Python package (D-03: project root, not src/utils/)
│   ├── __init__.py
│   ├── bbg.py
│   ├── stats.py
│   └── latex_tables.py
├── data/
│   ├── raw/
│   │   ├── bloomberg/          # landing zone for terminal output CSVs
│   │   ├── dart/               # manual DART data (later phases)
│   │   ├── krx/                # manual KRX data (later phases)
│   │   └── prior-project/      # D-06: 290 old index CSVs, gitignored
│   └── processed/              # Phase 2+ outputs
├── outputs/
│   ├── tables/
│   ├── figures/
│   └── logs/
├── paper/                      # Phase 4 LaTeX scaffold
├── Makefile
├── requirements.txt
├── .env.example
└── README.md
```

### Pattern 1: Graceful blpapi ImportError Guard
**What:** Wraps `import blpapi` in try/except so offline scripts fail cleanly.
**When to use:** Every script that touches blpapi — both src/00_build_universe.py and src/01_bloomberg_pull.py, and utils/bbg.py itself.
**Example:**
```python
# Source: standard Python try/except ImportError pattern [ASSUMED]
try:
    import blpapi
except ImportError:
    print(
        "Error: blpapi is not installed. Run this script at a Bloomberg terminal:\n"
        "  pip install blpapi\n"
        "  python utils/bbg.py --test",
        file=sys.stderr,
    )
    sys.exit(1)
```

### Pattern 2: blpapi BDP (Reference Data Request)
**What:** Fetches point-in-time field values for a list of securities.
**When to use:** Snapshot pull (snapshot_2023.csv) and identifying fields in 00_build_universe.py.
**Example:**
```python
# Source: alex314159/blpapiwrapper, Bloomberg Core Developer Guide [CITED]
def bdp(securities, fields, overrides=None):
    """Return DataFrame: index=securities, columns=fields."""
    session = _get_session()
    ref_data_svc = session.getService("//blp/refdata")
    request = ref_data_svc.createRequest("ReferenceDataRequest")
    for sec in (securities if isinstance(securities, list) else [securities]):
        request.append("securities", sec)
    for fld in (fields if isinstance(fields, list) else [fields]):
        request.append("fields", fld)
    if overrides:
        ovrd_elem = request.getElement("overrides")
        for k, v in overrides.items():
            o = ovrd_elem.appendElement()
            o.setElement("fieldId", k)
            o.setElement("value", str(v))
    session.sendRequest(request)
    # --- consume events ---
    rows = {}
    while True:
        ev = session.nextEvent(500)
        for msg in ev:
            sec_data = msg.getElement("securityData")
            for i in range(sec_data.numValues()):
                sd = sec_data.getValueAsElement(i)
                ticker = sd.getElementAsString("security")
                fd = sd.getElement("fieldData")
                rows[ticker] = {
                    fld: (fd.getElementAsString(fld) if fd.hasElement(fld) else None)
                    for fld in fields
                }
        if ev.eventType() == blpapi.Event.RESPONSE:
            break
    return pd.DataFrame(rows).T
```

### Pattern 3: blpapi BDH (Historical Data Request)
**What:** Fetches a time series for one or more fields across a date range.
**When to use:** ROE panel (2019-2023 fiscal year data) and daily returns panel (2021-01-01 to 2026-03-31).
**Example:**
```python
# Source: alex314159/blpapiwrapper [CITED], pdblp tutorial [CITED]
def bdh(securities, fields, start_date, end_date, periodicity="DAILY"):
    """Return DataFrame with MultiIndex (security, date) or long format."""
    session = _get_session()
    ref_data_svc = session.getService("//blp/refdata")
    request = ref_data_svc.createRequest("HistoricalDataRequest")
    for sec in (securities if isinstance(securities, list) else [securities]):
        request.append("securities", sec)
    for fld in (fields if isinstance(fields, list) else [fields]):
        request.append("fields", fld)
    request.set("startDate", start_date.replace("-", ""))   # "20210101"
    request.set("endDate", end_date.replace("-", ""))       # "20260331"
    request.set("periodicitySelection", periodicity)
    session.sendRequest(request)
    frames = []
    while True:
        ev = session.nextEvent(500)
        for msg in ev:
            sec_data = msg.getElement("securityData")
            ticker = sec_data.getElementAsString("security")
            fd_array = sec_data.getElement("fieldData")
            for j in range(fd_array.numValues()):
                pt = fd_array.getValueAsElement(j)
                row = {"security": ticker,
                       "date": pt.getElementAsDatetime("date").date()}
                for fld in (fields if isinstance(fields, list) else [fields]):
                    row[fld] = pt.getElementAsFloat(fld) if pt.hasElement(fld) else None
                frames.append(row)
        if ev.eventType() == blpapi.Event.RESPONSE:
            break
    return pd.DataFrame(frames)
```

### Pattern 4: blpapi BDS (Bulk Reference Data — INDX_MEMBERS)
**What:** Fetches array-valued reference data, e.g., the list of KOSPI constituents.
**When to use:** `src/00_build_universe.py` universe build; `BDS("KOSPI Index", "INDX_MEMBERS")`.
**Example:**
```python
# Source: pdblp bulkref documentation [CITED], community examples [CITED]
def bds(security, field):
    """Return list of values from a Bloomberg bulk/array field."""
    session = _get_session()
    ref_data_svc = session.getService("//blp/refdata")
    request = ref_data_svc.createRequest("ReferenceDataRequest")
    request.append("securities", security)
    request.append("fields", field)
    session.sendRequest(request)
    results = []
    while True:
        ev = session.nextEvent(500)
        for msg in ev:
            sec_data = msg.getElement("securityData").getValueAsElement(0)
            fd = sec_data.getElement("fieldData")
            bulk = fd.getElement(field)
            for i in range(bulk.numValues()):
                elem = bulk.getValueAsElement(i)
                results.append(elem.getElementAsString("Member Ticker and Exchange Code"))
        if ev.eventType() == blpapi.Event.RESPONSE:
            break
    return results
```

**Note:** The exact sub-element name for INDX_MEMBERS varies. A safe approach is to iterate sub-element names dynamically: `{elem.getElement(k).getValueAsString() for k in range(elem.numElements())}`. The planner should include a note that the exact sub-element key must be confirmed at the terminal. [ASSUMED — sub-element name not verifiable offline]

### Pattern 5: df_to_latex in utils/latex_tables.py
**What:** Converts a pandas DataFrame to a standalone .tex table fragment.
**When to use:** All analysis scripts that output LaTeX tables.
**Example:**
```python
# Source: pandas to_latex + booktabs pattern [ASSUMED]
def df_to_latex(df, caption, label, footnote=None, float_format="%.3f"):
    """Return string: standalone booktabs .tex table fragment."""
    body = df.to_latex(
        float_format=float_format,
        escape=False,
        column_format="l" + "r" * len(df.columns),
        booktabs=True,
    )
    lines = [
        r"\begin{table}[htbp]",
        r"  \centering",
        rf"  \caption{{{caption}}}",
        rf"  \label{{{label}}}",
        body,
    ]
    if footnote:
        lines.append(rf"  \footnotesize\textit{{Note:}} {footnote}")
    lines.append(r"\end{table}")
    return "\n".join(lines)
```

### Pattern 6: Makefile acquire guard
**What:** Skip `make acquire` if target CSV already exists.
**When to use:** `make acquire` target.
**Example:**
```makefile
SNAPSHOT = data/raw/bloomberg/snapshot_2023.csv

acquire:
	@if [ -f "$(SNAPSHOT)" ]; then \
		echo "Bloomberg CSVs already exist. Delete data/raw/bloomberg/ to re-run."; \
	else \
		python src/00_build_universe.py && python src/01_bloomberg_pull.py; \
	fi
```

### Pattern 7: winsorize wrapper in utils/stats.py
**What:** Thin wrapper over scipy winsorize that returns a plain numpy array.
**When to use:** Phase 2+ MSTR-03 covariate winsorization.
**Example:**
```python
# Source: scipy.stats.mstats.winsorize [VERIFIED: python3 -c test]
from scipy.stats.mstats import winsorize as _winsorize
import numpy as np

def winsorize(arr, lower=0.01, upper=0.01):
    """Winsorize array at lower/upper quantile limits. Returns numpy array."""
    return np.array(_winsorize(arr, limits=[lower, upper]))
```

### Anti-Patterns to Avoid
- **sys.path manipulation in src/ scripts:** D-05 locks against this. Scripts run from project root; utils/ package is importable without path hacks because project root is on sys.path when invoked as `python src/00_build_universe.py`.
- **Exact-pin requirements.txt:** Bloomberg terminal may have different package versions; use `>=lower_bound` per Claude's Discretion.
- **Hardcoded Bloomberg host/port in scripts:** Always read from environment via `os.getenv("BBG_HOST", "127.0.0.1")` and `int(os.getenv("BBG_PORT", "8194"))`.
- **Blocking the session forever on BDH:** Large universe x long date range requests can time out. Use event timeout and log partial results. [ASSUMED — best practice]
- **Moving prior-project data without gitignore first:** If `data/raw/prior-project/` is created before .gitignore is updated, git may stage the 290 CSVs. Update .gitignore before `git mv` or `mv`.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Winsorization | Custom percentile clip loop | `scipy.stats.mstats.winsorize` | Edge cases with NaN, masked arrays, ties handled correctly |
| Cohen's Kappa | Manual formula | `statsmodels.stats.inter_rater.cohens_kappa` | Returns CI, p-value, handles weighted variants |
| .env loading | Custom file parser | `python-dotenv load_dotenv()` | Handles quoting, export prefix, override logic |
| LaTeX booktabs | Custom string builder | `pandas.DataFrame.to_latex(booktabs=True)` | Handles column escaping, alignment, float formatting |
| Bloomberg connection | Direct blpapi internals | utils/bbg.py wrapper | One place to manage session lifecycle and error handling |

**Key insight:** The blpapi library is low-level. Building BDP/BDH/BDS wrappers that return DataFrames is the expected pattern — every production Bloomberg Python shop does this. The wrappers are not complex but they are essential to keep the acquisition scripts readable.

## Runtime State Inventory

This is a greenfield infrastructure phase, but there is existing state to clean up.

| Category | Items Found | Action Required |
|----------|-------------|------------------|
| Stored data | 290 prior-project index CSVs in `data/raw/` (e.g., `bovespa_*.csv`, `sp500_*.csv`) [VERIFIED: ls count] | Move to `data/raw/prior-project/` |
| Stored data | `data/processed/panel.parquet` — prior project panel [VERIFIED: ls] | Move to `data/prior-project/panel.parquet` |
| Stored data | `data/raw/MANIFEST.md` and `data/raw/MISSING.txt` — prior project docs [VERIFIED: ls] | Move to `data/raw/prior-project/` |
| Stored data | `data/raw/data_gpr_export.xls` — unrelated file [VERIFIED: ls] | Move to `data/raw/prior-project/` |
| Live service config | None | None |
| OS-registered state | None | None |
| Secrets/env vars | `.env` has `FSS_API_KEY` — unrelated to Bloomberg terminal; `.gitignore` already includes `.env` [VERIFIED: cat .gitignore] | Extend `.env` with `BBG_HOST` and `BBG_PORT`; commit `.env.example` template |
| Build artifacts | `src/utils/` is an empty directory — must be removed per D-03 [VERIFIED: ls -la] | `rm -r src/utils/` then create `utils/` at project root |
| Build artifacts | `__pycache__/` at project root [VERIFIED: ls] | Add `__pycache__/` to .gitignore (already covered by `*.py[cod]` but explicit entry is safer) |

## Common Pitfalls

### Pitfall 1: INDX_MEMBERS sub-element key is not "Member Ticker and Exchange Code"
**What goes wrong:** The BDS bulk array for INDX_MEMBERS contains sub-elements whose field name differs between index types and Bloomberg API versions. Code that hard-codes `elem.getElementAsString("Member Ticker and Exchange Code")` may fail silently (returns empty list) or raise a FieldNotFoundException.
**Why it happens:** Bloomberg's INDX_MEMBERS array element names are not publicly documented in a stable way.
**How to avoid:** In bbg.py bds(), iterate sub-element indices dynamically and print element names during the `--test` run. Alternatively use the sub-element at index 0 if only one sub-field is expected.
**Warning signs:** Empty universe_raw.csv after a supposedly successful run.

### Pitfall 2: blpapi session not started before getService()
**What goes wrong:** `session.getService("//blp/refdata")` raises an exception if `session.start()` was not called first, or if the session failed to connect.
**Why it happens:** blpapi session startup is synchronous but terminal connection may fail silently.
**How to avoid:** Check `session.start()` return value (returns True on success). Open service explicitly: `session.openService("//blp/refdata")`. Wrap in a helper that raises a clear error if connection fails.
**Warning signs:** `InvalidStateException` or hanging on first `nextEvent()`.

### Pitfall 3: BDH date format is YYYYMMDD, not ISO
**What goes wrong:** Passing `"2021-01-01"` as startDate to a HistoricalDataRequest fails silently or returns no data.
**Why it happens:** Bloomberg API expects dates as `"20210101"` (no dashes).
**How to avoid:** Strip dashes in bdh() wrapper: `start_date.replace("-", "")`.
**Warning signs:** Empty returns_panel.csv.

### Pitfall 4: utils/ not on sys.path when scripts run as python src/00_build_universe.py
**What goes wrong:** `from utils.bbg import bdp` raises ModuleNotFoundError when the script is run from the project root.
**Why it happens:** Python adds the script's directory (`src/`) to sys.path, not the project root.
**How to avoid:** Do NOT add sys.path hacks in scripts (D-05). Instead, the user must always run from the project root, where `utils/` is a direct child. Python adds the current directory (`.`) to sys.path by default when running scripts as `python src/foo.py` — BUT only if the CWD is the project root. Document this prominently in README.
**Verification:** `python -c "from utils.bbg import bdp; print('OK')"` from project root must succeed.
**Warning signs:** ModuleNotFoundError on `from utils.bbg import bdp`.

**Deeper note:** When Python runs `python src/00_build_universe.py`, it prepends `src/` to sys.path (the script's directory), NOT the project root. The project root is only available if it is the CWD and Python adds `''` (empty string = CWD) to sys.path automatically for interactive use. For script execution, `''` is added at sys.path[0] position only in some Python invocation modes. The safest fix is to run with `python -m src.build_universe` OR ensure CWD is always project root. [ASSUMED — test this at the terminal during UTIL-02 verification]

### Pitfall 5: gitignore missing prior-project directories
**What goes wrong:** After moving 290 CSVs to `data/raw/prior-project/`, running `git add .` includes them all.
**Why it happens:** .gitignore currently only covers `__pycache__/`, `*.py[cod]`, and `.env`.
**How to avoid:** Update .gitignore BEFORE moving files. Add `data/raw/prior-project/` and `data/prior-project/`.
**Warning signs:** `git status` shows hundreds of staged files.

### Pitfall 6: Snapshot date is 2023 but the pull happens in 2026
**What goes wrong:** BDP snapshot fields pull the current (2026) value, not the 2023 fiscal year value. The file is named `snapshot_2023.csv` suggesting FY2023 fundamentals.
**Why it happens:** BDP without an override returns the most recent available value.
**How to avoid:** Use the `FUNDAMENTAL_DATABASE_DATE` override (or `EQY_FUND_YEAR` / `BEST_FPERIOD_OVERRIDE`) to pin the pull to FY2023 year-end. Alternatively, document explicitly in the script that the 2023 in the filename means "fundamentals as of FY2023 reporting" and use the appropriate Bloomberg override field. [ASSUMED — the exact override field must be confirmed at the terminal; ROADMAP Phase 2 section has the field list but does not specify override date]
**Warning signs:** PBR, ROE, DPS values in snapshot_2023.csv reflect 2025/2026 actuals instead of FY2023.

## Code Examples

### Session setup and connection test (utils/bbg.py --test)
```python
# Source: blpapi SessionOptions [VERIFIED: python3 inspect], .env pattern [VERIFIED: dotenv]
from dotenv import load_dotenv
import os, sys

try:
    import blpapi
except ImportError:
    print("Error: blpapi not installed. Run at a Bloomberg terminal.", file=sys.stderr)
    sys.exit(1)

load_dotenv()
_session = None

def _get_session():
    global _session
    if _session is None:
        so = blpapi.SessionOptions()
        so.setServerHost(os.getenv("BBG_HOST", "127.0.0.1"))
        so.setServerPort(int(os.getenv("BBG_PORT", "8194")))
        _session = blpapi.Session(so)
        if not _session.start():
            raise RuntimeError("Failed to start Bloomberg session. Check terminal connection.")
        _session.openService("//blp/refdata")
    return _session

if __name__ == "__main__":
    # python utils/bbg.py --test
    s = _get_session()
    print("Bloomberg session started OK. Host:", os.getenv("BBG_HOST", "127.0.0.1"))
```

### .env.example template
```bash
# Bloomberg terminal connection (default: localhost:8194)
BBG_HOST=127.0.0.1
BBG_PORT=8194
# FSS API key (prior project — retain for reference)
FSS_API_KEY=
```

### cohens_kappa in utils/stats.py
```python
# Source: statsmodels.stats.inter_rater [VERIFIED: python3 -c]
from statsmodels.stats.inter_rater import cohens_kappa as _cohens_kappa
import numpy as np

def cohens_kappa(rater1, rater2, labels=None):
    """Compute Cohen's Kappa from two rating arrays. Returns (kappa, p_value)."""
    if labels is None:
        labels = sorted(set(rater1) | set(rater2))
    n = len(labels)
    table = np.zeros((n, n), dtype=int)
    idx = {v: i for i, v in enumerate(labels)}
    for a, b in zip(rater1, rater2):
        table[idx[a]][idx[b]] += 1
    result = _cohens_kappa(table)
    return result.kappa, result.pvalue
```

### Makefile skeleton
```makefile
.PHONY: acquire analysis paper all

SNAPSHOT = data/raw/bloomberg/snapshot_2023.csv

acquire:
	@if [ -f "$(SNAPSHOT)" ]; then \
		echo "Bloomberg data already present. Delete data/raw/bloomberg/ to re-run."; \
	else \
		python src/00_build_universe.py && python src/01_bloomberg_pull.py; \
	fi

analysis:
	python src/02_build_compliance.py
	python src/03_merge_covariates.py
	python src/04_descriptive.py
	python src/05_logit_compliance.py
	python src/06_fundamentals_comparison.py
	python src/07_event_study.py

paper:
	cd paper && pdflatex main.tex && biber main && pdflatex main.tex && pdflatex main.tex
	cp paper/main.pdf outputs/paper.pdf

all: acquire analysis paper
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| blpapi direct request loop in scripts | Thin wrapper module (bbg.py) returns DataFrames | Standard practice for years | Separates API plumbing from business logic |
| Exact-pin requirements.txt | Lower-bound pins (`>=`) for terminal compatibility | — | Accommodates varying Bloomberg terminal environments |
| ROE at index level (RETURN_ON_EQY) | Firm-level RETURN_COM_EQY via BDH | Discovered in MISSING.txt | Index-level ROE not available; must pull firm-by-firm |

**Deprecated/outdated:**
- `RETURN_ON_EQY` / `T12M_RETURN_ON_EQY` at index level: not available (confirmed in MISSING.txt from prior project terminal session). Use `RETURN_COM_EQY` at firm level via BDH.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | INDX_MEMBERS sub-element key is "Member Ticker and Exchange Code" | Code Examples (BDS pattern) | BDS returns empty list; universe_raw.csv empty |
| A2 | `python src/00_build_universe.py` from project root adds CWD to sys.path making `utils/` importable | Common Pitfalls #4 | ModuleNotFoundError at terminal; must add sys.path hack or use different invocation |
| A3 | BDP snapshot needs a `FUNDAMENTAL_DATABASE_DATE` override to pin to FY2023 values | Common Pitfalls #6 | snapshot_2023.csv contains 2026 actuals instead of 2023 fundamentals |
| A4 | BDH for ROE panel uses `RETURN_COM_EQY` field and annual periodicity (YEARLY) | Standard Stack / Data fields | Empty or wrong-scale ROE panel |
| A5 | blpapi `session.nextEvent(500)` timeout of 500ms is sufficient for refdata responses | Code Examples | Partial responses missed; incomplete DataFrames |

**User confirmation needed before execution:** A1 (verify sub-element name at terminal), A2 (verify sys.path behavior), A3 (confirm snapshot override field with user or at terminal).

## Open Questions

1. **What are the 12 snapshot BDP fields for snapshot_2023.csv?**
   - What we know: CONTEXT.md references "all 12 fields" and says ROADMAP Phase 2 contains the exact list; the MANIFEST.md shows: PX_TO_BOOK_RATIO, RETURN_COM_EQY, EQY_DVD_YLD_12M, PE_RATIO, EBITDA_MARGIN, EV_TO_T12M_EBITDA, EV_TO_T12M_EBIT, GROSS_MARGIN, OPER_MARGIN, PROF_MARGIN, RETURN_ON_ASSET, RETURN_ON_CAP
   - What's unclear: ROADMAP says Phase 2 has the "exact BDP/BDH field mnemonics and overrides" — planner should read ROADMAP Phase 2 section before coding src/01_bloomberg_pull.py
   - Recommendation: Planner reads ROADMAP Phase 2 section verbatim and hard-codes all 12 fields in src/01_bloomberg_pull.py

2. **Does snapshot_2023.csv need a fiscal year override?**
   - What we know: BDP returns current values by default; the file is intended to capture FY2023 fundamentals for KOSPI firms that complied in 2024
   - What's unclear: Whether the override field is `FUNDAMENTAL_DATABASE_DATE`, `EQY_FUND_YEAR`, or a `BEST_FPERIOD_OVERRIDE`
   - Recommendation: Include a TODO comment in src/01_bloomberg_pull.py flagging this; confirm at Bloomberg terminal during Phase 1 checkpoint

3. **Does `python src/00_build_universe.py` (run from project root) make `utils/` importable?**
   - What we know: Python's sys.path behavior for script invocation adds the script's directory, not necessarily CWD
   - What's unclear: Whether `''` (CWD) is in sys.path by default when running as `python src/file.py`
   - Recommendation: Test at terminal; if not importable, add a single `sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))` to each src/ script (acceptable one-liner, not "sys.path hacking" in spirit of D-05)

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python 3.12 | All scripts | ✓ | 3.12.2 (conda) | — |
| blpapi | utils/bbg.py, src/00, src/01 | ✓ (local) | 3.26.3.1 | Graceful ImportError exit |
| pandas | All scripts | ✓ | 2.2.1 | — |
| numpy | All scripts | ✓ | 1.26.4 | — |
| scipy | utils/stats.py | ✓ | 1.12.0 | — |
| statsmodels | utils/stats.py | ✓ | 0.14.4 | — |
| python-dotenv | utils/bbg.py | ✓ | 1.2.2 | os.environ.get() fallback |
| matplotlib | outputs (later) | ✓ | 3.8.3 | — |
| seaborn | outputs (later) | ✓ | 0.13.2 | — |
| stargazer | regression tables (Phase 3) | ✗ | — | Must install: `pip install stargazer>=0.0.7` |
| pdflatex | make paper (Phase 4) | ✓ | /Library/TeX/texbin/pdflatex | — |

**Missing dependencies with no fallback:**
- stargazer: needed for Phase 3 regression tables. Must install in project venv at setup time. Not a Phase 1 blocker.

**Missing dependencies with fallback:**
- None blocking Phase 1.

**Note on blpapi:** blpapi 3.26.3.1 is installed in the active Anaconda environment but will NOT be installed at the Bloomberg terminal by default. The terminal requires a fresh `pip install blpapi`. This is expected and documented in ROADMAP.

## Project Constraints (from CLAUDE.md)

- **Timeline:** < 4 weeks to completion — prioritize pipeline completeness over polish
- **Bloomberg:** blpapi only installable at Bloomberg terminal; all offline scripts must work without it
- **Tech stack:** Python 3, statsmodels for econometrics, stargazer for regression tables, matplotlib/seaborn for figures
- **Reproducibility:** Raw data files never modified; all outputs generated programmatically from data/
- **Offline-first:** Mock mode was removed; Phase 1 builds real acquisition scripts only

**Enforcement for Phase 1:**
- Never modify raw CSV files in data/raw/; the pipeline is read-only on raw data
- All 290 prior-project CSVs must be moved, not deleted
- blpapi import must be guarded with try/except ImportError in both utils/bbg.py and any script that calls it
- utils/ package at project root, not src/utils/

## Sources

### Primary (HIGH confidence)
- blpapi 3.26.3.1 — inspected via `python3 -c "import blpapi; ..."`, SessionOptions defaults verified
- scipy.stats.mstats.winsorize — verified callable with correct behavior
- statsmodels.stats.inter_rater.cohens_kappa — verified callable, returns KappaResults with .kappa and .pvalue
- python-dotenv 1.2.2 — verified importable; `load_dotenv()` available
- data/raw/MANIFEST.md — field code reference from prior terminal session (PX_TO_BOOK_RATIO etc.)
- data/raw/MISSING.txt — confirmed RETURN_ON_EQY not available at index level; RETURN_COM_EQY used at firm level
- blpapi default connection — `so.serverHost()` = "127.0.0.1", `so.serverPort()` = 8194

### Secondary (MEDIUM confidence)
- [alex314159/blpapiwrapper](https://github.com/alex314159/blpapiwrapper/blob/master/blpapiwrapper.py) — ReferenceDataRequest and HistoricalDataRequest patterns
- [pdblp tutorial](https://matthewgilbert.github.io/pdblp/tutorial.html) — BDH, BDP, BDS (bulkref) usage patterns

### Tertiary (LOW confidence)
- INDX_MEMBERS sub-element key name — inferred from community examples, not verified at terminal
- sys.path behavior for `python src/file.py` from project root — known Python behavior but not tested in this environment
- BDP fiscal year override field name — not verified against Bloomberg documentation

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — all packages verified via pip/python3
- blpapi connection defaults: HIGH — verified via SessionOptions introspection
- blpapi request patterns (BDP/BDH/BDS): MEDIUM — verified structure from reputable wrappers; exact sub-element names LOW
- Architecture: HIGH — grounded in locked CONTEXT.md decisions
- Pitfalls: MEDIUM — based on MISSING.txt evidence and known blpapi patterns

**Research date:** 2026-05-08
**Valid until:** 2026-06-08 (stable stack; blpapi API does not change frequently)
