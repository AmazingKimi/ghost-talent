# Retrospective Validation Protocol

Retrospective validation is an **exploratory plausibility test**, not a substitute for the prospective benchmark.

Its purpose is to ask:

> If Ghost Talent had existed at an earlier date, would evidence that was genuinely observable then have ranked later-obvious technical people unusually high relative to simple baselines?

## Why this exists

Prospective cohorts require time. Retrospective cases can expose obviously broken assumptions sooner, help calibrate thresholds, and reveal whether the model only works because present-day information leaks backward.

## Hard rule: historical observability

A retrospective case may use only evidence that can be demonstrated to have existed on or before the case `as_of_date`.

Do **not** inject:

- current follower counts,
- current repository stars,
- current maintainer status,
- present-day profile descriptions,
- current employer information,
- PR outcomes that happened after `as_of_date`,
- citations accrued after `as_of_date`,
- any later-known breakout label into the historical score.

If a historical field cannot be reconstructed reliably, it must be marked `unavailable`, not estimated from the present.

## Case structure

Each retrospective case should contain:

- `case_id`
- `person_subject_id`
- `as_of_date`
- `evidence_sources`
- `historical_evidence`
- `missing_historical_fields`
- `ghost_score_version_used_for_replay`
- `baseline_values`
- `later_outcome`
- `outcome_date`
- `lead_time_days`
- `leakage_review`

## Candidate selection

Use a preregistered case list rather than selecting only people that make Ghost Talent look good.

A useful first set should include:

- later-obvious positive cases from inference / compiler / kernel ecosystems,
- technically strong people who did **not** later show a public breakout,
- noisy high-activity accounts,
- already-visible people,
- false-positive style cases.

Positive-only retrospective storytelling is prohibited.

## Baselines

Where historically observable, compare against:

- followers,
- repository stars,
- raw contribution count,
- contributor rank within the discovery repositories.

If a baseline cannot be reconstructed at the original date, omit it and state why.

## Output

The first retrospective report should publish:

- number of cases attempted,
- number with sufficient historical evidence,
- cases excluded for leakage risk,
- Ghost Talent rank / score,
- baseline ranks,
- wins,
- misses,
- obvious false positives,
- threshold failures,
- evidence reconstruction limitations.

Do not publish a headline such as “we found X months earlier” unless the underlying historical evidence and baseline state are independently reproducible.

## Relationship to the prospective benchmark

Retrospective validation answers:

> Does the hypothesis appear plausible under historical reconstruction?

The prospective benchmark answers the stronger question:

> Did a frozen, pre-outcome system actually identify later breakouts earlier than baselines?

Prospective evidence has priority whenever the two disagree.
