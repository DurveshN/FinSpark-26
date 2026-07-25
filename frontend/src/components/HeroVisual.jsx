// Hero visual: an animated threat-correlation graph (SVG). Cyber nodes (device/IP/
// login) linked to transaction nodes (account/payee) — a compromised path pulses red.
const NODES = [
  { id: "dev", x: 60, y: 60, r: 9, c: "#38bdf8", label: "Device" },
  { id: "ip", x: 150, y: 40, r: 7, c: "#38bdf8", label: "IP" },
  { id: "login", x: 120, y: 130, r: 10, c: "#a78bfa", label: "Login" },
  { id: "acct", x: 230, y: 110, r: 11, c: "#a78bfa", label: "Account" },
  { id: "txn", x: 300, y: 60, r: 14, c: "#f43f5e", label: "Transfer", bad: true },
  { id: "payee", x: 340, y: 150, r: 9, c: "#fbbf24", label: "Payee" },
  { id: "b1", x: 250, y: 200, r: 6, c: "#34d399" },
  { id: "b2", x: 90, y: 200, r: 6, c: "#34d399" },
];
const EDGES = [
  ["dev", "login"], ["ip", "login"], ["login", "acct"], ["acct", "txn"],
  ["txn", "payee"], ["acct", "b1"], ["login", "b2"], ["ip", "acct"],
];
const P = Object.fromEntries(NODES.map((n) => [n.id, n]));

export default function HeroVisual() {
  return (
    <svg viewBox="0 0 400 240" className="h-full w-full">
      <defs>
        <radialGradient id="glow" cx="50%" cy="50%" r="50%">
          <stop offset="0%" stopColor="#f43f5e" stopOpacity="0.5" />
          <stop offset="100%" stopColor="#f43f5e" stopOpacity="0" />
        </radialGradient>
      </defs>
      {EDGES.map(([a, b], i) => {
        const bad = P[a].bad || P[b].bad;
        return (
          <line key={i} x1={P[a].x} y1={P[a].y} x2={P[b].x} y2={P[b].y}
            stroke={bad ? "#f43f5e" : "#475569"} strokeWidth={bad ? 2 : 1} strokeOpacity={bad ? 0.8 : 0.4}>
            {bad && <animate attributeName="stroke-opacity" values="0.3;0.9;0.3" dur="2s" repeatCount="indefinite" />}
          </line>
        );
      })}
      <circle cx={P.txn.x} cy={P.txn.y} r="30" fill="url(#glow)">
        <animate attributeName="r" values="22;34;22" dur="2s" repeatCount="indefinite" />
      </circle>
      {NODES.map((n) => (
        <g key={n.id}>
          <circle cx={n.x} cy={n.y} r={n.r} fill={n.c} fillOpacity={n.bad ? 0.9 : 0.75}
            stroke={n.c} strokeWidth="1.5" strokeOpacity="0.6">
            {n.bad && <animate attributeName="fill-opacity" values="0.6;1;0.6" dur="1.5s" repeatCount="indefinite" />}
          </circle>
          {n.label && <text x={n.x} y={n.y - n.r - 5} textAnchor="middle" className="fill-slate-400" fontSize="9">{n.label}</text>}
        </g>
      ))}
    </svg>
  );
}
