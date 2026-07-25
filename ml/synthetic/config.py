"""Synthetic-bank generation constants: population sizes, rates, scenario mix.

Single source of tunable knobs for the synthetic data generator. No logic here.
"""
from __future__ import annotations

# --- population ---
N_CUSTOMERS = 6000
DAYS = 45                     # simulated history length
SEED = 20260725

# --- per-customer behaviour baselines (drawn per customer, then sampled) ---
LOGINS_PER_DAY = (0.3, 3.0)   # (min, max) mean logins/day, uniform per customer
TXNS_PER_DAY = (0.2, 4.0)     # mean transactions/day per customer
AMOUNT_LOGNORM = (7.5, 1.0)   # lognormal (mu, sigma) for INR transaction amounts

CHANNELS = ("UPI", "NEFT", "IMPS", "CARD", "SWIFT")
CHANNEL_WEIGHTS = (0.55, 0.15, 0.15, 0.12, 0.03)

# --- crypto posture (for the honest quantum module) ---
# Most sessions use modern TLS; a minority use quantum-vulnerable / weak config.
TLS_MODERN = ("TLS1.3:X25519MLKEM768", "TLS1.3:X25519")      # PQC-hybrid / strong
TLS_LEGACY = ("TLS1.2:ECDHE-RSA", "TLS1.2:RSA", "TLS1.0:RSA-EXPORT")  # quantum-vulnerable / weak
TLS_LEGACY_RATE = 0.18        # baseline share of legacy connections

# --- attack scenario counts (injected, labeled) ---
N_ATO = 220                   # account-takeover episodes
N_MULE_RINGS = 40             # money-mule rings
MULE_RING_SIZE = (4, 9)       # accounts per ring
N_HNDL = 120                  # harvest-indicator chains
N_BENIGN_ANOMALY = 400        # legit-but-unusual (teaches false-positive suppression)

# --- label values ---
LABEL_BENIGN = 0
LABEL_MALICIOUS = 1

SCENARIO_NORMAL = "normal"
SCENARIO_ATO = "account_takeover"
SCENARIO_MULE = "mule_ring"
SCENARIO_HNDL = "hndl_indicator"
SCENARIO_BENIGN_ANOMALY = "benign_anomaly"
