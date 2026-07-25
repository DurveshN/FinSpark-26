// Live alert queue. Each item is a real flagged transaction from the model, with
// its scenario tag and score. Clicking selects it for the XAI waterfall.

const SCENARIO_LABEL = {
  account_takeover: 'Account Takeover',
  mule_ring: 'Mule Ring',
  hndl_indicator: 'HNDL Indicator',
  benign_anomaly: 'Benign Anomaly',
  normal: 'Anomaly',
};

export default function AlertsList({ alerts, selected, onSelect }) {
  return (
    <div className="db-alerts-list">
      <div className="db-chart-header">
        <span className="chart-label">Live Alert Queue</span>
        <span className="chart-val">{alerts.length}</span>
      </div>
      {alerts.length === 0 && <div className="alert-desc" style={{ padding: 12 }}>No active threats in current window.</div>}
      {alerts.map((a) => {
        const sev = a.prob >= 0.9 ? '#ef4444' : a.prob >= 0.7 ? '#f59e0b' : '#10b981';
        const isSel = selected && selected.txn_id === a.txn_id;
        return (
          <div key={a.txn_id} className="db-alert-item" onClick={() => onSelect(a)}
               style={{ cursor: 'pointer', borderLeft: isSel ? `3px solid ${sev}` : '3px solid transparent' }}>
            <div className="alert-item-left">
              <span className="alert-severity-dot" style={{ background: sev }} />
              <div className="alert-text">
                <div className="alert-title">{SCENARIO_LABEL[a.scenario] || 'Threat'} — {a.txn_id}</div>
                <div className="alert-desc">₹{Number(a.amount).toLocaleString('en-IN')} · {(a.prob * 100).toFixed(0)}% confidence</div>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
