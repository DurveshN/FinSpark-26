"""Inject labeled attack + benign-anomaly scenarios into baseline events.

Mutates copies of the login/transaction tables to create ground-truth-labeled
episodes: account takeover, mule rings, HNDL indicators, and benign anomalies
(legit-but-unusual, to teach false-positive suppression). Returns updated tables.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from . import config as C


def inject(entities: dict[str, pd.DataFrame], base: dict[str, pd.DataFrame],
           seed: int = C.SEED + 2) -> dict[str, pd.DataFrame]:
    rng = np.random.default_rng(seed)
    logins = base["logins"].copy()
    txns = base["transactions"].copy()
    customers = entities["customers"]["customer_id"].values
    accounts = entities["accounts"].set_index("customer_id")["account_id"].to_dict()

    new_logins, new_txns = [], []
    lseq = [len(logins) + 1_000_000]
    tseq = [len(txns) + 1_000_000]

    def mk_login(**kw):
        lid = f"LX{lseq[0]:08d}"; lseq[0] += 1
        row = {"login_id": lid, "new_device": 0, "failed_prior": 0,
               "tls": C.TLS_MODERN[0], "scenario": C.SCENARIO_NORMAL,
               "label": C.LABEL_BENIGN}
        row.update(kw); return row

    def mk_txn(**kw):
        tid = f"TX{tseq[0]:08d}"; tseq[0] += 1
        row = {"txn_id": tid, "new_payee": 0, "sec_since_login": 3600.0,
               "sec_since_payee_add": 86400.0 * 30, "channel": "UPI",
               "scenario": C.SCENARIO_NORMAL, "label": C.LABEL_BENIGN}
        row.update(kw); return row

    # --- 1. Account takeover: hostile login (new device+geo, failed bursts) -> new payee -> drain ---
    for cid in rng.choice(customers, C.N_ATO, replace=False):
        t = rng.uniform(1, C.DAYS - 1)
        new_logins.append(mk_login(customer_id=cid, t_day=t, hour=int(rng.integers(1, 5)),
            device_id=f"{cid}-EVIL", city=int(rng.integers(0, 40)), new_device=1,
            failed_prior=int(rng.integers(3, 12)),
            tls=C.TLS_LEGACY[rng.integers(0, len(C.TLS_LEGACY))],
            scenario=C.SCENARIO_ATO, label=C.LABEL_MALICIOUS))
        drain = float(np.exp(rng.normal(11.5, 0.5)))  # large
        new_txns.append(mk_txn(customer_id=cid, account_id=accounts[cid],
            t_day=t + rng.uniform(0.0005, 0.003), amount=round(drain, 2),
            payee_id=f"MULE-{rng.integers(0, 9999):04d}", new_payee=1,
            sec_since_login=float(rng.uniform(30, 180)),
            sec_since_payee_add=float(rng.uniform(20, 120)),
            scenario=C.SCENARIO_ATO, label=C.LABEL_MALICIOUS))

    # --- 2. Mule rings: cluster of accounts passing funds in a cycle ---
    for r in range(C.N_MULE_RINGS):
        size = int(rng.integers(*C.MULE_RING_SIZE))
        members = rng.choice(customers, size, replace=False)
        hub = f"RINGPAY-{r:03d}"
        t0 = rng.uniform(1, C.DAYS - 2)
        for j, cid in enumerate(members):
            amt = float(np.exp(rng.normal(10.8, 0.3)))
            nxt = members[(j + 1) % size]
            new_txns.append(mk_txn(customer_id=cid, account_id=accounts[cid],
                t_day=t0 + j * 0.01 + rng.uniform(0, 0.005), amount=round(amt, 2),
                payee_id=f"{hub}-{nxt}", new_payee=1, channel="IMPS",
                sec_since_payee_add=float(rng.uniform(60, 600)),
                scenario=C.SCENARIO_MULE, label=C.LABEL_MALICIOUS))

    # --- 3. HNDL indicators: crypto-downgrade login + bulk-egress staging txn ---
    for cid in rng.choice(customers, C.N_HNDL, replace=False):
        t = rng.uniform(1, C.DAYS - 1)
        new_logins.append(mk_login(customer_id=cid, t_day=t, hour=int(rng.integers(0, 24)),
            device_id=f"{cid}-SVC", city=int(rng.integers(0, 40)), new_device=1,
            failed_prior=0, tls=C.TLS_LEGACY[2],  # weak/export = downgrade indicator
            scenario=C.SCENARIO_HNDL, label=C.LABEL_MALICIOUS))
        # staging "transaction" = bulk data-movement proxy: huge, SWIFT-channel, off-hours
        new_txns.append(mk_txn(customer_id=cid, account_id=accounts[cid],
            t_day=t + rng.uniform(0.001, 0.01), amount=round(float(np.exp(rng.normal(13.0, 0.4))), 2),
            payee_id=f"EGRESS-{rng.integers(0, 999):03d}", new_payee=1, channel="SWIFT",
            sec_since_login=float(rng.uniform(60, 400)),
            sec_since_payee_add=float(rng.uniform(30, 300)),
            scenario=C.SCENARIO_HNDL, label=C.LABEL_MALICIOUS))

    # --- 4. Benign anomalies: legit-but-unusual (big purchase, new device travel) — LABEL BENIGN ---
    for cid in rng.choice(customers, C.N_BENIGN_ANOMALY, replace=False):
        t = rng.uniform(1, C.DAYS - 1)
        if rng.random() < 0.5:
            new_txns.append(mk_txn(customer_id=cid, account_id=accounts[cid], t_day=t,
                amount=round(float(np.exp(rng.normal(11.8, 0.4))), 2),  # genuinely large
                payee_id=f"MERCHANT-{rng.integers(0, 500):03d}", new_payee=1, channel="CARD",
                sec_since_payee_add=float(rng.uniform(300, 3600)),
                scenario=C.SCENARIO_BENIGN_ANOMALY, label=C.LABEL_BENIGN))
        else:
            new_logins.append(mk_login(customer_id=cid, t_day=t, hour=int(rng.integers(6, 22)),
                device_id=f"{cid}-NEWPHONE", city=int(rng.integers(0, 40)), new_device=1,
                failed_prior=0, tls=C.TLS_MODERN[0],  # strong crypto = benign signal
                scenario=C.SCENARIO_BENIGN_ANOMALY, label=C.LABEL_BENIGN))

    logins = pd.concat([logins, pd.DataFrame(new_logins)], ignore_index=True)
    txns = pd.concat([txns, pd.DataFrame(new_txns)], ignore_index=True)
    return {"logins": logins, "transactions": txns}
