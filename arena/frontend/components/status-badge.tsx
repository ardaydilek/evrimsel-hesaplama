import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import type { Status } from "@/lib/types";

type Variant = { label: string; className: string; dot: string; pulse?: boolean };

const VARIANT: Record<Status, Variant> = {
  queued: {
    label: "Sırada",
    className:
      "border-border bg-muted text-muted-foreground hover:bg-muted",
    dot: "bg-muted-foreground/60",
  },
  running: {
    label: "Çalışıyor",
    className:
      "border-sky-500/30 bg-sky-500/10 text-sky-700 hover:bg-sky-500/10 dark:text-sky-300",
    dot: "bg-sky-500",
    pulse: true,
  },
  scored: {
    label: "Puanlandı",
    className:
      "border-primary/30 bg-primary/10 text-primary hover:bg-primary/10",
    dot: "bg-primary",
  },
  failed: {
    label: "Başarısız",
    className:
      "border-destructive/30 bg-destructive/10 text-destructive hover:bg-destructive/10",
    dot: "bg-destructive",
  },
};

export function StatusBadge({ status }: { status: Status }) {
  const v = VARIANT[status];
  return (
    <Badge
      className={cn(
        "h-6 gap-1.5 rounded-full border px-2.5 text-[11px] font-medium uppercase tracking-[0.1em]",
        v.className,
      )}
      data-testid="status-badge"
    >
      <span
        aria-hidden
        className={cn("size-1.5 rounded-full", v.dot, v.pulse && "animate-signal")}
      />
      {v.label}
    </Badge>
  );
}
