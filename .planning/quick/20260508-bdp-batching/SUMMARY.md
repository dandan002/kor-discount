---
status: complete
date: 2026-05-08
commit: 53c0d86
files_modified:
  - utils/bbg.py
---

# Quick Task: Batch bdp requests in chunks of 100

**One-liner:** Extracted `_bdp_batch` helper and rewrote `bdp` to loop in 100-security chunks with 0.5s inter-batch sleep, mirroring the existing `_bdh_batch`/`bdh` pattern.

## What was done

- Extracted `_bdp_batch(securities, fields, overrides)` private helper that:
  - Builds and sends one `ReferenceDataRequest`
  - Applies overrides if provided
  - Guards with `if not msg.hasElement("securityData"): continue`
  - Calls `_raise_bbg_errors(msg)` and `_raise_bbg_errors(msg, sd)`
  - Returns `dict[ticker -> dict[field -> value]]`
- Rewrote `bdp` to:
  - Normalise `securities`/`fields` to lists before the loop
  - Iterate in chunks of 100 (`batch_size = 100`)
  - Sleep 0.5s between batches, skip after last batch
  - Merge all returned dicts into `all_rows`, build `pd.DataFrame(all_rows).T`
  - Updated docstring noting batching behaviour

## Deviations

None — plan executed exactly as specified.
