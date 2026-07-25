// Rolling threat-score trend across recent scored windows (real model output).

import { AreaChart, Area, ResponsiveContainer, Tooltip, YAxis } from 'recharts';

export default function ThreatTrend({ history }) {
  const data = (history || []).map((h, i) => ({ i, score: h.threat_score }));
  return (
    <div className="db-chart-container">
      <div className="db-chart-header">
        <span className="chart-label">Composite Threat Score (live)</span>
        <span className="chart-val">{data.length ? data[data.length - 1].score.toFixed(1) : '0.0'}/100</span>
      </div>
      <div className="chart-wrapper">
        <ResponsiveContainer width="100%" height={120}>
          <AreaChart data={data}>
            <defs>
              <linearGradient id="threatFill" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#ef4444" stopOpacity={0.5} />
                <stop offset="100%" stopColor="#ef4444" stopOpacity={0} />
              </linearGradient>
            </defs>
            <YAxis hide domain={[0, 100]} />
            <Tooltip contentStyle={{ background: '#0d1117', border: '1px solid #30363d', fontSize: 12 }} />
            <Area type="monotone" dataKey="score" stroke="#ef4444" fill="url(#threatFill)" strokeWidth={2} />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
