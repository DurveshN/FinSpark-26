// React hook: subscribe to the backend WebSocket telemetry stream.
// Exposes the latest scored window, a rolling history for charts, connection
// status, and accumulated flagged alerts. Auto-reconnects. No rendering here.

import { useEffect, useRef, useState, useCallback } from 'react';
import { WS_URL } from '../api/config';

const MAX_HISTORY = 30;

export function useTelemetryStream() {
  const [latest, setLatest] = useState(null);
  const [history, setHistory] = useState([]);   // [{t, threat_score, active_threats}]
  const [alerts, setAlerts] = useState([]);      // flagged transactions w/ reason codes
  const [connected, setConnected] = useState(false);
  const wsRef = useRef(null);
  const retryRef = useRef(null);

  const connect = useCallback(() => {
    const ws = new WebSocket(WS_URL);
    wsRef.current = ws;

    ws.onopen = () => { setConnected(true); ws.send('hello'); };
    ws.onclose = () => {
      setConnected(false);
      retryRef.current = setTimeout(connect, 2000);   // auto-reconnect
    };
    ws.onerror = () => ws.close();
    ws.onmessage = (evt) => {
      const p = JSON.parse(evt.data);
      setLatest(p);
      setHistory((h) => [...h.slice(-(MAX_HISTORY - 1)), {
        t: p.window ? p.window[1] : 0,
        threat_score: p.threat_score,
        active_threats: p.active_threats,
      }]);
      if (p.flagged && p.flagged.length) {
        setAlerts((a) => [...p.flagged, ...a].slice(0, 50));
      }
    };
  }, []);

  useEffect(() => {
    connect();
    return () => {
      clearTimeout(retryRef.current);
      wsRef.current && wsRef.current.close();
    };
  }, [connect]);

  return { latest, history, alerts, connected };
}
