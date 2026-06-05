import { test, expect } from "@playwright/test";

test("submit a python solver → scored 699 → appears on the leaderboard", async ({ page }) => {
  await page.goto("/submit");
  await page.getByLabel(/takma ad/i).fill("e2e");
  // default preset is python; the starter main.py already prints the identity tour (length 699)
  await page.getByRole("button", { name: /^gönder$/i }).click();

  // navigated to the detail page; the page polls until terminal
  await expect(page.getByTestId("status-badge")).toHaveText("Puanlandı", { timeout: 40_000 });
  await expect(page.getByText("699")).toBeVisible();
  await expect(page.getByTestId("tour-map")).toBeVisible();

  // leaderboard shows the entry
  await page.goto("/");
  await expect(page.getByText("e2e")).toBeVisible();
});
