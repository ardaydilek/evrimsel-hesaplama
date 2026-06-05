// Maps a raw failure reason (the sandbox's stderr or the scorer's message) to a short,
// actionable Turkish hint. Returns null when nothing matches, so the UI falls back to
// showing just the raw error. Match strings are the literals produced by the backend:
// the run-phase stderr (e.g. "Read-only file system"), the validator ("no TOUR line
// found in output", "tour has N cities, expected 42") and the timeout reason.
const RULES: [RegExp, string][] = [
  [
    /read-only file system/i,
    "Çözümün diske yazmaya çalıştı. Sandbox dosya sistemi salt-okunur — sonucu yalnızca stdout'a `TOUR …` olarak yazdır, dosya/dizin oluşturma.",
  ],
  [
    /no TOUR line/i,
    "Çıktıda geçerli bir `TOUR …` satırı yok. Çözümün son satırda turu `TOUR 1 2 3 …` biçiminde yazdırmalı.",
  ],
  [
    /tour has \d+ cities, expected/i,
    "Tur yanlış sayıda şehir içeriyor — 42 şehrin tamamı, her biri bir kez, 1–42 kimlikleriyle yazdırılmalı.",
  ],
  [
    /timed out/i,
    "Çözüm süre sınırını (10 sn) aştı. Daha hızlı bir yaklaşım dene.",
  ],
];

export function hintForFailure(reason: string | null | undefined): string | null {
  if (!reason) return null;
  for (const [re, hint] of RULES) {
    if (re.test(reason)) return hint;
  }
  return null;
}
