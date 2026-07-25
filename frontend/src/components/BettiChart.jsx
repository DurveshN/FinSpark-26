// Live topology chart: real Betti-1 curve (persistent-homology loop counts) per window.
import { AreaChart, Area, ResponsiveContainer, Tooltip, YAxis } from "recharts";
import { Badge } from "@/components/ui/badge";
import ChartCard from "./ChartCard";

export default function BettiChart({ curve }) {
  const data = (curve || []).map((v, i) => ({ radius: i, value: v }));
  const peak = data.length ? Math.max(...data.map((d) => d.value)) : 0;
  return (
    <ChartCard
      title="β₁ Betti Curve"
      badge={<Badge variant="secondary" className="text-[10px]">topology · loops</Badge>}
      right={`peak ${peak.toFixed(1)}`}>
      <ResponsiveContainer width="100%" height={150}>
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
            labelFormatter={(l) => `radius ${l}`} formatter={(v) => [v, "loops"]} />
          <Area type="monotone" dataKey="value" stroke="var(--chart-1)" fill="url(#bettiFill)" strokeWidth={2} isAnimationActive={false} />
        </AreaChart>
      </ResponsiveContainer>
    </ChartCard>
  );
}
