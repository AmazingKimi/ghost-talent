from __future__ import annotations

import re
from typing import Any

ORCID_RE = re.compile(r"(?:orcid\.org/)?(\d{4}-\d{4}-\d{4}-[\dX]{4})", re.IGNORECASE)


def stable_subject_id(github_profile: dict[str, Any]) -> str:
    user_id = github_profile.get("github_user_id")
    if user_id is not None:
        return f"github-id:{user_id}"
    login = str(github_profile.get("login") or "").strip().lower()
    return f"github:{login}"


def _extract_orcid(value: str | None) -> str | None:
    if not value:
        return None
    match = ORCID_RE.search(value)
    return match.group(1).upper() if match else None


def resolve_openalex_identity(github_profile: dict[str, Any], match: dict[str, Any]) -> dict[str, Any]:
    """Verify only explicit public cross-links; otherwise preserve uncertainty."""
    github_orcid = _extract_orcid(str(github_profile.get("blog") or ""))
    openalex_orcid = _extract_orcid(str(match.get("orcid") or ""))

    if github_orcid and openalex_orcid and github_orcid == openalex_orcid:
        return {
            "identity_status": "verified_external_link",
            "identity_confidence": 0.95,
            "identity_evidence": [f"matching ORCID {github_orcid} linked from GitHub profile"],
        }

    return {
        "identity_status": "uncertain_name_match",
        "identity_confidence": 0.35,
        "identity_evidence": ["exact normalized public name match only"],
    }
