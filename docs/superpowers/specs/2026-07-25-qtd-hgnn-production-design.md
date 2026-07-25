# QTD-HGNN — Production Design Spec

**FinSpark'26 · Problem Statement 2 · Team Hexacon**
Date: 2026-07-25 · Status: Draft for approval

---

## 0. Intent & the one honesty rule

We build the **QTD-HGNN** concept from the team's PDF — Topological Data Analysis (Betti numbers) + Graph Neural Network + SHAP explainability, streamed to a SOC dashboard — but **as a real, trained, production system**, not the current demo (which fakes every number).

**The single rule that separates this from the old repo:** every number on screen is computed, not invented.

| Old repo (slop) | This build (real) |
|---|---|
| GNN untrained, output discarded, `random.uniform(68,92)` | GNN trained on labeled synthetic data; threat score = model output |
| Betti = `10 - variance + random` | Betti = true persistent homology via `ripser` |
| SHAP values hardcoded in JS | SHAP computed from the trained model |
| Random geometric graphs, no transactions | Synthetic bank: entities + cyber telemetry + transactions, joined |
| Scripted kill-chain metrics | Kill-chain is a labeled scenario the model actually scores |

**Honest scientific framing (what we claim):** the model detects **structural and behavioural anomalies in a correlated cyber+transaction graph**. Topology (Betti curves) is a genuine structural-anomaly signal. "Quantum/HNDL" is framed as detecting **observable indicators** (crypto-downgrade, exfiltration staging, anomalous graph structure) — never "detecting passive interception," which is physically impossible. This framing keeps the PDF's narrative and dashboard intact while surviving technical scrutiny.

---

## 1. What the product is

A real-time threat-correlation engine that ingests cyber telemetry + transactions, lifts them into a graph, computes topological + node features, classifies threat with a trained GNN, explains each flag with SHAP, and streams it to a SOC dashboard. Deploys to Azure (backend) + Vercel (frontend).

Answers all six PS2 outcomes: correlation (graph fuses both domains), proactive detection (GNN), fraud patterns (structural anomalies), quantum indicators (crypto-posture + observable HNDL-chain signals), false-positive reduction (cross-domain corroboration + trained model vs rules), explainability (SHAP).

---

## 2. Repository layout (monorepo, modular)

Every file gets a short top-of-file header comment stating its single job. One file = one responsibility.

```
FinSpark-26/
├── infra.md                      # global infra (Azure RG, resources, CI/CD)
├── learning.md                   # global running log of decisions/lessons
├── docs/superpowers/specs/       # this spec
├── .github/workflows/            # CI/CD (backend->Azure, tests, lint)
│   ├── backend-deploy.yml
│   └── ci.yml
├── frontend/                     # NEW — React/Vite SOC dashboard (moved from root)
│   ├── infra.md                  # frontend infra (Vercel)
│   ├── learning.md
│   ├── src/
│   │   ├── main.jsx
│   │   ├── App.jsx               # router/shell only (thin)
│   │   ├── api/                  # websocket + REST clients (one file per concern)
│   │   ├── components/           # dumb presentational components
│   │   ├── views/                # Overview, ThreatGraph, XAI, QuantumMonitor, Alerts...
│   │   └── hooks/                # useTelemetryStream, etc.
│   ├── package.json
│   └── vite.config.js
├── backend/
│   ├── infra.md                  # backend infra (Azure Container App, Postgres)
│   ├── learning.md
│   ├── .venv/                    # local venv (gitignored)
│   ├── requirements.txt
│   ├── alembic.ini
│   ├── migrations/               # Alembic migrations
│   ├── Dockerfile
│   └── app/
│       ├── main.py               # FastAPI app assembly only
│       ├── config.py             # settings (env)
│       ├── db/                   # SQLAlchemy engine, session, base
│       ├── models/               # SQLAlchemy ORM models (one domain per file)
│       ├── schemas/              # Pydantic DTOs
│       ├── api/                  # routes (one router per resource) + ws stream
│       ├── ml/                   # inference: load model, score, SHAP, betti
│       └── services/             # telemetry replay, alert persistence
└── ml/                           # OFFLINE training + data (not shipped in API image)
    ├── infra.md
    ├── learning.md
    ├── generate_synthetic.py     # synthetic bank generator -> DB/CSV
    ├── features.py               # feature engineering + persistent homology
    ├── train.py                  # train GNN, save weights + SHAP background
    ├── evaluate.py               # precision/recall/F1/AUC, confusion matrix
    └── artifacts/                # trained model.pt, scaler, metrics.json
```

Old root files (`src/App.jsx` at root, `engine.py`, PoC notebook, slop README) are removed/relocated. `reference/`, `assets/screenshots` stay gitignored.

---

## 3. The ML pipeline (real, end-to-end)

