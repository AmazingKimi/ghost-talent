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


def _contribution_quality(candidate: Candidate) -> tuple[float, dict]:
    quality = candidate.contribution_quality or {}
    top_pr = quality.get("top_pr") or {}
    if not quality.get("available") or not top_pr:
        return 0.0, {
            "available": False,
            "score": 0.0,
            "reason": "merged PR quality evidence unavailable",
        }

    merged_pr_count = max(int(quality.get("merged_pr_count", 0)), 0)
    core_file_count = max(int(top_pr.get("core_file_count", 0)), 0)
    changed_files = max(int(top_pr.get("changed_files_sampled", 0)), 0)
    keyword_hits = top_pr.get("keyword_hits") or []
    change_volume = max(int(top_pr.get("additions", 0)), 0) + max(int(top_pr.get("deletions", 0)), 0)

    merged_signal = min(28.0, 12.0 * math.log1p(merged_pr_count))
    core_ratio = min(core_file_count / max(changed_files, 1), 1.0)
    core_signal = 34.0 * core_ratio
    keyword_signal = min(22.0, 5.5 * len(keyword_hits))
    scope_signal = min(16.0, 4.0 * math.log1p(change_volume))
    score = _clamp(merged_signal + core_signal + keyword_signal + scope_signal)

    return score, {
        "available": True,
        "score": score,
        "repository": quality.get("repository"),
        "merged_pr_count": merged_pr_count,
        "top_pr": top_pr,
        "core_ratio": round(core_ratio, 2),
    }


def score_candidate(candidate: Candidate) -> dict:
    scored_repositories = [
        {**repo, "capability_signal": round(_repo_capability(repo), 1)}
        for repo in candidate.repositories
    ]
    scored_repositories.sort(key=lambda repo: repo["capability_signal"], reverse=True)

    repo_scores = [repo["capability_signal"] for repo in scored_repositories]
    if repo_scores:
        top = repo_scores[:3]
        base_capability = _clamp(sum(top) / len(top) + 4.0 * math.log1p(len(repo_scores)))
    else:
        base_capability = 0.0

    contribution_quality, quality_driver = _contribution_quality(candidate)
    capability = _clamp(base_capability + 0.18 * contribution_quality)

    prior_60d = max(candidate.recent_events_90d - candidate.recent_events_30d, 0)
    prior_weekly_rate = prior_60d / 8.57 if prior_60d else 0.0
    current_weekly_rate = float(candidate.recent_events_7d)

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

    confidence_reasons = ["GitHub repository contribution evidence"]
    evidence_confidence = 35.0
    if candidate.name:
        evidence_confidence += 8.0
        confidence_reasons.append("public GitHub name available")
    evidence_confidence += min(12.0, 4.0 * len(candidate.repositories))
    if len(candidate.repositories) > 1:
        confidence_reasons.append(f"evidence across {len(candidate.repositories)} repositories")
    if quality_driver.get("available"):
        evidence_confidence += 8.0
        confidence_reasons.append("merged PR quality evidence")
    if candidate.paper_matches:
        evidence_confidence += 10.0
        evidence_confidence += min(10.0, 5.0 * max(len(candidate.paper_matches) - 1, 0))
        confidence_reasons.append(f"{len(candidate.paper_matches)} OpenAlex name match(es)")
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

    top_repository = scored_repositories[0] if scored_repositories else None
    drivers = {
        "capability": {
            "repository_count": len(candidate.repositories),
            "base_capability": base_capability,
            "contribution_quality": contribution_quality,
            "top_repository": top_repository,
            "top_repositories": scored_repositories[:3],
        },
        "contribution_quality": quality_driver,
        "momentum": {
            "events_7d": candidate.recent_events_7d,
            "events_30d": candidate.recent_events_30d,
            "events_90d": candidate.recent_events_90d,
            "active_days_30d": candidate.active_days_30d,
            "current_weekly_rate": round(current_weekly_rate, 2),
            "prior_weekly_rate": round(prior_weekly_rate, 2),
            "acceleration_ratio": round(short_acceleration, 2),
            "observed_event_span_days": candidate.observed_event_span_days,
        },
        "visibility": {
            "followers": candidate.followers,
            "visibility_score": visibility,
        },
        "confidence": {
            "paper_matches": len(candidate.paper_matches),
            "reasons": confidence_reasons,
        },
    }

    return {
        "score_version": "0.1.3",
        "ghost_score": ghost_score,
        "capability": capability,
        "momentum": momentum,
        "visibility_gap": visibility_gap,
        "evidence_confidence": evidence_confidence,
        "trend": trend,
        "drivers": drivers,
        "candidate": asdict(candidate),
    }
