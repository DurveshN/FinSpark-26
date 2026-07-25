// Marketing landing page — premium dark hero + feature grid. Static by design.
import { Play, Network, Boxes, FileSearch, ShieldCheck } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

const FEATURES = [
  { icon: Network, title: "Cyber × Transaction Correlation",
    desc: "Fuses login/device/IP telemetry with payment behaviour so account-takeover patterns that neither the SIEM nor the fraud engine catch alone become visible." },
  { icon: Boxes, title: "Topological Anomaly Detection",
    desc: "Real persistent homology (Betti numbers via Ripser) captures the structural shape of transaction behaviour and feeds it to the graph neural network." },
  { icon: FileSearch, title: "Explainable by Design",
    desc: "Every alert ships computed SHAP reason codes — auditable per-feature attributions, aligned to RBI fraud-risk and DPDP requirements." },
  { icon: ShieldCheck, title: "Quantum Risk Posture",
    desc: "Honest crypto-inventory: flags quantum-vulnerable TLS and downgrade events (RBI Q-SAFE). Does not claim to detect passive interception — physically impossible." },
];

export default function Landing({ onEnter }) {
  return (
    <div className="relative min-h-screen overflow-hidden bg-background">
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_at_top_left,theme(colors.primary/12%),transparent_55%)]" />
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_at_bottom_right,theme(colors.chart-2/10%),transparent_55%)]" />

      <div className="relative mx-auto max-w-6xl px-6 py-20">
        <Badge variant="outline" className="mb-6 border-primary/30 bg-primary/10 text-primary">
          Next-Gen Quantum-Topological Threat Detection
        </Badge>

        <h1 className="max-w-3xl text-5xl font-bold leading-[1.05] tracking-tight text-foreground sm:text-6xl">
          See Threats{" "}
          <span className="bg-gradient-to-r from-primary via-fuchsia-400 to-sky-400 bg-clip-text text-transparent">
            Before They Strike.
          </span>
        </h1>

        <p className="mt-6 max-w-2xl text-lg leading-relaxed text-muted-foreground">
          QTD-HGNN correlates cybersecurity telemetry with transactional behaviour using a trained
          graph neural network, topological data analysis, and explainable AI — built for
          RBI-regulated banks, deployable in the bank's own cloud.
        </p>

        <div className="mt-8 flex flex-wrap gap-3">
          <Button size="lg" onClick={onEnter} className="gap-2">
            <Play className="h-4 w-4" /> Open Live Dashboard
          </Button>
        </div>

        <div className="mt-16 grid grid-cols-1 gap-4 sm:grid-cols-2">
          {FEATURES.map((f) => (
            <Card key={f.title} className="group border-border/60 bg-card/50 p-6 backdrop-blur transition-colors hover:border-primary/40 hover:bg-card/70">
              <div className="mb-3 inline-flex rounded-lg bg-primary/10 p-2.5 text-primary ring-1 ring-primary/20">
                <f.icon className="h-5 w-5" />
              </div>
              <h3 className="mb-1.5 text-base font-semibold text-foreground">{f.title}</h3>
              <p className="text-sm leading-relaxed text-muted-foreground">{f.desc}</p>
            </Card>
          ))}
        </div>

        <footer className="mt-16 border-t border-border/50 pt-6 text-sm text-muted-foreground">
          FinSpark'26 · Problem Statement 2 · Team Hexacon — every metric on the dashboard is computed by the trained model, not simulated.
        </footer>
      </div>
    </div>
  );
}
