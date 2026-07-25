# Learning Log — QTD-HGNN (global)

> Running log of decisions, gotchas, and lessons. Append newest at top. Update after every meaningful change.

## 2026-07-25

- **Project reset.** Old `FinSpark-26` demo was slop: GNN untrained + output replaced with `random.uniform`; Betti = `variance + random`; SHAP hardcoded; no transactions; no training. Rebuilding the same QTD-HGNN *idea* (TDA + GNN + SHAP + SOC dashboard) for real.
- **Design spec:** `docs/superpowers/specs/2026-07-25-qtd-hgnn-production-design.md` (approved).
- **Honesty line:** every on-screen number computed, not invented. Quantum module = observable *indicators* on synthetic data, labeled as a demo (passive HNDL interception is physically undetectable — never claim otherwise).
- **Repo restructured** into monorepo: `frontend/`, `backend/`, `ml/`, `docs/`. Moved root `App.jsx` → `frontend/`. Removed `engine.py`, `main.py`, PoC notebook, `diagrams.puml`; old README → `docs/OLD_README_slop.md`.
- **Env probe:** Python 3.13.5 (NEW — watch for torch_geometric/ripser/shap wheel availability; pin versions, note fallbacks), Node 22.14, Docker 28.5, Azure CLI 2.88 (logged in, "Azure subscription 1"), gh authed (DurveshN, scopes repo+workflow).
- **ML model choice:** deferred to build time — will benchmark GNN vs XGBoost baseline and document the winner.
- **Deploy targets:** backend → Azure (one resource group, Container App + Postgres + ACR); frontend → Vercel.
