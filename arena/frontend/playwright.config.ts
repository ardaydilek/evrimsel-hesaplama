import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: "./e2e",
  timeout: 60_000,
  use: { baseURL: "http://localhost:3000" },
  webServer: [
    {
      command:
        "cd ../backend && ARENA_RUNNER=local DATABASE_URL=sqlite:///./arena_e2e.db " +
        ".venv/bin/uvicorn arena_core.app:build_app --factory --port 8000",
      url: "http://localhost:8000/api/problem",
      reuseExistingServer: !process.env.CI,
      timeout: 60_000,
    },
    {
      command: "npm run dev",
      url: "http://localhost:3000",
      reuseExistingServer: !process.env.CI,
      timeout: 120_000,
    },
  ],
});
