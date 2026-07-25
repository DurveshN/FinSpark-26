# Backend Learning Log

> Append newest at top.

## 2026-07-25
- Backend scaffolded: `app/{db,models,schemas,api,ml,services}`, `migrations/`. Old fake `engine.py`/`main.py` removed.
- Decision: telemetry "stream" replays synthetic/held-out windows but each is scored by the REAL trained model — no randomised outputs.
- **Phase 4 built:** `config.py` (env settings), `db/base.py` (SQLAlchemy engine+session, SQLite local / Postgres prod), `models/alert.py` (auditable Alert row w/ SHAP reason_codes JSON), `ml/model_store.py` (loads model.pt+scaler+shap bg), `ml/scorer.py` (score a window via build_graph+GNN, reuses offline feature code so train/infer features match), `ml/explain.py` (SHAP KernelExplainer per node, graph fixed), `services/telemetry.py` (window replay+scoring loop), `services/alerts.py` (persist/query), `api/routes.py` (/health /metrics /alerts), `api/stream.py` (WS /ws/stream + ConnectionManager + stream_loop persisting flagged alerts), `main.py` (lifespan: create tables, load model, apply tuned threshold, start stream loop). Alembic wired (`alembic.ini`, `migrations/env.py` pulls URL+metadata from app).
- **Pending:** end-to-end smoke test once model.pt exists; Alembic initial migration; Dockerfile.
