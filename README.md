# QTD-HGNN — Quantum-Topological Threat Correlation

**FinSpark'26 · Bank of Maharashtra National Cybersecurity Hackathon · Problem Statement 2**
*AI-Driven Correlation of Cybersecurity Telemetry & Transactional Behaviour · Team Hexacon*

A real, trained system that correlates cybersecurity telemetry (logins, devices, IPs, TLS posture) with transactional behaviour (payments, payees, channels) to detect account takeover, mule rings, and quantum-risk indicators — with explainable, auditable alerts.

> Every number in the dashboard is computed by the trained model and pipeline. No simulated metrics, no random outputs, no hardcoded explanations.

## What it does (mapped to PS2 outcomes)

1. **Correlates cyber + transaction** — a heterogeneous transaction graph fuses login/device/TLS features with payment features per customer.
2. **Detects threats proactively** — a trained GraphSAGE model scores each transaction; account-takeover chains (hostile login → new payee → drain) surface in real time.
3. **Identifies fraud patterns** — same-payee / same-customer graph edges expose mule-ring structure; real persistent-homology (Betti) features capture behavioural shape.
4. **Quantum-risk indicators (honest)** — crypto-posture monitoring: % of connections on quantum-vulnerable TLS, downgrade/weak-cipher events (aligned to RBI Q-SAFE). It measures *observable* HNDL indicators; it does **not** claim to detect passive interception, which is physically undetectable.
5. **Reduces false positives** — cross-domain corroboration + a tuned decision threshold. Held-out precision 0.71 at recall 0.98.
6. **Explainable** — every alert ships computed SHAP reason codes (auditable per RBI/DPDP).

## Held-out model metrics (real)

| Metric | Value |
|---|---|
| Recall | 0.977 |
| Precision | 0.714 |
| F1 | 0.825 |
| AUC | 0.99998 |

16 fused features including real topological (`cust_betti0/1/2`) signals. See `ml/artifacts/metrics.json`.

## Architecture

```
Ingest (cyber + txn) -> Fuse (graph + topology) -> Detect (GraphSAGE) -> Explain (SHAP) -> SOC dashboard
```

- `ml/` — synthetic bank generator, feature engineering + persistent homology (Ripser), GNN training + evaluation.
- `backend/` — FastAPI + SQLAlchemy/Alembic; loads the trained model, scores live telemetry windows, persists auditable alerts, streams over WebSocket.
- `frontend/` — React/Vite SOC dashboard bound entirely to the live backend.
- `infra/`, `.github/workflows/` — Azure provisioning + CI/CD.

## Run locally

```bash
# 1. ML: generate data + train the model
python -m ml.generate_synthetic
python -m ml.train                     # writes ml/artifacts/

# 2. Backend (from backend/, venv active)
alembic upgrade head
uvicorn app.main:app --port 8000

# 3. Frontend
cd frontend && npm install && npm run dev
```

## Deploy

Backend → Azure (one resource group: ACR + Container App, optional PostgreSQL) via `bash infra/provision.sh`.
Frontend → Vercel (project root `frontend/`, set `VITE_API_BASE` + `VITE_WS_URL`).
See `infra.md`.

## Honesty

This project deliberately avoids the pseudoscience common in this space. Topology is a genuine structural-anomaly signal (computed with Ripser), the GNN is genuinely trained and evaluated on held-out data, SHAP values are computed per alert, and the quantum module reports real cryptographic posture rather than claiming to detect undetectable attacks. Data is synthetic (no public dataset joins both domains) and the ingestion format is designed to be swapped for real bank feeds.
