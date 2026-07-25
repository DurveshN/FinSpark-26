// Live SOC Dashboard. All panels bound to the REAL backend telemetry stream +
// trained-model metrics. No mock data. Premium dark SOC layout (Tailwind + shadcn).
import { useState, useCallback } from "react";
import { ShieldAlert, Activity, ScanLine, Radio, ArrowLeft } from "lucide-react";
import { useTelemetryStream } from "../hooks/useTelemetryStream";
import { useMetrics } from "../hooks/useMetrics";
import { fetchExplain } from "../api/rest";
import { Button } from "@/components/ui/button";
import KpiCard from "../components/KpiCard";
import ThreatTrend from "../components/ThreatTrend";
import BettiChart from "../components/BettiChart";
import AlertsList from "../components/AlertsList";
import XaiWaterfall from "../components/XaiWaterfall";
import QuantumMonitor from "../components/QuantumMonitor";
import ModelMetrics from "../components/ModelMetrics";
import StatusBadge from "../components/StatusBadge";
import ChartCard from "../components/ChartCard";
import { Badge } from "@/components/ui/badge";

export default function Dashboard({ onExit }) {
  const { latest, history, alerts, connected } = useTelemetryStream();
  const { metrics } = useMetrics();
  const [selected, setSelected] = useState(null);

  const onSelect = useCallback((alert) => {
    setSelected(alert);
    if (alert && (!alert.reason_codes || alert.reason_codes.length === 0)) {
      fetchExplain(alert.txn_id, alert.node_idx)
        .then((r) => setSelected((cur) => (cur && cur.txn_id === alert.txn_id ? { ...cur, reason_codes: r.reason_codes } : cur)))
        .catch(() => {});
    }
  }, []);

  const threat = latest ? latest.threat_score : 0;
  const active = latest ? latest.active_threats : 0;
  const scanned = latest ? latest.n_transactions : 0;

  return (
    <div className="min-h-screen bg-background">
      {/* ambient gradient */}
      <div className="pointer-events-none fixed inset-0 bg-[radial-gradient(ellipse_at_top,theme(colors.primary/8%),transparent_60%)]" />

      <div className="relative mx-auto max-w-7xl px-6 py-6">
        {/* header */}
        <header className="mb-6 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="grid h-10 w-10 place-items-center rounded-xl bg-primary/15 text-primary ring-1 ring-primary/30">
              <ShieldAlert className="h-5 w-5" />
            </div>
            <div>
              <h1 className="text-lg font-bold tracking-tight text-foreground">QTD-HGNN</h1>
              <p className="text-xs text-muted-foreground">Quantum-Topological Threat Correlation</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <StatusBadge connected={connected} />
            <Button variant="outline" size="sm" onClick={onExit}>
              <ArrowLeft className="mr-1 h-4 w-4" /> Landing
            </Button>
          </div>
        </header>

        {/* KPI row */}
        <div className="mb-6 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <KpiCard label="Threat Score" value={`${threat.toFixed(1)}/100`} icon={ShieldAlert}
            subtitle={threat >= 65 ? "Elevated" : "Nominal"} accent={threat >= 65 ? "text-red-400" : "text-emerald-400"} />
          <KpiCard label="Active Threats" value={active} icon={Activity}
            subtitle="flagged this window" accent={active > 0 ? "text-amber-400" : "text-emerald-400"} />
          <KpiCard label="Transactions Scanned" value={scanned.toLocaleString("en-IN")} icon={ScanLine} subtitle="current window" />
          <KpiCard label="Connection" value={connected ? "Live" : "—"} icon={Radio}
            subtitle="PyTorch backend" accent={connected ? "text-emerald-400" : "text-red-400"} />
        </div>

        {/* trend + topology */}
        <div className="mb-6 grid grid-cols-1 gap-4 lg:grid-cols-2">
          <ThreatTrend history={history} />
          <BettiChart curve={latest ? latest.betti_curve1 : []} betti={latest ? latest.betti : null} />
        </div>

        {/* alerts + XAI */}
        <div className="mb-6 grid grid-cols-1 gap-4 lg:grid-cols-2">
          <ChartCard title="Live Alert Queue" right={alerts.length}
            badge={<Badge variant="secondary" className="text-[10px]">cross-domain correlation</Badge>}>
            <AlertsList alerts={alerts} selected={selected} onSelect={onSelect} />
          </ChartCard>
          <ChartCard title="Explainable AI · SHAP" badge={<Badge variant="secondary" className="text-[10px]">per-alert</Badge>}>
            <XaiWaterfall alert={selected} />
          </ChartCard>
        </div>

        {/* quantum + model */}
        <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
          <QuantumMonitor quantum={latest ? latest.quantum : null} />
          <ModelMetrics metrics={metrics} />
        </div>
      </div>
    </div>
  );
}
