import { test, expect } from "@playwright/test";

// A GEN-emitting python solver so the detail page shows the animated convergence
// dashboard (gen_log populated). It prints a descending best/avg then the optimal
// identity tour (scored 699 by the server-side scorer).
const SOLVER = [
  "import sys",
  "best=1200.0; avg=1400.0",
  "for g in range(60):",
  "    best=max(699.0, best*0.97); avg=max(720.0, avg*0.965)",
  "    print(f'GEN {g} {best:.1f} {avg:.1f}')",
  "print('TOUR ' + ' '.join(str(i) for i in range(1, 43)))",
].join("\n");

test("capture arena leaderboard + animated detail", async ({ page, request }) => {
  // submit via the API (proxied through the Next rewrite)
  const res = await request.post("/api/submissions", {
    data: { handle: "demo", preset: "python", files: { "main.py": SOLVER } },
  });
  const { id } = await res.json();

  // poll to scored
  await expect
    .poll(
      async () => {
        const r = await request.get(`/api/submissions/${id}`);
        return (await r.json()).status;
      },
      { timeout: 60_000 },
    )
    .toBe("scored");

  // hide the Next.js dev-mode indicator so the submission screenshots are clean
  const hideDevBadge = "nextjs-portal{display:none!important}";

  // leaderboard
  await page.goto("/");
  await page.addStyleTag({ content: hideDevBadge });
  await expect(page.getByText("demo").first()).toBeVisible();
  await page.screenshot({ path: "../../assets/arena_leaderboard.png", fullPage: true });

  // detail (animated dashboard) — let the replay advance, then capture
  await page.goto(`/submissions/${id}`);
  await page.addStyleTag({ content: hideDevBadge });
  await expect(page.getByTestId("status-badge")).toHaveText("Puanlandı", { timeout: 40_000 });
  // the animated convergence dashboard (proves gen_log populated)
  await expect(page.getByTestId("convergence-chart")).toBeVisible();
  await page.waitForTimeout(5000); // let the replay finish (full curves + drawn-in tour)
  await page.screenshot({ path: "../../assets/arena_detail.png", fullPage: true });
});
