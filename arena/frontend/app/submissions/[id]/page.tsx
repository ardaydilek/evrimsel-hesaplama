"use client";

import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { StatusBadge } from "@/components/status-badge";
import { SubmissionReplay } from "@/components/submission-replay";
import { TourMap } from "@/components/tour-map";
import { getProblem, getSubmission } from "@/lib/api";
import { hintForFailure } from "@/lib/failure-hints";
import type { Problem, Status, Submission } from "@/lib/types";

const TERMINAL = new Set<Status>(["scored", "failed"]);
const OPTIMAL = 699;

export default function SubmissionDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [sub, setSub] = useState<Submission | null>(null);
  const [problem, setProblem] = useState<Problem | null>(null);
  const [error, setError] = useState<string | null>(null);
  const timer = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => {
    let stopped = false;
    const stop = () => {
      if (timer.current) {
        clearInterval(timer.current);
        timer.current = null;
      }
    };
    const tick = async () => {
      try {
        const s = await getSubmission(id);
        if (stopped) return;
        setSub(s);
        if (TERMINAL.has(s.status)) stop();
      } catch (e: unknown) {
        if (stopped) return;
        setError(e instanceof Error ? e.message : String(e));
        stop();
      }
    };
    tick();
    timer.current = setInterval(tick, 1000);
    return () => {
      stopped = true;
      stop();
    };
  }, [id]);

  useEffect(() => {
    if (sub?.status === "scored" && sub.tour && !problem) {
      getProblem()
        .then(setProblem)
        .catch(() => {});
    }
  }, [sub, problem]);

  if (error) {
    return (
      <main className="mx-auto w-full max-w-3xl px-6 py-12">
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      </main>
    );
  }

  if (!sub) {
    return (
      <main className="mx-auto w-full max-w-3xl px-6 py-12">
        <div className="flex items-center gap-3 text-muted-foreground">
          <span
            className="size-2 animate-signal rounded-full bg-muted-foreground"
            aria-hidden
          />
          <p className="text-sm">Yükleniyor…</p>
        </div>
      </main>
    );
  }

  const gap = (sub.length ?? 0) - OPTIMAL;
  const running = sub.status === "queued" || sub.status === "running";
  const hint = sub.status === "failed" ? hintForFailure(sub.fail_reason) : null;

  return (
    <main className="mx-auto w-full max-w-3xl space-y-8 px-6 py-12">
      <Link
        href="/"
        className="inline-flex items-center gap-1.5 text-xs text-muted-foreground transition-colors hover:text-foreground"
      >
        <span aria-hidden>←</span> Lider Tablosu
      </Link>

      <header className="animate-rise space-y-3">
        <div className="flex flex-wrap items-center gap-3">
          <p className="eyebrow">Gönderim</p>
          <StatusBadge status={sub.status} />
        </div>
        <h1 className="text-4xl font-semibold tracking-tighter sm:text-5xl">
          {sub.handle}
        </h1>
        <p className="flex flex-wrap items-center gap-2 text-sm text-muted-foreground">
          <span className="text-foreground/80">{sub.id}</span>
          <span aria-hidden>·</span>
          <span className="inline-flex items-center rounded border border-border/70 bg-muted/50 px-1.5 py-0.5 text-xs">
            {sub.preset}
          </span>
        </p>
      </header>

      {sub.status === "failed" && sub.fail_reason && (
        <div className="animate-rise space-y-3">
          <Alert variant="destructive">
            <AlertDescription className="text-sm">
              {sub.fail_reason}
            </AlertDescription>
          </Alert>
          {hint && (
            <div className="rounded-lg border border-border/70 bg-muted/40 px-4 py-3.5 text-sm text-muted-foreground">
              <p>{hint}</p>
              <Link
                href="/submit"
                className="mt-2 inline-block text-foreground underline-offset-4 transition-colors hover:underline"
              >
                Şablon ve ipuçları →
              </Link>
            </div>
          )}
        </div>
      )}

      {running && (
        <div className="animate-rise flex items-center gap-3 rounded-lg border border-border/70 bg-card/60 px-4 py-3.5 shadow-sm">
          <span className="relative flex size-2.5 shrink-0" aria-hidden>
            <span className="absolute inline-flex size-full animate-ping rounded-full bg-sky-400 opacity-60" />
            <span className="relative inline-flex size-2.5 rounded-full bg-sky-500" />
          </span>
          <p className="text-sm text-muted-foreground">
            Çalışıyor… bu sayfa otomatik güncellenir.
          </p>
        </div>
      )}

      {sub.status === "scored" && (
        <Card className="animate-rise overflow-hidden">
          <CardHeader className="border-b pb-4">
            <CardTitle className="text-xs uppercase tracking-[0.14em] text-muted-foreground">
              Sonuç
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-6 pt-2">
            <dl className="grid grid-cols-3 divide-x divide-border/60">
              <Stat label="Uzunluk" value={sub.length} />
              <Stat
                label="Fark"
                value={gap === 0 ? "optimum" : `+${gap}`}
                accent={gap === 0}
              />
              <Stat label="Süre" value={`${sub.runtime_ms} ms`} />
            </dl>
            {problem && sub.tour && (
              sub.gen_log && sub.gen_log.length > 0 ? (
                <SubmissionReplay
                  genLog={sub.gen_log}
                  tour={sub.tour}
                  coordinates={problem.coordinates}
                  optimal={problem.optimal}
                />
              ) : (
                <div className="flex flex-col items-center gap-3">
                  <TourMap coordinates={problem.coordinates} tour={sub.tour} />
                  <p className="eyebrow self-start">
                    {problem.coordinates.length} şehir üzerinde kapalı tur
                  </p>
                </div>
              )
            )}
          </CardContent>
        </Card>
      )}
    </main>
  );
}

function Stat({
  label,
  value,
  accent,
}: {
  label: string;
  value: React.ReactNode;
  accent?: boolean;
}) {
  return (
    <div className="px-4 first:pl-0 last:pr-0">
      <dt className="text-[11px] uppercase tracking-[0.12em] text-muted-foreground">
        {label}
      </dt>
      <dd
        className={
          "mt-1 text-2xl tabular-nums " +
          (accent ? "text-primary" : "text-foreground")
        }
      >
        {value}
      </dd>
    </div>
  );
}
