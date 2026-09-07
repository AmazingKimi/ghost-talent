from pathlib import Path

import uvicorn
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse

from .scout import scout
from .snapshot import save_snapshot


app = FastAPI(title="Ghost Talent", version="0.2.0")
ROOT = Path(__file__).resolve().parent.parent


@app.get("/")
async def index():
    return FileResponse(ROOT / "web" / "index.html")


@app.get("/favicon.ico", include_in_schema=False)
@app.get("/favicon.svg", include_in_schema=False)
async def favicon():
    return FileResponse(ROOT / "web" / "favicon.svg", media_type="image/svg+xml")


@app.get("/api/scout")
async def run_scout(q: str = Query(min_length=2, max_length=120), limit: int = 20):
    try:
        scout_result = await scout(q, limit=max(1, min(limit, 20)))
        results = scout_result["results"]
        sources = scout_result["sources"]
        snapshot = save_snapshot(ROOT, q, results)
        return {
            "query": q,
            "count": len(results),
            "results": results,
            "sources": sources,
            "snapshot": snapshot,
        }
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Scout failed: {exc}") from exc


@app.get("/health")
async def health():
    return {"status": "ok", "version": "0.2.0"}


def main():
    uvicorn.run("ghost_talent.app:app", host="127.0.0.1", port=8765, reload=False)


if __name__ == "__main__":
    main()
