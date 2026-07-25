// React hook: fetch the trained model's real evaluation metrics once on mount.
// Feeds the "Model Insights" panel with genuine precision/recall/F1/AUC from
// ml/artifacts/metrics.json (via the backend /metrics endpoint). No fake numbers.

import { useEffect, useState } from 'react';
import { fetchMetrics } from '../api/rest';

export function useMetrics() {
  const [metrics, setMetrics] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    let alive = true;
    fetchMetrics()
      .then((m) => alive && setMetrics(m))
      .catch((e) => alive && setError(e.message));
    return () => { alive = false; };
  }, []);

  return { metrics, error };
}
