"""Technical Notes PDF - part 2: transactions, features, model, storage, dashboard."""
from __future__ import annotations
from docs.pdfgen.pdfkit import Doc, ACCENT, WARN, OK


def add_rest(d: Doc) -> None:
    d.h2("4.3 Transactional behaviour - transaction events")
    d.table(["Field", "Meaning"],
            [["txn_id, customer_id, account_id", "Transaction id + owning customer/account"],
             ["t_day", "Timestamp (fractional day)"],
             ["amount", "Transaction value (INR)"],
             ["channel", "UPI / NEFT / IMPS / CARD / SWIFT"],
             ["payee_id, new_payee", "Beneficiary; 1 if payee is new (ATO/mule signal)"],
             ["sec_since_login", "Seconds between the preceding login and this transaction"],
             ["sec_since_payee_add", "Age of the payee relationship (fresh payee = risk)"],
             ["label, scenario", "Ground truth label + scenario tag"]],
            [50, 124])

    d.h2("4.4 Injected labelled scenarios (the ground truth)")
    d.bullet("Hostile login (new device + geo, failed-login burst, weak TLS) -> new payee -> large "
             "drain, seconds apart. ~220 episodes.", "Account takeover")
    d.bullet("A ring of accounts passing funds in a cycle through a shared hub (layering). ~40 rings.", "Mule ring")
    d.bullet("Crypto-downgrade login (weak/export cipher) + bulk-egress staging transaction "
             "(huge, SWIFT, off-hours). ~120 chains.", "HNDL indicator")
    d.bullet("Legitimate-but-unusual events (a real large purchase, a genuine new phone) - LABELLED "
             "BENIGN so the model learns NOT to flag them. ~400. This is what trains false-positive "
             "suppression.", "Benign anomaly")

    d.h1("5. Feature engineering - the fusion row (16 features)")
    d.para("For each transaction, the nearest preceding login is joined in, and cross-domain "
           "features are computed. Cyber columns and transaction columns sit in the SAME row - the "
           "thing no siloed bank tool builds. The model consumes these 16 features:")
    d.table(["Feature", "Domain / meaning"],
            [["amount_zscore", "Txn: amount vs this customer's normal (std deviations)"],
             ["log_amount", "Txn: log transaction size"],
             ["new_payee", "Txn: payee is new"],
             ["sec_since_login, sec_since_payee_add", "Txn: timing - login->txn gap, payee age"],
             ["is_swift, is_imps", "Txn: channel flags"],
             ["login_new_device", "Cyber: login from an unseen device"],
             ["login_failed_prior", "Cyber: prior failed-login count"],
             ["login_odd_hour", "Cyber: login in 00:00-06:00"],
             ["tls_quantum_vulnerable", "Cyber/quantum: RSA/ECDHE-RSA (not PQC-hybrid)"],
             ["tls_weak_downgrade", "Cyber/quantum: export/weak cipher (downgrade indicator)"],
             ["geo_mismatch", "Cross: geo inconsistency signal"],
             ["cust_betti0 / betti1 / betti2", "Topology: shape of this customer's transaction cloud"]],
            [60, 114])
    d.callout("The fixed disconnect",
              "In the discarded prototype, Betti numbers were computed but NEVER fed to the model, "
              "and were faked as 'variance + random'. Here they are real Ripser persistent homology "
              "AND are actual model features (cust_betti0/1/2).")

    d.h1("6. Topology - persistent homology (real)")
    d.para("A point cloud of feature vectors is built and a Vietoris-Rips filtration is computed "
           "with Ripser. Betti numbers count holes that persist across scales: b0 = connected "
           "components (clusters), b1 = loops (ring-like structure - money-mule signal), b2 = voids. "
           "Validated: a malicious feature cloud shows b1 = 18 loops vs 0 for benign. On the live "
           "dashboard, Betti is computed on a rolling buffer of the most-anomalous points so ring "
           "structure accumulates and b1 loops surface during attacks.")

    d.h1("7. The model - GraphSAGE GNN")
    d.bullet("Nodes = transactions. Edges connect transactions sharing a customer (temporal "
             "sequence -> ATO) and sharing a payee (hub -> mule ring).", "Graph")
    d.bullet("2-layer GraphSAGE, 16 input features (incl. topology) -> 2 classes. Class-weighted "
             "for the ~0.1% fraud rate; train/test split; best-F1 checkpoint; decision threshold "
             "tuned on train predictions to cut false positives.", "Architecture")
    d.h2("Held-out test metrics (real, not inflated)")
    d.table(["Metric", "Value", "Meaning"],
            [["Recall", "0.977", "catches 97.7% of real fraud"],
             ["Precision", "0.714", "71% of alerts are true (~29% FP - vs 90%+ cited in current SOCs)"],
             ["F1", "0.825", "balance of the two"],
             ["AUC", "0.99998", "near-perfect ranking"],
             ["Threshold", "0.99", "tuned; 559,661 txns scored, 776 flagged"]],
            [30, 26, 118])

    d.h1("8. Explainability - SHAP")
    d.para("Every flagged transaction is explained by computing SHAP values on the node's local "
           "2-hop subgraph (fast, ~0.4s, real values on the actual trained model). Positive values "
           "push toward malicious, negative toward benign. Example for a real account-takeover: "
           "amount_zscore +0.52, login_new_device +0.22, is_swift +0.09. These become plain-English "
           "reason codes - auditable per RBI Fraud-Risk & DPDP.")

    d.h1("9. How data is stored")
    d.bullet("PostgreSQL (prod) / SQLite (local), via SQLAlchemy ORM; schema managed by Alembic "
             "migrations. Raw synthetic data lives as CSV; the trained model as model.pt + scaler; "
             "the pre-scored dataset as scored.csv + graph.pt (built into the image).", "Stores")
    d.h2("The Alert table (one row per flagged transaction - auditable)")
    d.table(["Column", "Meaning"],
            [["id", "Primary key"],
             ["txn_id, customer_id", "Which transaction / customer"],
             ["amount", "Transaction value"],
             ["threat_score", "0-100 (model probability x 100)"],
             ["predicted_label", "0 benign / 1 malicious"],
             ["scenario", "Ground-truth tag (synthetic): account_takeover / mule_ring / hndl_indicator / ..."],
             ["reason_codes", "JSON: [{feature, value, shap_value}] - the SHAP explanation"],
             ["created_at", "Timestamp (indexed)"]],
            [40, 134])
    d.callout("Why a real DB matters",
              "Under RBI + DPDP a bank cannot act on a black-box score. Persisting each alert with "
              "its SHAP reason codes makes every decision reproducible and legally defensible - "
              "versus the discarded prototype's ephemeral random JSON.")

    d.h1("10. What the dashboard shows - every field")
    d.table(["Panel / field", "Source & meaning"],
            [["Threat Score (KPI + trend)", "Mean of the top-20 window probabilities x100 - severity of riskiest activity"],
             ["Active Threats", "Count of transactions >= 0.99 in the current window"],
             ["Transactions Scanned", "Transactions in the current 0.5-day window"],
             ["Connection", "Live WebSocket status to the PyTorch backend"],
             ["Betti panel (b0/b1/b2 + curve)", "Real Ripser homology on the rolling anomaly buffer"],
             ["Live Alert Queue", "Flagged transactions: scenario badge, amount, confidence"],
             ["SHAP waterfall", "On-click: real per-feature Shapley attributions for that alert"],
             ["Quantum Risk Posture", "% quantum-vulnerable TLS, downgrade events, modern % (from window logins)"],
             ["Model Insights", "Real held-out precision/recall/F1/AUC from metrics.json"]],
            [56, 118])

    d.h1("11. Runtime data flow")
    d.bullet("Data generated + whole dataset scored -> scored.csv + graph.pt baked into the image. "
             "Makes startup instant and the container self-contained.", "Build time")
    d.bullet("Model + pre-scored artifacts loaded (~0.8s). Each 1.5s tick slices the pre-scored rows "
             "for the next time window and broadcasts over WebSocket. No heavy compute on the event "
             "loop (that previously hung the server).", "Startup + stream")
    d.bullet("When an analyst clicks an alert, GET /explain/{txn_id} computes SHAP on the node's "
             "subgraph off the event loop (~0.4s), cached.", "On demand")

    d.h1("12. Honesty notes")
    d.para("Data is synthetic (no public dataset joins both domains), with a swappable ingestion "
           "format. The quantum module reports real cryptographic posture and observable HNDL "
           "indicators (crypto-downgrade, bulk egress); it does NOT claim to detect passive "
           "interception, which is physically undetectable - the mitigation is PQC migration. "
           "Topology, the trained GNN, SHAP, and all metrics are genuine and reproducible.")
