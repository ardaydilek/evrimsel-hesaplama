import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { TourMap } from "@/components/tour-map";

describe("TourMap", () => {
  it("draws a dot per city and a closed path through the tour", () => {
    const coordinates: [number, number][] = [[0, 0], [10, 0], [10, 10], [0, 10]];
    render(<TourMap coordinates={coordinates} tour={[1, 2, 3, 4]} />);
    const svg = screen.getByTestId("tour-map");
    expect(svg.querySelectorAll("circle")).toHaveLength(4);
    const path = screen.getByTestId("tour-path").getAttribute("d")!;
    expect(path.startsWith("M ")).toBe(true);
    expect(path.trim().endsWith("Z")).toBe(true);
    expect((path.match(/L /g) ?? []).length).toBe(3);
  });

  it("draws the tour in partially when progress < 1", () => {
    const coordinates: [number, number][] = [[0, 0], [10, 0], [10, 10], [0, 10]];
    render(<TourMap coordinates={coordinates} tour={[1, 2, 3, 4]} progress={0.5} />);
    const path = screen.getByTestId("tour-path");
    expect(path).toHaveAttribute("pathLength", "1");
    expect(path.getAttribute("stroke-dashoffset")).toBe("0.5");
  });

  it("renders the full tour (no dash) when progress is omitted", () => {
    const coordinates: [number, number][] = [[0, 0], [10, 0], [10, 10], [0, 10]];
    render(<TourMap coordinates={coordinates} tour={[1, 2, 3, 4]} />);
    expect(screen.getByTestId("tour-path")).not.toHaveAttribute("stroke-dashoffset");
  });
});
