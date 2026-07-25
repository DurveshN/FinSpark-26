// KPI stat card for the dashboard header row. Presentational; live values passed in.
import { Card } from "@/components/ui/card";
import { cn } from "@/lib/utils";

export default function KpiCard({ label, value, subtitle, accent = "text-foreground", icon: Icon }) {
  return (
    <Card className="relative overflow-hidden border-border/60 bg-card/60 p-5 backdrop-blur">
      <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-primary/40 to-transparent" />
      <div className="flex items-start justify-between">
        <div className="space-y-1">
          <p className="text-[11px] font-medium uppercase tracking-wider text-muted-foreground">{label}</p>
          <p className={cn("text-3xl font-semibold tabular-nums leading-none", accent)}>{value}</p>
          {subtitle && <p className="text-xs text-muted-foreground">{subtitle}</p>}
        </div>
        {Icon && (
          <div className="rounded-lg bg-primary/10 p-2 text-primary">
            <Icon className="h-4 w-4" />
          </div>
        )}
      </div>
    </Card>
  );
}
