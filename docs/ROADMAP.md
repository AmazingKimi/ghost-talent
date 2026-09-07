# Ghost Talent Roadmap

Ghost Talent is being built as an open-source emerging AI talent intelligence system and benchmark, not a generic recruiting search tool.

The roadmap is intentionally public so methodology changes, product scope and benchmark milestones can be inspected over time.

## v0.1 — Public foundation

Status: substantially complete

- [x] GitHub repository discovery
- [x] contributor discovery
- [x] merged-PR author discovery
- [x] OpenAlex research evidence
- [x] deterministic Ghost Score
- [x] Contribution Quality
- [x] explainable score drivers
- [x] repository dominance control
- [x] immutable Scout snapshots
- [x] first-detected ledger
- [x] Ghost Radar / EARLY SIGNAL
- [x] local macOS launcher
- [x] explicit source-status reporting
- [x] conservative identity handling
- [x] subject IDs across evidence records

## v0.2 — Time becomes the moat

Goal: turn isolated rankings into a longitudinal intelligence system.

- [x] score history per candidate
- [x] Radar history per candidate
- [x] Rising Fast detection
- [x] rank delta and score delta
- [x] query-scoped candidate history
- [x] 7-day and 30-day trajectory semantics
- [x] local watchlist runner
- [ ] snapshot browser
- [ ] historical `as_of_date` plumbing for retrospective backtests
- [ ] persistent local cache
- [ ] source degradation history
- [ ] automatic OS-level scheduling for Watch

## v0.3 — Benchmark

Goal: test whether Ghost Talent actually finds people earlier than simple visibility baselines.

- [x] frozen benchmark cohort format and immutable freeze command
- [x] versioned Breakout Outcome v0.1 definition
- [x] Precision@K evaluation engine
- [x] comparison against followers / stars / raw contributions
- [x] Breakout Lead Time calculation
- [x] outcome-adjudication template
- [x] no-future-leakage publication protocol
- [ ] freeze first real production cohort from local Scout history
- [ ] 30-day outcome adjudication
- [ ] 90-day outcome adjudication
- [ ] 180-day outcome adjudication
- [ ] breakout rate by Ghost Score bucket
- [ ] calibration analysis
- [ ] publish wins and misses from a mature cohort
- [ ] reproducible public benchmark artifacts

Protocol: [`BENCHMARK.md`](BENCHMARK.md)

## v0.4 — Multi-source talent graph

- [ ] stronger GitHub identity graph
- [ ] arXiv / additional scholarly sources
- [ ] cross-project contribution graph
- [ ] maintainer interaction signals
- [ ] review / merge relationship signals
- [ ] collaboration graph shifts
- [ ] project-quality weighting

## v0.5 — Watch

- [x] query watchlist runner
- [ ] candidate watchlists
- [ ] score-change alerts
- [ ] new high-quality PR alerts
- [ ] maintainer-status changes
- [ ] paper / research trajectory changes
- [ ] large Radar delta alerts

## Research questions

We are especially interested in testing:

1. Can technical contribution quality outperform raw activity volume?
2. Can momentum outperform follower count for early discovery?
3. How much lead time can a public-evidence system achieve before a candidate becomes obvious?
4. Which public signals remain useful across different AI subfields?
5. How stable is Ghost Score across source failures and missing data?

## Non-goals

Ghost Talent is not trying to become:

- a LinkedIn scraper
- an automated outreach bot
- an employment decision system
- a sensitive-attribute inference engine
- a black-box résumé ranker

## Contributing

Useful contributions include new evidence sources, better identity resolution, benchmark design, reproducibility improvements, source-status handling, scoring critiques and documented failure cases.

Open an issue with a concrete proposal and evidence for why it improves discovery quality or benchmark validity.
