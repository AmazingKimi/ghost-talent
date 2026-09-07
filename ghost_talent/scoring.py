import math
from dataclasses import asdict

from .models import Candidate


def _clamp(value: float) -> float:
    return round(max(0.0, min(100.0, value)), 1)


def score_candidate(candidate: Candidate) -> dict:
    repo_count = len(candidate.repositories)
    contribution_total = sum(int(r.get("contributions", 0)) for r in candidate.repositories)
    repo_signal = sum(math.log1p(max(int(r.get("stars", 0)), 0)) for r in candidate.repositories)

    capability = _clamp(
        16 * math.log1p(contribution_total)
        + 9 * math.log1p(repo_count)
        + 2.2 * repo_signal
    )

    baseline_30d = candidate.recent_events_90d / 3 if candidate.recent_events_90d else 0
    if baseline_30d == 0:
        momentum = 20.0 if candidate.recent_events_30d else 0.0
    else:
        acceleration = candidate.recent_events_30d / baseline_30d
        momentum = _clamp(42 + 28 * math.log2(max(acceleration, 0.25)))

    visibility = _clamp(18 * math.log1p(candidate.followers))
    visibility_gap = _clamp(capability - visibility + 50)

    identity_confidence = 60.0
    if candidate.name:
        identity_confidence += 10
    if candidate.paper_matches:
        identity_confidence += 25
    evidence_confidence = _clamp(identity_confidence)

    ghost_score = _clamp(
        0.35 * capability
        + 0.35 * momentum
        + 0.20 * visibility_gap
        + 0.10 * evidence_confidence
    )

    trend = "stable"
    if momentum >= 66:
        trend = "accelerating"
    elif momentum < 35:
        trend = "decelerating"

    return {
        "ghost_score": ghost_score,
        "capability": capability,
        "momentum": momentum,
        "visibility_gap": visibility_gap,
        "evidence_confidence": evidence_confidence,
        "trend": trend,
        "candidate": asdict(candidate),
    }
