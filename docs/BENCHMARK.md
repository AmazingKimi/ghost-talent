# Ghost Talent Benchmark

> **Governing protocol:** [`BENCHMARK_PROTOCOL_v2.md`](BENCHMARK_PROTOCOL_v2.md) is the single source of truth for benchmark design, evaluation, controls, adjudication, reporting, and evidence eligibility. This file is the operational registry/status page. If a summary here conflicts with protocol v2, protocol v2 governs.

## Current status

No 30/90/180-day outcome horizon has matured. **Predictive validity is not established.**

Six historical prospective freeze records are recorded: one under score version `0.1.5` and five under `0.2.8`. Public `main` currently contains a full member-level cohort file only for the distributed-training v0.2.8 cohort.

For v0.2.8, **20/100 recorded positions are member-by-member inspectable in this repository**. The four unpublished v0.2.8 member files do not have a public SHA-256 commitment at protocol-v2 adoption time; their member-level artifact existence is therefore treated as **unverified from public evidence**, not as cryptographically committed evidence. They are not eligible for headline predictive-validity claims under v2 unless an original artifact is recovered with defensible provenance. They must never be reconstructed from later API data.

## Registry

| Benchmark ID | Query | Source snapshot | As-of | Score | Positions | Full file public? | SHA-256 commitment |
|---|---|---|---|---:|---:|---|---|
| `2026-09-08-cuda-triton-v01` | `LLM inference CUDA Triton` | `20260907T162245054462Z-b36e731d` | `2026-09-07T16:22:45.054462Z` | 0.1.5 | 20 | No | not available from public repo |
| `2026-09-08-llm-inference-cuda-triton-v028` | `LLM inference CUDA Triton` | `20260908T005128477579Z-fd9bc3d3` | `2026-09-08T00:51:28.477579Z` | 0.2.8 | 20 | No | unverified; publish immediately only if original artifact is recovered |
| `2026-09-08-ai-compiler-runtime-v028` | `AI compiler runtime` | `20260908T005340535599Z-29700119` | `2026-09-08T00:53:40.535599Z` | 0.2.8 | 20 | No | unverified; publish immediately only if original artifact is recovered |
| `2026-09-08-quantization-kernels-v028` | `quantization kernels` | `20260908T005531156995Z-7dbcac45` | `2026-09-08T00:55:31.156995Z` | 0.2.8 | 20 | No | unverified; publish immediately only if original artifact is recovered |
| `2026-09-08-inference-infrastructure-v028` | `inference infrastructure` | `20260908T005721112409Z-09e4b189` | `2026-09-08T00:57:21.112409Z` | 0.2.8 | 20 | No | unverified; publish immediately only if original artifact is recovered |
| `2026-09-08-distributed-training-systems-v028` | `distributed training systems` | `20260908T033259838534Z-0675dccf` | `2026-09-08T03:32:59.838534Z` | 0.2.8 | 20 | [`cohort.json`](../benchmarks/2026-09-08-distributed-training-systems-v028/cohort.json) | historical artifact predates v2 hash-at-freeze requirement |

The five v0.2.8 cohorts were created in one execution window and are **not independent temporal replications**. Candidates may overlap. No pooled metric may be published until a stable-identity deduplicating evaluator exists.

## Protocol-v2 gates

Protocol v2 deliberately makes future validation harder:

- 90 days is the primary horizon; 30/180 are secondary.
- Future v2 rounds require naive baselines plus a same-population random control for at least one query per round.
- The existing 2026-09-08 cohorts had no synchronized random control at T0 and therefore cannot by themselves satisfy the v2 headline-validity gate.
- Outcome adjudication must be blind to Ghost/Radar scores, recommendation state, and scored/control status; inability to blind must be disclosed.
- Pooled metrics require stable-subject deduplication.
- Every new v2 cohort must publish the full artifact and SHA-256 commitment at freeze time.
- Wins, misses, null results, and protocol failures receive equal publication prominence.

These v2 rules were adopted after the 2026-09-08 freezes but before any outcome horizon matured. They must not be misrepresented as original T0 design choices.

## Existing tooling versus protocol

Current tooling supports immutable cohort creation, single-cohort outcome templates/evaluation, 30/90/180 horizons, and simple follower/star/raw-contribution baselines.

Protocol v2 additionally requires code enforcement before any v2 headline claim: random-control generation, blind templates, outcome-field/T0 validation, pooled stable-identity deduplication, artifact SHA-256 generation/verification, and exclusion of ineligible historical cohorts. Until those are implemented and tested, the protocol is a stricter publication gate than the software.

## Historical commands

```bash
ghost-talent-benchmark prospective-batch

ghost-talent-benchmark outcome-template \
  --benchmark-id "2026-09-08-distributed-training-systems-v028" \
  --horizon-days 90

ghost-talent-benchmark evaluate \
  --benchmark-id "2026-09-08-distributed-training-systems-v028" \
  --outcomes path/to/outcomes-90d.json
```

See [`BENCHMARK_PROTOCOL_v2.md`](BENCHMARK_PROTOCOL_v2.md) before interpreting any result produced by these commands.
