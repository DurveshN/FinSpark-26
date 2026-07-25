// Rolling composite threat-score trend across recent scored windows (real model output).
import { AreaChart, Area, ResponsiveContainer, Tooltip, YAxis } from "recharts";
import ChartCard from "./ChartCard";

export default function ThreatTrend({ history }) {
  const data = (history || []).map((h, i) => ({ i, score: h.threat_score }));
  const last = data.length ? data[data.length - 1].score : 0;
  return (
    <ChartCard title="Composite Threat Score" right={`${last.toFixed(1)} / 100`}>
      <ResponsiveContainer width="100%" height={150}>
        <AreaChart data={data} margin={{ top: 4, right: 4, left: 4, bottom: 0 }}>
          <defs>
            <linearGradient id="threatFill" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="var(--chart-4)" stopOpacity={0.55} />
              <stop offset="100%" stopColor="var(--chart-4)" stopOpacity={0} />
            </linearGradient>
          </defs>
          <YAxis hide domain={[0, 100]} />
          <Tooltip
            contentStyle={{ background: "var(--popover)", border: "1px solid var(--border)", borderRadius: 8, fontSize: 12, color: "var(--foreground)" }}
            labelFormatter={() => ""} formatter={(v) => [`${Number(v).toFixed(1)}/100`, "threat"]} />
          <Area type="monotone" dataKey="score" stroke="var(--chart-4)" fill="url(#threatFill)" strokeWidth={2} isAnimationActive={false} />
        </AreaChart>
      </ResponsiveContainer>
    </ChartCard>
  );
}
