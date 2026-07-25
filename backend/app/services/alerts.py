"""Persist and query threat alerts.

Thin data-access layer over the Alert model: write a detection, list recent alerts.
Keeps DB logic out of routes and the streaming loop.
"""
from __future__ import annotations

from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.models.alert import Alert


def save_alert(db: Session, *, txn_id: str, customer_id: str, amount: float,
               threat_score: float, predicted_label: int, scenario: str,
               reason_codes: list[dict]) -> Alert:
    alert = Alert(
        txn_id=txn_id, customer_id=customer_id, amount=amount,
        threat_score=threat_score, predicted_label=predicted_label,
        scenario=scenario, reason_codes=reason_codes,
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return alert


def recent_alerts(db: Session, limit: int = 50) -> list[Alert]:
    return db.query(Alert).order_by(desc(Alert.created_at)).limit(limit).all()
