# Ghost Talent Credibility Phase

The current priority is not feature expansion. It is evidence that the system behaves sensibly now and can later be judged honestly against future outcomes.

## A. Public-methodology alignment

Completed in the current repository:

- README reflects score version 0.2.6.
- Ghost Score documentation reflects External Validation, Evidence Mix, recommendation gates, and PROVEN / ALREADY VISIBLE.
- Methodology explicitly states that current thresholds are hypotheses, not calibrated probabilities.
- "historical moat" language is downgraded to prospective evaluation infrastructure until evidence exists.

## B. Adversarial sanity suite

Public test categories are defined in `docs/ADVERSARIAL_TESTS.md` and backed by regression tests where deterministic fixtures are sufficient.

Required invariants include:

- activity-only cannot produce EARLY / STRONG,
- self-owned activity is not external validation,
- already-visible strong candidates route to PROVEN,
- noise blocks recommendation,
- missing external validation caps confidence,
- strong emerging recommendations require recent external technical validation.

## C. Component-correlation audit

`ghost_talent.credibility` can compute pairwise Pearson correlations across score components from immutable snapshot rows.

Important pairs:

- Internal Capability ↔ Momentum,
- External Validation ↔ Capability,
- External Validation ↔ Momentum,
- Ghost Score ↔ Radar.

Absolute correlation >= 0.85 is flagged for diagnostic review by default.

This is not predictive validation. It is a check for duplicated weighting / dimension collapse.

## D. Identity audit

For any manual identity sample, record:

| GitHub login | Proposed external identity | Status | Public linking evidence | Reviewer note |
| --- | --- | --- | --- | --- |
| example | example | verified / uncertain / wrong | URL or explicit cross-link | note |

Rules:

- name-only match is never "verified",
- uncertain matches remain uncertain,
- wrong matches remain in the audit report,
- published error rates must state sample size and sampling method.

Do not publish an identity-accuracy percentage until a real manual sample has been reviewed.

## E. Prospective cohort matrix

The existing cohort remains immutable:

- `2026-09-08-cuda-triton-v01`
- score version `0.1.5`
- never recompute it.

For the current v0.2.6 model, the recommended next prospective areas are:

1. `CUDA Triton inference kernels`
2. `AI compiler runtime MLIR GPU`
3. `distributed training NCCL FSDP systems`
4. `quantization kernels inference optimization`
5. `LLM serving runtime scheduler KV cache`

Each cohort must be created only from a snapshot that already exists at freeze time. Do not backfill a historical cohort with evidence collected later.

Suggested IDs:

- `2026-09-08-cuda-triton-v026`
- `2026-09-08-ai-compiler-runtime-v026`
- `2026-09-08-distributed-training-v026`
- `2026-09-08-quant-kernels-v026`
- `2026-09-08-llm-serving-v026`

Example after a local Scout snapshot exists:

```bash
ghost-talent-benchmark freeze \
  --query "CUDA Triton inference kernels" \
  --benchmark-id "2026-09-08-cuda-triton-v026" \
  --top-k 20
```

Repeat only for queries that have a real current snapshot. The CLI's immutable write semantics should reject accidental overwrite.

## F. 30 / 90 / 180-day publication

When outcome windows mature, publish at minimum:

- Precision@5 / @10 / @20,
- breakout rate,
- Breakout Lead Time,
- followers baseline,
- stars baseline,
- raw contribution baseline,
- wins,
- misses.

Negative results must remain visible.

## G. What not to claim yet

Do not claim:

- validated predictive accuracy,
- superiority to recruiters or technical leads,
- a proven historical moat,
- calibrated probabilities of future success,
- enterprise readiness.

Those claims require prospective outcome evidence.

## H. Next model research question

The most important unresolved model question is whether **activity acceleration** can be separated from **validated trajectory**.

A future validated-trajectory signal should reward changes such as:

- peripheral files → core technical paths,
- self-owned work → external accepted work,
- ordinary external PR → maintainer-approved PR,
- one important upstream → multiple independent important upstreams,
- stale validation → recent validation.

This should only become a score component after enough longitudinal data exists to test whether it adds information rather than duplicating current External Validation and Momentum.
