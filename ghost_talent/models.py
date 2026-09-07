from dataclasses import dataclass, field
from typing import Any


@dataclass
class Evidence:
    type: str
    source: str
    source_url: str
    observed_at: str | None = None
    value: dict[str, Any] = field(default_factory=dict)
    confidence: float = 1.0


@dataclass
class Candidate:
    login: str
    name: str | None
    profile_url: str
    followers: int
    repositories: list[dict[str, Any]]
    recent_events_7d: int
    recent_events_30d: int
    recent_events_90d: int
    active_days_30d: int
    observed_event_span_days: float
    contribution_quality: dict[str, Any]
    paper_matches: list[dict[str, Any]]
    evidence: list[Evidence]
