// Live topology chart: plots the real Betti-1 curve (persistent-homology loop
// counts) streamed from the backend. Data is genuine ripser output per window.

import { AreaChart, Area, ResponsiveContainer, Tooltip, YAxis } from 'recharts';

export default function BettiChart({ curve, title = 'β₁ Betti Curve (loops)', color = '#a78bfa' }) {
  const data = (curve || []).map((v, i) => ({ radius: i, value: v }));
  const peak = data.length ? Math.max(...data.map((d) => d.value)) : 0;
  return (
    <div className="db-chart-container">
      <div className="db-chart-header">
        <span className="chart-label">{title}</span>
        <span className="chart-val">peak {peak.toFixed(1)}</span>
      </div>
      <div className="chart-wrapper">
        <ResponsiveContainer width="100%" height={120}>
          <AreaChart data={data}>
            <defs>
              <linearGradient id="bettiFill" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor={color} stopOpacity={0.5} />
                <stop offset="100%" stopColor={color} stopOpacity={0} />
              </linearGradient>
            </defs>
            <YAxis hide domain={[0, 'dataMax + 1']} />
            <Tooltip contentStyle={{ background: '#0d1117', border: '1px solid #30363d', fontSize: 12 }} />
            <Area type="monotone" dataKey="value" stroke={color} fill="url(#bettiFill)" strokeWidth={2} />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
