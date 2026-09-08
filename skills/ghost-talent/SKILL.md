# Ghost Talent Skill

Use Ghost Talent to discover emerging AI engineers and researchers from public open-source evidence, inspect candidate dossiers, and explain recommendation status without altering the scoring model.

## Use when

Use this skill when the user asks to:
- discover emerging AI talent in a technical area;
- identify candidates worth watching before they become obvious;
- inspect why a candidate received STRONG SIGNAL, EARLY SIGNAL, WATCH, DISCOVERED, LOW CONFIDENCE, or PROVEN / ALREADY VISIBLE;
- compare candidate evidence quality, momentum, external validation, or visibility gap;
- inspect or maintain the local watchlist;
- inspect benchmark/validation state;
- produce a short recruiting/research recommendation grounded in Ghost Talent evidence.

## Local interface

Ghost Talent runs locally at `http://127.0.0.1:8765`.

### Discovery
- `GET /api/scout?q=<query>&limit=<1-20>` performs real evidence-backed discovery, validation, dossier construction, and snapshot writing only when the source-integrity gate passes.
- `GET /api/scout/preview` is intentionally disabled. It returns `409 preview_disabled`, `complete: false`, and writes no snapshot. It must never be interpreted as an empty talent market.
- A failed/incomplete real scan can return `503`. Treat this as source/discovery failure, **not** as zero candidates. The response includes source health and `snapshot_written: false`.

### Candidate state and validation
- `GET /api/watchlist` reads the persistent local watchlist.
- `PUT /api/watchlist/{login}` saves or updates a candidate.
- `DELETE /api/watchlist/{login}` removes a candidate.
- `GET /api/validation` returns protocol-v2 cohort registry, current artifact hashes, freeze-time commitment state, maturity horizons, and headline-claim readiness.
- `GET /api/runtime` returns app/runtime and GitHub connection state.
- `GET /health` returns service health.

### GitHub connection
- `POST /api/github/connect/start` begins GitHub OAuth Device Flow.
- `GET /api/github/connect/poll?flow_id=...` polls that flow.
- `GET /api/github/status` reports GitHub auth/quota state.
- `DELETE /api/github/connect` disconnects a locally stored OAuth token. Environment-provided `GITHUB_TOKEN` cannot be removed through this endpoint.

## Workflow

1. Translate the user's talent need into a concise technical search query, preserving important constraints.
2. Call `/api/scout`; do not use preview as discovery.
3. If `/api/scout` fails or is incomplete, report the source failure. Never turn a failed scan into “no talent found.”
4. Rank and discuss candidates using `recommendation_status` first, then Radar only as a secondary ordering signal.
5. For each candidate being recommended, inspect the embedded `dossier` and explain:
   - why the candidate matters;
   - strongest external evidence and source links;
   - what appears to be accelerating, if history supports that claim;
   - technical profile;
   - evidence confidence and limitations;
   - final recommendation status.
6. Distinguish candidate-owned/discovery-repository activity from independent external contributions. High self-owned activity alone is not strong independent validation.
7. When asked about benchmark credibility, use `/api/validation` and distinguish current artifact hashes from true freeze-time commitments. Never retroactively describe a post-freeze hash as a freeze-time commitment.
8. Keep claims evidence-grounded. If external evidence is unavailable or confidence is low, state that clearly.

## Integrity rules

- Do not modify scoring, gates, benchmark cohorts, frozen snapshots, or benchmark protocol while using this skill.
- Do not recompute or overwrite frozen cohorts.
- Do not convert DISCOVERED into a recommendation merely because Radar is high.
- Do not claim employment suitability, identity traits, or private facts that are not supported by collected public evidence.
- Treat Ghost Talent as a discovery and evidence-ranking system, not an automated hiring decision maker.
- “Public frozen artifact”, “current SHA-256”, “freeze-time commitment”, and “predictively validated” are different claims.
- Missing evidence stays missing. Historical commitments that did not exist at freeze time must not be fabricated later.

## Recommended output

For a shortlist, keep the result decision-oriented:

`Candidate — Recommendation status — Why now — Best independent evidence — Main uncertainty`

When the user asks for detail, expand with the full dossier evidence and source links returned by Ghost Talent.
