from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import uvicorn
from dotenv import load_dotenv
from fastapi import Body, FastAPI, HTTPException, Query
from fastapi.responses import FileResponse, HTMLResponse

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

from .dossier import build_dossier
from .github_auth import (
    auth_mode,
    disconnect_github,
    github_auth_status,
    github_client_id,
    load_connected_token,
    poll_device_flow,
    start_device_flow,
)
from .scout import scout
from .snapshot import save_snapshot

APP_VERSION = "0.3.3"
SCORE_VERSION = "0.2.8"
WATCHLIST_PATH = ROOT / "ledger" / "watchlist.json"

KNOWN_COHORTS = [
    {"id": "2026-09-08-cuda-triton-v01", "score_version": "0.1.5", "size": 20, "artifact_status": "historical-unverified"},
    {"id": "2026-09-08-llm-inference-cuda-triton-v028", "score_version": "0.2.8", "size": 20, "artifact_status": "existence-unverified"},
    {"id": "2026-09-08-ai-compiler-runtime-v028", "score_version": "0.2.8", "size": 20, "artifact_status": "existence-unverified"},
    {"id": "2026-09-08-quantization-kernels-v028", "score_version": "0.2.8", "size": 20, "artifact_status": "existence-unverified"},
    {"id": "2026-09-08-inference-infrastructure-v028", "score_version": "0.2.8", "size": 20, "artifact_status": "existence-unverified"},
    {"id": "2026-09-08-distributed-training-systems-v028", "score_version": "0.2.8", "size": 20, "artifact_status": "public-frozen"},
]

app = FastAPI(title="Ghost Talent", version=APP_VERSION)


@app.get("/")
async def index():
    html = (ROOT / "web" / "index.html").read_text(encoding="utf-8")
    html = html.replace("</head>", '<link rel="stylesheet" href="/ui-overrides.css?v=2"/>\n</head>')
    html = html.replace("</body>", '<script src="/preferences.js?v=2"></script>\n</body>')
    return HTMLResponse(html, headers={"Cache-Control": "no-store"})


@app.get("/ui-overrides.css", include_in_schema=False)
async def ui_overrides():
    return FileResponse(ROOT / "web" / "ui-overrides.css", media_type="text/css", headers={"Cache-Control": "no-store"})


@app.get("/preferences.js", include_in_schema=False)
async def preferences_script():
    return FileResponse(ROOT / "web" / "preferences.js", media_type="application/javascript", headers={"Cache-Control": "no-store"})


@app.get("/favicon.ico", include_in_schema=False)
@app.get("/favicon.svg", include_in_schema=False)
async def favicon():
    return FileResponse(ROOT / "web" / "favicon.svg", media_type="image/svg+xml")


def _load_watchlist() -> list[dict[str, Any]]:
    if not WATCHLIST_PATH.exists():
        return []
    try:
        payload = json.loads(WATCHLIST_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    items = payload.get("items", []) if isinstance(payload, dict) else []
    return [item for item in items if isinstance(item, dict)]


def _save_watchlist(items: list[dict[str, Any]]) -> None:
    WATCHLIST_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": "0.1",
        "updated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "items": items,
    }
    temp = WATCHLIST_PATH.with_suffix(".tmp")
    temp.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temp.replace(WATCHLIST_PATH)


def snapshot_allowed(scout_result: dict[str, Any]) -> tuple[bool, str | None]:
    if not scout_result.get("complete", False):
        return False, "source_incomplete"
    github = (scout_result.get("sources") or {}).get("github") or {}
    if github.get("status") != "ok":
        return False, "github_not_healthy"
    return True, None


def _cohort_maturity(frozen_at: str | None) -> dict[str, Any]:
    if not frozen_at:
        return {"d30": "unknown", "d90": "unknown", "d180": "unknown"}
    try:
        frozen = datetime.fromisoformat(frozen_at.replace("Z", "+00:00"))
    except ValueError:
        return {"d30": "unknown", "d90": "unknown", "d180": "unknown"}
    elapsed = max(0, (datetime.now(timezone.utc) - frozen).days)
    return {
        "elapsed_days": elapsed,
        "d30": "matured" if elapsed >= 30 else f"{30 - elapsed}d remaining",
        "d90": "matured" if elapsed >= 90 else f"{90 - elapsed}d remaining",
        "d180": "matured" if elapsed >= 180 else f"{180 - elapsed}d remaining",
    }


def validation_registry(root: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for record in KNOWN_COHORTS:
        row = dict(record)
        path = root / "benchmarks" / record["id"] / "cohort.json"
        if path.exists():
            raw = path.read_bytes()
            try:
                payload = json.loads(raw.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError):
                payload = {}
            row.update({
                "artifact_status": "public-frozen",
                "artifact_path": str(path.relative_to(root)),
                "artifact_sha256_current": hashlib.sha256(raw).hexdigest(),
                "freeze_time_commitment": payload.get("sha256_commitment") or payload.get("artifact_sha256"),
                "frozen_at": payload.get("frozen_at") or payload.get("as_of_date"),
                "size": payload.get("cohort_size", row["size"]),
                "score_version": (payload.get("members") or [{}])[0].get("score_version", row["score_version"]),
            })
        row["maturity"] = _cohort_maturity(row.get("frozen_at"))
        rows.append(row)
    return rows


@app.get("/api/runtime")
async def runtime():
    github = await github_auth_status()
    return {
        "status": "ok",
        "version": APP_VERSION,
        "github_token_configured": bool(load_connected_token()),
        "github_auth_mode": auth_mode(),
        "github_oauth_client_configured": bool(github_client_id()),
        "github": github,
    }


@app.post("/api/github/connect/start")
async def github_connect_start():
    try:
        return await start_device_flow()
    except RuntimeError as exc:
        raise HTTPException(status_code=409, detail={"error": "oauth_not_configured", "message": str(exc)}) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail={"error": "oauth_start_failed", "message": str(exc)}) from exc


