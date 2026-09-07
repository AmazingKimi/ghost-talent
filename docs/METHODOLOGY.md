# Ghost Talent Methodology

Ghost Talent is an evidence-grounded system for discovering emerging AI engineers and researchers before conventional visibility signals make them obvious.

## Research question

Can public technical evidence identify people whose technical capability and momentum are rising faster than their market visibility?

## Ghost Score

Ghost Score is built from four independently inspectable dimensions:

- **Capability** — current technical strength inferred from public contribution evidence.
- **Momentum** — recent technical activity relative to the candidate's prior observable baseline.
- **Visibility Gap** — the gap between observed technical strength and conventional public visibility.
- **Evidence Confidence** — how much reliable public evidence supports the candidate record.

Current formula:

`Ghost Score = 0.35 Capability + 0.35 Momentum + 0.20 Visibility Gap + 0.10 Evidence Confidence`

Every published score carries a `score_version`.

### Capability

Capability is not a raw contribution counter. Repository contribution intensity and project context establish a baseline, then contribution-quality evidence may raise the score when merged pull requests show technically substantive work.

### Momentum

Momentum compares recent public activity with an observable prior baseline and considers active-day density. It is intended to distinguish accelerating, stable and decelerating trajectories rather than reward permanent high volume.

### Visibility Gap

Visibility Gap compares technical evidence with conventional public visibility. Low followers alone do not create a strong score; there must also be capability evidence.

### Evidence Confidence

Evidence Confidence increases when multiple public signals support the record, such as a public GitHub identity, evidence across repositories, merged-PR evidence or research-paper matches. Ambiguous cross-source identity matches are not treated as certain.

## Contribution Quality

Raw commit or contribution volume is not treated as technical quality. Ghost Talent separately inspects merged pull-request evidence where available, including:

- number of merged pull requests
- changed-file scope
- technical-path coverage
- core implementation files
- change volume
- technical terms such as CUDA, Triton, kernels, compilers, inference, attention, GEMM, MoE, quantization, GPU and benchmarks

Missing contribution-quality evidence is reported as unavailable rather than estimated.

## Ghost Radar

Ghost Radar is a separate early-signal layer. It is not a replacement for Ghost Score.

Radar asks:

> Which candidates combine strong recent momentum, technical contribution quality and low current visibility strongly enough to deserve immediate attention?

Current formula:

`Radar Score = 0.35 Momentum + 0.30 Contribution Quality + 0.25 Visibility Gap + 0.10 Evidence Confidence`

`EARLY SIGNAL` is emitted only when all current hard gates are met:

- merged-PR contribution-quality evidence is available
- Momentum is at least 60
- Visibility Gap is at least 45
- Radar Score is at least 65

These gates are intentionally conservative. Activity volume by itself cannot produce an EARLY SIGNAL.

## Discovery

Current discovery uses multiple GitHub paths rather than a single contributor ranking:

1. repository search for the requested technical topic
2. contributor discovery across relevant repositories
3. recent merged-PR author discovery
4. bounded enrichment of candidate profiles and public activity
5. OpenAlex research evidence where a conservative public-name match is available

Repository dominance control limits how many candidates from one primary repository can occupy the final ranking before overflow is used.

## Evidence standard

A score is not evidence by itself. Candidate records should retain the public source URL, observation time, evidence type, structured value and confidence. Concrete claims shown to users must be traceable to public evidence.

LLMs may explain evidence but must not invent evidence or silently replace deterministic scoring.

## Identity policy

A matching name alone is not sufficient proof that a paper author and GitHub account are the same person. Cross-source identities must eventually be supported by public linking evidence such as a homepage, institution, verified profile link or equivalent evidence. Ambiguous identities remain uncertain.

## Historical snapshots

Every successful Scout run can create an immutable dated snapshot containing the ranking, component scores, score version, drivers and evidence references.

Candidate first-detection records are stored separately so the project can later prove when a person first entered the system.

Published historical snapshots are append-only. They must never be retroactively rewritten to improve past performance.

## No future leakage

A historical backtest may use only evidence observable on or before its `as_of_date`. Evidence discovered later cannot be injected into an earlier snapshot.

## Breakout evaluation

Future benchmark versions will measure whether high-ranked candidates later show independently observable breakout outcomes, for example:

- becoming a maintainer of an important project
- producing high-impact technical work
- sustained research impact
- increased responsibility across important open-source projects

Primary planned metrics include:

- Precision@K
- breakout rate by rank bucket
- Breakout Lead Time
- calibration by Ghost Score range
- comparison against simple baselines such as followers, stars and raw contribution count

Outcome definitions must be versioned before they are used for headline claims.

## Publication rules

1. Evidence and score versions are explicit.
2. Missing data remains missing; it is not fabricated.
3. Source failures and rate limits should be visible.
4. Historical snapshots are append-only.
5. Methodology changes are versioned.
6. Wins and failures are both retained.
7. Headline benchmark claims must be reproducible from published artifacts.

## Sensitive attributes

Ghost Talent does not infer or rank candidates using sensitive personal attributes such as race, ethnicity, religion, health, political beliefs, sexual orientation or similar traits.

## v0.1.0 methodology status

The public v0.1.0 milestone establishes the first versioned methodology for Ghost Score, contribution quality, Ghost Radar, immutable snapshots and first detection. The next major research milestones are score-history analysis, stronger identity resolution and historical benchmark evaluation.
