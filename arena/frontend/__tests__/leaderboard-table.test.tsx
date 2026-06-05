import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { LeaderboardTable } from "@/components/leaderboard-table";

describe("LeaderboardTable", () => {
  it("shows an empty state when there are no rows", () => {
    render(<LeaderboardTable rows={[]} />);
    expect(screen.getByText(/henüz puanlanmış çözüm yok/i)).toBeInTheDocument();
  });

  it("renders rows with gap formatting and a detail link", () => {
    render(
      <LeaderboardTable
        rows={[
          { id: "1", handle: "ada", preset: "python", length: 699, gap: 0, runtime_ms: 5 },
          { id: "2", handle: "bob", preset: "cpp", length: 709, gap: 10, runtime_ms: 8 },
        ]}
      />,
    );
    expect(screen.getByText("ada").closest("a")).toHaveAttribute("href", "/submissions/1");
    expect(screen.getByText("optimum")).toBeInTheDocument();
    expect(screen.getByText("+10")).toBeInTheDocument();
  });
});