@app.get("/api/github/connect/poll")
async def github_connect_poll(flow_id: str = Query(min_length=8, max_length=128)):
    try:
        return await poll_device_flow(flow_id)
    except Exception as exc:
        raise HTTPException(status_code=502, detail={"error": "oauth_poll_failed", "message": str(exc)}) from exc


@app.get("/api/github/status")
async def github_status():
    return await github_auth_status()


@app.delete("/api/github/connect")
async def github_disconnect():
    if os.getenv("GITHUB_TOKEN"):
        raise HTTPException(status_code=409, detail={"error": "environment_token", "message": "GITHUB_TOKEN is supplied by the environment; remove it from .env to disconnect."})
    disconnect_github()
    return {"status": "disconnected"}


@app.get("/api/scout/preview")
async def run_scout_preview(q: str = Query(min_length=2, max_length=120), limit: int = 6):
    authenticated = bool(load_connected_token())
    return {
        "query": q,
        "count": 0,
        "results": [],
        "complete": True,
        "sources": {"github": {"status": "ok", "authenticated": authenticated, "mode": auth_mode()}},
    }


@app.get("/api/scout")
async def run_scout(q: str = Query(min_length=2, max_length=120), limit: int = 20):
    try:
        scout_result = await scout(q, limit=max(1, min(limit, 20)))
        allowed, reason = snapshot_allowed(scout_result)
        if not allowed:
            error = scout_result.get("error") or {"code": "discovery_incomplete", "message": "Discovery evidence is incomplete. No snapshot was written."}
            raise HTTPException(status_code=503, detail={**error, "snapshot_written": False, "integrity_gate": reason, "sources": scout_result.get("sources", {})})
        results = scout_result["results"]
        sources = scout_result["sources"]
        snapshot = save_snapshot(ROOT, q, results, sources=sources)
        histories = snapshot.get("history", {})
        trajectories = snapshot.get("trajectory", {})
        for row in results:
            login = str(row.get("candidate", {}).get("login") or "")
            row["history"] = histories.get(login, {"status": "building_history"})
            row["trajectory"] = trajectories.get(login, {"observation_count": 1, "d7": {"status": "building_history", "days": 7}, "d30": {"status": "building_history", "days": 30}})
            row["dossier"] = build_dossier(row)
        return {"query": q, "count": len(results), "results": results, "sources": sources, "source_health": scout_result.get("source_health", {}), "snapshot": snapshot, "integrity_gate": "passed"}
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=502, detail={"code": "scout_failed", "message": str(exc)}) from exc


@app.get("/api/watchlist")
async def get_watchlist():
    items = _load_watchlist()
    return {"count": len(items), "items": items}


@app.put("/api/watchlist/{login}")
async def put_watchlist(login: str, row: dict[str, Any] = Body(...)):
    login = login.strip()
    candidate = row.get("candidate") or {}
    row_login = str(candidate.get("login") or login)
    if row_login.lower() != login.lower():
        raise HTTPException(status_code=400, detail="Candidate login does not match path.")
    items = _load_watchlist()
    payload = {**row, "saved_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")}
    for index, item in enumerate(items):
        existing = str((item.get("candidate") or {}).get("login") or "")
        if existing.lower() == login.lower():
            items[index] = payload
            break
    else:
        items.append(payload)
    _save_watchlist(items)
    return {"saved": True, "login": login, "count": len(items), "item": payload}


@app.delete("/api/watchlist/{login}")
async def delete_watchlist(login: str):
    items = _load_watchlist()
    filtered = [item for item in items if str((item.get("candidate") or {}).get("login") or "").lower() != login.lower()]
    _save_watchlist(filtered)
    return {"saved": False, "login": login, "count": len(filtered)}


@app.get("/api/validation")
async def validation():
    cohorts = validation_registry(ROOT)
    return {
        "protocol": "v2",
        "score_version": SCORE_VERSION,
        "cohorts": cohorts,
        "summary": {
            "registered": len(cohorts),
            "public_frozen": sum(1 for row in cohorts if row.get("artifact_status") == "public-frozen"),
            "freeze_time_committed": sum(1 for row in cohorts if row.get("freeze_time_commitment")),
            "primary_horizon_days": 90,
            "headline_claim_ready": False,
        },
        "message": "No predictive-validity headline claim is permitted before the registered primary horizon matures and protocol-v2 gates are satisfied.",
    }


@app.get("/health")
async def health():
    return {"status": "ok", "app_version": APP_VERSION, "score_version": SCORE_VERSION}


def main():
    uvicorn.run("ghost_talent.app:app", host="127.0.0.1", port=8765, reload=False)


if __name__ == "__main__":
    main()
