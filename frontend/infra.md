# Frontend Infra

React 19 + Vite SOC dashboard. Deployed on **Vercel** (git-integrated; project root = `frontend/`).

## Runtime
- Node 18+ (dev verified on 22.14). `npm run dev` (Vite), `npm run build` → `dist/`.
- Env: `VITE_API_BASE` (backend REST), `VITE_WS_URL` (backend WebSocket). Set in Vercel project settings.

## Layout (target after refactor)
- `src/App.jsx` — thin router/shell only.
- `src/api/` — WebSocket + REST clients.
- `src/hooks/` — e.g. `useTelemetryStream`.
- `src/views/` — Overview, ThreatGraph, XAIInsights, QuantumMonitor, Alerts, Landing.
- `src/components/` — presentational only.

## Data
All values come from the backend (WS/REST). No `Math.random()` generators, no hardcoded SHAP.

## Deploy
Vercel auto-builds on push to `main`. Root directory set to `frontend/` in Vercel project config.
