---
status: complete
date: 2026-05-08
task: bbg-securitydata-guard
files_modified:
  - utils/bbg.py
---

# Quick Fix: Guard securityData getElement with hasElement in all three loops

Added `if not msg.hasElement("securityData"): continue` guards before every `msg.getElement("securityData")` call in `utils/bbg.py`. Bloomberg sends multiple event types during a session (status, admin, partial) and not every message contains a `securityData` element; calling `getElement` on a missing element raises `blpapi.exception.NotFoundException`. The fix was applied to three locations: the `bdp` function (reference data loop), the `_bdh_batch` function (historical data loop), and the `bds` function (bulk reference data loop). Non-data messages are now silently skipped via `continue`, so the loop proceeds to the next message and collects data only from messages that actually carry `securityData`.
