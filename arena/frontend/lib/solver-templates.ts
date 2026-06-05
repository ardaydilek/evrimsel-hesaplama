import type { FileEntry } from "@/components/multi-file-editor";
import raw from "./solver-templates.json";

// Canonical per-language starter templates: a compact nearest-neighbor solver that reads
// the auto-provided distance matrix and prints a TOUR line — demonstrating the submission
// contract (single source file, read input, print to stdout, write nothing to disk). The
// same JSON is verified end-to-end by the backend's gated test_templates.py, so what a
// submitter receives is exactly what is known to build and score.
export const TEMPLATES = raw as Record<string, FileEntry[]>;

const DIL: Record<string, string> = {
  python: "Python",
  cpp: "C++",
  go: "Go",
  rust: "Rust",
  node: "JavaScript (Node)",
  java: "Java",
};

// A copy-paste prompt the submitter hands to their coding agent to reshape an arbitrary
// (often multi-file, disk-writing) solver into one conforming file.
export function agentPrompt(preset: string): string {
  const dil = DIL[preset] ?? preset;
  return [
    `Aşağıdaki TSP çözümümü tek bir ${dil} dosyasına dönüştür. Program, çalışma klasöründeki`,
    "`intercityDistance.txt` dosyasından 42×42 tam sayı mesafe matrisini okuyabilir (satır i,",
    "sütun j = i ve j şehirleri arası mesafe; şehirler 1-tabanlı). Sonucu YALNIZCA stdout'a",
    "tek satır olarak `TOUR k1 k2 … k42` biçiminde yazsın (42 şehrin 1-tabanlı ziyaret sırası).",
    "Diske hiçbir dosya veya dizin YAZMA — dosya sistemi salt-okunur. İşte kodum:",
    "",
    "[KODUNU BURAYA YAPIŞTIR]",
  ].join("\n");
}
