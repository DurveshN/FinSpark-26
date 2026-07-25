"""Generate baseline (benign) login and transaction events for the population.

Simulates each customer's normal daily rhythm over the sim window. Produces the
login and transaction event tables that scenarios later mutate. All events labeled
benign here; scenario injection flips labels afterwards.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from . import config as C


def _pick_tls(rng: np.random.Generator, legacy_rate: float = C.TLS_LEGACY_RATE) -> str:
    """Choose a TLS/cipher descriptor; a minority are quantum-vulnerable/weak."""
    if rng.random() < legacy_rate:
        return C.TLS_LEGACY[rng.integers(0, len(C.TLS_LEGACY))]
    return C.TLS_MODERN[rng.integers(0, len(C.TLS_MODERN))]


def generate_baseline(entities: dict[str, pd.DataFrame], seed: int = C.SEED + 1
                      ) -> dict[str, pd.DataFrame]:
    """Return dict with 'logins' and 'transactions' DataFrames (all benign)."""
    rng = np.random.default_rng(seed)
    customers = entities["customers"]
    accounts = entities["accounts"].set_index("customer_id")
    devices = entities["devices"]
    payees = entities["payees"]["payee_id"].values

    dev_by_cust = devices.groupby("customer_id")["device_id"].apply(list).to_dict()
    city_by_dev = devices.set_index("device_id")["usual_city"].to_dict()

    logins, txns = [], []
    login_seq = txn_seq = 0

    for row in customers.itertuples(index=False):
        cid = row.customer_id
        acct = accounts.loc[cid, "account_id"]
        cust_devices = dev_by_cust[cid]

        n_logins = rng.poisson(row.login_rate * C.DAYS)
        for _ in range(int(n_logins)):
            t = rng.uniform(0, C.DAYS)
            dev = cust_devices[rng.integers(0, len(cust_devices))]
            hour = int((t % 1) * 24)
            login_id = f"L{login_seq:08d}"; login_seq += 1
            logins.append({
                "login_id": login_id, "customer_id": cid, "t_day": t, "hour": hour,
                "device_id": dev, "city": city_by_dev[dev],
                "new_device": 0, "failed_prior": int(rng.poisson(0.2)),
                "tls": _pick_tls(rng), "label": C.LABEL_BENIGN,
                "scenario": C.SCENARIO_NORMAL,
            })

        n_txns = rng.poisson(row.txn_rate * C.DAYS)
        for _ in range(int(n_txns)):
            t = rng.uniform(0, C.DAYS)
            amt = float(np.exp(rng.normal(row.amount_mu, row.amount_sigma)))
            ch = C.CHANNELS[rng.choice(len(C.CHANNELS), p=C.CHANNEL_WEIGHTS)]
            txns.append({
                "txn_id": f"T{txn_seq:08d}", "customer_id": cid, "account_id": acct,
                "t_day": t, "amount": round(amt, 2), "channel": ch,
                "payee_id": payees[rng.integers(0, len(payees))],
                "new_payee": int(rng.random() < 0.05),
                "sec_since_login": float(rng.exponential(3600)),
                "sec_since_payee_add": float(rng.exponential(86400 * 30)),
                "label": C.LABEL_BENIGN, "scenario": C.SCENARIO_NORMAL,
            })
            txn_seq += 1

    return {"logins": pd.DataFrame(logins), "transactions": pd.DataFrame(txns)}
