# Ghost Talent Roadmap

Ghost Talent is being built as an open-source emerging AI talent intelligence research system and benchmark, not a generic recruiting search tool.

The roadmap is intentionally public so methodology changes, product scope, benchmark milestones, wins, and misses can be inspected over time.

## Current research status

- Active scoring model: **0.2.7**
- First real prospective benchmark cohort: **frozen and immutable**
- Benchmark ID: `2026-09-08-cuda-triton-v01`
- Cohort size: 20
- Frozen score version: `0.1.5`
- 30 / 90 / 180-day outcomes: **not yet mature**
- Predictive validity: **not yet established**

The frozen v0.1.5 cohort will never be recomputed with later scoring versions.

## v0.1 — Public foundation

Status: complete as the original public foundation; later scoring semantics have evolved.

- [x] GitHub repository discovery
- [x] contributor discovery
- [x] merged-PR author discovery
- [x] OpenAlex research evidence
- [x] deterministic, versioned Ghost Score
- [x] explainable score drivers
- [x] repository dominance control
- [x] immutable Scout snapshots
- [x] first-detected ledger
- [x] Ghost Radar / recommendation states
- [x] local macOS convenience launcher
- [x] explicit source-status reporting
- [x] conservative identity handling
- [x] subject IDs across evidence records

## v0.2 — Evidence quality and credibility

Goal: reduce obvious false positives before claiming predictive value.

- [x] separate Internal Capability from External Validation
- [x] Evidence Mix for self-owned vs external evidence
- [x] external merged-PR evidence
- [x] recognized-upstream context
- [x] changed-file core-path inspection
- [x] owner/member maintainer-approval evidence
- [x] substantive-change gate for inspected upstream PRs
- [x] exclude docs/tests/examples/CI from core-path evidence
- [x] exclude stars/forks/general issue activity from Momentum
- [x] stop inferring acceleration when prior history is missing
- [x] report/cap 100-event-truncated Momentum history
- [x] route already-visible candidates to `PROVEN / ALREADY VISIBLE`
- [x] adversarial / anti-gaming test plan
- [x] component-correlation analysis tooling
- [x] retrospective-validation protocol
- [x] responsible-use / employment-decision boundary
- [ ] complete a documented identity-resolution audit sample
- [ ] migrate all longitudinal history keys to stable GitHub numeric identity where available
- [ ] expand project-quality evidence beyond a curated upstream allowlist

## v0.3 — Prospective benchmark

Goal: test whether Ghost Talent actually identifies later-breakout technical people earlier than simple visibility/activity baselines.

- [x] frozen benchmark cohort format and immutable freeze command
- [x] versioned Breakout Outcome v0.1 definition
- [x] Precision@K evaluation engine
- [x] comparison against followers / stars / raw contributions
- [x] Breakout Lead Time calculation
- [x] outcome-adjudication template
- [x] no-future-leakage publication protocol
- [x] **freeze first real production cohort from local Scout history**
- [ ] freeze additional prospective cohorts under the current scoring model
- [ ] 30-day outcome adjudication
- [ ] 90-day outcome adjudication
- [ ] 180-day outcome adjudication
- [ ] breakout rate by score / recommendation bucket
- [ ] calibration analysis
- [ ] publish wins and misses from mature cohorts
- [ ] reproducible public benchmark artifacts

First frozen cohort:

- benchmark ID: `2026-09-08-cuda-triton-v01`
- query: `LLM inference CUDA Triton`
- source snapshot: `20260907T162245054462Z-b36e731d`
- as-of: `2026-09-07T16:22:45.054462Z`
- cohort size: 20
- score version: `0.1.5`

Protocol: [`BENCHMARK.md`](BENCHMARK.md)

## v0.4 — Historical and multi-source validation

Goal: test signal plausibility sooner without contaminating the prospective benchmark.

- [x] retrospective-validation protocol with historical-observability rules
- [ ] construct first leakage-audited retrospective dataset
- [ ] compare historical Ghost signals with historical followers/stars only where those values are actually recoverable
- [ ] publish failure cases and unavailable historical fields rather than impute them
- [ ] stronger GitHub identity graph
- [ ] arXiv / additional scholarly sources
- [ ] cross-project contribution graph
- [ ] review / merge relationship signals
- [ ] collaboration graph shifts
- [ ] project-quality weighting

Retrospective work is a plausibility/calibration aid. It does not replace the prospective 30 / 90 / 180-day benchmark.

## v0.5 — Watch and workflow

These features are deliberately secondary until signal quality is better established.

- [x] query watchlist runner
- [ ] candidate watchlists
- [ ] score-change alerts
- [ ] new high-quality PR alerts
- [ ] maintainer-status changes
- [ ] paper / research trajectory changes
- [ ] large Radar delta alerts
- [ ] persistent local cache
- [ ] source degradation history
- [ ] automatic scheduling

ATS/CRM integration, automated outreach, and employment-decision automation are not current priorities. Any future workflow integration requires a separate privacy, compliance, retention, correction, and human-review design.

## Research questions

1. Can externally validated contribution depth outperform raw activity volume?
2. Can validated trajectory add information beyond short-term GitHub activity?
3. Does Visibility Gap add independent information beyond Capability and follower count?
4. How correlated are Internal Capability, External Validation, Momentum, Ghost Score, and Radar in real cohorts?
5. How much lead time can a public-evidence system achieve before a candidate becomes broadly visible?
6. Which signals survive adversarial behavior and source truncation?
7. How often does cross-source identity resolution fail or remain uncertain?

## Non-goals

Ghost Talent is not currently trying to become:

- a LinkedIn scraper
- an automated outreach bot
- an employment decision system
- a sensitive-attribute inference engine
- a black-box résumé ranker
- an ATS/CRM replacement

## Publication rule

Do not describe benchmark infrastructure as benchmark success.

The correct current statement is:

> **The first real prospective cohort is frozen; outcome results have not matured yet.**

Predictive-validity claims require frozen cohorts, explicit outcome rules, a stated evaluation horizon, and baseline comparisons. Wins and misses both stay visible.
