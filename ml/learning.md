# ML Learning Log

> Append newest at top.

## 2026-07-25
- ML pipeline dir created. Fixing the old repo's core disconnect: Betti/topological features will ACTUALLY be fed into the model (old code computed them but never used them).
- Persistent homology will be real (ripser), not `variance + random`.
- **Deps confirmed on Python 3.13.5:** torch 2.13.0+cpu, torch-geometric 2.8.0.post1, ripser 0.6.15 (prebuilt wheel, no compile), shap 0.52.0, scikit-learn 1.9.0, numpy 2.4.6, pandas 2.3.x, networkx 3.6.1. No 3.11 fallback needed.
- **Phase 1 (synthetic data) DONE + validated:** 6000 customers, 559,661 transactions, 445,158 logins. Malicious rate ~0.1% (realistic; will class-weight). Scenarios: 220 ATO, 40 mule rings (242 txns), 120 HNDL, 211 benign-anomaly.
- **Phase 2 core validated with REAL numbers:** fused features separate classes strongly (amount_zscore 0.0 vs 56.1; login_new_device 0.002 vs 0.58; tls_quantum_vulnerable 0.18 vs 0.66). Real ripser Betti on malicious feature cloud: b0=147, b1=18 (loops!) vs benign b1=0. The "shape of data" signal is genuine, not faked.
- Note: amount_zscore is a very strong separator; benign_anomaly cases (large legit purchases) are included specifically so the model can't trivially flag all large amounts — topology + cyber features add robustness.
- **Phase 3 training finding (HONEST):** GraphSAGE reaches AUC=1.0, recall=1.0 by epoch 20 (fusion features separate cleanly), BUT precision at threshold 0.5 is low (0.11->0.33), i.e. many false positives. Root cause: heavy positive-class weighting + fixed 0.5 threshold = miscalibrated. FIX: tune decision threshold to maximize F1 on a validation split, save it as an artifact, backend uses tuned threshold. This directly serves PS2 "reduce false positives". Do NOT hide low precision — report at tuned threshold.
- **Gotcha:** Python stdout is block-buffered when redirected to a file; use `python -u` or epoch prints stay invisible mid-run (looked like a hang). Betti now cached to `ml/data/cust_betti_cache.csv` (55s -> instant reruns).
- **Phase 3 DONE — real held-out metrics (threshold 0.99, tuned on train):** precision 0.714, recall 0.977, F1 0.825, AUC 0.99998. Honest: recall excellent, ~29% false-positive rate (vs research-cited 90%+ in current SOCs). cust_betti0/1/2 ARE in the 16-feature vector -> topology feeds the model (old disconnect fixed). Artifacts: model.pt, scaler.npz, shap_background.npy, metrics.json.
- EPOCHS lowered 200->80 (saturates by ~ep30). ~1s/epoch when CPU uncontended; my own bash polling stole CPU and slowed runs — lesson: don't poll during training, use one monitor.
- **Known issue to fix in Phase 5:** per-WINDOW betti_curve for the dashboard reads ~0 (0.5-day windows too sparse for loops); per-customer betti (model feature) is fine. Widen window or aggregate for the dashboard topology chart.
