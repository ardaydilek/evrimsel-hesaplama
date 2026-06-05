import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";
import path from "path";

export default defineConfig({
  plugins: [react()],
  test: {
    environment: "jsdom",
    setupFiles: ["./vitest.setup.ts"],
    globals: true,
    // Unit/component tests live in __tests__/; keep vitest out of e2e/ (Playwright specs).
    include: ["__tests__/**/*.{test,spec}.{ts,tsx}"],
  },
  resolve: { alias: { "@": path.resolve(__dirname, ".") } },
});
