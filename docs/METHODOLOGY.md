# Ghost Talent Methodology

Ghost Talent is an evidence-grounded system for discovering emerging AI engineers and researchers before conventional visibility signals make them obvious.

## Research question

Can public technical evidence identify people whose technical capability and momentum are rising faster than their market visibility?

## Core dimensions

Ghost Score is built from four independently inspectable dimensions:

- **Capability** — current technical strength inferred from public contribution evidence.
- **Momentum** — recent technical activity relative to the candidate's prior observable baseline.
- **Visibility Gap** — the gap between observed technical strength and conventional public visibility.
- **Evidence Confidence** — how much reliable public evidence supports the candidate record.

The current score is:

`0.35 Capability + 0.35 Momentum + 0.20 Visibility Gap + 0.10 Evidence Confidence`

Every published score must carry a `score_version`.

## Evidence standard

A score is not evidence by itself. Candidate records should retain the public source URL, observation time, evidence type, structured value and confidence. Concrete claims shown to users must be traceable to public evidence.

LLMs may explain evidence but must not invent evidence or silently replace deterministic scoring.

## Contribution quality

Raw commit or contribution volume is not treated as technical quality. Ghost Talent separately inspects merged pull-request evidence where available, including changed-file scope and technical-path signals such as CUDA, Triton, kernels, compilers, inference, attention, GEMM, MoE, quantization, GPU and benchmarks.

Missing contribution-quality evidence is reported as unavailable rather than estimated.

## Identity policy

A matching name alone is not sufficient proof that a paper author and GitHub account are the same person. Cross-source identities must eventually be supported by public linking evidence such as a homepage, institution, verified profile link or equivalent evidence. Ambiguous identities remain uncertain.

## Historical snapshots

Historical evaluation requires immutable, dated observations. A snapshot must record at minimum:

- snapshot timestamp / `as_of_date`
- query or cohort definition
- candidate identifier
- score version
- Ghost Score and component scores
- evidence references used at snapshot time
- source availability / degradation state

Published historical snapshots must never be retroactively rewritten to improve past predictions. Corrections or methodology changes create a new version or snapshot.

## No future leakage

A historical backtest may use only evidence observable on or before its `as_of_date`. Evidence discovered later cannot be injected into an earlier snapshot.

## Breakout evaluation

Future benchmark versions will measure whether high-ranked candidates later show independently observable breakout outcomes, for example becoming a maintainer of an important project, producing high-impact technical work, joining a high-quality technical team, or showing sustained research impact.

Primary planned metrics include:

- Precision@K
- breakout rate by rank bucket
- lead time before breakout
- calibration by Ghost Score range
- comparison against simple baselines such as followers, stars and raw contribution count

Outcome definitions must be versioned before they are used for headline claims.

## Publication rules

1. Evidence and score versions are explicit.
2. Missing data remains missing; it is not fabricated.
3. Source failures and rate limits are visible.
4. Historical snapshots are append-only.
5. Methodology changes are versioned.
6. Wins and failures are both retained.
7. Headline benchmark claims must be reproducible from published artifacts.

## Sensitive attributes

Ghost Talent does not infer or rank candidates using sensitive personal attributes such as race, ethnicity, religion, health, political beliefs, sexual orientation or similar traits.

## Current status

The project is early-stage. Score v0.1.3 introduces contribution-quality evidence. Historical snapshotting and formal backtesting are the next benchmark milestones.
