import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { ConvergenceChart } from "@/components/convergence-chart";

const GEN_LOG: [number, number, number][] = [
  [0, 1200, 1500],
  [1, 1000, 1300],
  [2, 800, 1100],
  [3, 699, 950],
];

describe("ConvergenceChart", () => {
  it("draws best + avg polylines up to upToGen and an optimal reference line", () => {
    render(<ConvergenceChart genLog={GEN_LOG} optimal={699} upToGen={2} />);
    const best = screen.getByTestId("best-curve");
    const avg = screen.getByTestId("avg-curve");
    expect(best.getAttribute("points")!.trim().split(/\s+/)).toHaveLength(3); // points 0..2
    expect(avg.getAttribute("points")!.trim().split(/\s+/)).toHaveLength(3);
    expect(screen.getByTestId("optimal-line")).toBeInTheDocument();
  });

  it("clamps a single-point frame", () => {
    render(<ConvergenceChart genLog={GEN_LOG} optimal={699} upToGen={0} />);
    expect(screen.getByTestId("best-curve").getAttribute("points")!.trim().split(/\s+/)).toHaveLength(1);
  });
});
