"""WebSocket telemetry stream + connection manager.

Broadcasts one pre-scored window per interval. SHAP for flagged transactions is
computed OFF the event loop (thread pool), cached per txn_id, and bounded to the
top few — so the async loop is never blocked (the bug that hung the server before).
"""
from __future__ import annotations

import asyncio
import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.config import settings
from app.db.base import SessionLocal
from app.ml import explain
from app.ml.model_store import store
from app.services.alerts import save_alert
from app.services.telemetry import replay

router = APIRouter()

_shap_cache: dict[str, list] = {}     # txn_id -> reason_codes
MAX_SHAP_PER_TICK = 3                  # bound off-loop work per window


class ConnectionManager:
    def __init__(self) -> None:
        self.active: list[WebSocket] = []

    async def connect(self, ws: WebSocket) -> None:
        await ws.accept()
        self.active.append(ws)

    def disconnect(self, ws: WebSocket) -> None:
        if ws in self.active:
            self.active.remove(ws)

    async def broadcast(self, message: dict) -> None:
        dead = []
        payload = json.dumps(message)
        for ws in self.active:
            try:
                await ws.send_text(payload)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(ws)


manager = ConnectionManager()


def explain_txn(node_idx: int, txn_id: str) -> list:
    """Compute (or return cached) SHAP reason codes for one transaction. Thread-safe."""
    if txn_id in _shap_cache:
        return _shap_cache[txn_id]
    if replay.data is None:
        return []
    try:
        _shap_cache[txn_id] = explain.reason_codes(node_idx, replay.data.x, replay.data.edge_index)
    except Exception:
        _shap_cache[txn_id] = []
    return _shap_cache[txn_id]


def _persist_flagged(flagged: list[dict]) -> None:
    """Off-loop: persist flagged transactions as alerts (SHAP added lazily via /explain)."""
    db = SessionLocal()
    try:
        for s in flagged:
            save_alert(db, txn_id=s["txn_id"], customer_id=s["customer_id"],
                       amount=s["amount"], threat_score=round(s["prob"] * 100, 1),
                       predicted_label=1, scenario=s["scenario"],
                       reason_codes=_shap_cache.get(s["txn_id"], []))
    finally:
        db.close()


async def stream_loop() -> None:
    while True:
        try:
            if manager.active and store.loaded:
                payload = replay.next_window()
                flagged = payload.get("flagged", [])
                # Broadcast IMMEDIATELY. No SHAP here — computed on-demand via /explain.
                await manager.broadcast(payload)
                if flagged:
                    asyncio.create_task(asyncio.to_thread(_persist_flagged, flagged))
            await asyncio.sleep(settings.stream_interval_sec)
        except Exception as e:
            print(f"stream_loop error: {e}", flush=True)
            await asyncio.sleep(settings.stream_interval_sec)


@router.websocket("/ws/stream")
async def ws_stream(ws: WebSocket) -> None:
    await manager.connect(ws)
    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(ws)
