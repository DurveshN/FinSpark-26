"""Pydantic response DTOs for the API.

Shapes the JSON the frontend consumes. No logic; serialization contracts only.
"""
from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel


class ReasonCode(BaseModel):
    feature: str
    value: float
    shap_value: float


class AlertOut(BaseModel):
    id: int
    txn_id: str
    customer_id: str
    amount: float
    threat_score: float
    predicted_label: int
    scenario: str
    reason_codes: list[ReasonCode]
    created_at: datetime

    class Config:
        from_attributes = True


class MetricsOut(BaseModel):
    precision: float
    recall: float
    f1: float
    auc: float
    threshold: float
    model: str
    features: list[str]
