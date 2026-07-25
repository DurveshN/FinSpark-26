"""REST routes: health, model metrics, and recent alerts.

Read-only endpoints the dashboard uses alongside the WebSocket stream. Detection
logic lives in services/ml; routes only marshal requests/responses.
"""
from __future__ import annotations

import json
import os

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.config import settings
from app.db.base import get_session
from app.models.alert import Alert
from app.services.alerts import recent_alerts

router = APIRouter()


@router.get("/health")
def health() -> dict:
    from app.ml.model_store import store
    return {"status": "ok", "model_loaded": store.loaded}


@router.get("/metrics")
def metrics() -> dict:
    path = os.path.join(settings.model_path, "metrics.json")
    if not os.path.exists(path):
        return {"error": "model not trained yet"}
    with open(path) as f:
        return json.load(f)


@router.get("/alerts")
def alerts(limit: int = 50, db: Session = Depends(get_session)) -> list[dict]:
    rows = recent_alerts(db, limit=limit)
    return [
        {
            "id": a.id, "txn_id": a.txn_id, "customer_id": a.customer_id,
            "amount": a.amount, "threat_score": a.threat_score,
            "predicted_label": a.predicted_label, "scenario": a.scenario,
            "reason_codes": a.reason_codes, "created_at": a.created_at.isoformat(),
        }
        for a in rows
    ]
