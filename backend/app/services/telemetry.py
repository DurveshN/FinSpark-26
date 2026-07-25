"""Telemetry replay + scoring for the live dashboard.

Design: score the ENTIRE synthetic dataset ONCE (in a background thread at startup),
then each stream tick just SLICES the pre-scored results by time window. This keeps
the async event loop free — heavy model/graph/topology work never runs per-tick
(which previously blocked uvicorn and hung the server). SHAP is computed lazily,
off-loop, and cached (see api/stream.py).
"""
from __future__ import annotations

import os
import numpy as np
import pandas as pd
import torch

from app.config import settings
from app.ml.model_store import store
from ml.features.fusion import build_features
from ml.features.graph import build_graph
from ml.features.topology import betti_curve

WINDOW_DAYS = 0.5

_TOPO_COLS = ["amount_zscore", "log_amount", "new_payee",
              "sec_since_login", "login_new_device", "login_failed_prior",
              "tls_quantum_vulnerable"]


class TelemetryReplay:
    def __init__(self) -> None:
        self.logins: pd.DataFrame | None = None
        self.txns: pd.DataFrame | None = None
        self.feats: pd.DataFrame | None = None      # all rows + prob + node_idx + t_day
        self.data = None                             # full PyG graph (for SHAP)
        self.cursor = 0.0
        self.max_day = 0.0
        self.min_day = 0.0
        self.threshold = 0.5
        self.ready = False

    def load(self) -> bool:
        lp = os.path.join(settings.data_dir, "logins.csv")
        tp = os.path.join(settings.data_dir, "transactions.csv")
        if not (os.path.exists(lp) and os.path.exists(tp)):
            return False
        self.logins = pd.read_csv(lp)
        self.txns = pd.read_csv(tp)
        self.min_day = float(self.txns["t_day"].min())
        self.max_day = float(self.txns["t_day"].max())
        self.cursor = self.min_day
        return True

    def prepare(self) -> None:
        """One-time full scoring (runs in a background thread). Heavy; sets ready."""
        if store.model is None or self.txns is None:
            return
        cache = os.path.join(settings.data_dir, "cust_betti_cache.csv")
        feats = build_features(self.logins, self.txns)
        data, _cols = build_graph(feats, self.txns, betti_cache=cache if os.path.exists(cache) else None)
        data.x = torch.tensor(store.standardize(data.x.numpy()), dtype=torch.float32)
        with torch.no_grad():
            prob = torch.softmax(store.model(data.x, data.edge_index), dim=1)[:, 1].numpy()
        feats = feats.reset_index(drop=True)
        feats["prob"] = prob
        feats["node_idx"] = np.arange(len(feats))
        feats["t_day"] = feats["txn_id"].map(self.txns.set_index("txn_id")["t_day"].to_dict())
        self.feats = feats
        self.data = data
        self.ready = True
        # SHAP is computed ON DEMAND when an analyst clicks an alert (/explain),
        # never in the stream loop — computing it here (776 nodes) would hold the
        # GIL and starve the event loop. On-demand subgraph SHAP is ~0.4s per click.

    def next_window(self) -> dict:
        """Slice pre-scored results for the next window. Fast + non-blocking."""
        if not self.ready or self.feats is None:
            return {"warming_up": True, "window": [0, 0], "n_transactions": 0,
                    "threat_score": 0.0, "active_threats": 0, "betti_curve1": [],
                    "quantum": {}, "flagged": []}

        lo, hi = self.cursor, self.cursor + WINDOW_DAYS
        w = self.feats[(self.feats["t_day"] >= lo) & (self.feats["t_day"] < hi)]
        self.cursor = hi if hi < self.max_day else self.min_day     # loop

        probs = w["prob"].to_numpy()
        threat = round(100 * float(probs.mean()), 1) if len(probs) else 0.0
        flagged_rows = w[w["prob"] >= self.threshold].sort_values("prob", ascending=False).head(10)
        flagged = [
            {"txn_id": r.txn_id, "customer_id": r.customer_id, "amount": float(r.amount),
             "prob": float(r.prob), "node_idx": int(r.node_idx), "scenario": r.scenario}
            for r in flagged_rows.itertuples(index=False)
        ]
        curve = betti_curve(w[_TOPO_COLS].to_numpy(dtype=float), dim=1, n_bins=10) if len(w) else []
        lg_win = self.logins[(self.logins["t_day"] >= lo) & (self.logins["t_day"] < hi)]

        return {
            "window": [round(lo, 3), round(hi, 3)],
            "n_transactions": int(len(w)),
            "threat_score": threat,
            "active_threats": int((w["prob"] >= self.threshold).sum()),
            "betti_curve1": [round(x, 2) for x in curve],
            "quantum": self._crypto_posture(lg_win),
            "flagged": flagged,
        }

    @staticmethod
    def _crypto_posture(lg_win: pd.DataFrame) -> dict:
        """Real quantum-risk posture from window logins (crypto exposure), not attack detection."""
        if lg_win.empty:
            return {"total_conns": 0, "quantum_vulnerable_pct": 0.0, "downgrade_events": 0, "modern_pct": 0.0}
        tls = lg_win["tls"].astype(str)
        vuln = tls.str.contains("RSA") | tls.str.startswith("TLS1.0") | tls.str.startswith("TLS1.2:ECDHE-RSA")
        weak = tls.str.contains("EXPORT") | tls.str.startswith("TLS1.0")
        n = len(lg_win)
        return {"total_conns": int(n), "quantum_vulnerable_pct": round(100 * float(vuln.mean()), 1),
                "downgrade_events": int(weak.sum()), "modern_pct": round(100 * float((~vuln).mean()), 1)}


replay = TelemetryReplay()
