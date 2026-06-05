"use client";

import { Button } from "@/components/ui/button";

export interface PlaybackControlsProps {
  playing: boolean;
  currentFrame: number;
  frameCount: number;
  onToggle: () => void;
  onReplay: () => void;
  onSeek: (frame: number) => void;
}

export function PlaybackControls({
  playing,
  currentFrame,
  frameCount,
  onToggle,
  onReplay,
  onSeek,
}: PlaybackControlsProps) {
  const last = Math.max(0, frameCount - 1);
  return (
    <div className="flex items-center gap-3" data-testid="playback-controls">
      <Button
        type="button"
        variant="outline"
        size="sm"
        onClick={onToggle}
        aria-label={playing ? "Duraklat" : "Oynat"}
      >
        {playing ? "Duraklat" : "Oynat"}
      </Button>
      <Button
        type="button"
        variant="ghost"
        size="sm"
        onClick={onReplay}
        aria-label="Tekrar"
      >
        Tekrar
      </Button>
      <input
        type="range"
        data-testid="scrubber"
        aria-label="nesil"
        min={0}
        max={last}
        value={currentFrame}
        onChange={(e) => onSeek(Number(e.target.value))}
        className="h-1 flex-1 cursor-pointer accent-primary"
      />
      <span className="text-xs tabular-nums text-muted-foreground">
        nesil {currentFrame + 1} / {frameCount}
      </span>
    </div>
  );
}
