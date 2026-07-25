// Quantum-readiness panel — HONEST crypto-posture, not attack detection.
// Bank's own exposure: % quantum-vulnerable key exchange + weak/downgrade events.
import { Badge } from "@/components/ui/badge";
import ChartCard from "./ChartCard";

export default function QuantumMonitor({ quantum }) {
  const q = quantum || { total_conns: 0, quantum_vulnerable_pct: 0, downgrade_events: 0, modern_pct: 0 };
  const stats = [
    { label: "Quantum-vulnerable conns", value: `${q.quantum_vulnerable_pct}%`, tone: "text-amber-400" },
    { label: "PQC-ready / modern TLS", value: `${q.modern_pct}%`, tone: "text-emerald-400" },
    { label: "Downgrade / weak-cipher", value: q.downgrade_events, tone: "text-red-400" },
    { label: "Connections scanned", value: q.total_conns, tone: "text-primary" },
  ];
  return (
    <ChartCard title="Quantum Risk Posture" badge={<Badge variant="secondary" className="text-[10px]">RBI Q-SAFE · crypto inventory</Badge>}>
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
        {stats.map((s) => (
          <div key={s.label}>
            <p className={`text-2xl font-semibold tabular-nums ${s.tone}`}>{s.value}</p>
            <p className="mt-0.5 text-[11px] leading-tight text-muted-foreground">{s.label}</p>
          </div>
        ))}
      </div>
      <p className="mt-3 border-t border-border/50 pt-2 text-[11px] text-muted-foreground">
        Observable HNDL indicators (crypto exposure + downgrades). Passive external interception is undetectable — mitigation is PQC migration.
      </p>
    </ChartCard>
  );
}
