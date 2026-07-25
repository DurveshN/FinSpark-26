"""WebSocket telemetry stream + connection manager.

Broadcasts one scored window per interval to all connected dashboards. Each tick
runs the real model; flagged transactions get SHAP reason codes and are persisted
as alerts. Replaces the old repo's random broadcast.
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


def _persist_flagged(payload: dict) -> list[dict]:
    """Compute SHAP for flagged txns, persist alerts, return enriched flagged list."""
    data, feats = payload.pop("_data", None), payload.pop("_feats", None)
    enriched = []
    if data is None or feats is None or not payload.get("flagged"):
        return payload.get("flagged", [])
    db = SessionLocal()
    try:
        for s in payload["flagged"]:
            codes = explain.reason_codes(s["node_idx"], data.x, data.edge_index)
            save_alert(db, txn_id=s["txn_id"], customer_id=s["customer_id"],
                       amount=s["amount"], threat_score=round(s["prob"] * 100, 1),
                       predicted_label=1, scenario=s["scenario"], reason_codes=codes)
            enriched.append({**s, "reason_codes": codes})
    finally:
        db.close()
    return enriched


async def stream_loop() -> None:
    """Background task: score a window each interval and broadcast."""
    while True:
        try:
            if manager.active and store.loaded:
                payload = replay.next_window()
                if payload:
                    payload["flagged"] = _persist_flagged(payload)
                    await manager.broadcast(payload)
            await asyncio.sleep(settings.stream_interval_sec)
        except Exception as e:  # keep the loop alive
            print(f"stream_loop error: {e}", flush=True)
            await asyncio.sleep(settings.stream_interval_sec)


@router.websocket("/ws/stream")
async def ws_stream(ws: WebSocket) -> None:
    await manager.connect(ws)
    try:
        while True:
            await ws.receive_text()   # keep-alive; client sends pings
    except WebSocketDisconnect:
        manager.disconnect(ws)
