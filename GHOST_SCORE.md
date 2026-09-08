# Ghost Score

Ghost Score is the public deterministic scoring framework behind Ghost Talent.

It is designed for **early technical talent discovery**, not résumé screening, role fit, or employment decisions.

## Current version

Active score version: **0.2.7**.

The model is explicit and versioned. Its weights and thresholds are research hypotheses that require empirical validation; they are not learned probabilities.

## Ghost Score

`Ghost Score = 0.30 Capability + 0.25 External Validation + 0.25 Momentum + 0.10 Visibility Gap + 0.10 Evidence Confidence`

`Capability = 0.65 Internal Capability + 0.35 External Validation`

All dimensions are normalized to 0–100.

## External Validation

External Validation is separate from self-controlled activity. v0.2.7 only gives strong upstream credit to evidence that survives additional checks:

- external merged PR discovery,
- substantive-change gate for inspected upstream PRs,
- recognized upstream repository context,
- changed-file verified core implementation paths,
- owner/member-approved reviews,
- recency of external evidence.

`COLLABORATOR` review status is not treated as maintainer acceptance. Documentation, tests, examples, CI and other non-core paths are excluded from core-path evidence. A recognized repository name alone is insufficient for strong technical credit.

## Momentum

Momentum now counts only a bounded set of development-relevant GitHub public event types rather than stars, forks and general issue activity.

Important v0.2.7 rules:

- no prior observable history means acceleration is **not inferred**,
- insufficient history caps Momentum and blocks EARLY / STRONG,
- a 100-event-truncated public-event sample is reported and conservatively capped,
- activity acceleration is not treated as technical improvement.

This directly addresses the false-positive pattern where a newly active account, star-heavy account, or short burst of public activity could look like a breakout trajectory.

## Visibility Gap

Current visibility is approximated using log-scaled GitHub followers. Followers are a weak proxy for market visibility, so Visibility Gap is a supporting signal rather than proof of under-recognition.

v0.2.7 reduces the follower proxy's saturation rate and lowers the degree to which Capability is effectively counted twice through the gap calculation. This remains an unresolved research dimension and must be tested empirically.

## Evidence Mix

Ghost Talent distinguishes self-owned repository evidence, external repository contributions, verified external PR evidence, verified research evidence and unclassified repository evidence.

Self-owned concentration cannot independently create an emerging recommendation.

## Ghost Radar

`Radar = 0.35 External Validation + 0.25 Momentum + 0.20 Visibility Gap + 0.15 Capability + 0.05 Evidence Confidence`

Radar is a prioritization score, not a recommendation by itself.

## Recommendation states

**STRONG SIGNAL** requires Radar >= 75, External Validation >= 70, Evidence Confidence >= 65, low current visibility, sufficient momentum history, and recent same-PR owner/member-approved core-path evidence.

**EARLY SIGNAL** requires Radar >= 65, External Validation >= 50, Evidence Confidence >= 55, low current visibility, sufficient momentum history, recent recognized-upstream evidence, plus recent owner/member approval or changed-file core-path evidence.

**WATCH** is used when internal capability or Radar is interesting but the stronger external-validation gates are not satisfied.

**PROVEN / ALREADY VISIBLE** routes strong candidates with high existing visibility away from emerging recommendations.

**LOW CONFIDENCE** is used when external validation is not inspected, evidence is noisy, or confidence is below the minimum threshold.

## Important invariants

1. High GitHub activity alone cannot create EARLY or STRONG.
2. Self-owned repository activity is not external validation.
3. A merged PR is not automatically a substantive contribution.
4. A recognized upstream repository is context, not proof of technical depth.
5. Missing history does not become synthetic acceleration.
6. GitHub stars, forks and general issue activity do not drive Momentum.
7. A famous strong candidate should not be mislabeled as emerging.
8. Missing external evidence caps recommendation confidence.
9. Noise can block recommendation even when raw activity is high.
10. Historical and recent evidence are not treated as equivalent.

## Known weaknesses

The current model still has unresolved weaknesses:

- Capability and Momentum may remain statistically correlated.
- GitHub followers remain a rough visibility proxy.
- thresholds are not calibrated probabilities.
- public GitHub evidence undercovers excellent closed-source engineers.
- recognized-upstream coverage is incomplete and partly curated.
- PR inspection is bounded, not a complete code review.
- GitHub public-event history is incomplete and can be truncated.
- OpenAlex cross-source identity coverage is conservative and sparse.

These weaknesses should be measured rather than explained away.

## Credibility validation

Before prospective outcomes mature, Ghost Talent uses four separate credibility layers:

- adversarial / anti-gaming tests,
- recommendation-state invariants,
- component correlation analysis,
- identity audit protocol.

These are sanity checks, not predictive-validity evidence.

## Historical evaluation

Every score carries a `score_version`. Any material change to weights, normalization, evidence semantics or recommendation gates creates a new score version.

The first real benchmark cohort remains frozen on score version `0.1.5` and must never be recomputed using v0.2.7.

Retrospective validation may only use evidence proven to have been observable at the historical `as_of_date`; current follower counts or current repository state may not be injected into historical rankings.

Prospective benchmark outcomes at 30 / 90 / 180 days remain the primary test of predictive validity.

## Non-goals

Ghost Score is not a hiring decision, résumé score, probability of success, popularity score, substitute for expert technical review, or guarantee of future breakout.

See `docs/METHODOLOGY.md`, `docs/ADVERSARIAL_TESTS.md`, and `docs/CREDIBILITY_PHASE.md`.
