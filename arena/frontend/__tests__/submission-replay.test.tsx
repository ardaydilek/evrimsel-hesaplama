import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";

const replay = vi.hoisted(() => ({
  current: { currentFrame: 1, playing: true, play: vi.fn(), pause: vi.fn(), toggle: vi.fn(), replay: vi.fn(), seek: vi.fn() },
}));
vi.mock("@/lib/use-replay", () => ({ useReplay: () => replay.current }));

import { SubmissionReplay } from "@/components/submission-replay";

const GEN_LOG: [number, number, number][] = [[0, 1200, 1500], [1, 1000, 1300], [2, 699, 950]];
const COORDS: [number, number][] = [[0, 0], [10, 0], [10, 10], [0, 10]];

beforeEach(() => { replay.current.currentFrame = 1; });

describe("SubmissionReplay", () => {
  it("renders the chart, tour map, and controls, wired to the current frame", () => {
    render(<SubmissionReplay genLog={GEN_LOG} tour={[1, 2, 3, 4]} coordinates={COORDS} optimal={699} />);
    expect(screen.getByTestId("convergence-chart")).toBeInTheDocument();
    expect(screen.getByTestId("playback-controls")).toBeInTheDocument();
    // chart drew up to frame 1 => 2 points on the best curve
    expect(screen.getByTestId("best-curve").getAttribute("points")!.trim().split(/\s+/)).toHaveLength(2);
    // tour drew in to progress 1/(3-1) = 0.5 => dashoffset 0.5
    expect(screen.getByTestId("tour-path").getAttribute("stroke-dashoffset")).toBe("0.5");
  });
});
