// SHAP explanation panel: REAL per-feature Shapley attributions for a selected alert
// (computed on-demand by the backend). Positive -> malicious, negative -> benign.
import { Badge } from "@/components/ui/badge";

const LABEL = {
  amount_zscore: "Amount vs customer normal", log_amount: "Transaction size",
  new_payee: "New payee added", sec_since_login: "Time since login",
  sec_since_payee_add: "Payee age", is_swift: "SWIFT channel", is_imps: "IMPS channel",
  login_new_device: "Login from new device", login_failed_prior: "Prior failed logins",
  login_odd_hour: "Odd-hour login", tls_quantum_vulnerable: "Quantum-vulnerable TLS",
  tls_weak_downgrade: "Weak / downgraded cipher", geo_mismatch: "Geo mismatch",
  cust_betti0: "Topology · components (β₀)", cust_betti1: "Topology · loops (β₁)",
  cust_betti2: "Topology · voids (β₂)",
};

export default function XaiWaterfall({ alert }) {
  if (!alert) {
    return (
      <div className="flex h-[340px] flex-col items-center justify-center rounded-lg border border-dashed border-border/50 text-center">
        <p className="text-sm text-muted-foreground">Select an alert to see its SHAP explanation.</p>
        <p className="mt-1 text-xs text-muted-foreground/70">Per-feature Shapley attributions, computed on the model.</p>
      </div>
    );
  }
  const codes = alert.reason_codes;
  const maxAbs = codes && codes.length ? Math.max(1e-6, ...codes.map((c) => Math.abs(c.shap_value))) : 1;
  return (
    <div className="flex h-[340px] flex-col">
      <div className="mb-3 flex items-center justify-between">
        <div>
          <p className="text-sm font-semibold text-foreground">Why flagged · <span className="font-mono text-xs">{alert.txn_id}</span></p>
          <p className="text-xs text-muted-foreground">₹{Number(alert.amount).toLocaleString("en-IN")}</p>
        </div>
        <Badge className="bg-primary/15 text-primary border-primary/30">{(alert.prob * 100).toFixed(0)}% confidence</Badge>
      </div>
      <div className="flex-1 space-y-2.5 overflow-y-auto pr-1">
        {!codes && <p className="py-6 text-center text-sm text-muted-foreground">Computing SHAP…</p>}
        {codes && codes.length === 0 && <p className="py-6 text-center text-sm text-muted-foreground">No attributions.</p>}
        {codes && codes.map((c) => {
          const pct = (Math.abs(c.shap_value) / maxAbs) * 100;
          const pos = c.shap_value >= 0;
          return (
            <div key={c.feature}>
              <div className="mb-1 flex items-center justify-between text-xs">
                <span className="text-foreground/90">{LABEL[c.feature] || c.feature}</span>
                <span className={pos ? "font-semibold text-red-400" : "font-semibold text-emerald-400"}>
                  {pos ? "+" : ""}{c.shap_value.toFixed(3)}
                </span>
              </div>
              <div className="h-2 overflow-hidden rounded-full bg-muted">
                <div className={pos ? "h-full rounded-full bg-red-500" : "h-full rounded-full bg-emerald-500"} style={{ width: `${pct}%` }} />
              </div>
            </div>
          );
        })}
      </div>
      <p className="mt-3 border-t border-border/50 pt-2 text-[11px] text-muted-foreground">
        Computed Shapley values — auditable per RBI fraud-risk & DPDP.
      </p>
    </div>
  );
}
