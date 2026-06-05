import { describe, it, expect, vi, beforeEach } from "vitest";
import { getLeaderboard, createSubmission } from "@/lib/api";

beforeEach(() => { vi.restoreAllMocks(); });

describe("api client", () => {
  it("getLeaderboard fetches and returns json", async () => {
    const rows = [{ id: "1", handle: "ada", preset: "python", length: 699, gap: 0, runtime_ms: 5 }];
    vi.stubGlobal("fetch", vi.fn(async () => new Response(JSON.stringify(rows), { status: 200 })));
    expect(await getLeaderboard()).toEqual(rows);
  });

  it("createSubmission posts the body and returns {id,status}", async () => {
    const fetchMock = vi.fn(async () =>
      new Response(JSON.stringify({ id: "7", status: "queued" }), { status: 200 }));
    vi.stubGlobal("fetch", fetchMock);
    const out = await createSubmission({ handle: "x", preset: "python", files: { "main.py": "print(1)" } });
    expect(out).toEqual({ id: "7", status: "queued" });
    const [url, opts] = (fetchMock.mock.calls[0] as unknown as [string, RequestInit]);
    expect(url).toBe("/api/submissions");
    expect(JSON.parse(opts.body as string).preset).toBe("python");
  });

  it("throws ApiError with backend detail on 422", async () => {
    vi.stubGlobal("fetch", vi.fn(async () =>
      new Response(JSON.stringify({ detail: "unknown preset: x" }), { status: 422 })));
    await expect(createSubmission({ handle: "x", preset: "x", files: { a: "b" } }))
      .rejects.toMatchObject({ status: 422, message: "unknown preset: x" });
  });
});
