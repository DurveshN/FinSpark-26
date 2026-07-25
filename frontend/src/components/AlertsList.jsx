// Live alert queue. Each item is a real flagged transaction; click selects it for XAI.
import { ScrollArea } from "@/components/ui/scroll-area";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

const SCENARIO = {
  account_takeover: { label: "Account Takeover", tone: "bg-red-500/15 text-red-400 border-red-500/30" },
  mule_ring: { label: "Mule Ring", tone: "bg-amber-500/15 text-amber-400 border-amber-500/30" },
  hndl_indicator: { label: "HNDL Indicator", tone: "bg-fuchsia-500/15 text-fuchsia-400 border-fuchsia-500/30" },
  benign_anomaly: { label: "Benign Anomaly", tone: "bg-emerald-500/15 text-emerald-400 border-emerald-500/30" },
  normal: { label: "Anomaly", tone: "bg-slate-500/15 text-slate-300 border-slate-500/30" },
};

export default function AlertsList({ alerts, selected, onSelect }) {
  return (
    <ScrollArea className="h-[340px] pr-3">
      <div className="space-y-2">
        {alerts.length === 0 && (
          <p className="px-1 py-6 text-center text-sm text-muted-foreground">No active threats in current window.</p>
        )}
        {alerts.map((a) => {
          const s = SCENARIO[a.scenario] || SCENARIO.normal;
          const sev = a.prob >= 0.9 ? "bg-red-500" : a.prob >= 0.7 ? "bg-amber-500" : "bg-emerald-500";
          const isSel = selected && selected.txn_id === a.txn_id;
          return (
            <button
              key={a.txn_id}
              onClick={() => onSelect(a)}
              className={cn(
                "flex w-full items-center gap-3 rounded-lg border p-3 text-left transition-colors",
                isSel ? "border-primary/60 bg-primary/10" : "border-border/50 bg-card/40 hover:bg-accent/40"
              )}>
              <span className={cn("h-2 w-2 shrink-0 rounded-full", sev)} />
              <div className="min-w-0 flex-1">
                <div className="flex items-center gap-2">
                  <Badge variant="outline" className={cn("text-[10px]", s.tone)}>{s.label}</Badge>
                  <span className="truncate font-mono text-xs text-muted-foreground">{a.txn_id}</span>
                </div>
                <p className="mt-1 text-sm text-foreground">
                  ₹{Number(a.amount).toLocaleString("en-IN")}
                  <span className="ml-2 text-xs text-muted-foreground">{(a.prob * 100).toFixed(0)}% confidence</span>
                </p>
              </div>
            </button>
          );
        })}
      </div>
    </ScrollArea>
  );
}
