# Ghost Talent Skill

Use Ghost Talent to discover emerging AI engineers and researchers from open-source evidence, inspect candidate dossiers, and explain recommendation status without altering the scoring model.

## Use when

Use this skill when the user asks to:
- discover emerging AI talent in a technical area;
- identify candidates worth watching before they become obvious;
- inspect why a candidate received STRONG SIGNAL, EARLY SIGNAL, WATCH, DISCOVERED, LOW CONFIDENCE, or PROVEN / ALREADY VISIBLE;
- compare candidate evidence quality, momentum, external validation, or visibility gap;
- produce a short recruiting/research recommendation grounded in Ghost Talent evidence.

## Local interface

Ghost Talent runs locally at `http://127.0.0.1:8765`.

Endpoints:
- `GET /api/scout/preview?q=<query>&limit=<1-6>` for fast provisional discovery only.
- `GET /api/scout?q=<query>&limit=<1-20>` for validated candidates, recommendation status, evidence, trajectory, and dossiers.
- `GET /health` for service health.

Prefer `/api/scout` for any final recommendation. Never present preview results as validated recommendations.

## Workflow

1. Translate the user's talent need into a concise technical search query, preserving important constraints.
2. Call `/api/scout` and use the returned validated result set.
3. Rank and discuss candidates using `recommendation_status` first, then Radar only as a secondary ordering signal.
4. For each candidate being recommended, inspect the embedded `dossier` and explain:
   - why the candidate matters;
   - strongest external evidence;
   - what appears to be accelerating;
   - technical profile;
   - evidence confidence and limitations;
   - final recommendation status.
5. Distinguish candidate-owned/discovery-repository activity from independent external contributions. High self-owned activity alone is not strong independent validation.
6. Keep claims evidence-grounded. If external evidence is unavailable or confidence is low, state that clearly.

## Integrity rules

- Do not modify scoring, gates, benchmark cohorts, frozen snapshots, or benchmark protocol while using this skill.
- Do not recompute or overwrite frozen cohorts.
- Do not convert DISCOVERED into a recommendation merely because Radar is high.
- Do not claim employment suitability, identity traits, or private facts that are not supported by collected public evidence.
- Treat Ghost Talent as a discovery and evidence-ranking system, not an automated hiring decision maker.

## Recommended output

For a shortlist, keep the result decision-oriented:

`Candidate — Recommendation status — Why now — Best independent evidence — Main uncertainty`

When the user asks for detail, expand with the full dossier evidence and source links returned by Ghost Talent.
