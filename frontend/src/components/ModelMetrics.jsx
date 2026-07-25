// Model Insights panel — REAL held-out metrics from ml/artifacts/metrics.json (/metrics).
import { Badge } from "@/components/ui/badge";
import ChartCard from "./ChartCard";

export default function ModelMetrics({ metrics }) {
  if (!metrics || metrics.error) {
    return (
      <ChartCard title="Model Insights">
        <p className="text-sm text-muted-foreground">Metrics unavailable — train the model first.</p>
      </ChartCard>
    );
  }
  const pct = (v) => `${(v * 100).toFixed(1)}%`;
  const items = [
    { label: "Recall (fraud caught)", value: pct(metrics.recall), tone: "text-emerald-400" },
    { label: "Precision (alert accuracy)", value: pct(metrics.precision), tone: "text-sky-400" },
    { label: "F1 score", value: metrics.f1.toFixed(3), tone: "text-primary" },
    { label: "AUC", value: metrics.auc.toFixed(4), tone: "text-amber-400" },
  ];
  return (
    <ChartCard title={`Model Insights · ${metrics.model}`} badge={<Badge variant="secondary" className="text-[10px]">held-out test</Badge>}>
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
        {items.map((it) => (
          <div key={it.label}>
            <p className={`text-2xl font-semibold tabular-nums ${it.tone}`}>{it.value}</p>
            <p className="mt-0.5 text-[11px] leading-tight text-muted-foreground">{it.label}</p>
          </div>
        ))}
      </div>
      <p className="mt-3 border-t border-border/50 pt-2 text-[11px] text-muted-foreground">
        Decision threshold {metrics.threshold} · {metrics.features?.length || 0} fused cyber+transaction+topology features.
      </p>
    </ChartCard>
  );
}
