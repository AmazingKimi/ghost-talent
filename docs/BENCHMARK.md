# Ghost Talent Benchmark v0.1

The benchmark exists to test a falsifiable claim:

> Can Ghost Talent identify later-breakout technical people earlier than simple visibility baselines?

It is not a leaderboard for hiring decisions. It is a longitudinal research protocol over public technical evidence.

## Current benchmark status

Ghost Talent currently has **six frozen prospective cohorts**: one legacy cohort under score version `0.1.5` and five cohorts under the current score version `0.2.8`.

No cohort has mature outcome results yet. Predictive validity is therefore **not established**.

For v0.2.8, **20/100 frozen cohort positions are currently member-by-member inspectable in this repository**. The remaining 80 positions have immutable freeze metadata recorded here but their original full cohort files are not currently public. Positions are not unique people: a candidate may appear in more than one cohort.

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

| Benchmark ID | Query | Source snapshot | As-of | Cohort | Public cohort file |
| --- | --- | --- | --- | ---: | --- |
| `2026-09-08-llm-inference-cuda-triton-v028` | `LLM inference CUDA Triton` | `20260908T005128477579Z-fd9bc3d3` | `2026-09-08T00:51:28.477579Z` | 20 | not currently in repo |
| `2026-09-08-ai-compiler-runtime-v028` | `AI compiler runtime` | `20260908T005340535599Z-29700119` | `2026-09-08T00:53:40.535599Z` | 20 | not currently in repo |
| `2026-09-08-quantization-kernels-v028` | `quantization kernels` | `20260908T005531156995Z-7dbcac45` | `2026-09-08T00:55:31.156995Z` | 20 | not currently in repo |
| `2026-09-08-inference-infrastructure-v028` | `inference infrastructure` | `20260908T005721112409Z-09e4b189` | `2026-09-08T00:57:21.112409Z` | 20 | not currently in repo |
| `2026-09-08-distributed-training-systems-v028` | `distributed training systems` | `20260908T033259838534Z-0675dccf` | `2026-09-08T03:32:59.838534Z` | 20 | [`cohort.json`](../benchmarks/2026-09-08-distributed-training-systems-v028/cohort.json) |

The fifth current-model cohort was produced by the GitHub Actions prospective runner after the source-resilience fixes. The workflow reported `status: complete`, score version `0.2.8`, cohort size 20, and committed its immutable cohort evidence to `main`.

The first four v0.2.8 cohorts were frozen before automated artifact publication was added. Their freeze metadata is retained above, but their full local cohort files are **not claimed to be publicly inspectable** from this repository. They must not be reconstructed from later evidence merely to close that publication gap.

Accordingly, distinguish these claims:

- **Frozen:** five v0.2.8 cohorts have immutable freeze records.
- **Publicly inspectable in this repository:** the distributed-training v0.2.8 cohort file is currently public; the earlier four full cohort files are not.
- **Validated:** none. Outcome horizons have not matured.

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

The outcome rubric is part of the benchmark version, not something to be chosen after results are observed. Existing cohorts retain `outcome_definition_version: 0.1`. Any substantive change to the outcome definition creates a new outcome-definition version and **cannot be retroactively used as the headline evaluation of cohorts frozen under v0.1**.

## 2. Evaluation horizons and execution-time dependence

Default horizons are 30, 90, and 180 days.

Longer horizons may be added later, but headline comparisons must state the horizon explicitly.

The five v0.2.8 cohorts were frozen in one execution window on 2026-09-08. They are **not independent replications across time**. Shared API state, source availability, or pipeline defects could affect several cohorts simultaneously. They test query-domain breadth under one execution period, not temporal replication.

Future benchmark rounds intended as replication must be frozen on different dates/execution sessions. Results from those later rounds must be reported separately before any pooled cross-time claim is made.

## 3. Breakout Outcome v0.1 — pre-registered adjudication rule

Outcome Definition v0.1 is frozen for the existing cohorts as of this protocol revision and must not be loosened after inspecting candidate outcomes.

A candidate may be marked `breakout=true` only when **new public evidence after the cohort `as_of_date`** establishes at least one of the following pre-registered outcome types:

- `maintainer_or_core_role` — public project records show the candidate newly obtained maintainer/core-committer responsibility after T0;
- `major_oss_contribution` — after T0, the candidate produced a substantive implementation contribution accepted into an external project, with public evidence of merge/acceptance and technical scope;
- `project_breakout` — after T0, the candidate created or became a key contributor to a public technical project that subsequently shows externally observable adoption/responsibility evidence;
- `research_breakout` — after T0, a research contribution receives a materially new public impact signal, with attributable public evidence;
- `public_role_transition` — after T0, a publicly verifiable move into a technically significant AI research/engineering role, treated only as an observable transition rather than a hiring-quality judgment.

A positive adjudication requires:

1. at least one public evidence URL;
2. evidence attributable to the same candidate under the benchmark's identity rules;
3. evidence whose relevant event occurred after T0;
4. an `outcome_type` from the list above;
5. a breakout date when the public evidence permits one.

Evidence that merely restates information already observable at T0 is **not** a breakout. Ambiguous identity, ambiguous timing, or ambiguous technical significance remains `unadjudicated`; it must not be forced into a positive result.

A candidate is a **miss at a stated horizon** only when the horizon has elapsed, the candidate has been reviewed under this same v0.1 rubric, and no qualifying post-T0 breakout evidence was found. Missing review is not a miss and is not a win.

