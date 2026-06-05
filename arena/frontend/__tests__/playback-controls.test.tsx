import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { PlaybackControls } from "@/components/playback-controls";

describe("PlaybackControls", () => {
  it("wires toggle, replay, and seek; shows the generation counter", async () => {
    const user = userEvent.setup();
    const onToggle = vi.fn();
    const onReplay = vi.fn();
    const onSeek = vi.fn();
    render(
      <PlaybackControls
        playing={true}
        currentFrame={2}
        frameCount={10}
        onToggle={onToggle}
        onReplay={onReplay}
        onSeek={onSeek}
      />,
    );
    expect(screen.getByText(/nesil 3 \/ 10/i)).toBeInTheDocument(); // 1-based display
    await user.click(screen.getByRole("button", { name: /duraklat/i }));
    expect(onToggle).toHaveBeenCalled();
    await user.click(screen.getByRole("button", { name: /tekrar/i }));
    expect(onReplay).toHaveBeenCalled();
    const scrubber = screen.getByTestId("scrubber") as HTMLInputElement;
    expect(scrubber.value).toBe("2");
  });
});
