"""SHAP reason codes for a flagged transaction — fast, real, off the full graph.

Runs SHAP's KernelExplainer on the node's local k-hop subgraph (not the full
559k-node graph), so each explanation is ~100x cheaper while still explaining the
actual trained GNN. Positive SHAP -> pushes toward malicious, negative -> benign.
"""
from __future__ import annotations

import numpy as np
import shap
import torch
from torch_geometric.utils import k_hop_subgraph

from app.ml.model_store import store

_NSAMPLES = 60
_BG = 20


def reason_codes(node_idx: int, x: torch.Tensor, edge_index: torch.Tensor,
                 top_k: int = 5) -> list[dict]:
    """Top_k feature attributions [{feature, value, shap_value}] for one node."""
    if store.background is None or store.model is None:
        return []

    # local 2-hop subgraph around the node (GNN is 2 layers) — keeps SHAP cheap
    subset, sub_edge, mapping, _ = k_hop_subgraph(
        int(node_idx), num_hops=2, edge_index=edge_index, relabel_nodes=True)
    sub_x = x[subset].clone()
    local_idx = int(mapping.item())

    base = sub_x.clone()

    def f(rows: np.ndarray) -> np.ndarray:
        probs = []
        for row in rows:
            xx = base.clone()
            xx[local_idx] = torch.tensor(row, dtype=torch.float32)
            with torch.no_grad():
                out = store.model(xx, sub_edge)
                probs.append(torch.softmax(out[local_idx], dim=0)[1].item())
        return np.array(probs)

    bg = shap.sample(store.background, min(_BG, len(store.background)))
    explainer = shap.KernelExplainer(f, bg)
    row = x[node_idx].numpy().reshape(1, -1)
    vals = explainer.shap_values(row, nsamples=_NSAMPLES, silent=True)[0]

    order = np.argsort(-np.abs(vals))[:top_k]
    return [{"feature": store.cols[i], "value": float(x[node_idx, i]), "shap_value": float(vals[i])}
            for i in order]
