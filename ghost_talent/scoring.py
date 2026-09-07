import math
from dataclasses import asdict

from .models import Candidate


def _clamp(value: float) -> float:
    return round(max(0.0, min(100.0, value)), 1)


def _repo_capability(repository: dict) -> float:
    contributions = max(int(repository.get("contributions", 0)), 0)
    stars = max(int(repository.get("stars", 0)), 0)

    contribution_signal = 8.0 * math.log1p(min(contributions, 250))
    quality_signal = 4.0 * math.log1p(stars)
    return min(92.0, contribution_signal + quality_signal)


def score_candidate(candidate: Candidate) -> dict:
    repo_scores = sorted(
        (_repo_capability(repo) for repo in candidate.repositories),
        reverse=True,
    )
    if repo_scores:
        top = repo_scores[:3]
        capability = _clamp(sum(top) / len(top) + 4.0 * math.log1p(len(repo_scores)))
    else:
        capability = 0.0

    prior_60d = max(candidate.recent_events_90d - candidate.recent_events_30d, 0)
    prior_weekly_rate = prior_60d / 8.57 if prior_60d else 0.0
    current_weekly_rate = candidate.recent_events_7d

    if prior_weekly_rate > 0:
        short_acceleration = current_weekly_rate / prior_weekly_rate
    elif current_weekly_rate > 0:
        short_acceleration = 1.6
    else:
        short_acceleration = 0.0

    active_day_ratio = min(candidate.active_days_30d / 12.0, 1.0)
    recency_density = 0.0
    if candidate.observed_event_span_days > 0:
        recency_density = min(30.0 / candidate.observed_event_span_days, 2.0) / 2.0

    if candidate.recent_events_30d == 0:
        momentum = 0.0
    else:
        acceleration_score = 50.0 + 24.0 * math.log2(max(short_acceleration, 0.25))
        momentum = _clamp(
            0.65 * _clamp(acceleration_score)
            + 20.0 * active_day_ratio
            + 15.0 * recency_density
        )

    visibility = _clamp(18.0 * math.log1p(max(candidate.followers, 0)))
    visibility_gap = _clamp(50.0 + 0.6 * (capability - visibility))

    evidence_confidence = 35.0
    if candidate.name:
        evidence_confidence += 8.0
    evidence_confidence += min(12.0, 4.0 * len(candidate.repositories))
    if candidate.paper_matches:
        evidence_confidence += 10.0
        evidence_confidence += min(10.0, 5.0 * max(len(candidate.paper_matches) - 1, 0))
    evidence_confidence = _clamp(evidence_confidence)

    ghost_score = _clamp(
        0.35 * capability
        + 0.35 * momentum
        + 0.20 * visibility_gap
        + 0.10 * evidence_confidence
    )

    trend = "stable"
    if momentum >= 65:
        trend = "accelerating"
    elif momentum < 38:
        trend = "decelerating"

    return {
        "score_version": "0.1.1",
        "ghost_score": ghost_score,
        "capability": capability,
        "momentum": momentum,
        "visibility_gap": visibility_gap,
        "evidence_confidence": evidence_confidence,
        "trend": trend,
        "candidate": asdict(candidate),
    }
