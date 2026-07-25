// Live SOC Dashboard. Assembles all panels against the REAL backend telemetry
// stream (useTelemetryStream) and the trained model's metrics (useMetrics).
// Every number here is computed by the model/pipeline — no mock data.

import { useState } from 'react';
import { useTelemetryStream } from '../hooks/useTelemetryStream';
import { useMetrics } from '../hooks/useMetrics';
import KpiCard from '../components/KpiCard';
import ThreatTrend from '../components/ThreatTrend';
import BettiChart from '../components/BettiChart';
import AlertsList from '../components/AlertsList';
import XaiWaterfall from '../components/XaiWaterfall';
import QuantumMonitor from '../components/QuantumMonitor';
import ModelMetrics from '../components/ModelMetrics';
import StatusBadge from '../components/StatusBadge';

export default function Dashboard({ onExit }) {
  const { latest, history, alerts, connected } = useTelemetryStream();
  const { metrics } = useMetrics();
  const [selected, setSelected] = useState(null);

  const threat = latest ? latest.threat_score : 0;
  const active = latest ? latest.active_threats : 0;
  const scanned = latest ? latest.n_transactions : 0;
  const betti = latest ? latest.betti_curve1 : [];
  const quantum = latest ? latest.quantum : null;

  return (
    <div className="db-main">
      <header className="db-header">
        <div className="db-logo" onClick={onExit} style={{ cursor: 'pointer' }}>
          <div className="db-logo-text">
            <div className="db-logo-title">QTD-HGNN</div>
            <div className="db-logo-subtitle">Quantum-Topological Threat Correlation</div>
          </div>
        </div>
        <div className="db-header-actions">
          <StatusBadge connected={connected} />
          <button className="btn-back-landing" onClick={onExit}>← Landing</button>
        </div>
      </header>

      {/* KPI row — live model output */}
      <div className="db-metrics-row">
        <KpiCard label="Threat Score" value={`${threat.toFixed(1)}/100`}
                 subtitle={threat >= 65 ? 'Elevated' : 'Nominal'} accent={threat >= 65 ? '#ef4444' : '#10b981'} />
        <KpiCard label="Active Threats" value={active} subtitle="flagged this window"
                 accent={active > 0 ? '#f59e0b' : '#10b981'} />
        <KpiCard label="Transactions Scanned" value={scanned.toLocaleString('en-IN')} subtitle="current window" />
        <KpiCard label="Connection" value={connected ? 'Live' : '—'}
                 subtitle="PyTorch backend" accent={connected ? '#10b981' : '#ef4444'} />
      </div>

      {/* trend + topology */}
      <div className="db-content-grid">
        <ThreatTrend history={history} />
        <BettiChart curve={betti} />
      </div>

      {/* alerts + XAI */}
      <div className="db-middle-row">
        <AlertsList alerts={alerts} selected={selected} onSelect={setSelected} />
        <XaiWaterfall alert={selected} />
      </div>

      {/* quantum posture + model metrics */}
      <div className="db-bottom-row">
        <QuantumMonitor quantum={quantum} />
        <ModelMetrics metrics={metrics} />
      </div>
    </div>
  );
}
