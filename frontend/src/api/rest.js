// REST client for the backend. Thin fetch wrappers for model metrics and alerts.
// No UI logic here.

import { API_BASE } from './config';

async function getJSON(path) {
  const res = await fetch(`${API_BASE}${path}`);
  if (!res.ok) throw new Error(`${path} -> ${res.status}`);
  return res.json();
}

export const fetchMetrics = () => getJSON('/metrics');
export const fetchAlerts = (limit = 50) => getJSON(`/alerts?limit=${limit}`);
export const fetchHealth = () => getJSON('/health');
export const fetchExplain = (txnId, nodeIdx) => getJSON(`/explain/${txnId}?node_idx=${nodeIdx}`);
