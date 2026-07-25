"""Fuse transaction + cyber telemetry into per-transaction feature rows.

For each transaction, joins the nearest preceding login for that customer and
computes cross-domain features (the correlation the SIEM and fraud engine each miss
alone). Output: a feature matrix + labels ready for the graph/model. No topology here.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

# quantum-vulnerable / weak TLS descriptors (see synthetic/config.TLS_LEGACY)
_WEAK_TLS = ("TLS1.2:RSA", "TLS1.0:RSA-EXPORT")
_VULN_TLS = ("TLS1.2:ECDHE-RSA",) + _WEAK_TLS  # not PQC-hybrid


def _tls_flags(tls: str) -> tuple[int, int]:
    """Return (quantum_vulnerable, weak_downgrade) flags from a TLS descriptor."""
    vuln = int(any(tls.startswith(v) or tls == v for v in _VULN_TLS))
    weak = int(tls in _WEAK_TLS)
    return vuln, weak


def build_features(logins: pd.DataFrame, txns: pd.DataFrame) -> pd.DataFrame:
    """Return per-transaction rows with fused cyber+transaction features + label."""
    logins = logins.sort_values("t_day")
    txns = txns.sort_values("t_day").reset_index(drop=True)

    # per-customer amount baselines (from benign history) for anomaly ratios
    base = txns[txns["label"] == 0].groupby("customer_id")["amount"]
    cust_mean = base.mean().to_dict()
    cust_std = base.std().fillna(1.0).to_dict()

    # nearest preceding login per (customer, txn) via merge_asof
    lg = logins[["customer_id", "t_day", "new_device", "failed_prior", "hour", "tls", "city"]].copy()
    lg = lg.rename(columns={"t_day": "login_t"})
    merged = pd.merge_asof(
        txns, lg.sort_values("login_t"),
        left_on="t_day", right_on="login_t", by="customer_id", direction="backward",
    )

    tls_vuln, tls_weak = zip(*merged["tls"].fillna("TLS1.3:X25519").map(_tls_flags))
    cmean = merged["customer_id"].map(cust_mean).fillna(merged["amount"].median())
    cstd = merged["customer_id"].map(cust_std).replace(0, 1.0).fillna(1.0)

    feats = pd.DataFrame({
        "txn_id": merged["txn_id"],
        "customer_id": merged["customer_id"],
        "amount": merged["amount"],
        "amount_zscore": (merged["amount"] - cmean) / cstd,
        "log_amount": np.log1p(merged["amount"]),
        "new_payee": merged["new_payee"].fillna(0),
        "sec_since_login": merged["sec_since_login"].fillna(1e6),
        "sec_since_payee_add": merged["sec_since_payee_add"].fillna(1e7),
        "is_swift": (merged["channel"] == "SWIFT").astype(int),
        "is_imps": (merged["channel"] == "IMPS").astype(int),
        # --- fused cyber features (the correlation) ---
        "login_new_device": merged["new_device"].fillna(0),
        "login_failed_prior": merged["failed_prior"].fillna(0),
        "login_odd_hour": merged["hour"].fillna(12).apply(lambda h: int(h < 6)),
        "tls_quantum_vulnerable": list(tls_vuln),
        "tls_weak_downgrade": list(tls_weak),
        "geo_mismatch": (merged["hour"].notna() & (merged["failed_prior"].fillna(0) > 2)).astype(int),
        # --- label + scenario ---
        "label": merged["label"],
        "scenario": merged["scenario"],
    }).fillna(0)

    return feats
