# Ghost Talent Roadmap

Ghost Talent is being built as an open-source emerging AI talent intelligence system and benchmark, not a generic recruiting search tool.

The roadmap is intentionally public so methodology changes, product scope and benchmark milestones can be inspected over time.

## v0.1 — Public foundation

Status: in progress

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
- [ ] explicit source-status reporting
- [ ] stronger identity resolution
- [ ] subject IDs across evidence records

## v0.2 — Time becomes the moat

Goal: turn isolated rankings into a longitudinal intelligence system.

- [ ] score history per candidate
- [ ] Radar history per candidate
- [ ] Rising Fast detection
- [ ] rank delta and score delta
- [ ] query/cohort history
- [ ] snapshot browser
- [ ] historical `as_of_date` plumbing
- [ ] persistent local cache
- [ ] source degradation history

## v0.3 — Benchmark

Goal: test whether Ghost Talent actually finds people earlier than simple visibility baselines.

- [ ] frozen benchmark cohorts
- [ ] versioned breakout definitions
- [ ] Precision@K
- [ ] breakout rate by score bucket
- [ ] Breakout Lead Time
- [ ] calibration analysis
- [ ] comparison against followers / stars / raw contributions
- [ ] publish wins and misses
- [ ] reproducible benchmark artifacts

## v0.4 — Multi-source talent graph

- [ ] stronger GitHub identity graph
- [ ] arXiv / additional scholarly sources
- [ ] cross-project contribution graph
- [ ] maintainer interaction signals
- [ ] review / merge relationship signals
- [ ] collaboration graph shifts
- [ ] project-quality weighting

## v0.5 — Watch

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
