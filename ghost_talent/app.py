from pathlib import Path
import os

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
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
app = FastAPI(title="Ghost Talent", version=APP_VERSION)


@app.get("/")
async def index():
    html = (ROOT / "web" / "index.html").read_text(encoding="utf-8")
    html = html.replace("</head>", '<link rel="stylesheet" href="/ui-overrides.css"/>\n</head>')
    html = html.replace("</body>", '<script src="/preferences.js"></script>\n</body>')
    return HTMLResponse(html)


@app.get("/ui-overrides.css", include_in_schema=False)
async def ui_overrides():
    return FileResponse(ROOT / "web" / "ui-overrides.css", media_type="text/css")


@app.get("/preferences.js", include_in_schema=False)
async def preferences_script():
    return FileResponse(ROOT / "web" / "preferences.js", media_type="application/javascript")


@app.get("/favicon.ico", include_in_schema=False)
@app.get("/favicon.svg", include_in_schema=False)
async def favicon():
    return FileResponse(ROOT / "web" / "favicon.svg", media_type="image/svg+xml")


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
        raise HTTPException(
            status_code=409,
            detail={"error": "environment_token", "message": "GITHUB_TOKEN is supplied by the environment; remove it from .env to disconnect."},
        )
    disconnect_github()
    return {"status": "disconnected"}


@app.get("/api/scout/preview")
async def run_scout_preview(q: str = Query(min_length=2, max_length=120), limit: int = 6):
    # Preview is intentionally quota-free. The full scout request owns GitHub discovery.
    authenticated = bool(load_connected_token())
    return {
        "query": q,
        "count": 0,
        "results": [],
        "complete": True,
        "sources": {
            "github": {
                "status": "ok",
                "authenticated": authenticated,
                "mode": auth_mode(),
            }
        },
    }


@app.get("/api/scout")
async def run_scout(q: str = Query(min_length=2, max_length=120), limit: int = 20):
    try:
        scout_result = await scout(q, limit=max(1, min(limit, 20)))
        results = scout_result["results"]
        sources = scout_result["sources"]
        complete = bool(scout_result.get("complete", True))
        if not complete:
            raise HTTPException(status_code=503, detail={
                "error": "discovery_incomplete",
                "message": scout_result.get("error", {}).get("message", "Critical source incomplete; no snapshot written."),
                "sources": sources,
                "snapshot_written": False,
            })
        snapshot = save_snapshot(ROOT, q, results, sources=sources)
        histories = snapshot.get("history", {})
        trajectories = snapshot.get("trajectory", {})
        for row in results:
            login = str(row.get("candidate", {}).get("login") or "")
            row["history"] = histories.get(login, {"status": "building_history"})
            row["trajectory"] = trajectories.get(login, {
                "observation_count": 1,
                "d7": {"status": "building_history", "days": 7},
                "d30": {"status": "building_history", "days": 30},
            })
            row["dossier"] = build_dossier(row)
        return {"query": q, "count": len(results), "results": results, "sources": sources, "snapshot": snapshot}
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Scout failed: {exc}") from exc


@app.get("/health")
async def health():
    return {"status": "ok", "version": APP_VERSION}


def main():
    uvicorn.run("ghost_talent.app:app", host="127.0.0.1", port=8765, reload=False)


if __name__ == "__main__":
    main()
