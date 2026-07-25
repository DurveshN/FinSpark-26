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
- **One resource group** holds all backend resources (name TBD, e.g. `rg-qtdhgnn`).
- Region: TBD (India — e.g. `centralindia`) for data-residency alignment.
- Resources: ACR, Container App (+ environment), PostgreSQL flexible server.

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
