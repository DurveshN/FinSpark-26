# Backend Infra

FastAPI + Uvicorn service. Loads trained model from `ml/artifacts/`, scores telemetry windows, persists alerts to PostgreSQL (SQLAlchemy + Alembic), serves REST + WebSocket.

## Runtime
- Python 3.11 in Docker (pinned; local dev may use 3.13 venv — see learning.md for wheel caveats).
- Entrypoint: `uvicorn app.main:app`.
- Env: `DATABASE_URL`, `CORS_ORIGIN`, `MODEL_PATH` (default `../ml/artifacts`).

## Layout
- `app/main.py` — app assembly only.
- `app/config.py` — settings from env.
- `app/db/` — engine, session, declarative base.
- `app/models/` — ORM models (one domain per file).
- `app/schemas/` — Pydantic DTOs.
- `app/api/` — routers (one per resource) + `/ws/stream`.
- `app/ml/` — model load, scoring, betti, SHAP.
- `app/services/` — telemetry replay, alert persistence.
- `migrations/` — Alembic.

## Deploy
Docker image → ACR → Azure Container App. Migrations via `alembic upgrade head` on release.
