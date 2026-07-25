"""Alert ORM model — a persisted, auditable threat detection.

One row per flagged transaction: the score, predicted label, scenario, top SHAP
reason codes (JSON), and timestamp. This is what makes detections real and
auditable (RBI/DPDP), versus the old repo's ephemeral random JSON.
"""
from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, Float, DateTime, JSON

from app.db.base import Base


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    txn_id = Column(String, index=True, nullable=False)
    customer_id = Column(String, index=True, nullable=False)
    amount = Column(Float, nullable=False)
    threat_score = Column(Float, nullable=False)      # 0-100
    predicted_label = Column(Integer, nullable=False)  # 0 benign / 1 malicious
    scenario = Column(String, nullable=False)          # ground-truth tag (synthetic)
    reason_codes = Column(JSON, nullable=False)        # [{feature, shap_value}, ...]
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
