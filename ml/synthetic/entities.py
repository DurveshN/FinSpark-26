"""Generate the static population of the synthetic bank.

Produces the entity tables (customers, accounts, devices, payees) that events and
transactions later reference. Pure data generation; no event/time logic here.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from . import config as C


def _rng(seed: int) -> np.random.Generator:
    return np.random.default_rng(seed)


def generate_entities(seed: int = C.SEED) -> dict[str, pd.DataFrame]:
    """Return dict of DataFrames: customers, accounts, devices, payees."""
    rng = _rng(seed)
    n = C.N_CUSTOMERS

    # --- customers: each gets stable behavioural baselines ---
    customers = pd.DataFrame({
        "customer_id": [f"C{i:06d}" for i in range(n)],
        "home_city": rng.integers(0, 40, n),                 # 40 cities as ids
        "login_rate": rng.uniform(*C.LOGINS_PER_DAY, n),     # mean logins/day
        "txn_rate": rng.uniform(*C.TXNS_PER_DAY, n),         # mean txns/day
        "amount_mu": rng.normal(C.AMOUNT_LOGNORM[0], 0.4, n),
        "amount_sigma": np.clip(rng.normal(C.AMOUNT_LOGNORM[1], 0.2, n), 0.3, 2.0),
    })

    # --- accounts: one primary account per customer ---
    accounts = pd.DataFrame({
        "account_id": [f"A{i:06d}" for i in range(n)],
        "customer_id": customers["customer_id"].values,
        "opened_day": rng.integers(-720, -30, n),            # opened before sim window
    })

    # --- devices: 1-3 known devices per customer ---
    dev_rows = []
    for cid in customers["customer_id"].values:
        k = rng.integers(1, 4)
        for d in range(k):
            dev_rows.append((f"{cid}-D{d}", cid, int(rng.integers(0, 40))))
    devices = pd.DataFrame(dev_rows, columns=["device_id", "customer_id", "usual_city"])

    # --- payees: a shared pool of known beneficiaries ---
    n_payees = n // 2
    payees = pd.DataFrame({
        "payee_id": [f"P{i:06d}" for i in range(n_payees)],
        "risk_flag": (rng.random(n_payees) < 0.03).astype(int),   # 3% pre-flagged risky
    })

    return {"customers": customers, "accounts": accounts, "devices": devices, "payees": payees}
