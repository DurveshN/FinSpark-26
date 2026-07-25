"""Score a window of transactions with the trained QTD-HGNN.

Builds the fused+topological graph for a batch of transactions, runs the GNN, and
returns per-transaction malicious probabilities plus the window's real Betti curves
for the dashboard. Reuses the offline feature/graph code so training and inference
compute identical features.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import torch

from app.ml.model_store import store
from ml.features.fusion import build_features
from ml.features.graph import build_graph
from ml.features.topology import betti_curve

_TOPO_COLS = ["amount_zscore", "log_amount", "new_payee",
              "sec_since_login", "login_new_device", "login_failed_prior",
              "tls_quantum_vulnerable"]


def score_window(logins: pd.DataFrame, txns: pd.DataFrame) -> dict:
    """Return dict: per-transaction scores + window Betti curves + graph feats.

    scores: list of {txn_id, customer_id, amount, prob, node_idx, scenario, label}
    betti_curve1: list[float] for the dashboard's live topology chart.
    """
    if store.model is None or txns.empty:
        return {"scores": [], "betti_curve1": [], "feats": None, "data": None}

    feats = build_features(logins, txns)
    data, _cols = build_graph(feats, txns)
    data.x = torch.tensor(store.standardize(data.x.numpy()), dtype=torch.float32)

    with torch.no_grad():
        prob = torch.softmax(store.model(data.x, data.edge_index), dim=1)[:, 1].numpy()

    scores = [
        {"txn_id": r.txn_id, "customer_id": r.customer_id, "amount": float(r.amount),
         "prob": float(prob[i]), "node_idx": int(i),
         "scenario": r.scenario, "label": int(r.label)}
        for i, r in enumerate(feats.itertuples(index=False))
    ]
    curve = betti_curve(feats[_TOPO_COLS].to_numpy(dtype=float), dim=1, n_bins=10)
    return {"scores": scores, "betti_curve1": curve, "feats": feats, "data": data}
