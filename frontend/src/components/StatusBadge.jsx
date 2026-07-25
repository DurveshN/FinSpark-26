// Live WebSocket connection indicator.
import { cn } from "@/lib/utils";

export default function StatusBadge({ connected }) {
  return (
    <div className={cn(
      "inline-flex items-center gap-2 rounded-full border px-3 py-1 text-xs font-medium",
      connected ? "border-emerald-500/30 bg-emerald-500/10 text-emerald-400"
                : "border-amber-500/30 bg-amber-500/10 text-amber-400"
    )}>
      <span className={cn("relative flex h-2 w-2")}>
        {connected && <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-75" />}
        <span className={cn("relative inline-flex h-2 w-2 rounded-full", connected ? "bg-emerald-400" : "bg-amber-400")} />
      </span>
      {connected ? "Live · connected" : "Reconnecting…"}
    </div>
  );
}
