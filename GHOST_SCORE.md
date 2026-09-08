# Ghost Score

Ghost Score is the public deterministic scoring framework behind Ghost Talent.

It is designed for **early technical talent discovery**, not résumé screening, role fit, or employment decisions.

## Current version

Active score version: **0.2.6**.

The model is intentionally explicit and versioned. Its weights and thresholds are hypotheses that require empirical validation; they are not learned probabilities.

## Ghost Score

`Ghost Score = 0.30 Capability + 0.25 External Validation + 0.25 Momentum + 0.10 Visibility Gap + 0.10 Evidence Confidence`

All dimensions are normalized to 0–100.

### Capability

Capability combines internal execution evidence and external validation:

`Capability = 0.65 Internal Capability + 0.35 External Validation`

Internal Capability is derived from public repository contribution evidence and project context. Large contribution volume is log-scaled and capped; it cannot by itself create an emerging recommendation.

### External Validation

External Validation is intentionally separate from self-controlled activity.

Current signals include:

- external merged pull requests,
- merged PRs in recognized upstream repositories,
- changed-file verified core technical paths,
- maintainer-approved reviews,
- same-PR maintainer approval + core-path evidence,
- recency of external evidence.

External Validation is the most important Radar component because Ghost Talent should reward work accepted by high-quality external systems, not merely work performed in a candidate's own repository.

### Momentum

Momentum estimates recent activity acceleration from observable public GitHub events, active-day density, and observed event span.

Momentum is **not** treated as proof of technical improvement. A person can become more active without becoming more technically important. Therefore Momentum cannot independently produce EARLY or STRONG recommendation states.

### Visibility Gap

Current visibility is approximated using public GitHub followers. The Visibility Gap compares evidence-backed capability with that visibility proxy.

Followers are an imperfect proxy. A high Visibility Gap is therefore a supporting signal, not proof that the market has overlooked someone.

### Evidence Confidence

Evidence Confidence increases with independent supporting evidence and decreases when evidence is missing, noisy, or concentrated.

Current confidence logic includes:

- number of observed repositories,
- presence of a public name,
- external merged PR evidence,
- recognized upstream evidence,
- maintainer-approved evidence,
- self-owned evidence concentration risk,
- bot / course / tutorial noise,
- whether external validation was actually inspected.

## Evidence Mix

Ghost Talent distinguishes:

- self-owned repository evidence,
- external repository contributions,
- verified external PR evidence,
- verified research evidence,
- unclassified repository evidence.

If more than 80% of weighted evidence is self-owned repository activity and there is no external merged PR, confidence is reduced.

## Ghost Radar

Ghost Radar asks a narrower question than Ghost Score:

> Which candidates deserve technical attention now?

Current formula:

`Radar = 0.35 External Validation + 0.25 Momentum + 0.20 Visibility Gap + 0.15 Capability + 0.05 Evidence Confidence`

## Recommendation states

A candidate is never recommended merely because Radar is high.

### STRONG SIGNAL

Requires all of the following:

- Radar >= 75,
- External Validation >= 70,
- Evidence Confidence >= 65,
- GitHub followers < 500,
- recent same-PR evidence of a maintainer-approved core-path contribution.

### EARLY SIGNAL

Requires all of the following:

- Radar >= 65,
- External Validation >= 50,
- Evidence Confidence >= 55,
- GitHub followers < 500,
- recent recognized-upstream evidence,
- plus recent maintainer approval or recent changed-file core-path evidence.

### WATCH

Used when the candidate has interesting internal capability or a reasonably high Radar score, but current evidence does not satisfy the stronger external-validation gates.

### PROVEN / ALREADY VISIBLE

Strong externally validated candidates with high existing visibility are routed away from emerging recommendations.

Current visible gate:

- External Validation >= 60,
- followers >= 500.

This state means "strong, but no longer a ghost".

### LOW CONFIDENCE

Used when:

- external validation was not inspected,
- noise is flagged,
- or confidence is below the minimum recommendation threshold.

## Important invariants

1. **High GitHub activity alone cannot create EARLY or STRONG.**
2. **Self-owned repository activity is not external validation.**
3. **A famous strong candidate should not be mislabeled as emerging.**
4. **Missing external evidence caps recommendation confidence.**
5. **Noise can block recommendation even when raw activity is high.**
6. **Historical evidence and recent evidence are not treated as equivalent for emerging signals.**

## Known weaknesses

The current score is intentionally explicit about unresolved weaknesses:

- Capability and Momentum may still be statistically correlated.
- GitHub followers are only a rough visibility proxy.
- deterministic thresholds are not calibrated probabilities.
- public GitHub activity can overrepresent people whose work is already public and underrepresent excellent closed-source engineers.
- recognized-upstream coverage is incomplete.
- external PR inspection is bounded, not a complete technical review.

These weaknesses should be measured rather than explained away.

## Correlation and adversarial validation

Before prospective benchmark outcomes mature, Ghost Talent runs credibility checks for:

- component correlation,
- self-owned activity concentration,
- activity-only false positives,
- documentation / tiny-PR style gaming patterns,
- bot / course noise,
- already-visible strong candidates,
- recommendation-state invariants.

See `docs/ADVERSARIAL_TESTS.md`.

These tests are sanity checks, **not predictive-validity evidence**.

## Historical evaluation

Every score carries a `score_version`. Historical snapshots preserve the version used at observation time.

Any material change to weights, normalization, thresholds, evidence semantics, or recommendation gates requires a new score version.

Historical evaluation may only use evidence observable on or before the original snapshot `as_of_date`.

The first real benchmark cohort remains frozen on score version `0.1.5` and must never be recomputed using v0.2.6.

## Non-goals

Ghost Score is not:

- a hiring decision,
- a résumé score,
- a probability of success,
- a popularity score,
- a substitute for expert technical review,
- a guarantee of future breakout.

For the broader methodology and publication policy, see `docs/METHODOLOGY.md`.
