"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { LeaderboardTable } from "@/components/leaderboard-table";
import { buttonVariants } from "@/components/ui/button";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { getLeaderboard } from "@/lib/api";
import { cn } from "@/lib/utils";
import type { LeaderboardRow } from "@/lib/types";

const OPTIMAL = 699;

export default function LeaderboardPage() {
  const [rows, setRows] = useState<LeaderboardRow[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getLeaderboard()
      .then(setRows)
      .catch((e) => setError(String(e?.message ?? e)));
  }, []);

  const scored = rows?.length ?? 0;

  return (
    <main className="mx-auto w-full max-w-5xl space-y-10 px-6 py-12">
      <header className="animate-rise flex flex-col gap-6 sm:flex-row sm:items-end sm:justify-between">
        <div className="space-y-3">
          <p className="eyebrow">Genel Sıralama</p>
          <h1 className="text-balance text-4xl font-semibold tracking-tighter sm:text-5xl">
            Lider Tablosu
          </h1>
          <p className="max-w-xl text-pretty text-muted-foreground">
            Her çözüm aynı{" "}
            <span className="font-medium text-foreground">42 şehirlik</span>{" "}
            problemde izole çalışır; tur uzunluğuna, sonra süreye göre sıralanır.
            Bilinen optimum{" "}
            <span className="font-medium text-foreground">{OPTIMAL}</span>.
          </p>
        </div>
        <Link
          href="/submit"
          className={cn(buttonVariants({ size: "lg" }), "shrink-0 shadow-sm")}
        >
          Çözüm Gönder
        </Link>
      </header>

      <section
        className="animate-rise rounded-xl border border-border/70 bg-card/60 shadow-sm backdrop-blur-sm"
        style={{ animationDelay: "80ms" }}
      >
        <div className="flex items-center justify-between gap-4 border-b border-border/70 px-5 py-3.5">
          <div className="flex items-center gap-2.5">
            <span className="size-1.5 rounded-full bg-primary" aria-hidden />
            <h2 className="text-xs font-medium uppercase tracking-[0.14em] text-foreground">
              Sıralama
            </h2>
          </div>
          {rows && scored > 0 && (
            <p className="text-xs tabular-nums text-muted-foreground">
              <span className="text-foreground">{scored}</span> puanlı
            </p>
          )}
        </div>
        <div className="p-1.5 sm:p-2">
          {error && (
            <div className="p-3">
              <Alert variant="destructive">
                <AlertDescription>Yüklenemedi: {error}</AlertDescription>
              </Alert>
            </div>
          )}
          {!rows && !error && <LeaderboardSkeleton />}
          {rows && <LeaderboardTable rows={rows} />}
        </div>
      </section>
    </main>
  );
}

function LeaderboardSkeleton() {
  return (
    <div className="space-y-1 p-2" aria-hidden>
      {/* Visible "Yükleniyor…" preserves the asserted text + gives a label. */}
      <p className="px-2 pb-2 text-xs text-muted-foreground">
        Yükleniyor…
      </p>
      {Array.from({ length: 5 }).map((_, i) => (
        <div
          key={i}
          className="flex items-center gap-4 rounded-md px-2 py-2.5"
          style={{ opacity: 1 - i * 0.14 }}
        >
          <div className="h-4 w-6 animate-pulse rounded bg-muted" />
          <div className="h-4 flex-1 animate-pulse rounded bg-muted" />
          <div className="h-4 w-16 animate-pulse rounded bg-muted" />
          <div className="h-4 w-12 animate-pulse rounded bg-muted" />
        </div>
      ))}
    </div>
  );
}
