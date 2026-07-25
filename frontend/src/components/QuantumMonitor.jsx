// Quantum-readiness panel — HONEST crypto-posture, not attack detection.
// Shows the bank's own exposure: % of connections using quantum-vulnerable key
// exchange (RSA/ECDHE-RSA) and count of weak/downgraded ciphers this window.
// Explicitly does NOT claim to detect passive interception (physically impossible).

export default function QuantumMonitor({ quantum }) {
  const q = quantum || { total_conns: 0, quantum_vulnerable_pct: 0, downgrade_events: 0, modern_pct: 0 };
  const stats = [
    { label: 'Quantum-vulnerable connections', value: `${q.quantum_vulnerable_pct}%`, accent: '#f59e0b' },
    { label: 'PQC-ready / modern TLS', value: `${q.modern_pct}%`, accent: '#10b981' },
    { label: 'Downgrade / weak-cipher events', value: q.downgrade_events, accent: '#ef4444' },
    { label: 'Connections scanned', value: q.total_conns, accent: '#a78bfa' },
  ];
  return (
    <div className="db-chart-container">
      <div className="db-chart-header">
        <span className="chart-label">Quantum Risk Posture (crypto inventory)</span>
        <span className="chart-val">RBI Q-SAFE</span>
      </div>
      <div className="db-metrics-row" style={{ marginTop: 8 }}>
        {stats.map((s) => (
          <div key={s.label} className="metric-card-left" style={{ flex: 1 }}>
            <div className="metric-value" style={{ color: s.accent, fontSize: 22 }}>{s.value}</div>
            <div className="metric-label" style={{ fontSize: 11 }}>{s.label}</div>
          </div>
        ))}
      </div>
      <div className="xai-footer" style={{ marginTop: 8 }}>
        Measures observable HNDL indicators (crypto exposure + downgrades). Passive
        external interception is undetectable — mitigation is PQC migration.
      </div>
    </div>
  );
}
