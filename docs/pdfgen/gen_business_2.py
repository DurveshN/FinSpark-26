"""Business Case PDF - part 2: deployment, integration, scale, maintenance, commercial."""
from __future__ import annotations
from docs.pdfgen.pdfkit import Doc, ACCENT, WARN, OK


def add_deploy_scale_sections(d: Doc) -> None:
    d.h1("3. Where it runs & where data lives")
    d.para("This is the question that decides viability for an Indian bank, so we answer it head-on.")
    d.bullet("It deploys INSIDE the bank's own cloud tenant (Azure, India region) - not our SaaS. "
             "Raw transaction data and PII never leave the bank's security boundary. This is "
             "mandatory under RBI data-localization + DPDP Act 2023, and it is the single most "
             "important architectural decision - driven by law, not preference.", "Data residency")
    d.bullet("Containerised (Docker -> Azure Kubernetes / Container Apps), deployed via an "
             "infrastructure-as-code template into the bank's subscription. Storage uses the bank's "
             "own database; compute is the bank's own cluster.", "Delivery")
    d.bullet("The vendor receives zero raw data. Cloud-prem / BYOC: vendor-managed control plane, "
             "data plane in the bank's VPC. Air-gapped installs for the most locked-down banks.", "Isolation")
    d.callout("Reference: this exact product",
              "Backend runs on Azure Container Apps in one resource group (ACR + app + Postgres/SQLite). "
              "Frontend on Vercel. CI/CD via GitHub Actions. Live, deployed, and streaming real model "
              "output today - the deployment model is proven, not hypothetical.")

    d.h1("4. How it integrates (be a good citizen, not a rip-and-replace)")
    d.para("The product sits ON TOP of what the bank already owns and ingests from it.")
    d.table(["Integration point", "Mechanism"],
            [["Network telemetry", "Passive TAP / SPAN mirror port -> Zeek/Suricata sensors (out-of-band, nothing to break)"],
             ["TLS / crypto posture", "JA3/JA4 fingerprinting on ClientHello - flags weak/quantum-vulnerable ciphers WITHOUT decryption"],
             ["SIEM", "Ingest + push-back via syslog/CEF, Kafka, REST to Splunk / QRadar / Microsoft Sentinel"],
             ["Core banking / payments", "Feed from Finacle, payment switch, IAM via syslog / Kafka / DB export"],
             ["Response", "Fire SOAR playbooks (webhook/REST); alerts appear in the existing SOC queue"],
             ["Threat intel", "STIX 2.1 over TAXII 2.1 in/out"]],
            [42, 132])
    d.para("What makes it 'easy to integrate' for a buyer: prebuilt SIEM connectors, open schemas, "
           "TAXII in/out, and no requirement to reroute production traffic.")

    d.h1("5. How it scales")
    d.bullet("The trained model is small and CPU-only (no GPU cluster). Inference is milliseconds; "
             "the heavy work is pre-computed offline at build time.", "Per-node")
    d.bullet("Each bank runs its own isolated instance (per-tenant). You scale operationally by "
             "adding tenants, never by centralising anyone's data.", "Per-bank")
    d.bullet("Banks opt into a federated threat-intelligence exchange: only ANONYMISED attack "
             "fingerprints are shared (mule-ring hashes, ATO patterns) - never customer data. Each "
             "new bank makes every bank's detection better. This is the network-effect moat, and it "
             "mirrors the real I4C Suspect Registry model (share indicators, not data).", "Cross-bank")
    d.callout("Honest scope note", "Federated learning across banks is on the roadmap (research-grade "
              "today). Shipping now: per-tenant deployment + IOC/TAXII indicator sharing, which is "
              "proven production practice.", tone=WARN)

    d.h1("6. How it is operated & maintained")
    d.bullet("Slots into the bank's mandated 24x7 SOC: L1 analysts triage the alert queue, escalate "
             "to L2/L3 as cases, drive response via SOAR.", "Day-to-day")
    d.bullet("Model retraining, drift monitoring, and false-positive tuning - run on the bank's own "
             "data on a schedule; jointly owned by the SOC and vendor support.", "MLOps")
    d.bullet("Push-to-deploy CI/CD; model weights hot-swappable; migrations automated. Explainable "
             "outputs give a permanent audit trail (every alert decomposes into SHAP reason codes).", "Upkeep")

    d.h1("7. Where it fits & the market")
    d.bullet("An intelligence overlay between the SOC (security) and the fraud/EFRMS engine - the "
             "seam neither currently owns. It does not replace Splunk, QRadar, or the fraud engine.", "Fit")
    d.bullet("RBI-regulated banks (public & private), co-operative banks and RRBs (underserved by "
             "enterprise vendors), SWIFT participants, insurance, capital markets - anyone facing "
             "the fraud + quantum-risk mandate.", "Market")
    d.h2("Adoption path")
    d.para("Phase 1 (M1-3): pilot in a single SOC, passive TAP/SPAN PoC.  Phase 2 (M4-6): SIEM "
           "connector + fraud-feed integration.  Phase 3 (M7-9): multi-branch rollout.  "
           "Phase 4 (M10-12): full production + PQC-posture monitoring.")

    d.h1("8. Commercial model")
    d.bullet("Annual license per deployment, tiered by transaction volume / branch count.", "Core")
    d.bullet("Q-SAFE crypto-inventory + audit-reporting module as a separate SKU (maps to a deadline "
             "-> high margin).", "Compliance add-on")
    d.bullet("Federated-intelligence subscription - recurring, and the moat.", "Network")
    d.bullet("Expansion: SWIFT participants, insurance, capital markets, and export to other "
             "emerging-market regulators with similar data-residency laws.", "Growth")
    d.callout("The one-line pitch",
              "The only layer that sees the crypto-vulnerability of a data movement AND its "
              "transactional context in one place - answering 'was this bulk KYC export protected by "
              "quantum-breakable crypto, and did it have any legitimate business reason?' Neither the "
              "bank's EFRMS, nor its SIEM, nor a generic crypto tool can ask that question.", tone=OK)

    d.h1("9. Honesty & compliance posture")
    d.para("Every dashboard number is computed by the trained model, not simulated. The quantum "
           "module reports real cryptographic posture and observable HNDL indicators; it does not "
           "claim to detect passive interception, which is physically undetectable - the mitigation "
           "is PQC migration. Data is synthetic today, with an ingestion format designed to swap in "
           "real bank feeds. This honesty is a selling point: it survives technical due diligence and "
           "satisfies RBI/DPDP/EU-AI-Act transparency expectations.")