**3.1 Synthetic data** (`ml/generate_synthetic.py`) — a believable bank:
- Entities: ~5–10k customers, devices, IPs, accounts, payees, sessions.
- Cyber telemetry: login events (device/IP/geo/result), session behaviour, failed-login bursts.
- Transactions: amount, channel (UPI/NEFT/SWIFT), payee, timestamp, per-customer normal baselines.
- **Injected labeled scenarios**: account-takeover (hostile login → new payee → drain), money-mule ring (structural), HNDL-indicator chain (downgrade → staging → bulk exfil), **plus benign-anomalies** (real big purchase) to teach false-positive suppression.
- Output: written to Postgres (via SQLAlchemy) + CSV snapshot for training.

**3.2 Graph + features** (`ml/features.py`):
- Build heterogeneous graph per time-window: nodes = entities, edges = observed relations (login-from-device, txn-to-payee, etc.).
- Node features: transaction stats + cyber stats (the fusion row).
- **Topological features**: build point cloud from window features → `ripser` persistent homology → real Betti curves β0/β1/β2 (vectorised) → appended to node/window features. This is genuine TDA, computed offline + cached; real-time uses windowed recompute with a bounded point count.

**3.3 Train** (`ml/train.py`):
- GNN (GraphSAGE/GCN, PyTorch Geometric) node classifier, features INCLUDING topological vector (fixing the old repo's disconnect where Betti was never fed in).
- Train/val/test split, CrossEntropy, Adam, early stopping. Save `model.pt` + SHAP background sample + feature scaler to `ml/artifacts/`.

**3.4 Evaluate** (`ml/evaluate.py`): precision, recall, F1, AUC, confusion matrix → `metrics.json`. Reported honestly on held-out test set. No score inflation.

**3.5 Explain**: SHAP over the model → per-flag feature attributions → the dashboard's XAI waterfall (real values).

---

## 4. Backend (FastAPI, on Azure)

- **`app/ml/`** loads `model.pt` + artifacts at startup; scores incoming windows; computes Betti + SHAP on demand.
- **`app/services/telemetry.py`** replays the synthetic stream (or a held-out test slice) window-by-window to simulate live traffic — but each window is *scored by the real model*, not randomised.
- **Persistence (SQLAlchemy + Alembic)**: Postgres stores entities, events, transactions, and produced alerts (score, label, SHAP top-features, timestamp). Alembic manages schema. This is what makes it "real" — auditable alerts in a real DB, not ephemeral random JSON.
- **`app/api/`**: REST (`/alerts`, `/entities/{id}`, `/metrics`, `/health`) + WebSocket `/ws/stream` broadcasting scored telemetry payloads (threatScore, betti0/1/2, entropy, activeThreats, per-alert SHAP).
- Model weights hot-loadable; CORS locked to the Vercel origin in prod.

## 5. Frontend (React/Vite, on Vercel)

- Keep the PDF's dashboard look & UX (Overview, Threat Graph, XAI Insights, Quantum Monitor, Alerts) — but **refactor the 2831-line `App.jsx` into modular views/components/hooks**, one job per file. This directly addresses "make dashboard not look like AI slop" — clean structure + real data.
- All values arrive from the backend WebSocket/REST. No `Math.random()` data generators, no hardcoded SHAP.
- Landing page + SOC dashboard preserved. Betti curves, threat graph node colouring, XAI waterfall all bound to real model output.

## 6. Deployment & infra

- **One Azure resource group** (via Azure CLI) holds everything backend: Azure Container App (or App Service) running the FastAPI image, Azure Database for PostgreSQL, Azure Container Registry. Documented in root `infra.md` + `backend/infra.md`.
- **Frontend on Vercel** (git-integrated; `frontend/` as project root). `frontend/infra.md` documents it.
- **CI/CD via GitHub Actions**: `ci.yml` (lint + tests on PR), `backend-deploy.yml` (build Docker → push ACR → deploy Container App on main). Vercel auto-deploys frontend on push.
- **Secrets**: Azure creds + DB URL in GitHub Actions secrets / Container App env. Never committed.

## 7. Docs discipline

`infra.md` (what's deployed, where, how) and `learning.md` (running log of decisions, gotchas, fixes) maintained at **global root** and inside **frontend/** and **backend/**, updated after every meaningful change.

## 8. Explicitly out of scope (v1)

Live bank feeds (synthetic only, format kept swappable); federated/cross-bank; real fiber-tap/OTDR hardware; real HSM/CBOM scanning (quantum module is synthetic-indicator + posture *demo*, honestly labeled).

## 9. Risks / honesty caveats

- Real-time persistent homology is costly; we bound point-cloud size per window and cache. `[Inference]`
- GNNs can underperform simpler models on tabular data; if test metrics disappoint we document it honestly and may add a boosted-tree comparison rather than hide it.
- Quantum module is a demonstration of *observable indicators* on synthetic data, not detection of real quantum attacks — stated plainly in UI copy and docs.

