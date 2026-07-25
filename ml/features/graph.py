"""Assemble the transaction graph (PyG Data) with fused + topological node features.

Nodes = transactions. Edges connect transactions sharing a customer (temporal
sequence -> account takeover) and sharing a payee (hub -> mule rings). Per-customer
persistent-homology features are attached so the GNN actually consumes topology
(the fix for the old repo, where Betti was computed but never used).
"""
from __future__ import annotations

import os
import warnings

import numpy as np
import pandas as pd
import torch
from torch_geometric.data import Data

from .topology import betti_numbers

warnings.filterwarnings("ignore", module="ripser")

# node feature columns fed to the model (order matters — reused at inference)
FEATURE_COLS = [
    "amount_zscore", "log_amount", "new_payee", "sec_since_login",
    "sec_since_payee_add", "is_swift", "is_imps",
    "login_new_device", "login_failed_prior", "login_odd_hour",
    "tls_quantum_vulnerable", "tls_weak_downgrade", "geo_mismatch",
    "cust_betti0", "cust_betti1", "cust_betti2",   # <-- topological features
]

_TOPO_COLS = ["amount_zscore", "log_amount", "new_payee",
              "sec_since_login", "login_new_device", "login_failed_prior",
              "tls_quantum_vulnerable"]


def _per_customer_betti(feats: pd.DataFrame, cache_path: str | None = None) -> pd.DataFrame:
    """Compute real Betti numbers over each customer's transaction feature cloud.

    Cached to CSV (keyed by cache_path) since ripser over all customers is ~55s.
    """
    if cache_path and os.path.exists(cache_path):
        return pd.read_csv(cache_path)
    rows = []
    for cid, grp in feats.groupby("customer_id"):
        pts = grp[_TOPO_COLS].to_numpy(dtype=float)
        b = betti_numbers(pts)
        rows.append((cid, b["betti0"], b["betti1"], b["betti2"]))
    out = pd.DataFrame(rows, columns=["customer_id", "cust_betti0", "cust_betti1", "cust_betti2"])
    if cache_path:
        out.to_csv(cache_path, index=False)
    return out


def _edge_index(feats: pd.DataFrame) -> np.ndarray:
    """Build undirected edges: same-customer sequential + same-payee hub (capped)."""
    edges = []
    idx = np.arange(len(feats))
    # same-customer: link each txn to the customer's previous txn (temporal chain)
    for _, grp in feats.assign(_i=idx).sort_values("t_day_order").groupby("customer_id"):
        seq = grp["_i"].to_numpy()
        for a, b in zip(seq[:-1], seq[1:]):
            edges.append((a, b))
    # same-payee: link txns to a shared payee (cap per hub to keep edges O(n))
    for _, grp in feats.assign(_i=idx).groupby("payee_key"):
        seq = grp["_i"].to_numpy()
        if 2 <= len(seq) <= 40:               # skip giant generic hubs
            for a, b in zip(seq[:-1], seq[1:]):
                edges.append((a, b))
    if not edges:
        return np.empty((2, 0), dtype=np.int64)
    e = np.array(edges, dtype=np.int64).T
    return np.concatenate([e, e[::-1]], axis=1)   # undirected


def build_graph(feats: pd.DataFrame, txns: pd.DataFrame, seed: int = 42,
                betti_cache: str | None = None) -> tuple[Data, list[str]]:
    """Return (PyG Data with x/edge_index/y/train+test masks, feature column names)."""
    feats = feats.reset_index(drop=True).copy()
    # attach ordering + payee key needed for edges
    order = txns.set_index("txn_id")["t_day"].to_dict()
    payee = txns.set_index("txn_id")["payee_id"].to_dict()
    feats["t_day_order"] = feats["txn_id"].map(order)
    feats["payee_key"] = feats["txn_id"].map(payee)

    betti = _per_customer_betti(feats, cache_path=betti_cache)
    feats = feats.merge(betti, on="customer_id", how="left").fillna(0)

    x = torch.tensor(feats[FEATURE_COLS].to_numpy(dtype=np.float32))
    y = torch.tensor(feats["label"].to_numpy(dtype=np.int64))
    edge_index = torch.tensor(_edge_index(feats))

    # stratified train/test mask (skip empty class pools — e.g. an all-benign inference window)
    rng = np.random.default_rng(seed)
    n = len(feats)
    test = np.zeros(n, dtype=bool)
    labels = feats["label"].to_numpy()
    for lbl in (0, 1):
        pool = np.where(labels == lbl)[0]
        if len(pool) == 0:
            continue
        pick = rng.choice(pool, max(1, int(0.3 * len(pool))), replace=False)
        test[pick] = True
    train_mask = torch.tensor(~test)
    test_mask = torch.tensor(test)

    data = Data(x=x, edge_index=edge_index, y=y, train_mask=train_mask, test_mask=test_mask)
    return data, FEATURE_COLS
