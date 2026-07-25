// KPI stat card for the dashboard metrics row. Presentational only — value +
// label + optional subtitle/trend passed in from live telemetry.

export default function KpiCard({ label, value, subtitle, accent }) {
  return (
    <div className="db-metric-card">
      <div className="metric-card-left">
        <div className="metric-label">{label}</div>
        <div className="metric-value" style={accent ? { color: accent } : undefined}>{value}</div>
        {subtitle && <div className="metric-subtitle">{subtitle}</div>}
      </div>
    </div>
  );
}
