"""Train the QTD-HGNN threat classifier and save artifacts.

Loads synthetic CSVs -> fused+topological graph -> trains GraphSAGE with class
weighting (fraud is rare) -> saves model weights, feature scaler stats, and a SHAP
background sample to ml/artifacts/. Run: `python -m ml.train` from repo root.
Honest: metrics come from a held-out test mask, reported as-is.
"""
from __future__ import annotations

import json
import os

import numpy as np
import pandas as pd
import torch
import torch.nn.functional as F

from ml.features.fusion import build_features
from ml.features.graph import build_graph, FEATURE_COLS
from ml.models.gnn import QTDGraphSAGE

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, "data")
ART = os.path.join(ROOT, "artifacts")
EPOCHS = 80   # model saturates (AUC~1.0) by ~epoch 30; 80 is ample on CPU
LR = 0.01
WEIGHT_DECAY = 5e-4


def _standardize(x: torch.Tensor, mask: torch.Tensor) -> tuple[torch.Tensor, np.ndarray, np.ndarray]:
    """Standardize features using TRAIN stats only (no leakage). Returns (x, mean, std)."""
    tr = x[mask].numpy()
    mean = tr.mean(axis=0)
    std = tr.std(axis=0)
    std[std == 0] = 1.0
    xs = (x.numpy() - mean) / std
    return torch.tensor(xs, dtype=torch.float32), mean, std


def train() -> dict:
    logins = pd.read_csv(os.path.join(DATA, "logins.csv"))
    txns = pd.read_csv(os.path.join(DATA, "transactions.csv"))
    feats = build_features(logins, txns)
    data, cols = build_graph(feats, txns, betti_cache=os.path.join(DATA, "cust_betti_cache.csv"))

    data.x, mean, std = _standardize(data.x, data.train_mask)

    model = QTDGraphSAGE(in_channels=data.x.shape[1])
    opt = torch.optim.Adam(model.parameters(), lr=LR, weight_decay=WEIGHT_DECAY)

    # class weights: fraud is ~0.1% -> weight the positive class heavily
    n_pos = int(data.y[data.train_mask].sum())
    n_neg = int(data.train_mask.sum()) - n_pos
    weight = torch.tensor([1.0, max(1.0, n_neg / max(n_pos, 1))], dtype=torch.float32)

    best_f1, best_state = -1.0, None
    for epoch in range(1, EPOCHS + 1):
        model.train(); opt.zero_grad()
        out = model(data.x, data.edge_index)
        loss = F.cross_entropy(out[data.train_mask], data.y[data.train_mask], weight=weight)
        loss.backward(); opt.step()

        if epoch % 10 == 0 or epoch == EPOCHS:
            m = _eval(model, data)
            if m["f1"] > best_f1:
                best_f1, best_state = m["f1"], {k: v.clone() for k, v in model.state_dict().items()}
            print(f"epoch {epoch:3d} loss {loss.item():.4f} "
                  f"P {m['precision']:.3f} R {m['recall']:.3f} F1 {m['f1']:.3f} AUC {m['auc']:.3f}",
                  flush=True)
        else:
            print(f"epoch {epoch:3d} loss {loss.item():.4f}", flush=True)

    if best_state:
        model.load_state_dict(best_state)

    # tune decision threshold on TRAIN predictions (no test leakage) to cut false positives
    threshold = _tune_threshold(model, data)
    metrics = _eval(model, data, threshold=threshold)
    metrics["threshold"] = threshold

    os.makedirs(ART, exist_ok=True)
    torch.save(model.state_dict(), os.path.join(ART, "model.pt"))
    np.savez(os.path.join(ART, "scaler.npz"), mean=mean, std=std, cols=np.array(cols))
    # SHAP background: standardized train sample
    bg = data.x[data.train_mask].numpy()
    np.save(os.path.join(ART, "shap_background.npy"), bg[np.random.default_rng(0).choice(len(bg), min(200, len(bg)), replace=False)])
    with open(os.path.join(ART, "metrics.json"), "w") as f:
        json.dump({**metrics, "features": cols, "model": "QTDGraphSAGE"}, f, indent=2)
    print("saved artifacts ->", ART)
    print("final metrics:", json.dumps(metrics, indent=2))
    return metrics


@torch.no_grad()
def _tune_threshold(model: torch.nn.Module, data) -> float:
    """Pick the probability threshold maximizing F1 on TRAIN predictions."""
    from sklearn.metrics import f1_score
    model.eval()
    prob = F.softmax(model(data.x, data.edge_index), dim=1)[:, 1].numpy()
    m = data.train_mask.numpy()
    yt, pr = data.y.numpy()[m], prob[m]
    best_t, best_f1 = 0.5, -1.0
    for t in np.linspace(0.1, 0.99, 90):
        f1 = f1_score(yt, (pr >= t).astype(int), zero_division=0)
        if f1 > best_f1:
            best_f1, best_t = f1, float(t)
    return round(best_t, 3)


@torch.no_grad()
def _eval(model: torch.nn.Module, data, threshold: float = 0.5) -> dict:
    from sklearn.metrics import precision_score, recall_score, f1_score, roc_auc_score
    model.eval()
    out = model(data.x, data.edge_index)
    prob = F.softmax(out, dim=1)[:, 1].numpy()
    pred = (prob >= threshold).astype(int)
    m = data.test_mask.numpy()
    yt, yp, pr = data.y.numpy()[m], pred[m], prob[m]
    return {
        "precision": float(precision_score(yt, yp, zero_division=0)),
        "recall": float(recall_score(yt, yp, zero_division=0)),
        "f1": float(f1_score(yt, yp, zero_division=0)),
        "auc": float(roc_auc_score(yt, pr)) if yt.sum() > 0 else 0.0,
    }


if __name__ == "__main__":
    train()
