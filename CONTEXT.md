# CONTEXT — QTD-HGNN (session state)

Last updated: 2026-07-26

## What this is
FinSpark'26 PS2 — AI-driven correlation of cybersecurity telemetry & transactional behaviour.
QTD-HGNN: real trained GraphSAGE + real persistent homology (Ripser) + real SHAP + SOC dashboard.
Rebuilt from scratch to replace an "AI-slop" demo (untrained model, random outputs, faked Betti/SHAP).

## Repo
- github.com/DurveshN/FinSpark-26 (public, user-owned). Monorepo: `frontend/`, `backend/`, `ml/`.
- CI/CD: `.github/workflows/ci.yml` (lint+build+import check), `backend-deploy.yml` (ACR build -> Container App).
- Deploy secrets set on the repo (AZURE_CREDENTIALS, ACR_NAME, RESOURCE_GROUP, CONTAINER_APP).

## Live
- Backend: Azure Container Apps, RG `rg-qtdhgnn`, region centralindia.
  URL: https://ca-qtdhgnn-backend.ashyfield-9334e0d7.centralindia.azurecontainerapps.io
  Resources: ACR `acrqtdhgnn7764`, env `cae-qtdhgnn`, app `ca-qtdhgnn-backend`, Log Analytics.
- Frontend: Vercel (fin-spark-26.vercel.app) — connect DurveshN repo; VITE_API_BASE/VITE_WS_URL baked in frontend/.env.production.

## Model (real, held-out)
GraphSAGE, 16 fused features incl. cust_betti0/1/2. Precision 0.714 / Recall 0.977 / F1 0.825 / AUC 0.99998, threshold 0.99. 559k txns, 776 flagged.

## Architecture (key decisions)
- **Build-time prescoring**: `ml/prescore.py` runs in the Dockerfile — generates data + scores the whole dataset -> `ml/artifacts/scored.csv` + `graph.pt`. Makes the image self-contained AND startup instant.
- **Runtime**: `telemetry.prepare()` just LOADS pre-scored artifacts (~0.8s). Stream tick = slice pre-scored rows by 0.5-day window. NO scoring on the event loop.
- **SHAP on-demand**: `GET /explain/{txn_id}?node_idx=` computes SHAP on the node's 2-hop subgraph (~0.4s), cached. Never in the stream loop.
- Only the small trained model (model.pt/scaler/shap_bg, 36KB) is committed; data + betti cache + prescored outputs regenerate deterministically at build.

## Hard-won lessons (see backend/learning.md, infra.md)
- shap>=0.52 needs Python 3.12 (Dockerfile base).
- On Linux, pin `torch==2.13.0+cpu` (else pulls 2.5GB CUDA wheel).
- CPU-bound work on the async loop (even via asyncio.to_thread — GIL) hangs uvicorn: health times out, WS drops. Fixed via build-time prescore + on-demand SHAP.
- `az acr build` crashes Windows terminal (Unicode) — use --no-logs + check `az acr task list-runs` status.
- Don't double-push: each push to backend/** or ml/** triggers backend-deploy.yml; two at once race.

## Status
Phases 0-6 DONE. Backend LIVE and verified end-to-end (2026-07-26): instant startup (prescored),
steady 1.5s stream through alert windows, /health responsive under WS load, real on-demand SHAP.
Deployed via GitHub Actions CI/CD (backend-deploy.yml) on push. Frontend (fin-spark-26.vercel.app)
auto-reconnects (2s) — refresh to pick up the live stream. If Vercel is git-connected to DurveshN
repo it auto-redeploys latest frontend (incl. on-demand SHAP on alert click).
