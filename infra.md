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

## Deploy flow

1. Push to `main` → GitHub Actions `backend-deploy.yml` builds Docker image → pushes to ACR → updates Container App.
2. Vercel auto-builds `frontend/` on push.
3. Alembic migrations run on backend release.

## Secrets (never committed)

- GitHub Actions: `AZURE_CREDENTIALS`, `ACR_*`, `DATABASE_URL`.
- Container App env: `DATABASE_URL`, `CORS_ORIGIN`, `MODEL_PATH`.

## Local dev

- Backend: `backend/.venv` + `uvicorn app.main:app`. Local Postgres or Docker.
- Frontend: `cd frontend && npm install && npm run dev`.
- Env probe (verified 2026-07-25): Python 3.13.5, Node 22.14, Docker 28.5, az 2.88 (logged in), gh (DurveshN, repo+workflow).
