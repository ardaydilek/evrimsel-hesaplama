"use client";

import { ConvergenceChart } from "@/components/convergence-chart";
import { PlaybackControls } from "@/components/playback-controls";
import { TourMap } from "@/components/tour-map";
import { useReplay } from "@/lib/use-replay";

export interface SubmissionReplayProps {
  genLog: [number, number, number][];
  tour: number[];
  coordinates: [number, number][];
  optimal: number;
}

export function SubmissionReplay({ genLog, tour, coordinates, optimal }: SubmissionReplayProps) {
  const frameCount = genLog.length;
  const { currentFrame, playing, toggle, replay, seek } = useReplay(frameCount);
  const progress = frameCount > 1 ? currentFrame / (frameCount - 1) : 1;

  return (
    <div className="space-y-4" data-testid="submission-replay">
      <div className="grid gap-4 sm:grid-cols-2">
        <TourMap coordinates={coordinates} tour={tour} progress={progress} />
        <ConvergenceChart genLog={genLog} optimal={optimal} upToGen={currentFrame} />
      </div>
      <PlaybackControls
        playing={playing}
        currentFrame={currentFrame}
        frameCount={frameCount}
        onToggle={toggle}
        onReplay={replay}
        onSeek={seek}
      />
    </div>
  );
}
