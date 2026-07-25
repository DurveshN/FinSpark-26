# Frontend Learning Log

> Append newest at top.

## 2026-07-25
- Moved from repo root into `frontend/` (Vite/React 19, recharts, lucide-react). History preserved via git mv.
- **Phase 5 DONE — full modular refactor + real data.** 2831-line App.jsx replaced by:
  - `App.jsx` (thin router: landing | dashboard), `main.jsx` unchanged.
  - `api/config.js` (VITE_API_BASE / VITE_WS_URL), `api/rest.js` (/metrics /alerts /health).
  - `hooks/useTelemetryStream.js` (WS, auto-reconnect, rolling history + alerts), `hooks/useMetrics.js`.
  - `views/Landing.jsx` (honest static hero + features, no fake live metrics), `views/Dashboard.jsx` (assembles all panels on the live stream).
  - `components/`: KpiCard, ThreatTrend, BettiChart, AlertsList, XaiWaterfall (real SHAP), QuantumMonitor (real crypto posture), ModelMetrics (real held-out metrics), StatusBadge.
- ALL mock data removed (generateInitialData, simulationSteps, mockupNodes, graphNodes, dashboardQuantumData, hardcoded SHAP). Verified: no mock-data logic remains (only dead .mockup-* CSS + a comment).
- Reused existing App.css classes (db-/xai-/factor-/metric-/chart-/hero-/feature-); appended small supplement for landing-root/feature-card/hero-badge/hero-accent/hero-actions/landing-footer/db-status-badge.
- `npm run build` passes (593 modules, ~374ms). Bundle 541KB (recharts) — acceptable; could code-split later.
- Vercel project root must be set to `frontend/`; set VITE_API_BASE + VITE_WS_URL to the Azure backend URL.
