"use client";

import { useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Alert, AlertDescription } from "@/components/ui/alert";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  MultiFileEditor,
  filesToMap,
  type FileEntry,
} from "@/components/multi-file-editor";
import { SubmissionHelperDialog } from "@/components/submission-helper-dialog";
import { TEMPLATES } from "@/lib/solver-templates";
import { createSubmission, getPresets } from "@/lib/api";
import type { Preset } from "@/lib/types";

export default function SubmitPage() {
  const router = useRouter();
  const [presets, setPresets] = useState<Preset[]>([]);
  const [preset, setPreset] = useState("");
  const [handle, setHandle] = useState("");
  const [files, setFiles] = useState<FileEntry[]>(TEMPLATES.python);
  const [buildCmd, setBuildCmd] = useState("");
  const [runCmd, setRunCmd] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    getPresets()
      .then((ps) => {
        setPresets(ps);
        setPreset((cur) => cur || ps[0]?.name || "");
      })
      .catch((e) => setError(String(e?.message ?? e)));
  }, []);

  const selected = presets.find((p) => p.name === preset);

  // Base UI's <Select.Value> renders the label of the selected item when the
  // Root is given an `items` map (name -> label). We mirror the preset names.
  const items = useMemo(
    () => Object.fromEntries(presets.map((p) => [p.name, p.name])),
    [presets],
  );

  function onPresetChange(value: string) {
    setPreset(value);
    const template = TEMPLATES[value];
    if (template) setFiles(template);
  }

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    const map = filesToMap(files);
    if (!handle.trim()) {
      setError("Takma ad gerekli.");
      return;
    }
    if (!preset) {
      setError("Bir dil seç.");
      return;
    }
    if (Object.keys(map).length === 0) {
      setError("En az bir dosya (yol ile birlikte) gerekli.");
      return;
    }
    setSubmitting(true);
    try {
      const { id } = await createSubmission({
        handle: handle.trim(),
        preset,
        files: map,
        build_cmd: buildCmd.trim() || null,
        run_cmd: runCmd.trim() || null,
      });
      router.push(`/submissions/${id}`);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : String(err));
      setSubmitting(false);
    }
  }

  return (
    <main className="mx-auto w-full max-w-3xl space-y-10 px-6 py-12">
      <header className="animate-rise space-y-3">
        <p className="eyebrow">Yeni Gönderim</p>
        <h1 className="text-balance text-4xl font-semibold tracking-tighter sm:text-5xl">
          Çözüm Gönder
        </h1>
        <p className="max-w-xl text-pretty text-muted-foreground">
          Bir çalışma ortamı seç, dosyalarını ekle; biz de izole bir sandbox
          içinde derleyip çalıştırarak 42 şehirlik problemde puanlayalım.
        </p>
      </header>

      {error && (
        <Alert variant="destructive" className="animate-rise">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      <form
        onSubmit={onSubmit}
        className="animate-rise space-y-8"
        style={{ animationDelay: "80ms" }}
      >
        <Section
          step="01"
          title="Kimlik & ortam"
          hint="Tabloda nasıl görüneceğin ve hangi ortamın kullanılacağı."
        >
          <div className="grid gap-5 sm:grid-cols-2">
            <Field>
              <Label htmlFor="handle">Takma ad</Label>
              <Input
                id="handle"
                value={handle}
                onChange={(e) => setHandle(e.target.value)}
                placeholder="adın"
                autoComplete="off"
              />
            </Field>
            <Field>
              <Label htmlFor="preset">Dil</Label>
              <Select
                items={items}
                value={preset}
                onValueChange={(value) => onPresetChange(value as string)}
              >
                <SelectTrigger id="preset" className="w-full">
                  <SelectValue placeholder="Bir dil seç" />
                </SelectTrigger>
                <SelectContent>
                  {presets.map((p) => (
                    <SelectItem key={p.name} value={p.name}>
                      {p.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </Field>
          </div>
        </Section>

        <Section
          step="02"
          title="Kaynak dosyalar"
          hint="Sekmelerle birden çok dosya; sürükle-bırak da destekleniyor. Çözümün “TOUR 1 2 3 …” gibi bir satır yazdırmalı."
        >
          <div className="flex justify-end">
            <SubmissionHelperDialog preset={preset} onLoadTemplate={setFiles} />
          </div>
          <MultiFileEditor files={files} onChange={setFiles} />
          <p className="text-xs text-muted-foreground">
            Problem verisi çalışma klasörüne otomatik eklenir:{" "}
            <code className="rounded bg-muted px-1 py-0.5 font-mono text-[11px]">
              cityData.txt
            </code>{" "}
            ve{" "}
            <code className="rounded bg-muted px-1 py-0.5 font-mono text-[11px]">
              intercityDistance.txt
            </code>
            . İstersen okuyabilir ya da yok sayabilirsin.
          </p>
        </Section>

        <Section
          step="03"
          title="Komutlar"
          hint="İsteğe bağlı — boş bırakırsan ön tanımlı değerler kullanılır."
        >
          <div className="grid gap-5 sm:grid-cols-2">
            <Field>
              <Label htmlFor="build">Derleme komutu (isteğe bağlı)</Label>
              <Input
                id="build"
                className="text-sm"
                value={buildCmd}
                onChange={(e) => setBuildCmd(e.target.value)}
                placeholder={selected?.default_build_cmd ?? "(yok)"}
              />
            </Field>
            <Field>
              <Label htmlFor="run">Çalıştırma komutu (isteğe bağlı)</Label>
              <Input
                id="run"
                className="text-sm"
                value={runCmd}
                onChange={(e) => setRunCmd(e.target.value)}
                placeholder={selected?.default_run_cmd ?? ""}
              />
            </Field>
          </div>
        </Section>

        <div className="flex items-center gap-4 border-t border-border/60 pt-6">
          <Button type="submit" size="lg" disabled={submitting} className="shadow-sm">
            {submitting ? "Gönderiliyor…" : "Gönder"}
          </Button>
          <p className="text-xs text-muted-foreground">
            İzole çalışır · tur uzunluğuna göre puanlanır
          </p>
        </div>
      </form>
    </main>
  );
}

function Field({ children }: { children: React.ReactNode }) {
  return <div className="space-y-2">{children}</div>;
}

function Section({
  step,
  title,
  hint,
  children,
}: {
  step: string;
  title: string;
  hint: string;
  children: React.ReactNode;
}) {
  return (
    <section className="grid gap-5 sm:grid-cols-[auto_1fr] sm:gap-8">
      <div className="flex items-center gap-3 sm:flex-col sm:items-end sm:gap-1 sm:pt-1 sm:text-right">
        <span className="text-xs font-medium tabular-nums text-primary">
          {step}
        </span>
        <span className="hidden h-px w-8 bg-border sm:block" aria-hidden />
      </div>
      <div className="min-w-0 space-y-4">
        <div className="space-y-1">
          <h2 className="text-base font-medium tracking-tight">{title}</h2>
          <p className="text-sm text-muted-foreground">{hint}</p>
        </div>
        {children}
      </div>
    </section>
  );
}
