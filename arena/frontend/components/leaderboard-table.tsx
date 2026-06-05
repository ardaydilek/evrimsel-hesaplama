import Link from "next/link";
import {
  Table, TableBody, TableCell, TableHead, TableHeader, TableRow,
} from "@/components/ui/table";
import { cn } from "@/lib/utils";
import type { LeaderboardRow } from "@/lib/types";

const RANK_ACCENT: Record<number, string> = {
  1: "text-primary",
  2: "text-foreground",
  3: "text-muted-foreground",
};

export function LeaderboardTable({ rows }: { rows: LeaderboardRow[] }) {
  if (rows.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center gap-4 px-6 py-16 text-center">
        <div
          aria-hidden
          className="grid size-12 place-items-center rounded-full border border-dashed border-border text-muted-foreground"
        >
          <svg
            viewBox="0 0 24 24"
            className="size-5"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.6"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <path d="M4 19V5M4 19h16M8 19v-6M12 19v-9M16 19v-4" />
          </svg>
        </div>
        <p className="text-muted-foreground">Henüz puanlanmış çözüm yok.</p>
        <p className="max-w-xs text-sm text-muted-foreground/70">
          İlk sırayı sen kap — bir çözüm gönder ve çalışmasını izle.
        </p>
      </div>
    );
  }
  return (
    <Table>
      <TableHeader>
        <TableRow className="border-border/60 hover:bg-transparent">
          <TableHead className="w-12 pl-4 text-[11px] uppercase tracking-[0.12em]">
            #
          </TableHead>
          <TableHead className="text-[11px] uppercase tracking-[0.12em]">
            Takma ad
          </TableHead>
          <TableHead className="text-[11px] uppercase tracking-[0.12em]">
            Dil
          </TableHead>
          <TableHead className="text-right text-[11px] uppercase tracking-[0.12em]">
            Uzunluk
          </TableHead>
          <TableHead className="text-right text-[11px] uppercase tracking-[0.12em]">
            Fark
          </TableHead>
          <TableHead className="pr-4 text-right text-[11px] uppercase tracking-[0.12em]">
            Süre
          </TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {rows.map((r, i) => {
          const rank = i + 1;
          const optimal = r.gap === 0;
          return (
            <TableRow
              key={r.id}
              className={cn(
                "group border-border/50 transition-colors",
                rank === 1 && "bg-primary/[0.04]",
              )}
            >
              <TableCell className="pl-4">
                <span
                  className={cn(
                    "text-sm font-semibold tabular-nums",
                    RANK_ACCENT[rank] ?? "text-muted-foreground",
                  )}
                >
                  {rank}
                </span>
              </TableCell>
              <TableCell>
                <Link
                  href={`/submissions/${r.id}`}
                  className="font-medium decoration-primary/40 underline-offset-4 transition-colors hover:text-primary hover:underline"
                >
                  {r.handle}
                </Link>
              </TableCell>
              <TableCell>
                <span className="inline-flex items-center rounded border border-border/70 bg-muted/50 px-1.5 py-0.5 text-xs text-muted-foreground">
                  {r.preset}
                </span>
              </TableCell>
              <TableCell className="text-right text-sm tabular-nums">
                {r.length}
              </TableCell>
              <TableCell className="text-right text-sm tabular-nums">
                {optimal ? (
                  <span className="inline-flex items-center gap-1 font-medium text-primary">
                    <span className="size-1.5 rounded-full bg-primary" aria-hidden />
                    optimum
                  </span>
                ) : (
                  <span className="text-muted-foreground">{`+${r.gap}`}</span>
                )}
              </TableCell>
              <TableCell className="pr-4 text-right text-sm tabular-nums text-muted-foreground">
                {r.runtime_ms} ms
              </TableCell>
            </TableRow>
          );
        })}
      </TableBody>
    </Table>
  );
}
