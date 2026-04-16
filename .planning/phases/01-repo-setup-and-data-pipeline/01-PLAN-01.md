---
phase: 01-repo-setup-and-data-pipeline
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - config.py
  - requirements.txt
autonomous: true
requirements:
  - DATA-01
  - DATA-03
  - DATA-05

must_haves:
  truths:
    - "config.py exists at repo root with Japan reform event dates defined as date constants before any data loading logic"
    - "requirements.txt exists with pinned versions for all data pipeline dependencies"
    - "Running `pip install -r requirements.txt` in a fresh environment completes without error"
  artifacts:
    - path: "config.py"
      provides: "Event dates firewall — Japan reform dates locked to official policy records"
      contains: "STEWARDSHIP_CODE_DATE, CGC_DATE, TSE_PB_REFORM_DATE"
    - path: "requirements.txt"
      provides: "Pinned Python dependency manifest"
      contains: "pandas==, pyarrow==, numpy=="
  key_links:
    - from: "config.py"
      to: "src/data/build_panel.py"
      via: "import config — event dates imported from config, never redefined in analysis scripts"
      pattern: "import config"
---

<objective>
Create the two foundational repo scaffold files: `config.py` (the event dates firewall) and `requirements.txt` (pinned dependencies).

Purpose: The event dates firewall must exist before any data is loaded. Locking treatment dates in a single importable constant — before any time-series code is written — eliminates look-ahead bias by making it structurally impossible for any analysis script to silently alter the event windows. This is a non-negotiable prerequisite to all downstream phases.

Output: `config.py` at repo root containing Japan reform event dates as `datetime.date` constants; `requirements.txt` with pinned versions for all Phase 1–5 dependencies.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/ROADMAP.md
@.planning/STATE.md
@src/data/pull_bloomberg.py
</context>

<tasks>

