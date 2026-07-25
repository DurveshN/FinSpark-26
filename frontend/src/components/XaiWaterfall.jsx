// SHAP explanation panel: renders the REAL per-feature Shapley attributions for a
// selected flagged transaction (computed by the backend, not hardcoded). Positive
// values push toward malicious, negative toward benign.

const FEATURE_LABEL = {
  amount_zscore: 'Amount vs customer normal',
  log_amount: 'Transaction size',
  new_payee: 'New payee added',
  sec_since_login: 'Time since login',
  sec_since_payee_add: 'Payee age',
  is_swift: 'SWIFT channel',
  is_imps: 'IMPS channel',
  login_new_device: 'Login from new device',
  login_failed_prior: 'Prior failed logins',
  login_odd_hour: 'Odd-hour login',
  tls_quantum_vulnerable: 'Quantum-vulnerable TLS',
  tls_weak_downgrade: 'Weak/downgraded cipher',
  geo_mismatch: 'Geo mismatch',
  cust_betti0: 'Topology: components (β₀)',
  cust_betti1: 'Topology: loops (β₁)',
  cust_betti2: 'Topology: voids (β₂)',
};

export default function XaiWaterfall({ alert }) {
  if (!alert) {
    return (
      <div className="xai-card">
        <div className="xai-prompt">Select an alert to see its SHAP explanation.</div>
      </div>
    );
  }
  const codes = alert.reason_codes || [];
  const maxAbs = Math.max(1e-6, ...codes.map((c) => Math.abs(c.shap_value)));
  return (
    <div className="xai-card">
      <div className="xai-banner-title">Why flagged — {alert.txn_id}</div>
      <div className="xai-banner-desc">
        Model confidence {(alert.prob * 100).toFixed(0)}% · ₹{Number(alert.amount).toLocaleString('en-IN')}
      </div>
      <div className="xai-factors-list">
        {codes.length === 0 && <div className="xai-prompt">Computing SHAP…</div>}
        {codes.map((c) => {
          const pct = (Math.abs(c.shap_value) / maxAbs) * 100;
          const pos = c.shap_value >= 0;
          return (
            <div key={c.feature} className="xai-factor-item">
              <div className="xai-factor-header">
                <span className="factor-label">{FEATURE_LABEL[c.feature] || c.feature}</span>
                <span className="factor-percentage" style={{ color: pos ? '#ef4444' : '#10b981' }}>
                  {pos ? '+' : ''}{c.shap_value.toFixed(3)}
                </span>
              </div>
              <div className="factor-progress-bg">
                <div className="factor-progress-bar"
                     style={{ width: `${pct}%`, background: pos ? '#ef4444' : '#10b981' }} />
              </div>
            </div>
          );
        })}
      </div>
      <div className="xai-footer">Attributions are computed Shapley values (auditable, per RBI/DPDP).</div>
    </div>
  );
}
