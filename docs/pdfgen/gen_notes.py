"""Generate the Technical Notes PDF - what data, every field, storage, meaning.
Run: python -m docs.pdfgen.gen_notes
"""
from __future__ import annotations
import os
from docs.pdfgen.pdfkit import Doc, ACCENT, WARN, OK

OUT = os.path.join(os.path.dirname(__file__), "..", "QTD-HGNN_Technical_Notes.pdf")


def build() -> Doc:
    d = Doc("QTD-HGNN - Technical Notes",
            "Every data field, what it means, how it is stored, and how the system works")
    d.cover()

    # 1. overview
    d.h1("1. What the system is")
    d.para("QTD-HGNN correlates cybersecurity telemetry (logins, devices, IPs, TLS posture) with "
           "transactional behaviour (payments, payees, channels) to detect account takeover, mule "
           "rings, and quantum-risk indicators - with explainable, auditable alerts. Every number "
           "shown is computed by a trained model and a real pipeline; nothing is simulated.")
    d.para("Core thesis: a suspicious login and a large transfer to a new payee are each unalarming "
           "alone, but together = account takeover. The SIEM sees the first, the fraud engine sees "
           "the second, neither sees the attack. We fuse both domains in one model.")

    d.h1("2. The six PS2 outcomes -> what delivers each")
    d.table(["Expected outcome", "What delivers it"],
            [["Correlate cyber + transaction", "Heterogeneous graph fuses login/device/TLS with payment features per customer"],
             ["Detect threats proactively", "Trained GraphSAGE scores each transaction; ATO kill-chains surface in real time"],
             ["Identify fraud patterns", "Same-customer/same-payee graph edges + persistent-homology (Betti) structure"],
             ["Quantum-related indicators", "Crypto-posture: quantum-vulnerable TLS %, downgrade events (honest, observable)"],
             ["Reduce false positives", "Cross-domain corroboration + tuned decision threshold (precision 0.71 @ recall 0.98)"],
             ["Explainable AI", "Per-alert SHAP reason codes (auditable, RBI/DPDP-aligned)"]],
            [52, 122])

    d.h1("3. Architecture - 5-stage pipeline")
    d.code("Ingest        Fuse              Detect          Explain      Act\n"
           "cyber+txn --> graph+topology --> GraphSAGE  --> SHAP     --> SOC dashboard\n"
           "(logins,      (Ripser Betti     (16 fused      (subgraph    (alerts, threat\n"
           " payments)     b0/b1/b2)         features)      reason        score, quantum,\n"
           "                                                codes)        model insights)")
    d.bullet("ml/  - synthetic data generator, feature engineering + persistent homology, GNN "
             "training + evaluation, build-time pre-scoring.", "Layers")
    d.bullet("backend/  - FastAPI + SQLAlchemy/Alembic; loads the trained model, serves REST + a "
             "WebSocket telemetry stream, persists auditable alerts.")
    d.bullet("frontend/  - React/Vite SOC dashboard (Tailwind + shadcn), bound entirely to the "
             "live backend.")

    # 4. data model
    d.h1("4. Input data - the synthetic bank")
    d.para("No public dataset contains BOTH cyber telemetry and transactions for the SAME entities "
           "with labels (confirmed - production SOC+payment data cannot be released for privacy). "
           "The defensible standard approach: generate one shared customer population, attach both "
           "domains, and inject labelled attack scenarios. Scale: ~6,000 customers, 559,661 "
           "transactions, 445,158 logins over a 45-day window. The ingestion format is designed to "
           "swap in real bank feeds unchanged.")

    d.h2("4.1 Entities (static population)")
    d.table(["Table / field", "Meaning"],
            [["customers.customer_id", "Unique customer id (C000000...)"],
             ["customers.home_city", "Home city id (0-39) - baseline geo"],
             ["customers.login_rate / txn_rate", "Per-customer mean logins & transactions per day (behaviour baseline)"],
             ["customers.amount_mu / amount_sigma", "Lognormal params for this customer's normal transaction amount"],
             ["accounts.account_id", "Primary account per customer (A000000...)"],
             ["accounts.opened_day", "Day account opened (relative to sim window)"],
             ["devices.device_id / usual_city", "Known device per customer + its usual city"],
             ["payees.payee_id / risk_flag", "Beneficiary id; ~3% pre-flagged risky"]],
            [56, 118])

    d.h2("4.2 Cyber telemetry - login events")
    d.table(["Field", "Meaning"],
            [["login_id, customer_id", "Event id + owning customer"],
             ["t_day, hour", "Timestamp (fractional day) and hour-of-day"],
             ["device_id, city", "Device used and its city"],
             ["new_device", "1 if device never seen for this customer (ATO signal)"],
             ["failed_prior", "Failed login attempts before this success (credential stuffing signal)"],
             ["tls", "Negotiated TLS/cipher, e.g. TLS1.3:X25519MLKEM768 (strong) or TLS1.0:RSA-EXPORT (weak)"],
             ["label, scenario", "Ground truth: benign/malicious + scenario tag"]],
            [40, 134])
    return d


if __name__ == "__main__":
    doc = build()
    from docs.pdfgen.gen_notes_2 import add_rest
    add_rest(doc)
    doc.output(os.path.abspath(OUT))
    print("wrote", os.path.abspath(OUT))
