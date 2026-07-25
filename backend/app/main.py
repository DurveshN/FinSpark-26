"""FastAPI application assembly.

Wires CORS, DB tables, model + telemetry load, REST routes, and the WebSocket
stream loop. Assembly only — no business logic here.
"""
from __future__ import annotations

import json
import os
from contextlib import asynccontextmanager

import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.db.base import Base, engine
from app.ml.model_store import store
from app.services.telemetry import replay
from app.api import routes, stream


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)          # ensure tables (Alembic owns prod schema)
    loaded = store.load()
    if loaded and replay.load():
        # apply tuned threshold from training artifacts
        mpath = os.path.join(settings.model_path, "metrics.json")
        if os.path.exists(mpath):
            with open(mpath) as f:
                replay.threshold = float(json.load(f).get("threshold", 0.5))
        print(f"model loaded; stream threshold={replay.threshold}", flush=True)
    else:
        print("WARNING: model/data not found — train first (python -m ml.train)", flush=True)
    task = asyncio.create_task(stream.stream_loop())
    yield
    task.cancel()


app = FastAPI(title="QTD-HGNN Backend", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.cors_origin] if settings.cors_origin != "*" else ["*"],
    allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)

app.include_router(routes.router)
app.include_router(stream.router)


@app.get("/")
def root() -> dict:
    return {"service": "QTD-HGNN Backend", "docs": "/docs", "health": "/health"}
