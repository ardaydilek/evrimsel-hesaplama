import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";

vi.mock("next/navigation", () => ({ useParams: () => ({ id: "1" }) }));
vi.mock("@/lib/api", () => ({ getSubmission: vi.fn(), getProblem: vi.fn() }));
vi.mock("@/lib/use-replay", () => ({
  useReplay: () => ({
    currentFrame: 0, playing: false,
    play() {}, pause() {}, toggle() {}, replay() {}, seek() {},
  }),
}));

import { getSubmission, getProblem } from "@/lib/api";
import DetailPage from "@/app/submissions/[id]/page";

beforeEach(() => vi.resetAllMocks());

describe("SubmissionDetailPage", () => {
  it("renders the score + tour map when scored", async () => {
    vi.mocked(getSubmission).mockResolvedValue({
      id: "1", handle: "ada", preset: "python", status: "scored", fail_reason: null,
      length: 699, runtime_ms: 5, tour: [1, 2, 3, 4], gen_log: null,
    });
    vi.mocked(getProblem).mockResolvedValue({
      num_cities: 4, optimal: 699, matrix: [], coordinates: [[0, 0], [1, 0], [1, 1], [0, 1]],
    });
    render(<DetailPage />);
    await waitFor(() => expect(screen.getByTestId("status-badge")).toHaveTextContent("Puanlandı"));
    expect(screen.getByText("699")).toBeInTheDocument();
    await waitFor(() => expect(screen.getByTestId("tour-map")).toBeInTheDocument());
  });

  it("renders the failure reason when failed", async () => {
    vi.mocked(getSubmission).mockResolvedValue({
      id: "1", handle: "ada", preset: "cpp", status: "failed",
      fail_reason: "compile error: missing ;",
    });
    render(<DetailPage />);
    await waitFor(() => expect(screen.getByText(/compile error: missing ;/i)).toBeInTheDocument());
  });

  it("shows a helpful hint for a known failure (read-only filesystem)", async () => {
    vi.mocked(getSubmission).mockResolvedValue({
      id: "1", handle: "ada", preset: "cpp", status: "failed",
      fail_reason: "filesystem error: cannot create directories: Read-only file system [results]",
    });
    render(<DetailPage />);
    await waitFor(() => expect(screen.getByText(/salt-okunur/i)).toBeInTheDocument());
    expect(screen.getByRole("link", { name: /Şablon ve ipuçları/i })).toBeInTheDocument();
  });

  it("animates when the submission has a gen_log", async () => {
    vi.mocked(getSubmission).mockResolvedValue({
      id: "1", handle: "ada", preset: "python", status: "scored", fail_reason: null,
      length: 699, runtime_ms: 5, tour: [1, 2, 3, 4],
      gen_log: [[0, 1200, 1500], [1, 900, 1100], [2, 699, 950]],
    });
    vi.mocked(getProblem).mockResolvedValue({
      num_cities: 4, optimal: 699, matrix: [], coordinates: [[0, 0], [1, 0], [1, 1], [0, 1]],
    });
    render(<DetailPage />);
    await waitFor(() => expect(screen.getByTestId("submission-replay")).toBeInTheDocument());
    expect(screen.getByTestId("convergence-chart")).toBeInTheDocument();
  });
});
