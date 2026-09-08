# Ghost Talent Benchmark Registry

This file is the operational registry and status summary for Ghost Talent prospective benchmarks.

The governing methodology is [`BENCHMARK_PROTOCOL_v2.md`](BENCHMARK_PROTOCOL_v2.md). If this registry conflicts with the protocol, the protocol governs.

## Current status

Six historical prospective freeze records are recorded: one legacy record under score version `0.1.5` and five under `0.2.8`.

Only **one complete cohort file is currently public in the repository**: `2026-09-08-distributed-training-systems-v028`.

That means:

- **20/120 recorded positions overall** are currently member-by-member inspectable from public repository artifacts;
- within v0.2.8, **20/100** are currently member-by-member inspectable;
- the legacy cohort and four other v0.2.8 cohorts have historical freeze metadata but no public member file and no public pre-outcome SHA-256 commitment at protocol-v2 adoption time;
- those five unpublished member artifacts are therefore classified as **`existence-unverified from public evidence`** until an original artifact is recovered with defensible provenance;
- no 30/90/180-day outcome horizon has matured;
- predictive validity is **not established**.

## Cohort registry

| Benchmark ID | Query | Score version | Positions | As-of | Public full file | SHA-256 commitment | Eligibility for headline validity |
| --- | --- | --- | ---: | --- | --- | --- | --- |
| `2026-09-08-cuda-triton-v01` | `LLM inference CUDA Triton` | `0.1.5` | 20 | `2026-09-07T16:22:45.054462Z` | No | No | Ineligible unless original artifact recovered with provenance |
| `2026-09-08-llm-inference-cuda-triton-v028` | `LLM inference CUDA Triton` | `0.2.8` | 20 | `2026-09-08T00:51:28.477579Z` | No | No | Ineligible unless original artifact recovered with provenance |
| `2026-09-08-ai-compiler-runtime-v028` | `AI compiler runtime` | `0.2.8` | 20 | `2026-09-08T00:53:40.535599Z` | No | No | Ineligible unless original artifact recovered with provenance |
| `2026-09-08-quantization-kernels-v028` | `quantization kernels` | `0.2.8` | 20 | `2026-09-08T00:55:31.156995Z` | No | No | Ineligible unless original artifact recovered with provenance |
| `2026-09-08-inference-infrastructure-v028` | `inference infrastructure` | `0.2.8` | 20 | `2026-09-08T00:57:21.112409Z` | No | No | Ineligible unless original artifact recovered with provenance |
| `2026-09-08-distributed-training-systems-v028` | `distributed training systems` | `0.2.8` | 20 | `2026-09-08T03:32:59.838534Z` | [`cohort.json`](../benchmarks/2026-09-08-distributed-training-systems-v028/cohort.json) | Pending pre-outcome publication | Publicly inspectable, but not protocol-v2-valid by itself |

## Historical limitations

The five v0.2.8 cohorts were frozen in one execution window. They are not independent temporal replications.

They also had no synchronized random-control cohort at T0. A control sampled later must not be described as their contemporaneous random control. Therefore these historical cohorts cannot by themselves satisfy the protocol-v2 headline-validity gate.

The governing protocol was adopted after these freezes but before any outcome horizon matured. Requirements introduced by v2 must not be backdated to T0.

## Outcome evaluation

The existing cohort artifacts carry `outcome_definition_version: 0.1` where available. Protocol v2 operationalizes the outcome rules before any horizon matures, with adoption timing disclosed.

Primary future v2 headline endpoint:

- 90-day qualifying-breakout proportion across the full preregistered scored cohort;
- compared against an eligible synchronized random control;
- two-sided Fisher exact test at `alpha = 0.05`;
- effect size, Wilson 95% intervals, and full denominators reported alongside the p-value.

A nonsignificant result is inconclusive, not proof of equivalence.

## Publication rule

Positive, negative, and statistically inconclusive results receive equal publication prominence.

A result is not eligible as headline evidence of predictive validity unless all applicable artifacts, controls, adjudication evidence, protocol timing, baseline comparisons, integrity commitments, and statistical details required by protocol v2 are public.

Historical unpublished cohorts may remain in this registry for transparency, but missing member artifacts cannot be upgraded by later good-looking outcomes.

## Commands

Freeze prospective cohorts:

```bash
ghost-talent-benchmark prospective-batch
```

Generate an outcome template:

```bash
ghost-talent-benchmark outcome-template \
  --benchmark-id "2026-09-08-distributed-training-systems-v028" \
  --horizon-days 90
```

Evaluate adjudicated outcomes:

```bash
ghost-talent-benchmark evaluate \
  --benchmark-id "2026-09-08-distributed-training-systems-v028" \
  --outcomes path/to/outcomes-90d.json
```

Current code does **not yet implement all protocol-v2 enforcement requirements**. See §10 of [`BENCHMARK_PROTOCOL_v2.md`](BENCHMARK_PROTOCOL_v2.md).
