"""Universe XXV (v4.0) — Hardened Read-Only Observatory & APA Monograph Server.

Serves:
- `/` : Responsive Desktop & Mobile 3D Super-Earth Observatory
- `/api/papers` & `/papers/{filename}` : Locked 15–20p A4 APA 7th PDFs (Dr. Sergio Buedo Martínez)
- `/api/daily-summaries` : Bilingual (EN / ES) longitudinal day-by-day chronicles
- `/ws` : Strictly one-way read-only 60 FPS interpolated telemetry stream
"""

from __future__ import annotations

import asyncio
import json
import os
import shutil
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Set

from fastapi import FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse

from backend.academia.paper_generator import compile_weekly_apa_paper
from backend.mirofish_lab.observer import MiroFishObservatory

ROOT_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = ROOT_DIR / "frontend"
CHRONICLES_DIR = ROOT_DIR / "chronicles"
PAPERS_DIR = CHRONICLES_DIR / "papers"

if os.getenv("FRESH_GENESIS", "0") == "1" and CHRONICLES_DIR.exists():
    shutil.rmtree(CHRONICLES_DIR, ignore_errors=True)

DEFAULT_SPEED = int(os.getenv("COSMOS_SPEED", "5"))
observatory = MiroFishObservatory(ledger_dir=CHRONICLES_DIR, seed=4201, founders_per_lineage=7)
observatory.speed_multiplier = DEFAULT_SPEED
connected_clients: Set[WebSocket] = set()


async def simulation_loop() -> None:
    await observatory.cortex.probe()
    # Ensure Inaugural Monograph #1 PDF exists for immediate public reading
    manifest_file = PAPERS_DIR / "papers_manifest.json"
    if not manifest_file.exists():
        try:
            await asyncio.to_thread(
                compile_weekly_apa_paper,
                observatory.ledger_dir / "universe_xxv.sqlite",
                PAPERS_DIR,
                1,
            )
        except Exception:
            pass

    while True:
        speed = max(1, observatory.speed_multiplier)
        steps = max(1, speed)
        for _ in range(steps):
            await observatory.step_once()

        if connected_clients:
            payload = observatory.snapshot_for_ui()
            stale: Set[WebSocket] = set()
            for ws in list(connected_clients):
                try:
                    await ws.send_json(payload)
                except Exception:
                    stale.add(ws)
            connected_clients.difference_update(stale)

        await asyncio.sleep(0.25)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    loop_task = asyncio.create_task(simulation_loop())
    try:
        yield
    finally:
        loop_task.cancel()
        await observatory.cortex.close()
        observatory.warehouse.close()


app = FastAPI(
    title="Universe XXV (v4.0) — Super-Earth Longitudinal Observatory",
    version="4.0.0",
    docs_url=None,
    redoc_url=None,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.middleware("http")
async def security_headers(request: Request, call_next):
    resp = await call_next(request)
    resp.headers["X-Content-Type-Options"] = "nosniff"
    resp.headers["X-Frame-Options"] = "SAMEORIGIN"
    return resp


@app.get("/")
async def index() -> FileResponse:
    return FileResponse(FRONTEND_DIR / "index.html")


@app.get("/api/world-init")
async def get_world_init() -> JSONResponse:
    return JSONResponse(observatory.world_init_payload())


@app.get("/api/state")
async def get_state() -> JSONResponse:
    return JSONResponse(observatory.snapshot_for_ui())


@app.get("/api/daily-summaries")
async def get_daily_summaries() -> JSONResponse:
    return JSONResponse({"daily_logs": observatory.warehouse.recent_daily_summaries(limit=60)})


@app.get("/api/papers")
async def list_papers() -> JSONResponse:
    manifest_file = PAPERS_DIR / "papers_manifest.json"
    if not manifest_file.exists():
        return JSONResponse({"papers": []})
    papers = json.loads(manifest_file.read_text(encoding="utf-8"))
    return JSONResponse({"papers": papers})


@app.get("/papers/{filename}")
async def serve_locked_paper(filename: str) -> FileResponse:
    safe_name = Path(filename).name
    target = PAPERS_DIR / safe_name
    if not target.exists() or target.suffix.lower() != ".pdf":
        raise HTTPException(status_code=404, detail="Monograph not found")
    return FileResponse(
        target,
        media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="{safe_name}"'},
    )


@app.post("/api/local-pace")
async def set_local_pace(request: Request) -> JSONResponse:
    forwarded = request.headers.get("cf-connecting-ip") or request.headers.get("x-forwarded-for")
    client_host = request.client.host if request.client else ""
    if forwarded or client_host not in ("127.0.0.1", "::1", "localhost"):
        return JSONResponse({"mode": "client_dvr_only", "speed": observatory.speed_multiplier})
    body = await request.json()
    sp = int(body.get("speed", 5))
    if sp in (1, 2, 5, 10, 20):
        observatory.speed_multiplier = sp
    return JSONResponse({"mode": "server_clock", "speed": observatory.speed_multiplier})


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket) -> None:
    await ws.accept()
    connected_clients.add(ws)
    try:
        await ws.send_json(observatory.snapshot_for_ui())
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        connected_clients.discard(ws)
    except Exception:
        connected_clients.discard(ws)
