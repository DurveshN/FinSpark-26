"""Pre-score the whole dataset at BUILD time; the backend just loads the result.

Runs offline (in the Docker build): generate data if missing -> build fused+topological
graph -> score every transaction with the trained model -> save:
  ml/artifacts/scored.csv   (per-txn rows + prob + node_idx + t_day + topo cols)
  ml/artifacts/graph.pt     (standardized x + edge_index, for on-demand SHAP subgraphs)

This keeps runtime startup instant and non-blocking (no 559k-node scoring on the
event loop, which starved uvicorn). Run: `python -m ml.prescore` from repo root.
"""
from __future__ import annotations

import os
import numpy as np
import pandas as pd
import torch

from ml.features.fusion import build_features
from ml.features.graph import build_graph, FEATURE_COLS

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, "data")
ART = os.path.join(ROOT, "artifacts")

# columns the dashboard needs per window (topology curve + alert display)
_KEEP = ["txn_id", "customer_id", "amount", "scenario", "prob", "node_idx", "t_day",
         "amount_zscore", "log_amount", "new_payee", "sec_since_login",
         "login_new_device", "login_failed_prior", "tls_quantum_vulnerable"]


def main() -> None:
    # 1. ensure data exists (deterministic; safe to regenerate in a clean build)
    if not os.path.exists(os.path.join(DATA, "transactions.csv")):
        from ml.generate_synthetic import main as gen
        gen()

    logins = pd.read_csv(os.path.join(DATA, "logins.csv"))
    txns = pd.read_csv(os.path.join(DATA, "transactions.csv"))

    # 2. load trained artifacts
    sc = np.load(os.path.join(ART, "scaler.npz"), allow_pickle=True)
    mean, std, cols = sc["mean"], sc["std"], [str(c) for c in sc["cols"]]
    from ml.models.gnn import QTDGraphSAGE
    model = QTDGraphSAGE(in_channels=len(cols))
    model.load_state_dict(torch.load(os.path.join(ART, "model.pt"), map_location="cpu"))
    model.eval()

    # 3. build graph + score
    cache = os.path.join(DATA, "cust_betti_cache.csv")
    feats = build_features(logins, txns)
    data, _ = build_graph(feats, txns, betti_cache=cache if os.path.exists(cache) else None)
    x_std = torch.tensor((data.x.numpy() - mean) / std, dtype=torch.float32)
    with torch.no_grad():
        prob = torch.softmax(model(x_std, data.edge_index), dim=1)[:, 1].numpy()

    feats = feats.reset_index(drop=True)
    feats["prob"] = prob
    feats["node_idx"] = np.arange(len(feats))
    feats["t_day"] = feats["txn_id"].map(txns.set_index("txn_id")["t_day"].to_dict())

    # 4. save scored rows + graph tensors
    os.makedirs(ART, exist_ok=True)
    feats[_KEEP].to_csv(os.path.join(ART, "scored.csv"), index=False)
    torch.save({"x": x_std, "edge_index": data.edge_index}, os.path.join(ART, "graph.pt"))
    print(f"prescored {len(feats)} txns, {int((prob >= 0.99).sum())} flagged >=0.99 -> {ART}")


if __name__ == "__main__":
    main()
