# Ghost Talent Methodology

Ghost Talent is an evidence-grounded system for discovering emerging AI engineers and researchers before conventional visibility signals make them obvious.

## Research question

Can public technical evidence identify people whose technical capability, external validation, and trajectory are strengthening before market visibility becomes obvious?

The answer is not assumed. It must be tested prospectively.

## Current research status

Ghost Talent is experimental. The system has a frozen real benchmark cohort, but mature outcome windows have not yet elapsed. Therefore the project does not currently claim predictive validity or superiority over simple baselines.

The methodology is designed to make future claims falsifiable and auditable.

## Active score model

Active score version: **0.2.6**.

`Ghost Score = 0.30 Capability + 0.25 External Validation + 0.25 Momentum + 0.10 Visibility Gap + 0.10 Evidence Confidence`

`Capability = 0.65 Internal Capability + 0.35 External Validation`

`Radar = 0.35 External Validation + 0.25 Momentum + 0.20 Visibility Gap + 0.15 Capability + 0.05 Evidence Confidence`

Every published score carries a `score_version`.

## Internal Capability

Internal Capability measures what a candidate appears able to build or sustain in public technical work.

Signals may include repository contribution intensity, project context, sustained engineering work, technically relevant paths, and other deterministic evidence.

Internal Capability is intentionally insufficient for EARLY or STRONG recommendation states because self-controlled work is not the same as external validation.

## External Validation

External Validation measures whether a candidate's work has been accepted by technical systems outside the candidate's own control.

Current signals include:

- external merged pull requests,
- recognized upstream projects,
- changed-file core-path verification,
- maintainer-approved reviews,
- same-PR core-path + maintainer approval,
- recent external validation within the current recency window.

A merged PR is not automatically interpreted as deep technical work. Stronger evidence requires stronger context.

## Momentum

Momentum estimates recent public activity acceleration using GitHub public events, active-day density, and observed event span.

Momentum is a weak causal signal. It can reflect technical acceleration, but it can also reflect job searching, temporary bursts, training activity, or increased public posting.

Therefore:

- Momentum never creates EARLY or STRONG by itself.
- Momentum must be interpreted alongside External Validation.
- Future model versions should increasingly separate **activity acceleration** from **validated trajectory**.

Validated trajectory means the quality or level of external validation is improving over time, for example:

- peripheral contribution → core-path contribution,
- unreviewed contribution → maintainer-approved contribution,
- single external project → multiple important external projects,
- historical upstream evidence → recent upstream evidence.

## Visibility Gap

Visibility Gap compares evidence-backed capability with current public visibility.

Current visibility is approximated mainly by GitHub followers. This is explicitly an imperfect proxy and should not be interpreted as a complete model of market awareness.

A high Visibility Gap supports an emerging-talent hypothesis, but low followers alone never create a recommendation.

## Evidence Confidence

Evidence Confidence reflects whether the system has enough trustworthy evidence to interpret a candidate record.

Confidence is affected by:

- source availability,
- cross-source identity confidence,
- number and diversity of repositories,
- external PR evidence,
- recognized upstream evidence,
- maintainer approval,
- self-owned evidence concentration,
- bot / course / tutorial noise.

Missing evidence remains missing.

## Evidence Mix

Candidate records distinguish:

- self-owned repository evidence,
- external repository contribution evidence,
- verified external PR evidence,
- verified research evidence,
- unclassified evidence.

High self-owned concentration without external validation reduces confidence.

## Recommendation gates

Recommendation state is a separate decision layer from raw ranking.

### STRONG SIGNAL

Requires:

- Radar >= 75,
- External Validation >= 70,
- Evidence Confidence >= 65,
- low current visibility,
- recent same-PR maintainer-approved core-path evidence.

### EARLY SIGNAL

Requires:

- Radar >= 65,
- External Validation >= 50,
- Evidence Confidence >= 55,
- low current visibility,
- recent recognized-upstream evidence,
- plus recent maintainer approval or recent changed-file core-path evidence.

### WATCH

Used when capability or activity is interesting but external validation is not yet sufficient.

### DISCOVERED

The Scout found the person, but current evidence does not support a stronger conclusion.

### LOW CONFIDENCE

Used when source coverage, identity, or noise makes recommendation unsafe.

### PROVEN / ALREADY VISIBLE

