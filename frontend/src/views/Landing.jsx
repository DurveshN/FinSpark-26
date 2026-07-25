// Marketing landing page. Static by design (no fake live metrics). Explains the
// product honestly and routes into the live dashboard.

const FEATURES = [
  { title: 'Cyber × Transaction Correlation', desc: 'Fuses login/device/IP telemetry with payment behaviour so account-takeover patterns that neither the SIEM nor the fraud engine catch alone become visible.' },
  { title: 'Topological Anomaly Detection', desc: 'Real persistent homology (Betti numbers via Ripser) captures the structural shape of transaction behaviour and feeds it to the graph neural network.' },
  { title: 'Explainable by Design', desc: 'Every alert ships with computed SHAP reason codes — auditable per-feature attributions, aligned to RBI fraud-risk and DPDP requirements.' },
  { title: 'Quantum Risk Posture', desc: 'Honest crypto-inventory: flags quantum-vulnerable TLS and downgrade events (RBI Q-SAFE). Does not claim to detect passive interception — that is physically impossible.' },
];

export default function Landing({ onEnter }) {
  return (
    <div className="landing-root">
      <section className="hero-section">
        <div className="hero-badge">Next-Gen Quantum-Topological Threat Detection</div>
        <h1 className="hero-title">See Threats <span className="hero-accent">Before They Strike.</span></h1>
        <p className="hero-desc">
          QTD-HGNN correlates cybersecurity telemetry with transactional behaviour using a
          trained graph neural network, topological data analysis, and explainable AI — built
          for RBI-regulated banks, deployable in the bank's own cloud.
        </p>
        <div className="hero-actions">
          <button className="btn-view-prototype" onClick={onEnter}>▶ Open Live Dashboard</button>
        </div>
      </section>

      <section className="features-grid">
        {FEATURES.map((f) => (
          <div key={f.title} className="feature-card">
            <div className="feature-title">{f.title}</div>
            <div className="feature-desc">{f.desc}</div>
          </div>
        ))}
      </section>

      <footer className="landing-footer">
        FinSpark'26 · Problem Statement 2 · Team Hexacon — every metric on the dashboard is
        computed by the trained model, not simulated.
      </footer>
    </div>
  );
}
