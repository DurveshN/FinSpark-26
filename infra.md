# Infrastructure — QTD-HGNN (global)

> Single source of truth for what is deployed, where, and how. Update after every infra change.

## Overview

| Component | Tech | Hosted on | Status |
|---|---|---|---|
| Frontend (SOC dashboard) | React 19 + Vite | Vercel (git-integrated, root = `frontend/`) | planned |
| Backend (API + WS + inference) | FastAPI + Uvicorn | Azure Container App | planned |
| Database | PostgreSQL (SQLAlchemy + Alembic) | Azure Database for PostgreSQL | planned |
| Container registry | Docker image | Azure Container Registry (ACR) | planned |
| CI/CD | GitHub Actions | `.github/workflows/` | planned |

## Azure

- Subscription: `Azure subscription 1` (id `92ecea33-...`) — verify with `az account show`.
- **One resource group** `rg-qtdhgnn` holds all backend resources.
- Region: `centralindia` (data-residency alignment).
- Resources: ACR (Basic), Container Apps environment + Container App, optional PostgreSQL Flexible Server (B1ms) — defaults to in-container SQLite to avoid DB cost until Postgres is needed.
- **Provision:** `az login` then `bash infra/provision.sh` (edit vars at top; set `USE_POSTGRES=true` for managed DB). Script prints the backend URL + the values to put in GitHub Actions secrets.

## Cost note
- ACR Basic (~$5/mo) + Container App (scale-to-1, consumption) + optional Postgres B1ms (~$12-15/mo). SQLite mode keeps it to ACR + Container App only. Confirm subscription type (student credit vs pay-as-you-go) before provisioning.

## LIVE (2026-07-25)
- Backend: https://ca-qtdhgnn-backend.ashyfield-9334e0d7.centralindia.azurecontainerapps.io
- Health verified: `{"status":"ok","model_loaded":true}`; /metrics serves real held-out numbers.
- Resources in `rg-qtdhgnn`: ACR `acrqtdhgnn7764`, Container Apps env `cae-qtdhgnn`, Container App `ca-qtdhgnn-backend`, Log Analytics `workspace-rgqtdhgnn*`.
- Frontend Vercel env: `VITE_API_BASE` = the URL above; `VITE_WS_URL` = `wss://...azurecontainerapps.io/ws/stream`.

## Deploy flow

1. Push to `main` → GitHub Actions `backend-deploy.yml` builds Docker image → pushes to ACR → updates Container App.
2. Vercel auto-builds `frontend/` on push.
3. Alembic migrations run on backend release.

## Secrets (never committed)

- GitHub Actions: `AZURE_CREDENTIALS`, `ACR_NAME`, `RESOURCE_GROUP`, `CONTAINER_APP`.
- Container App env: `DATABASE_URL`, `CORS_ORIGIN`, `MODEL_PATH`, `DATA_DIR`.

## CI/CD access caveat (2026-07-25)
- DurveshN has **push + triage** on `adhraj12/FinSpark-26` but **not admin** → cannot create repo secrets. Options: (a) adhraj12 adds the Actions secrets, or (b) mirror to a repo under DurveshN who owns secrets. Until then, `ci.yml` runs fine (no secrets), but `backend-deploy.yml` needs the secrets to work — meanwhile deploy manually via `az acr build` + `az containerapp update` (or re-run `provision.sh`).

## Local dev

- Backend: `backend/.venv` + `uvicorn app.main:app`. Local Postgres or Docker.
- Frontend: `cd frontend && npm install && npm run dev`.
- Env probe (verified 2026-07-25): Python 3.13.5, Node 22.14, Docker 28.5, az 2.88 (logged in), gh (DurveshN, repo+workflow).

## Deploy gotchas (log)
- 2026-07-25: `az acr build` on Windows crashed with `'charmap' codec can't encode` — Azure CLI Unicode output bug streaming remote build logs. Only local log DISPLAY crashes; the remote build runs. But `--no-logs` also HID a real failure (returned exit 0). Lesson: after `--no-logs`, check `az acr task list-runs --top 1 --query [0].status`.
- 2026-07-25 ROOT CAUSE of build failures: **`shap==0.52.0` requires Python >=3.12** but Dockerfile used `python:3.11-slim` → pip "No matching distribution for shap==0.52.0". Local venv is 3.13 so it installed there, masking the mismatch. FIX: base image `python:3.12-slim` (torch 2.13.0+cpu + ripser 0.6.15 have cp312 linux wheels; verified). CI setup-python bumped to 3.12. Diagnosed by building locally with Docker (readable output) after ACR logs were unreadable on Windows.
- 2026-07-25: on Linux, `torch==2.13.0` pulls the CUDA wheel; pin `torch==2.13.0+cpu` (kept).
