# Ghost Talent Historical Snapshots

Every successful Scout run writes an immutable, timestamped JSON snapshot under:

`YYYY-MM-DD/<query-slug>/<snapshot-id>.json`

A snapshot records the ranked candidates, Ghost Score components, score version, score drivers, public evidence links, query, and UTC observation time exactly as observed at that run.

Snapshots are append-only. Existing snapshot files must not be edited or replaced. Historical evaluation and future backtests should read these records as frozen evidence and must not introduce information observed after the snapshot timestamp.

The snapshot corpus is intended to become the longitudinal evidence base for Ghost Talent Benchmark, including Precision@K and Breakout Lead Time measurements.
