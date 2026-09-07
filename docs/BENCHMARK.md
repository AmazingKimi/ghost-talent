# Ghost Talent Benchmark v0.1

The benchmark exists to test a falsifiable claim:

> Can Ghost Talent identify later-breakout technical people earlier than simple visibility baselines?

It is not a leaderboard for hiring decisions. It is a longitudinal research protocol over public technical evidence.

## 1. Freeze first, evaluate later

Every benchmark cohort is created from an immutable Scout snapshot. The cohort stores:

- benchmark ID
- original query
- source snapshot ID
- `as_of_date`
- score version(s)
- frozen rank
- Ghost Score and Radar Score
- component scores
- first-detected date
- simple baseline values: followers, top-repository stars, raw contributions
- evaluation horizons
- outcome-definition version

A frozen `cohort.json` must never be overwritten. Methodology changes require a new benchmark ID/version.

## 2. Evaluation horizons

Default horizons are:

- 30 days
- 90 days
- 180 days

Longer horizons may be added later, but headline comparisons must state the horizon explicitly.

## 3. Breakout Outcome v0.1

A candidate may be marked `breakout=true` only when later public evidence supports a meaningful technical-impact transition. Accepted outcome types include:

- `maintainer_or_core_role` — became a maintainer/core contributor in an important public project
- `major_oss_contribution` — produced clearly substantive public technical work with externally visible adoption or responsibility
- `project_breakout` — created or became a key contributor to a project that achieved substantial technical adoption
- `research_breakout` — later research impact became materially stronger and is supported by public evidence
- `public_role_transition` — a publicly verifiable move into a technically significant AI lab/startup/team, used only as one observable outcome rather than a hiring-quality judgment

Every positive outcome must keep at least one public evidence URL and, where possible, a breakout date. Ambiguous cases remain unadjudicated rather than being forced positive or negative.

The benchmark must not use sensitive personal attributes.

## 4. No future leakage

The frozen ranking may use only information present in the original snapshot. Later evidence is used exclusively to evaluate outcomes.

Never:

- recompute the old cohort with a newer score version
- insert later GitHub activity into the original score
- replace misses after the fact
- change the breakout definition after seeing results without creating a new benchmark version

## 5. Baselines

Ghost Talent must be compared with simple alternatives available at freeze time:

- GitHub followers
- top-repository stars
- raw contribution count

These baselines are intentionally simple. If Ghost Talent cannot beat them reliably, the predictive-validity claim is not established.

## 6. Metrics

Benchmark v0.1 supports:

- Precision@5
- Precision@10
- Precision@20
- overall breakout rate
- mean Breakout Lead Time for positive outcomes
- the same Precision@K calculations for followers, stars, and raw contributions

Calibration and score-bucket analysis remain future extensions.

## 7. Commands

Freeze the latest local snapshot for a query:

```bash
ghost-talent-benchmark freeze \
  --query "LLM inference CUDA Triton" \
  --benchmark-id "2026-09-08-cuda-triton-v01" \
  --top-k 20
```

This writes:

```text
benchmarks/<benchmark-id>/cohort.json
```

The file is created with exclusive-write semantics. Re-running the same benchmark ID fails instead of rewriting history.

Generate a future outcome-adjudication template:

```bash
ghost-talent-benchmark outcome-template \
  --benchmark-id "2026-09-08-cuda-triton-v01" \
  --horizon-days 90
```

After outcomes are independently reviewed and saved as JSON, evaluate them:

```bash
ghost-talent-benchmark evaluate \
  --benchmark-id "2026-09-08-cuda-triton-v01" \
  --outcomes path/to/outcomes-90d.json
```

## 8. Publication rule

Wins and misses stay published. A benchmark result is not considered evidence of predictive validity unless the frozen cohort, outcome rubric, evaluation horizon, and baseline comparison are all available for inspection.
