# Backend Learning Log

> Append newest at top.

## 2026-07-25
- Backend scaffolded: `app/{db,models,schemas,api,ml,services}`, `migrations/`. Old fake `engine.py`/`main.py` removed.
- Decision: telemetry "stream" replays synthetic/held-out windows but each is scored by the REAL trained model — no randomised outputs.
- **Phase 4 built:** `config.py` (env settings), `db/base.py` (SQLAlchemy engine+session, SQLite local / Postgres prod), `models/alert.py` (auditable Alert row w/ SHAP reason_codes JSON), `ml/model_store.py` (loads model.pt+scaler+shap bg), `ml/scorer.py` (score a window via build_graph+GNN, reuses offline feature code so train/infer features match), `ml/explain.py` (SHAP KernelExplainer per node, graph fixed), `services/telemetry.py` (window replay+scoring loop), `services/alerts.py` (persist/query), `api/routes.py` (/health /metrics /alerts), `api/stream.py` (WS /ws/stream + ConnectionManager + stream_loop persisting flagged alerts), `main.py` (lifespan: create tables, load model, apply tuned threshold, start stream loop). Alembic wired (`alembic.ini`, `migrations/env.py` pulls URL+metadata from app).
- **Pending:** end-to-end smoke test once model.pt exists; Alembic initial migration; Dockerfile.

## 2026-07-26 — CRITICAL production fix: hung backend
- **Symptom (live):** dashboard stuck "Reconnecting…", all zeros; `/health` timed out (HTTP 000), WS opened then closed repeatedly. Container "Running/Healthy" per Azure but app hung.
- **Root cause:** the stream loop ran heavy CPU work ON the async event loop every 1.5s — `build_graph` (per-customer Betti over ~5000 customers, ~60s) + SHAP KernelExplainer per flagged alert (full 559k-node graph forward × nsamples). This starved uvicorn's single event loop → health checks timed out, WS dropped. Worked in the one-shot smoke test; only fails under the repeating async loop.
- **Key gotcha:** `asyncio.to_thread` does NOT fix CPU-bound work — Python's GIL means the worker thread still blocks the event loop. Threads only help for I/O-bound work.
- **Fix (architectural):**
  1. Score the ENTIRE dataset ONCE in a background thread at startup (`replay.prepare()`), set `ready`; each stream tick just SLICES pre-scored rows by time window (fast, no model/graph/topology per tick). Dashboard shows `warming_up` until ready. Startup stays instant so `/health` responds during warmup.
  2. SHAP moved OUT of the hot path → computed ON DEMAND via `GET /explain/{txn_id}?node_idx=` when an analyst clicks an alert, on the node's 2-HOP SUBGRAPH (torch_geometric.k_hop_subgraph) instead of the full graph → ~0.4s vs full-graph, cached. This is also the real SOC workflow.
- **Numbers:** 776 flagged nodes; precomputing all = 5.4 min (rejected — GIL starves loop). On-demand subgraph SHAP = 0.42s/click with real values. Verified: steady 1.5s ticks through alert windows (5-6 flagged) with zero stalls.
