# ML Infra (offline training + data)

Offline pipeline. Not shipped in the API image; produces artifacts the backend loads.

## Layout
- `generate_synthetic.py` — synthetic bank (entities, cyber telemetry, transactions) with injected labeled scenarios → Postgres + CSV.
- `features.py` — heterogeneous graph per window, fused node features, real persistent homology (ripser) → Betti curves.
- `train.py` — train GNN (+ optional XGBoost baseline) incl. topological features → `artifacts/model.pt`, SHAP background, scaler.
- `evaluate.py` — precision/recall/F1/AUC, confusion matrix → `artifacts/metrics.json`.
- `artifacts/` — trained model + metadata (gitignored if large; metrics.json kept).

## Runtime
- Python venv. Key deps: torch, torch_geometric, ripser, shap, scikit-learn, networkx, pandas, sqlalchemy.
- Python 3.13 wheel availability is a risk — pin versions; fallback to 3.11 venv if needed (see learning.md).
