"use client";

import { useState } from "react";
import { CheckIcon, CopyIcon } from "lucide-react";
import { Button, buttonVariants } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { cn } from "@/lib/utils";
import { TEMPLATES, agentPrompt } from "@/lib/solver-templates";
import type { FileEntry } from "@/components/multi-file-editor";

const code = "rounded bg-muted px-1 py-0.5 font-mono text-[11px]";

// The main source file (the solver logic) — every template's source filename contains
// "main" (main.py / main.cpp / main.go / src/main.rs / main.js / Main.java); build
// manifests (Makefile, go.mod, …) do not.
function primarySource(files: FileEntry[]): FileEntry | undefined {
  return files.find((f) => /main/i.test(f.path)) ?? files[0];
}

function CopyButton({ text, label }: { text: string; label: string }) {
  const [copied, setCopied] = useState(false);
  return (
    <Button
      type="button"
      variant="outline"
      size="sm"
      onClick={async () => {
        try {
          await navigator.clipboard.writeText(text);
          setCopied(true);
          setTimeout(() => setCopied(false), 1500);
        } catch {
          /* clipboard unavailable — no-op */
        }
      }}
    >
      {copied ? <CheckIcon /> : <CopyIcon />}
      {copied ? "Kopyalandı" : label}
    </Button>
  );
}

export function SubmissionHelperDialog({
  preset,
  onLoadTemplate,
}: {
  preset: string;
  onLoadTemplate: (files: FileEntry[]) => void;
}) {
  const [open, setOpen] = useState(false);
  const files = TEMPLATES[preset] ?? [];
  const primary = primarySource(files);

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger className={cn(buttonVariants({ variant: "outline", size: "sm" }))}>
        Şablon & yapay zekâ ile hazırla
      </DialogTrigger>
      <DialogContent className="max-w-3xl">
        <DialogHeader>
          <DialogTitle>Çözümünü tek dosyaya hazırla</DialogTitle>
          <DialogDescription>
            Arena her çözümü izole, salt-okunur bir sandbox’ta çalıştırır. Çözümün şu
            kurallara uymalı:
          </DialogDescription>
        </DialogHeader>

        <ul className="space-y-1.5 text-sm text-muted-foreground">
          <li>• Tek bir kaynak dosya (gerekirse derleme dosyası: Makefile, go.mod…).</li>
          <li>
            • Girişi <code className={code}>cityData.txt</code> /{" "}
            <code className={code}>intercityDistance.txt</code>’ten okuyabilirsin (çalışma
            klasöründe hazır).
          </li>
          <li>
            • Sonucu YALNIZCA stdout’a <code className={code}>TOUR 1 2 3 …</code> olarak
            yazdır.
          </li>
          <li>• Diske hiçbir şey yazma — dosya sistemi salt-okunur.</li>
        </ul>

        {primary && (
          <section className="space-y-2">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <h3 className="text-sm font-medium">Seçili dil şablonu ({preset})</h3>
              <div className="flex gap-2">
                <CopyButton text={primary.content} label="Kodu kopyala" />
                <Button
                  type="button"
                  size="sm"
                  onClick={() => {
                    onLoadTemplate(files);
                    setOpen(false);
                  }}
                >
                  Editöre yükle
                </Button>
              </div>
            </div>
            {files.length > 1 && (
              <p className="text-xs text-muted-foreground">
                Şablon dosyaları: {files.map((f) => f.path).join(", ")}
              </p>
            )}
            <pre className="max-h-64 overflow-auto rounded-lg border border-border/70 bg-muted/40 p-3 font-mono text-xs leading-relaxed">
              {primary.content}
            </pre>
          </section>
        )}

        <section className="space-y-2">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <h3 className="text-sm font-medium">Yapay zekâ asistanı komutu</h3>
            <CopyButton text={agentPrompt(preset)} label="Komutu kopyala" />
          </div>
          <p className="text-xs text-muted-foreground">
            Kendi çözümünü bir kod asistanına (Claude, Cursor…) tek dosyaya dönüştürtmek
            için bu komutu kullan:
          </p>
          <pre className="max-h-48 overflow-auto rounded-lg border border-border/70 bg-muted/40 p-3 font-mono text-xs leading-relaxed whitespace-pre-wrap">
            {agentPrompt(preset)}
          </pre>
        </section>
      </DialogContent>
    </Dialog>
  );
}
