"""Telemetry replay + scoring loop for the live dashboard.

Loads the synthetic CSVs once, then walks them in time-ordered windows. Each window
is scored by the REAL trained model (no randomised output); high-scoring transactions
become persisted alerts with SHAP reason codes. Produces the payload the WebSocket
broadcasts. This is the honest replacement for the old repo's random generator.
"""
from __future__ import annotations

import os
import numpy as np
import pandas as pd

from app.config import settings
from app.ml import scorer
from app.ml.model_store import store

WINDOW_DAYS = 0.5           # slice width walked per tick
FLAG_MARGIN = 0.0           # added to tuned threshold if desired


class TelemetryReplay:
    def __init__(self) -> None:
        self.logins: pd.DataFrame | None = None
        self.txns: pd.DataFrame | None = None
        self.cursor = 0.0
        self.max_day = 0.0
        self.threshold = 0.5

    def load(self) -> bool:
        lp = os.path.join(settings.data_dir, "logins.csv")
        tp = os.path.join(settings.data_dir, "transactions.csv")
        if not (os.path.exists(lp) and os.path.exists(tp)):
            return False
        self.logins = pd.read_csv(lp)
        self.txns = pd.read_csv(tp)
        self.max_day = float(self.txns["t_day"].max())
        self.cursor = float(self.txns["t_day"].min())
        return True

    def next_window(self) -> dict:
        """Advance one window, score it, return a dashboard payload."""
        if self.txns is None:
            return {}
        lo, hi = self.cursor, self.cursor + WINDOW_DAYS
        tx_w = self.txns[(self.txns["t_day"] >= lo) & (self.txns["t_day"] < hi)]
        lg_w = self.logins[self.logins["t_day"] < hi]
        self.cursor = hi if hi < self.max_day else float(self.txns["t_day"].min())  # loop

        result = scorer.score_window(lg_w, tx_w)
        scores = result["scores"]
        flagged = [s for s in scores if s["prob"] >= self.threshold]
        threat_score = round(100 * float(np.mean([s["prob"] for s in scores])) if scores else 0.0, 1)

        return {
            "window": [round(lo, 3), round(hi, 3)],
            "n_transactions": len(scores),
            "threat_score": threat_score,
            "active_threats": len(flagged),
            "betti_curve1": [round(x, 2) for x in result["betti_curve1"]],
            "flagged": sorted(flagged, key=lambda s: -s["prob"])[:10],
            "_data": result["data"], "_feats": result["feats"],
        }


replay = TelemetryReplay()
