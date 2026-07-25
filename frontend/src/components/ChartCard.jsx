// Reusable titled card wrapper for chart/content panels.
import { Card } from "@/components/ui/card";

export default function ChartCard({ title, badge, right, children, className = "" }) {
  return (
    <Card className={`border-border/60 bg-card/60 p-5 backdrop-blur ${className}`}>
      <div className="mb-3 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <h3 className="text-sm font-semibold text-foreground">{title}</h3>
          {badge}
        </div>
        {right && <span className="text-sm font-semibold tabular-nums text-muted-foreground">{right}</span>}
      </div>
      {children}
    </Card>
  );
}
