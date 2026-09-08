# Ghost Talent Benchmark v0.1

The benchmark exists to test a falsifiable claim:

> Can Ghost Talent identify later-breakout technical people earlier than simple visibility baselines?

It is not a leaderboard for hiring decisions. It is a longitudinal research protocol over public technical evidence.

## Current benchmark status

Ghost Talent now has one legacy prospective cohort frozen under score version `0.1.5` and four additional prospective cohorts frozen under the current score version `0.2.8`.

No cohort has mature outcome results yet. Predictive validity is therefore **not established**.

### Legacy cohort — score version 0.1.5

- benchmark ID: `2026-09-08-cuda-triton-v01`
- query: `LLM inference CUDA Triton`
- source snapshot ID: `20260907T162245054462Z-b36e731d`
- snapshot as-of: `2026-09-07T16:22:45.054462Z`
- frozen at: `2026-09-07T16:22:56.618965Z`
- cohort size: 20
- score version: `0.1.5`
- evaluation horizons: 30 / 90 / 180 days
- outcome definition version: `0.1`
- status: `frozen — outcomes not yet mature`

This cohort remains immutable and must never be recomputed with a later model.

### Current-model cohorts — score version 0.2.8

The following cohorts were frozen on 2026-09-08 from fresh Scout runs using score version `0.2.8`:

| Benchmark ID | Query | Source snapshot | As-of | Cohort |
| --- | --- | --- | --- | ---: |
| `2026-09-08-llm-inference-cuda-triton-v028` | `LLM inference CUDA Triton` | `20260908T005128477579Z-fd9bc3d3` | `2026-09-08T00:51:28.477579Z` | 20 |
| `2026-09-08-ai-compiler-runtime-v028` | `AI compiler runtime` | `20260908T005340535599Z-29700119` | `2026-09-08T00:53:40.535599Z` | 20 |
| `2026-09-08-quantization-kernels-v028` | `quantization kernels` | `20260908T005531156995Z-7dbcac45` | `2026-09-08T00:55:31.156995Z` | 20 |
| `2026-09-08-inference-infrastructure-v028` | `inference infrastructure` | `20260908T005721112409Z-09e4b189` | `2026-09-08T00:57:21.112409Z` | 20 |

The planned `distributed training systems` cohort was not frozen in the same batch because GitHub evidence became unavailable during collection. It remains pending rather than being filled with degraded or partial evidence.

The current-model cohorts are the relevant prospective test of the stricter v0.2.8 logic. The legacy v0.1.5 cohort remains useful as a historical model test, but its future result must not be used as direct validation of v0.2.8.

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

- recompute an old cohort with a newer score version
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

Freeze the default current-model prospective batch:

```bash
ghost-talent-benchmark prospective-batch
```

Retry only the pending distributed-training cohort:

```bash
ghost-talent-benchmark prospective-batch \
  --query "distributed training systems"
```

Generated cohort files are immutable. Re-running an existing benchmark ID reuses the frozen cohort rather than rewriting it.

Generate a future outcome-adjudication template:

```bash
ghost-talent-benchmark outcome-template \
  --benchmark-id "2026-09-08-llm-inference-cuda-triton-v028" \
  --horizon-days 90
```

After outcomes are independently reviewed and saved as JSON, evaluate them:

```bash
ghost-talent-benchmark evaluate \
  --benchmark-id "2026-09-08-llm-inference-cuda-triton-v028" \
  --outcomes path/to/outcomes-90d.json
```

## 8. Publication rule

Wins and misses stay published. A benchmark result is not considered evidence of predictive validity unless the frozen cohort, outcome rubric, evaluation horizon, and baseline comparison are all available for inspection.

The correct current public wording is:

> **Five prospective cohorts are frozen in total — one under v0.1.5 and four under v0.2.8 — but outcome results have not matured yet.**
