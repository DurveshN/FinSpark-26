"""SHAP reason codes for a flagged transaction.

Explains a single node's malicious probability by perturbing ONLY that node's
feature vector while holding its graph neighbourhood fixed, then running SHAP's
KernelExplainer. Produces the per-feature attributions the dashboard shows as
plain-English reason codes (real values, not hardcoded).
"""
from __future__ import annotations

import numpy as np
import shap
import torch

from app.ml.model_store import store


def _node_score_fn(node_idx: int, x: torch.Tensor, edge_index: torch.Tensor):
    """Return f(feature_matrix) -> P(malicious) for one node, graph fixed."""
    base = x.clone()

    def f(feature_rows: np.ndarray) -> np.ndarray:
        probs = []
        for row in feature_rows:
            xx = base.clone()
            xx[node_idx] = torch.tensor(row, dtype=torch.float32)
            with torch.no_grad():
                out = store.model(xx, edge_index)
                probs.append(torch.softmax(out[node_idx], dim=0)[1].item())
        return np.array(probs)

    return f


def reason_codes(node_idx: int, x: torch.Tensor, edge_index: torch.Tensor,
                 top_k: int = 5) -> list[dict]:
    """Return top_k feature attributions [{feature, value, shap_value}] for a node."""
    if store.background is None or store.model is None:
        return []
    bg = shap.sample(store.background, min(40, len(store.background)))
    explainer = shap.KernelExplainer(_node_score_fn(node_idx, x, edge_index), bg)
    row = x[node_idx].numpy().reshape(1, -1)
    vals = explainer.shap_values(row, nsamples=100, silent=True)[0]

    order = np.argsort(-np.abs(vals))[:top_k]
    return [
        {"feature": store.cols[i], "value": float(x[node_idx, i]), "shap_value": float(vals[i])}
        for i in order
    ]
