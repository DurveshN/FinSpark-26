// Live WebSocket connection indicator.

export default function StatusBadge({ connected }) {
  return (
    <div className="db-status-badge">
      <span className="db-legend-dot" style={{ background: connected ? '#10b981' : '#ef4444' }} />
      {connected ? 'Live · connected' : 'Reconnecting…'}
    </div>
  );
}