Strong candidates whose public visibility is already high are explicitly separated from emerging-talent recommendations.

## Discovery

Current discovery uses multiple GitHub paths:

1. repository search for the requested technical topic,
2. contributor discovery,
3. merged-PR author discovery,
4. bounded profile / event enrichment,
5. bounded external-validation inspection,
6. OpenAlex research evidence under conservative identity rules.

Repository dominance control reduces the chance that one project fills the entire ranking.

## Evidence standard

A score is not evidence by itself.

Concrete candidate claims should retain:

- source URL,
- observation time,
- evidence type,
- structured value,
- confidence,
- inspection status.

LLMs may explain evidence but must not invent evidence or silently replace deterministic scoring.

## Identity policy

A matching name alone is not sufficient proof that a GitHub account and paper author are the same person.

Current policy is conservative:

- explicit public linking evidence may verify a cross-source identity,
- exact-name matches without stronger linking remain uncertain,
- ambiguous identities are never forced.

The project should publish identity-audit results when enough manually reviewed cases exist.

## Anti-gaming and adversarial policy

Ghost Talent assumes public activity can be gamed or misread.

Current defenses include:

- bot / automation filtering,
- course / homework / tutorial repository patterns,
- self-owned evidence concentration penalties,
- external-validation gates,
- recency gates,
- changed-file core-path checks,
- maintainer-review evidence,
- already-visible routing.

Public adversarial cases are documented in `docs/ADVERSARIAL_TESTS.md`.

The anti-gaming model is not considered complete.

## Correlation audit

The project should measure whether named dimensions contain genuinely distinct information.

Important pairwise checks include:

- Internal Capability vs Momentum,
- External Validation vs Capability,
- External Validation vs Momentum,
- followers / visibility vs Capability,
- Ghost Score vs Radar.

High correlation does not automatically invalidate a feature, but it can reveal duplicated weighting or dimension collapse.

Correlation analysis is a diagnostic, not predictive validation.

## Historical snapshots

Every successful Scout run can create an immutable dated snapshot containing ranking, score version, score components, drivers, and evidence references.

Candidate first-detection records are append-only.

These records are currently best described as **prospective evaluation infrastructure**, not proof of a historical moat.

## No future leakage

Historical evaluation may use only evidence observable on or before the original `as_of_date`.

Evidence discovered later cannot be injected into an earlier ranking.

## First real cohort

The first real cohort is frozen and immutable:

- benchmark ID: `2026-09-08-cuda-triton-v01`
- query: `LLM inference CUDA Triton`
- source snapshot: `20260907T162245054462Z-b36e731d`
- as-of: `2026-09-07T16:22:45.054462Z`
- cohort size: 20
- score version: `0.1.5`

It must never be recomputed under v0.2.6 or any later model.

## Breakout evaluation

Prospective benchmark outcomes may include independently observable events such as:

- becoming a maintainer of an important project,
- producing high-impact technical work,
- increased responsibility across important open-source systems,
- sustained research impact.

Primary metrics include:

- Precision@K,
- breakout rate by rank bucket,
- Breakout Lead Time,
- comparison against followers,
- comparison against stars,
- comparison against raw contribution count.

Outcome definitions must be versioned before evaluation.

## Publication rules

1. Evidence and score versions are explicit.
2. Missing data remains missing.
3. Source failures remain visible.
4. Historical snapshots are append-only.
5. Methodology changes require versioning.
6. Benchmark wins and misses both remain visible.
7. Headline benchmark claims must be reproducible.
8. Sanity tests must not be described as predictive validation.
9. Frozen cohorts must never be recomputed to match later methodology.
10. Negative benchmark results should still be published.

## Current major uncertainties

The project explicitly tracks these unresolved risks:

- whether Momentum adds independent information beyond activity volume,
- whether GitHub followers adequately approximate market visibility,
- whether score thresholds are calibrated sensibly,
- how much excellent talent is invisible to current public sources,
- identity-resolution error rate,
- robustness against deliberate gaming,
- whether Ghost Talent actually outperforms simple baselines.

These are research questions, not marketing objections to be explained away.

## Sensitive attributes

Ghost Talent does not infer or rank candidates using sensitive personal attributes such as race, ethnicity, religion, health, political beliefs, sexual orientation, or similar traits.
