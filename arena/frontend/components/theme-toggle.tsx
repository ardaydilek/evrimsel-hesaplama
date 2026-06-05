"use client";

import { useSyncExternalStore } from "react";

/**
 * Minimal, dependency-free dark-mode toggle. The initial theme is applied by an
 * inline script in the root layout (before paint) to avoid a flash; this button
 * reads the live `.dark` class via useSyncExternalStore and flips it on click.
 */

function subscribe(onChange: () => void) {
  const obs = new MutationObserver(onChange);
  obs.observe(document.documentElement, {
    attributes: true,
    attributeFilter: ["class"],
  });
  return () => obs.disconnect();
}

const isDark = () =>
  typeof document !== "undefined" &&
  document.documentElement.classList.contains("dark");

export function ThemeToggle() {
  // Server snapshot is `false`; the pre-paint script + observer reconcile on the
  // client. Icon swap is cosmetic, so a one-frame settle is acceptable.
  const dark = useSyncExternalStore(subscribe, isDark, () => false);

  function toggle() {
    const next = !document.documentElement.classList.contains("dark");
    document.documentElement.classList.toggle("dark", next);
    try {
      localStorage.setItem("theme", next ? "dark" : "light");
    } catch {
      // ignore persistence failures (private mode, etc.)
    }
  }

  return (
    <button
      type="button"
      onClick={toggle}
      aria-label="Temayı değiştir"
      className="grid size-8 place-items-center rounded-md border border-border/70 text-muted-foreground transition-colors hover:bg-muted hover:text-foreground"
    >
      {/* Sun (shown in dark mode → click for light) / Moon (light mode). */}
      <svg
        viewBox="0 0 24 24"
        className="size-4"
        fill="none"
        stroke="currentColor"
        strokeWidth="1.8"
        strokeLinecap="round"
        strokeLinejoin="round"
        aria-hidden
      >
        {dark ? (
          <>
            <circle cx="12" cy="12" r="4" />
            <path d="M12 2v2M12 20v2M2 12h2M20 12h2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4" />
          </>
        ) : (
          <path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8Z" />
        )}
      </svg>
    </button>
  );
}