The rubric intentionally uses categorical public-impact events rather than a single follower threshold. This creates adjudication judgment; therefore future published outcome files must retain the evidence URLs and outcome type so a third party can challenge each label.

The benchmark must not use sensitive personal attributes.

## 4. No future leakage

The frozen ranking may use only information present in the original snapshot. Later evidence is used exclusively to evaluate outcomes.

Never:

- recompute an old cohort with a newer score version;
- insert later GitHub activity into the original score;
- replace misses after the fact;
- reconstruct a missing historical cohort file from later data and present it as the original artifact;
- change the breakout definition after seeing results and apply it retroactively to improve the headline result;
- promote an outcome signal that was already observable at T0 into a post-T0 breakout.

If Outcome Definition v0.1 later proves too subjective or flawed, that failure must be reported. A revised definition belongs to a new benchmark/outcome version rather than rewriting the existing test.

## 5. Cohort overlap and aggregation rule

Cohort positions are **not statistically independent observations**. The same person may appear in multiple query cohorts, and the legacy cohort may overlap with v0.2.8 cohorts.

Therefore two different result types must remain separate:

1. **Per-cohort metrics.** Precision@K is computed within each frozen query cohort. A person's outcome may legitimately affect each cohort in which that person was originally ranked, because the metric answers a query-specific ranking question. These per-cohort numbers must not be summed and described as independent predictions.
2. **Cross-cohort headline metrics.** Any pooled person-level breakout rate, count, or model-level headline across multiple cohorts must deduplicate candidates by stable subject identity before calculation. One real-world breakout may count at most once in a pooled unique-person metric. The publication must report both total cohort positions and unique candidate count.

Cross-version comparison follows the same rule. A candidate appearing in both v0.1.5 and v0.2.8 cannot be presented as two independent breakout events in a pooled comparison. Version-specific cohort results may still be shown, but overlap must be disclosed and a deduplicated sensitivity view must accompany any cross-version conclusion.

The current evaluator computes a **single cohort at a time**. It does not yet implement pooled multi-cohort aggregation. Until a deduplicating pooled evaluator exists, Ghost Talent must not publish a pooled Precision@K or pooled breakout rate across the five v0.2.8 cohorts.

## 6. Baselines

Ghost Talent must be compared with simple alternatives available at freeze time:

- GitHub followers
- top-repository stars
- raw contribution count

These baselines are intentionally simple. If Ghost Talent cannot beat them reliably, the predictive-validity claim is not established.

## 7. Metrics

Benchmark v0.1 supports per-cohort:

- Precision@5
- Precision@10
- Precision@20
- overall breakout rate
- mean Breakout Lead Time for positive outcomes
- the same Precision@K calculations for followers, stars, and raw contributions

No pooled multi-cohort metric is currently supported or claimed. Calibration, uncertainty intervals, unique-person pooled analysis, and score-bucket analysis remain future extensions.

## 8. Publication and missing-artifact rule

For cohorts whose full frozen file is public, wins and misses must stay public together with the frozen cohort, rubric version, horizon, evidence URLs, and baseline comparison.

For the four v0.2.8 cohorts whose original full files are currently missing from the public repository, Ghost Talent makes a stronger anti-selection commitment:

- if the original frozen files can later be recovered byte-for-byte from the original local artifacts/backups, they will be published with provenance and hashes;
- they will **not** be reconstructed from later API data;
- if they cannot be recovered, they remain permanently classified as `metadata-only / not independently inspectable`;
- their future outcomes may be reported as exploratory records, but **must not be included in headline predictive-validity claims or pooled benchmark metrics that imply independent public verification**.

This rule prevents selective publication from turning missing artifacts into an advantage. A good-looking result does not upgrade a metadata-only cohort into validated evidence.

All future prospective cohorts created after automated publication support must publish their full frozen cohort artifact at freeze time. A run that fails to publish the artifact is not eligible for the publicly verifiable benchmark set.

## 9. Automation and commands

The prospective cohort workflow runs in GitHub Actions and publishes run evidence. Successful new cohort artifacts are committed to `main`; failed or incomplete runs must remain visible rather than silently producing degraded cohorts.

Freeze the default current-model prospective batch locally when needed:

```bash
ghost-talent-benchmark prospective-batch
```

Generate a future outcome-adjudication template:

```bash
ghost-talent-benchmark outcome-template \
  --benchmark-id "2026-09-08-distributed-training-systems-v028" \
  --horizon-days 90
```

After outcomes are independently reviewed and saved as JSON, evaluate them:

```bash
ghost-talent-benchmark evaluate \
  --benchmark-id "2026-09-08-distributed-training-systems-v028" \
  --outcomes path/to/outcomes-90d.json
```

## 10. Publication rule

A benchmark result is not considered evidence of predictive validity unless the frozen cohort, pre-registered outcome rubric, evaluation horizon, member-level adjudication evidence, and baseline comparison are all available for inspection.

Documentation must distinguish **frozen**, **publicly inspectable**, and **validated**. A tooling change, successful command, frozen metadata record, or unpublished cohort is not by itself evidence of predictive validity.

The correct current public wording is:

> **Six prospective cohort freeze records exist — one under v0.1.5 and five under v0.2.8. For v0.2.8, only 20/100 frozen positions are currently member-by-member inspectable in this repository; the other 80 positions are metadata-only here and are ineligible for headline predictive-validity claims unless their original frozen artifacts are recovered and published with provenance. No outcome horizon has matured, so predictive validity is not established.**
