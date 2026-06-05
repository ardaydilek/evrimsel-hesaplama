import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { renderHook, act } from "@testing-library/react";
import { useReplay } from "@/lib/use-replay";

beforeEach(() => vi.useFakeTimers());
afterEach(() => vi.useRealTimers());

describe("useReplay", () => {
  it("auto-plays and advances to the last frame, then stops", () => {
    const { result } = renderHook(() => useReplay(4));
    expect(result.current.currentFrame).toBe(0);
    expect(result.current.playing).toBe(true);
    act(() => { vi.advanceTimersByTime(40); });
    expect(result.current.currentFrame).toBe(1);
    act(() => { vi.advanceTimersByTime(40 * 5); });
    expect(result.current.currentFrame).toBe(3); // last (frameCount-1)
    expect(result.current.playing).toBe(false);  // stopped at the end
  });

  it("seek pauses and sets the frame; replay restarts", () => {
    const { result } = renderHook(() => useReplay(10));
    act(() => { result.current.seek(5); });
    expect(result.current.currentFrame).toBe(5);
    expect(result.current.playing).toBe(false);
    act(() => { result.current.replay(); });
    expect(result.current.currentFrame).toBe(0);
    expect(result.current.playing).toBe(true);
  });
});
