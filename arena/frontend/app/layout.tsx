import type { Metadata } from "next";
import { Plus_Jakarta_Sans, JetBrains_Mono } from "next/font/google";
import Link from "next/link";
import { ThemeToggle } from "@/components/theme-toggle";
import "./globals.css";

// Plus Jakarta Sans drives the whole UI; the variable name matches `--font-sans`
// consumed in globals.css.
const jakarta = Plus_Jakarta_Sans({
  variable: "--font-sans",
  subsets: ["latin"],
  display: "swap",
});
// Monospace is used in ONE place only — the code editor on the submit page
// (`--font-mono`); everything else renders in Plus Jakarta Sans.
const mono = JetBrains_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
  display: "swap",
});

export const metadata: Metadata = {
  title: "TSP Solver Arena",
  description: "TSP çözücülerini gönder, izole çalıştır ve lider tablosunda yüksel.",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html
      lang="tr"
      suppressHydrationWarning
      className={`${jakarta.variable} ${mono.variable} h-full antialiased`}
    >
      <body className="flex min-h-full flex-col bg-background text-foreground">
        {/* Initialize theme before paint to avoid a dark-mode flash. */}
        <script
          dangerouslySetInnerHTML={{
            __html: `(function(){try{var t=localStorage.getItem('theme');var d=t?t==='dark':window.matchMedia('(prefers-color-scheme: dark)').matches;if(d)document.documentElement.classList.add('dark');}catch(e){}})();`,
          }}
        />
        <header className="sticky top-0 z-40 border-b border-border/70 bg-background/80 backdrop-blur-md">
          <nav className="mx-auto flex w-full max-w-5xl items-center justify-between px-6 py-3.5">
            <Link
              href="/"
              className="group flex items-center gap-2.5 font-semibold tracking-tight"
            >
              <span
                aria-hidden
                className="grid size-7 place-items-center rounded-md bg-primary text-primary-foreground shadow-sm transition-transform group-hover:-translate-y-px"
              >
                <svg
                  viewBox="0 0 24 24"
                  className="size-4"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                >
                  <circle cx="5" cy="6" r="1.6" />
                  <circle cx="19" cy="9" r="1.6" />
                  <circle cx="9" cy="19" r="1.6" />
                  <path d="M5 6 19 9 9 19 5 6Z" className="opacity-70" />
                </svg>
              </span>
              <span className="flex items-baseline gap-1.5">
                TSP Solver Arena
                <span className="text-[10px] font-medium uppercase tracking-[0.18em] text-muted-foreground">
                  beta
                </span>
              </span>
            </Link>
            <div className="flex items-center gap-1">
              <Link
                href="/"
                className="rounded-md px-3 py-1.5 text-sm font-medium text-muted-foreground transition-colors hover:bg-muted hover:text-foreground"
              >
                Lider Tablosu
              </Link>
              <Link
                href="/submit"
                className="rounded-md px-3 py-1.5 text-sm font-medium text-muted-foreground transition-colors hover:bg-muted hover:text-foreground"
              >
                Gönder
              </Link>
              <ThemeToggle />
            </div>
          </nav>
        </header>
        <div className="flex-1">{children}</div>
        <footer className="border-t border-border/60">
          <div className="mx-auto flex w-full max-w-5xl items-center justify-between px-6 py-4 text-[11px] uppercase tracking-[0.14em] text-muted-foreground">
            <span>TSP Solver Arena</span>
            <span>izole · puanlı · sıralı</span>
          </div>
        </footer>
      </body>
    </html>
  );
}
