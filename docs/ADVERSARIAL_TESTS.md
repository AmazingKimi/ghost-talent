# Ghost Talent Adversarial & Credibility Tests

This document defines sanity and adversarial checks for Ghost Talent before mature prospective benchmark outcomes exist.

These tests do **not** prove predictive validity. They test whether the current deterministic model violates obvious product constraints or can be trivially gamed.

## 1. Activity-only false positive

Scenario:

- very high contribution volume,
- low followers,
- mostly self-owned repositories,
- no verified external merged PR.

Expected result:

- never STRONG SIGNAL,
- never EARLY SIGNAL,
- usually WATCH or lower,
- evidence concentration risk should be visible.

Purpose: prevent "busy GitHub profile" from being mistaken for externally validated technical talent.

## 2. External core-path validation

Scenario:

- recent external merged PR,
- recognized upstream project,
- changed-file evidence touches core technical path,
- maintainer-approved review on the same PR,
- low current visibility.

Expected result:

- External Validation rises materially,
- candidate may qualify for EARLY or STRONG if the remaining gates are met.

Purpose: reward externally accepted, technically relevant work rather than raw activity.

## 3. Already-visible strong candidate

Scenario:

- strong external evidence,
- recognized upstream work,
- high follower count / obvious public visibility.

Expected result:

- PROVEN / ALREADY VISIBLE,
- never marketed as an emerging "ghost".

Purpose: distinguish "strong" from "early".

## 4. Bot / automation noise

Scenario:

- bot-like login,
- automation identity,
- very high activity.

Expected result:

- LOW CONFIDENCE or filtered before recommendation,
- never EARLY / STRONG.

## 5. Course / homework / tutorial concentration

Scenario:

- activity concentrated in course, homework, tutorial, classroom, or exercise repositories.

Expected result:

- noise flag,
- recommendation blocked or confidence reduced.

## 6. Many tiny PRs / superficial activity

Scenario:

- many external merged PRs,
- no recognized upstream evidence,
- no changed-file core-path evidence,
- no maintainer-approved review evidence.

Expected result:

- external presence may be recorded,
- should not automatically become EARLY / STRONG.

Known limitation: Ghost Talent does not yet fully model documentation-only, formatting-only, or tiny-diff PR patterns across every external PR. This remains an open adversarial risk.

## 7. Stale external evidence

Scenario:

- strong external PR history exists,
- none of it is recent enough for the emerging window.

Expected result:

- external validation can remain historically strong,
- emerging recommendation should be withheld when recent evidence gates are not met.

## 8. Self-owned concentration

Scenario:

- >80% of weighted evidence comes from self-owned repositories,
- no external merged PR.

Expected result:

- confidence penalty,
- evidence concentration risk shown in Dossier,
- cannot become EARLY / STRONG.

## 9. Identity uncertainty

Scenario:

- GitHub and OpenAlex share a name,
- no explicit public cross-link.

Expected result:

- identity remains uncertain,
- research evidence cannot silently become verified.

## 10. Missing external validation coverage

Scenario:

- external validation was not inspected because of source failure, rate limit, or missing coverage.

Expected result:

- recommendation confidence is capped,
- LOW CONFIDENCE rather than an optimistic guess.

## Manual sanity set

The following manually reviewed profile patterns are useful acceptance anchors, but their exact live statuses should only be asserted after a fresh run with current evidence:

- **MerkyorLynn pattern**: strong internal execution, insufficient verified external validation → expected direction: WATCH.
- **MadrasLe pattern**: prolific builder, mostly self-controlled visible evidence → expected direction: WATCH unless stronger external evidence is found.
- **merrymercy pattern**: strong external validation but already obvious publicly → expected direction: PROVEN / ALREADY VISIBLE.

These examples are acceptance anchors, not hardcoded identities or special cases.

## Identity audit protocol

For a manually sampled set of cross-source matches, record:

- GitHub login,
- proposed OpenAlex author,
- match status: verified / uncertain / wrong,
- public linking evidence used,
- reviewer note.

Report all reviewed cases, including errors and uncertain cases. Do not convert name-only matches into verified identities.

## Component correlation audit

For a snapshot or pool of snapshots with the same `score_version`, compute pairwise Pearson correlation for:

- Internal Capability,
- External Validation,
- Capability,
- Momentum,
- Visibility Gap,
- Evidence Confidence,
- Ghost Score,
- Radar Score.

Pay particular attention to:

- Internal Capability ↔ Momentum,
- External Validation ↔ Capability,
- External Validation ↔ Momentum,
- Ghost Score ↔ Radar.

A very high absolute correlation (for example >0.85) should trigger review for duplicated weighting or dimension collapse. This threshold is diagnostic, not a statistical law.

## Publication rule

Credibility tests may demonstrate model discipline, but they must never be presented as evidence that Ghost Talent predicts future success.

Only prospective benchmark outcomes can support that claim.
