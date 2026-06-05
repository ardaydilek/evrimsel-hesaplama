import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";

vi.mock("@/lib/api", () => ({ getLeaderboard: vi.fn() }));
import { getLeaderboard } from "@/lib/api";
import LeaderboardPage from "@/app/page";

beforeEach(() => vi.resetAllMocks());

describe("LeaderboardPage", () => {
  it("loads and renders rows", async () => {
    vi.mocked(getLeaderboard).mockResolvedValue([
      { id: "1", handle: "ada", preset: "python", length: 699, gap: 0, runtime_ms: 5 },
    ]);
    render(<LeaderboardPage />);
    await waitFor(() => expect(screen.getByText("ada")).toBeInTheDocument());
    expect(screen.getByText("optimum")).toBeInTheDocument();
  });

  it("shows an error if the fetch fails", async () => {
    vi.mocked(getLeaderboard).mockRejectedValue(new Error("boom"));
    render(<LeaderboardPage />);
    await waitFor(() => expect(screen.getByText(/yüklenemedi/i)).toBeInTheDocument());
  });
});
