// Live topology panel: real Betti numbers (β₀/β₁/β₂) + β₁ curve, computed by Ripser
// on a rolling buffer of the most-anomalous points (where ring/ATO structure forms).
import { AreaChart, Area, ResponsiveContainer, Tooltip, YAxis } from "recharts";
import { Badge } from "@/components/ui/badge";
import ChartCard from "./ChartCard";

function Stat({ label, value, tone }) {
  return (
    <div className="rounded-lg bg-muted/40 px-3 py-2">
      <p className={`text-lg font-semibold tabular-nums ${tone}`}>{value}</p>
      <p className="text-[10px] uppercase tracking-wide text-muted-foreground">{label}</p>
    </div>
  );
}

export default function BettiChart({ curve, betti }) {
  const data = (curve || []).map((v, i) => ({ radius: i, value: v }));
  const peak = data.length ? Math.max(...data.map((d) => d.value)) : 0;
  const b = betti || { betti0: 0, betti1: 0, betti2: 0 };
  return (
    <ChartCard
      title="Topological Analysis"
      badge={<Badge variant="secondary" className="text-[10px]">Ripser · persistent homology</Badge>}
      right={`β₁ peak ${peak.toFixed(0)}`}>
      <div className="mb-3 grid grid-cols-3 gap-2">
        <Stat label="β₀ components" value={b.betti0} tone="text-sky-400" />
        <Stat label="β₁ loops" value={b.betti1} tone={b.betti1 > 0 ? "text-fuchsia-400" : "text-muted-foreground"} />
        <Stat label="β₂ voids" value={b.betti2} tone="text-primary" />
      </div>
      <ResponsiveContainer width="100%" height={96}>
        <AreaChart data={data} margin={{ top: 4, right: 4, left: 4, bottom: 0 }}>
          <defs>
            <linearGradient id="bettiFill" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="var(--chart-1)" stopOpacity={0.55} />
              <stop offset="100%" stopColor="var(--chart-1)" stopOpacity={0} />
            </linearGradient>
          </defs>
          <YAxis hide domain={[0, "dataMax + 1"]} />
          <Tooltip
            contentStyle={{ background: "var(--popover)", border: "1px solid var(--border)", borderRadius: 8, fontSize: 12, color: "var(--foreground)" }}
            labelFormatter={(l) => `radius ${l}`} formatter={(v) => [v, "loops alive"]} />
          <Area type="monotone" dataKey="value" stroke="var(--chart-1)" fill="url(#bettiFill)" strokeWidth={2} isAnimationActive={false} />
        </AreaChart>
      </ResponsiveContainer>
    </ChartCard>
  );
}
