// Model Insights panel — REAL held-out evaluation metrics from ml/artifacts/
// metrics.json (via /metrics). No invented accuracy numbers.

export default function ModelMetrics({ metrics }) {
  if (!metrics || metrics.error) {
    return <div className="db-chart-container"><div className="chart-desc">Model metrics unavailable — train the model first.</div></div>;
  }
  const pct = (v) => `${(v * 100).toFixed(1)}%`;
  const items = [
    { label: 'Recall (fraud caught)', value: pct(metrics.recall), accent: '#10b981' },
    { label: 'Precision (alert accuracy)', value: pct(metrics.precision), accent: '#3b82f6' },
    { label: 'F1 score', value: metrics.f1.toFixed(3), accent: '#a78bfa' },
    { label: 'AUC', value: metrics.auc.toFixed(4), accent: '#f59e0b' },
  ];
  return (
    <div className="db-chart-container">
      <div className="db-chart-header">
        <span className="chart-label">Model Insights — {metrics.model}</span>
        <span className="chart-val">held-out test</span>
      </div>
      <div className="db-metrics-row" style={{ marginTop: 8 }}>
        {items.map((it) => (
          <div key={it.label} className="metric-card-left" style={{ flex: 1 }}>
            <div className="metric-value" style={{ color: it.accent, fontSize: 22 }}>{it.value}</div>
            <div className="metric-label" style={{ fontSize: 11 }}>{it.label}</div>
          </div>
        ))}
      </div>
      <div className="xai-footer" style={{ marginTop: 8 }}>
        Decision threshold {metrics.threshold} · {metrics.features?.length || 0} fused
        cyber+transaction+topology features.
      </div>
    </div>
  );
}
