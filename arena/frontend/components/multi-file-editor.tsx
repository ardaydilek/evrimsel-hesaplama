"use client";

import { useState } from "react";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { cn } from "@/lib/utils";

export interface FileEntry {
  path: string;
  content: string;
}

export function filesToMap(files: FileEntry[]): Record<string, string> {
  return Object.fromEntries(
    files.filter((f) => f.path.trim()).map((f) => [f.path.trim(), f.content]),
  );
}

export function MultiFileEditor({
  files,
  onChange,
}: {
  files: FileEntry[];
  onChange: (files: FileEntry[]) => void;
}) {
  const [active, setActive] = useState(0);
  const [dragging, setDragging] = useState(false);

  const idx = Math.min(active, files.length - 1);
  const current = files[idx];

  const update = (i: number, patch: Partial<FileEntry>) =>
    onChange(files.map((f, j) => (j === i ? { ...f, ...patch } : f)));

  const add = () => {
    onChange([...files, { path: "", content: "" }]);
    setActive(files.length); // the new entry's index
  };

  const remove = (i: number) => {
    onChange(files.filter((_, j) => j !== i));
    setActive((a) => (a >= i && a > 0 ? a - 1 : a));
  };

  async function addDropped(list: FileList) {
    const entries: FileEntry[] = [];
    for (const file of Array.from(list)) {
      entries.push({ path: file.name, content: await file.text() });
    }
    if (entries.length) {
      onChange([...files, ...entries]);
      setActive(files.length); // focus the first dropped file
    }
  }

  function onDrop(e: React.DragEvent) {
    e.preventDefault();
    setDragging(false);
    if (e.dataTransfer.files?.length) void addDropped(e.dataTransfer.files);
  }

  return (
    <div
      data-testid="multi-file-editor"
      onDragOver={(e) => {
        e.preventDefault();
        setDragging(true);
      }}
      onDragLeave={(e) => {
        e.preventDefault();
        setDragging(false);
      }}
      onDrop={onDrop}
      className={cn(
        "overflow-hidden rounded-lg border bg-card shadow-sm transition-shadow",
        dragging ? "border-primary ring-2 ring-primary/40" : "border-border/70",
      )}
    >
      {/* Tab bar */}
      <div className="flex items-center gap-1 overflow-x-auto border-b border-border/70 bg-muted/40 px-2 py-1.5">
        {files.map((f, i) => (
          <div
            key={i}
            className={cn(
              "flex shrink-0 items-center gap-1.5 rounded-md px-2.5 py-1 text-xs transition-colors",
              i === idx
                ? "bg-background text-foreground shadow-sm"
                : "text-muted-foreground hover:bg-background/60",
            )}
          >
            <button type="button" className="font-mono" onClick={() => setActive(i)}>
              {f.path || "adsız"}
            </button>
            <button
              type="button"
              aria-label={`dosyayı sil ${i}`}
              onClick={() => remove(i)}
              disabled={files.length === 1}
              className="leading-none text-muted-foreground/60 transition-colors hover:text-destructive disabled:opacity-0"
            >
              ×
            </button>
          </div>
        ))}
        <button
          type="button"
          onClick={add}
          aria-label="dosya ekle"
          className="shrink-0 rounded-md px-2 py-1 text-sm text-muted-foreground transition-colors hover:bg-background/60 hover:text-foreground"
        >
          +
        </button>
      </div>

      {/* Active file */}
      {current && (
        <div className="relative">
          <Input
            aria-label={`dosya yolu ${idx}`}
            placeholder="yol (örn. main.cpp)"
            value={current.path}
            onChange={(e) => update(idx, { path: e.target.value })}
            className="h-8 rounded-none border-0 border-b border-border/60 bg-transparent px-3 font-mono text-xs shadow-none focus-visible:bg-background dark:bg-transparent"
          />
          <Textarea
            aria-label={`dosya içeriği ${idx}`}
            placeholder="dosya içeriği — veya dosyaları buraya sürükleyip bırakın"
            value={current.content}
            onChange={(e) => update(idx, { content: e.target.value })}
            className="min-h-48 resize-y rounded-none border-0 bg-transparent px-3 font-mono text-sm leading-relaxed shadow-none focus-visible:ring-0 dark:bg-transparent"
          />
          {dragging && (
            <div className="pointer-events-none absolute inset-0 grid place-items-center bg-primary/5 text-sm font-medium text-primary">
              Dosyaları buraya bırakın
            </div>
          )}
        </div>
      )}
    </div>
  );
}
