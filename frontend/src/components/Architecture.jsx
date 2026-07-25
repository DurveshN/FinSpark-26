// Architecture diagram — the real 5-stage QTD-HGNN pipeline, as styled cards.
import { Database, Share2, Brain, FileSearch, LayoutDashboard, ChevronRight } from "lucide-react";

const STAGES = [
  { icon: Database, title: "Ingest", sub: "Cyber + Transaction", detail: "Logins, device/IP, TLS posture + payments, payees, channels", tone: "text-sky-400 bg-sky-500/10 ring-sky-500/20" },
  { icon: Share2, title: "Fuse", sub: "Graph + Topology", detail: "Heterogeneous graph; Ripser persistent homology (β₀/β₁/β₂)", tone: "text-fuchsia-400 bg-fuchsia-500/10 ring-fuchsia-500/20" },
  { icon: Brain, title: "Detect", sub: "GraphSAGE GNN", detail: "16 fused features; trained; recall 0.977 / AUC 0.9999", tone: "text-primary bg-primary/10 ring-primary/20" },
  { icon: FileSearch, title: "Explain", sub: "SHAP", detail: "Per-alert Shapley reason codes on the node subgraph", tone: "text-amber-400 bg-amber-500/10 ring-amber-500/20" },
  { icon: LayoutDashboard, title: "Act", sub: "SOC Dashboard", detail: "Live alerts, threat score, quantum posture — analyst triage", tone: "text-emerald-400 bg-emerald-500/10 ring-emerald-500/20" },
];

export default function Architecture() {
  return (
    <div>
      <div className="mb-2 text-sm font-semibold uppercase tracking-wider text-primary">Architecture</div>
      <h2 className="mb-6 text-2xl font-bold text-foreground">End-to-end pipeline</h2>
      <div className="flex flex-col gap-3 lg:flex-row lg:items-stretch">
        {STAGES.map((s, i) => (
          <div key={s.title} className="flex flex-1 items-stretch gap-3">
            <div className="flex-1 rounded-xl border border-border/60 bg-card/50 p-4 backdrop-blur">
              <div className={`mb-3 inline-flex rounded-lg p-2 ring-1 ${s.tone}`}>
                <s.icon className="h-5 w-5" />
              </div>
              <p className="text-[10px] font-medium uppercase tracking-wider text-muted-foreground">Stage {i + 1}</p>
              <h3 className="text-sm font-semibold text-foreground">{s.title}</h3>
              <p className="mb-1 text-xs font-medium text-foreground/80">{s.sub}</p>
              <p className="text-[11px] leading-tight text-muted-foreground">{s.detail}</p>
            </div>
            {i < STAGES.length - 1 && (
              <div className="hidden items-center lg:flex">
                <ChevronRight className="h-5 w-5 text-muted-foreground/50" />
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
