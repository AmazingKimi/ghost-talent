# Ghost Score

Ghost Score is the public scoring framework behind Ghost Talent.

It is designed for **early technical talent discovery**, not role fit, résumé screening, or employment decisions.

The core question is:

> Who is demonstrating real technical capability and accelerating momentum before conventional visibility makes them obvious?

## Formula

`Ghost Score = 0.35 Capability + 0.35 Momentum + 0.20 Visibility Gap + 0.10 Evidence Confidence`

All dimensions are normalized to 0–100.

## Dimensions

### Capability — 35%

Evidence-backed technical strength visible in public work.

Current signals include repository contribution evidence and, where available, merged pull-request quality. Raw contribution count alone is deliberately insufficient.

### Momentum — 35%

Whether observable technical activity is accelerating relative to the candidate's own recent baseline.

Momentum is intended to distinguish a person who is becoming more active or important from someone whose historical activity is merely large.

### Visibility Gap — 20%

The mismatch between demonstrated technical strength and current public visibility.

A high Visibility Gap is the defining Ghost Talent condition: the evidence is stronger than the market attention.

### Evidence Confidence — 10%

How much trustworthy public evidence supports the record.

Missing evidence stays missing. Cross-source identity uncertainty must never be silently converted into certainty.

## Contribution Quality

Contribution Quality is a supporting technical-quality signal rather than a popularity metric.

Where public evidence is available, Ghost Talent inspects merged pull requests, changed-file scope, and technical paths such as CUDA, Triton, kernels, compilers, inference, attention, GEMM, MoE, quantization, GPU code and benchmarks.

A large number of commits does not automatically imply high technical quality.

## Ghost Radar

Ghost Score describes the current evidence-backed profile. Ghost Radar asks which people look unusually early and worth watching now.

`Ghost Radar = 0.35 Momentum + 0.30 Contribution Quality + 0.25 Visibility Gap + 0.10 Evidence Confidence`

The current `EARLY SIGNAL` gate requires:

- merged-PR quality evidence is available
- Momentum >= 60
- Visibility Gap >= 45
- Radar Score >= 65

Activity alone is never enough for an EARLY SIGNAL.

## Interpretation

Ghost Score is not a prediction that someone will become famous, join a specific company, or succeed in a job.

It is a discovery signal for a narrower hypothesis:

> public technical evidence may reveal people whose capability and momentum are rising faster than their visibility.

## Versioning

Every score must carry a `score_version`.

Any material change to weights, inputs, normalization, thresholds, or evidence semantics requires a new score version. Historical snapshots keep the score version used at observation time.

## Historical evaluation

Ghost Talent is designed to be backtested.

Historical evaluation must use only evidence observable on or before the snapshot `as_of_date`. Future information may not be injected into an earlier ranking.

Planned benchmark metrics include:

- Precision@K
- breakout rate by rank bucket
- calibration by score range
- Breakout Lead Time
- comparison against followers, stars, and raw contribution count

Wins and misses should both remain visible.

## Non-goals

Ghost Score is not:

- a résumé score
- a hiring recommendation
- a sensitive-attribute model
- a popularity score
- a substitute for technical review
- a guarantee of future success

For the broader evidence and publication policy, see `docs/METHODOLOGY.md`.