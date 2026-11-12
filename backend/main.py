"""FastAPI entry point serving the SPA frontend, REST health/catalog endpoints, and /ws/{client_id}."""

from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
import logging
from pathlib import Path
from typing import AsyncIterator

from fastapi import FastAPI, Query, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from backend.data.country_store import COUNTRIES_BANK
from backend.room_manager import RoomManager

logger = logging.getLogger("blackout")

BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"
MAX_WS_FRAME_BYTES = 64 * 1024  # 64 KB cap per incoming WebSocket frame

room_manager = RoomManager()


async def _tick_worker(manager: RoomManager) -> None:
    while True:
        await asyncio.sleep(0.20)
        try:
            await manager.tick_all_rooms()
        except Exception:
            logger.exception("Unhandled error in background room tick worker")


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    tick_task = asyncio.create_task(_tick_worker(room_manager))
    try:
        yield
    finally:
        tick_task.cancel()
        try:
            await tick_task
        except asyncio.CancelledError:
            pass


app = FastAPI(
    title="Blackout Arcade — Multiplayer Games Hub",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/health")
async def health_check() -> JSONResponse:
    return JSONResponse(
        {
            "status": "ok",
            "active_rooms": len(room_manager.rooms),
            "connected_clients": sum(
                1 for c in room_manager.clients.values() if c.websocket is not None
            ),
        }
    )


@app.get("/api/games")
async def list_games() -> JSONResponse:
    return JSONResponse({"games": room_manager.get_catalog()})


@app.get("/api/leaderboard")
async def get_leaderboard() -> JSONResponse:
    return JSONResponse(
        {"leaderboard": room_manager.leaderboard.get_summary(limit_per_game=10)}
    )


@app.get("/api/countries")
async def list_countries(
    q: str = Query(default="", max_length=80),
    continent: str = Query(default="All", max_length=40),
) -> JSONResponse:
    query = q.strip().lower()
    cont = continent.strip()
    filtered = [
        c
        for c in COUNTRIES_BANK
        if (cont == "All" or c.get("continent") == cont)
        and (
            not query
            or query in c["name"].lower()
            or query in c["capital"].lower()
            or query in c["code"].lower()
            or query in c["subregion"].lower()
        )
    ]
    return JSONResponse({"count": len(filtered), "countries": filtered})


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    client_id: str,
    secret: str | None = Query(default=None),
) -> None:
    connected = False
    try:
        connected = await room_manager.connect(client_id, websocket, secret=secret)
        if not connected:
            return
        while True:
            raw_text = await websocket.receive_text()
            if len(raw_text.encode("utf-8")) > MAX_WS_FRAME_BYTES:
                await room_manager.send_error(
                    client_id, "Message exceeds 64 KB frame size limit."
                )
                continue
            await room_manager.handle_message(client_id, raw_text)
    except WebSocketDisconnect:
        if connected:
            await room_manager.disconnect(client_id, websocket=websocket)
    except Exception:
        logger.exception("Unhandled WebSocket error for client %s", client_id)
        if connected:
            await room_manager.disconnect(client_id, websocket=websocket)


if (FRONTEND_DIR / "css").exists():
    app.mount("/css", StaticFiles(directory=FRONTEND_DIR / "css"), name="css")
if (FRONTEND_DIR / "js").exists():
    app.mount("/js", StaticFiles(directory=FRONTEND_DIR / "js"), name="js")
if (FRONTEND_DIR / "data").exists():
    app.mount("/data", StaticFiles(directory=FRONTEND_DIR / "data"), name="data")
if (FRONTEND_DIR / "vendor").exists():
    app.mount("/vendor", StaticFiles(directory=FRONTEND_DIR / "vendor"), name="vendor")
if (FRONTEND_DIR / "flags").exists():
    app.mount("/flags", StaticFiles(directory=FRONTEND_DIR / "flags"), name="flags")


@app.get("/")
async def serve_index() -> FileResponse:
    return FileResponse(FRONTEND_DIR / "index.html")
