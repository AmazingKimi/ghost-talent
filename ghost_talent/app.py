from pathlib import Path
import os

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse, HTMLResponse

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

from .dossier import build_dossier
from .scout import scout, scout_preview
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
    return {
        "status": "ok",
        "version": APP_VERSION,
        "github_token_configured": bool(os.getenv("GITHUB_TOKEN")),
    }


@app.get("/api/scout/preview")
async def run_scout_preview(q: str = Query(min_length=2, max_length=120), limit: int = 6):
    try:
        return await scout_preview(q, limit=max(1, min(limit, 6)))
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Preview failed: {exc}") from exc


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
