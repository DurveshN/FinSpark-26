"""Generate the Business Case PDF - who buys, why, integrate, scale, maintain, fit.
Run: python -m docs.pdfgen.gen_business
"""
from __future__ import annotations
import os
from docs.pdfgen.pdfkit import Doc, ACCENT, WARN, OK

OUT = os.path.join(os.path.dirname(__file__), "..", "QTD-HGNN_Business_Case.pdf")


def build() -> Doc:
    d = Doc("QTD-HGNN - Business Case",
            "Where it fits, why banks buy, how they integrate, scale & maintain")
    d.cover()

    d.h1("1. The problem worth money")
    d.para("Banks run 10-15 siloed security tools (EDR, SIEM, IAM, fraud engines) that do not "
           "talk to each other. The security team watches logins; the fraud team watches payments. "
           "An account takeover - a hostile login followed 90 seconds later by a large transfer to "
           "a new payee - is invisible to each team alone. That seam is where losses happen.")
    d.table(["Signal (all [Unverified] - from public reporting)", "Figure"],
            [["Bank frauds, FY25 (India) vs prior year", "~3x increase"],
             ["UPI fraud cases, FY25", "~85% rise (13.4 lakh cases)"],
             ["Mule accounts identified (India)", "~5.24 lakh"],
             ["False-positive rate in current SOCs", "90%+ (alert fatigue)"],
             ["Mean time to detect a breach (some sectors)", "~200 days"]],
            [124, 50])
    d.callout("Why now",
              "RBI is actively pushing MuleHunter.AI and a 'zero fraud' target; the RBI Q-SAFE "
              "committee (2026) mandates a cryptographic inventory + PQC migration roadmap; fraud "
              "is at record highs. Adopting now is compliance, not a nice-to-have.")

    d.h1("2. What we sell - and why they buy")
    d.para("An AI correlation + threat-intelligence OVERLAY that fuses cyber telemetry with "
           "transaction behaviour, catches what siloed tools miss, cuts false positives through "
           "cross-domain corroboration, and explains every alert for auditors.")
    d.h2("The buying levers, in the order a CISO cares")
    d.bullet("It helps meet obligations the bank must meet anyway - RBI Fraud Risk Management "
             "Master Direction (2024) mandates data-analytics Early Warning Signals + real-time "
             "transaction monitoring; RBI Q-SAFE mandates a crypto inventory. We are a ready-made "
             "way to satisfy both. Selling compliance is easier than selling technology.", "1. Regulation")
    d.bullet("Attacks a bleeding-money problem - even a small reduction in fraud loss or in analyst "
             "hours wasted on false positives is a hard ROI number.", "2. Loss reduction")
    d.bullet("Fewer, higher-confidence alerts cut SOC operating cost and analyst burnout.", "3. Efficiency")
    return d


if __name__ == "__main__":
    doc = build()
    from docs.pdfgen.gen_business_2 import add_deploy_scale_sections
    add_deploy_scale_sections(doc)
    doc.output(os.path.abspath(OUT))
    print("wrote", os.path.abspath(OUT))
