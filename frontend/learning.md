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

## 2026-07-26 — UI redesign: Tailwind v4 + shadcn/ui
- Replaced flat plain-CSS UI with premium dark SOC theme (slate/indigo, OKLCH design tokens).
- Setup: `@tailwindcss/vite` plugin, `@` alias (vite.config + jsconfig), `components.json` (new-york, jsx, base slate, css vars), `lib/utils.js` (cn). Deps: tailwindcss, clsx, tailwind-merge, class-variance-authority, tw-animate-css.
- shadcn components added (via MCP add command): card, badge, button, separator, scroll-area, progress, tooltip → `src/components/ui/`.
- Rebuilt all views/components on shadcn: Landing (gradient hero + icon feature cards), Dashboard (KPI cards w/ lucide icons + accent bar, themed recharts using var(--chart-*), scrollable alert queue w/ severity dots + scenario badges, SHAP waterfall bars, quantum + model stat panels, animated pulse status badge). Added ChartCard wrapper.
- Deleted old `App.css` (fully replaced by Tailwind). index.css = Tailwind import + @theme tokens.
- All data STILL 100% live from backend (no mock). `npm run build` passes (~605KB JS, recharts is bulk).
- Note: could not visually verify via Playwright (MCP not available this session); relied on clean build + no dangling old-class refs.
