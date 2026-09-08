# Ghost Score

Ghost Score is the public deterministic scoring framework behind Ghost Talent.

It is designed for **early technical talent discovery**, not résumé screening, role fit, or employment decisions.

## Current version

Active score version: **0.2.8**.

The model is explicit and versioned. Its weights and thresholds are research hypotheses that require empirical validation; they are not learned probabilities.

## Ghost Score

`Ghost Score = 0.30 Capability + 0.25 External Validation + 0.25 Momentum + 0.10 Visibility Gap + 0.10 Evidence Confidence`

`Capability = 0.65 Internal Capability + 0.35 External Validation`

All dimensions are normalized to 0–100.

## External Validation

External Validation is separate from self-controlled activity.

v0.2.8 changes a core assumption: **a curated recognized-upstream list is no longer a mandatory gateway to an emerging recommendation.**

The system now inspects a bounded mix of external PRs across:

- curated recognized upstream repositories,
- recent external repositories outside that list,
- and additional recent external PRs when inspection budget allows.

A non-curated project can produce credible external evidence when an inspected PR is substantive and has at least one of:

- changed-file verified core implementation work,
- owner/member approval from the external repository.

This produces a `verified_external_project` signal. Curated upstream status remains a **context bonus**, not proof of quality and not a mandatory EARLY gate.

Current external signals include:

- external merged PR discovery,
- substantive-change gate,
- verified external-project PRs,
- curated recognized-upstream context,
- changed-file verified core implementation paths,
- owner/member-approved reviews,
- recency of external evidence.

`COLLABORATOR` review status is not treated as maintainer acceptance. Documentation, tests, examples, CI and other non-core paths are excluded from core-path evidence. A repository name alone is never sufficient for strong technical credit.

## Momentum

Momentum counts only a bounded set of development-relevant GitHub public event types rather than stars, forks and general issue activity.

Important rules:

- no prior observable history means acceleration is **not inferred**,
- insufficient history caps Momentum and blocks EARLY / STRONG,
- a 100-event-truncated public-event sample is reported and conservatively capped,
- activity acceleration is not treated as technical improvement.

## Visibility Gap

Current visibility is approximated using log-scaled GitHub followers. Followers are a weak proxy for market visibility, so Visibility Gap is a supporting signal rather than proof of under-recognition.

The follower proxy has reduced weight and slower saturation than the original model, but this remains an unresolved research dimension and must be tested empirically.

## Evidence Mix

Ghost Talent distinguishes self-owned repository evidence, external repository contributions, verified external PR evidence, verified research evidence and unclassified repository evidence.

Self-owned concentration cannot independently create an emerging recommendation.

## Ghost Radar

`Radar = 0.35 External Validation + 0.25 Momentum + 0.20 Visibility Gap + 0.15 Capability + 0.05 Evidence Confidence`

Radar is a prioritization score, not a recommendation by itself.

## Recommendation states

**STRONG SIGNAL** requires Radar >= 75, External Validation >= 70, Evidence Confidence >= 65, low current visibility, sufficient momentum history, and recent same-PR owner/member-approved core-path evidence.

**EARLY SIGNAL** requires Radar >= 65, External Validation >= 50, Evidence Confidence >= 55, low current visibility, sufficient momentum history, and recent `verified_external_project` evidence with recent core-path or owner/member approval support.

A curated upstream repository is **not required** for EARLY SIGNAL in v0.2.8.

**WATCH** is used when internal capability or Radar is interesting but the stronger external-validation gates are not satisfied.

**PROVEN / ALREADY VISIBLE** routes strong candidates with high existing visibility away from emerging recommendations.

**LOW CONFIDENCE** is used when external validation is not inspected, evidence is noisy, or confidence is below the minimum threshold.

## Important invariants

1. High GitHub activity alone cannot create EARLY or STRONG.
2. Self-owned repository activity is not external validation.
3. A merged PR is not automatically a substantive contribution.
4. A curated upstream repository is context, not proof of technical depth.
5. A non-curated external project can count when the actual PR evidence is strong enough.
6. Missing history does not become synthetic acceleration.
7. GitHub stars, forks and general issue activity do not drive Momentum.
8. A famous strong candidate should not be mislabeled as emerging.
9. Missing external evidence caps recommendation confidence.
10. Historical and recent evidence are not treated as equivalent.

## Known weaknesses

The current model still has unresolved weaknesses:

- Capability and Momentum may remain statistically correlated.
- GitHub followers remain a rough visibility proxy.
- thresholds are not calibrated probabilities.
- public GitHub evidence undercovers excellent closed-source engineers.
- external PR inspection is bounded, not a complete code review.
- the current mixed inspection budget can still miss important PRs.
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

The first real benchmark cohort remains frozen on score version `0.1.5` and must never be recomputed using v0.2.8.

That cohort can only validate the old frozen model. Therefore a **new prospective cohort must be frozen under v0.2.8** so future outcome data can directly test the current model.

Retrospective validation may only use evidence proven to have been observable at the historical `as_of_date`; current follower counts or current repository state may not be injected into historical rankings.

Prospective benchmark outcomes at 30 / 90 / 180 days remain the primary test of predictive validity.

## Non-goals

Ghost Score is not a hiring decision, résumé score, probability of success, popularity score, substitute for expert technical review, or guarantee of future breakout.

See `docs/METHODOLOGY.md`, `docs/ADVERSARIAL_TESTS.md`, and `docs/CREDIBILITY_PHASE.md`.