<task type="auto">
  <name>Task 1: Create config.py with event dates firewall</name>
  <files>config.py</files>
  <read_first>
    - src/data/pull_bloomberg.py (for project path conventions and import style to match)
    - .planning/STATE.md (for locked decision: "Event dates must be locked in config.py before any data is loaded")
    - .planning/ROADMAP.md (for exact event dates: Phase 1 success criterion #2 states 2014-02-01, 2015-06-01, 2023-03-01)
  </read_first>
  <action>
Create `/Users/dandan/Desktop/Projects/kor-discount/config.py` at the repo root with the following exact content:

```python
"""
config.py — Project-wide constants for the Korea Discount study.

FIREWALL: Event dates are defined here and MUST be imported from this module
by all analysis scripts. Never re-define or hard-code event dates elsewhere.
This structural constraint eliminates look-ahead bias at the code level.

Japan reform event dates (locked to official policy records):
  - STEWARDSHIP_CODE_DATE : 2014-02-01
      FSC Japan Stewardship Code — announced and published February 2014.
  - CGC_DATE              : 2015-06-01
      Tokyo Stock Exchange Corporate Governance Code — effective June 2015.
  - TSE_PB_REFORM_DATE    : 2023-03-01
      TSE request to companies trading below P/B 1.0x — announced March 2023.
"""

import datetime

# ---------------------------------------------------------------------------
# Japan Reform Event Dates (DO NOT MODIFY)
# ---------------------------------------------------------------------------

STEWARDSHIP_CODE_DATE: datetime.date = datetime.date(2014, 2, 1)
CGC_DATE:              datetime.date = datetime.date(2015, 6, 1)
TSE_PB_REFORM_DATE:    datetime.date = datetime.date(2023, 3, 1)

EVENT_DATES: list[datetime.date] = [
    STEWARDSHIP_CODE_DATE,
    CGC_DATE,
    TSE_PB_REFORM_DATE,
]

EVENT_LABELS: dict[datetime.date, str] = {
    STEWARDSHIP_CODE_DATE: "Japan Stewardship Code (Feb 2014)",
    CGC_DATE:              "TSE Corporate Governance Code (Jun 2015)",
    TSE_PB_REFORM_DATE:    "TSE P/B Reform Request (Mar 2023)",
}

# ---------------------------------------------------------------------------
# Study Universe
# ---------------------------------------------------------------------------

COUNTRIES: list[str] = ["KOSPI", "TOPIX", "SP500", "MSCI_EM"]

# ---------------------------------------------------------------------------
# Data Paths
# ---------------------------------------------------------------------------

from pathlib import Path

PROJECT_ROOT: Path = Path(__file__).resolve().parent
RAW_DIR:      Path = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR:Path = PROJECT_ROOT / "data" / "processed"
OUTPUT_DIR:   Path = PROJECT_ROOT / "output"

# ---------------------------------------------------------------------------
# Known Data Limitations (documented here for traceability)
# ---------------------------------------------------------------------------

# kospi_pe_2004_2026.csv starts 2004-05-16 (not 2004-01-16).
# Four months of KOSPI P/E are unavailable at series start.
# build_panel.py will carry NaN for KOSPI PE rows 2004-01 through 2004-04.
KOSPI_PE_SERIES_START: datetime.date = datetime.date(2004, 5, 1)
```

Do not add any logic that reads data files. config.py must be pure constants and path definitions.
  </action>
  <verify>
    <automated>cd /Users/dandan/Desktop/Projects/kor-discount && python -c "import config; assert config.STEWARDSHIP_CODE_DATE.isoformat() == '2014-02-01'; assert config.CGC_DATE.isoformat() == '2015-06-01'; assert config.TSE_PB_REFORM_DATE.isoformat() == '2023-03-01'; assert len(config.EVENT_DATES) == 3; assert len(config.COUNTRIES) == 4; print('config.py OK')"</automated>
  </verify>
  <acceptance_criteria>
    - `grep -n "STEWARDSHIP_CODE_DATE" config.py` returns a line containing `datetime.date(2014, 2, 1)`
    - `grep -n "CGC_DATE" config.py` returns a line containing `datetime.date(2015, 6, 1)`
    - `grep -n "TSE_PB_REFORM_DATE" config.py` returns a line containing `datetime.date(2023, 3, 1)`
    - `grep -n "KOSPI_PE_SERIES_START" config.py` returns a line (documents the known data limitation)
    - `python -c "import config; print(config.TSE_PB_REFORM_DATE)"` prints `2023-03-01` with exit code 0
    - `grep -n "def \|class \|open(\|read_csv\|parquet" config.py` returns nothing (no data loading logic in config.py)
  </acceptance_criteria>
  <done>config.py exists at repo root, imports cleanly, all three event dates are accessible as `datetime.date` constants matching 2014-02-01, 2015-06-01, 2023-03-01, and KOSPI_PE_SERIES_START is documented.</done>
</task>

<task type="auto">
  <name>Task 2: Create requirements.txt with pinned dependencies</name>
  <files>requirements.txt</files>
  <read_first>
    - src/data/pull_bloomberg.py (for existing import list: blpapi, csv, datetime, pathlib — note blpapi is Bloomberg-only and should NOT be in requirements.txt for reproducibility)
    - .planning/ROADMAP.md (Phase 3 mentions linearmodels, Phase 4 mentions pysyncon/mlsynth — include linearmodels now; defer synth control library to Phase 4)
    - .planning/STATE.md (locked decisions: linearmodels.PanelOLS, wildboottest compatibility needed)
  </read_first>
  <action>
Create `/Users/dandan/Desktop/Projects/kor-discount/requirements.txt` with pinned versions. Use exact version pins (==) for all packages that affect numerical output (pandas, numpy, scipy, statsmodels, linearmodels). Use >= for tooling/visualization that does not affect analysis reproducibility.

Content to write:

```
# Korea Discount Study — pinned dependencies
# Python >= 3.11 required
# Install: pip install -r requirements.txt

# Core data
pandas==2.2.3
numpy==1.26.4
pyarrow==15.0.2

# Statistics and econometrics
scipy==1.13.1
statsmodels==0.14.4
linearmodels==6.1

# Wild bootstrap inference (Phase 3 — verify compatibility with linearmodels 6.x)
wildboottest==0.9.1

# Visualization (Phase 2+)
matplotlib==3.9.2
seaborn==0.13.2

# LaTeX table generation (Phase 3+)
# pandas has to_latex() built in; no extra package needed

# Utilities
tqdm==4.66.5
```

Do NOT include blpapi (Bloomberg Terminal SDK — not publicly installable, documented in MANIFEST.md as the data source). Do NOT include pysyncon or mlsynth — those are deferred to Phase 4 pending resolution of the library choice decision noted in STATE.md.
  </action>
  <verify>
    <automated>cd /Users/dandan/Desktop/Projects/kor-discount && python -c "import subprocess, sys; r = subprocess.run([sys.executable, '-m', 'pip', 'install', '--dry-run', '-r', 'requirements.txt'], capture_output=True, text=True); print(r.stdout[-500:] if r.stdout else r.stderr[-500:]); sys.exit(r.returncode)"</automated>
  </verify>
  <acceptance_criteria>
    - `grep "pandas==" requirements.txt` returns `pandas==2.2.3`
    - `grep "numpy==" requirements.txt` returns `numpy==1.26.4`
    - `grep "pyarrow==" requirements.txt` returns `pyarrow==15.0.2`
    - `grep "linearmodels==" requirements.txt` returns `linearmodels==6.1`
    - `grep "blpapi" requirements.txt` returns nothing (blpapi excluded)
    - `grep "pysyncon\|mlsynth" requirements.txt` returns nothing (deferred to Phase 4)
    - File contains a comment line starting with `# Python >= 3.11`
  </acceptance_criteria>
  <done>requirements.txt exists with == pins for all numerical analysis packages (pandas, numpy, pyarrow, scipy, statsmodels, linearmodels, wildboottest), blpapi excluded, pysyncon/mlsynth deferred to Phase 4.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| config.py constants → analysis scripts | Event dates consumed by all downstream analysis; mutation or override breaks look-ahead firewall |
| requirements.txt → pip install | Package versions resolved at install time; unpinned versions produce non-deterministic environments |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-01-01 | Tampering | config.py event dates | mitigate | Event dates defined as module-level constants (not settable via environment variable or function parameter); any override requires explicit source edit — making accidental mutation visible in git diff |
| T-01-02 | Tampering | requirements.txt version pins | mitigate | All analysis-affecting packages pinned with == (not >=); CI/CD or manual `pip check` will detect dependency drift |
| T-01-03 | Repudiation | Data provenance | accept | MANIFEST.md (already exists, vintage date 2026-04-16) documents Bloomberg source; config.py KOSPI_PE_SERIES_START documents known gap; low risk for local research repo with no external audit requirement |
| T-01-04 | Information Disclosure | No network-accessible surface | accept | Local research repo; no API endpoints, no user authentication, no PII; ASVS L1 network controls not applicable |
</threat_model>

<verification>
After both tasks complete:
1. `python -c "import config; print(config.EVENT_DATES)"` prints `[datetime.date(2014, 2, 1), datetime.date(2015, 6, 1), datetime.date(2023, 3, 1)]`
2. `python -m pip install --dry-run -r requirements.txt` exits 0 with no version conflicts
3. `grep "blpapi\|pysyncon\|mlsynth" requirements.txt` returns nothing
4. `python -c "import config; print(config.RAW_DIR)"` prints the absolute path ending in `data/raw`
</verification>

<success_criteria>
- config.py importable with zero errors; all three event dates accessible as `datetime.date` constants
- requirements.txt has == pins for pandas, numpy, pyarrow, scipy, statsmodels, linearmodels, wildboottest
- No data loading logic in config.py
- KOSPI PE gap documented in config.py as KOSPI_PE_SERIES_START
</success_criteria>

<output>
After completion, create `.planning/phases/01-repo-setup-and-data-pipeline/01-01-SUMMARY.md` following the summary template at `@$HOME/.claude/get-shit-done/templates/summary.md`.
</output>
