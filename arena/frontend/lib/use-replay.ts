import { useEffect, useRef, useState } from "react";

export interface Replay {
  currentFrame: number;
  playing: boolean;
  play: () => void;
  pause: () => void;
  toggle: () => void;
  replay: () => void;
  seek: (frame: number) => void;
}

const TICK_MS = 33; // ~30fps
const TARGET_TOTAL_MS = 4000; // whole replay aims for ~4s regardless of frame count

function prefersReducedMotion(): boolean {
  return typeof window !== "undefined" && typeof window.matchMedia === "function"
    ? window.matchMedia("(prefers-reduced-motion: reduce)").matches
    : false;
}

export function useReplay(frameCount: number): Replay {
  const last = Math.max(0, frameCount - 1);
  const reduced = prefersReducedMotion();
  const [currentFrame, setCurrentFrame] = useState(reduced ? last : 0);
  const [playing, setPlaying] = useState(!reduced && frameCount > 1);
  const step = Math.max(1, Math.round(frameCount / (TARGET_TOTAL_MS / TICK_MS)));

  // Mirror currentFrame so the interval reads the latest value without
  // re-subscribing every frame, and so the stop-at-end decision lives in the
  // frame source (the interval) rather than in a follow-up effect that would
  // call setState synchronously on every render (react-hooks/set-state-in-effect).
  const frameRef = useRef(currentFrame);
  const setFrame = (f: number) => {
    frameRef.current = f;
    setCurrentFrame(f);
  };

  useEffect(() => {
    if (!playing) return;
    const id = setInterval(() => {
      const next = Math.min(last, frameRef.current + step);
      setFrame(next);
      if (next >= last) setPlaying(false); // reached the end: stop driving
    }, TICK_MS);
    return () => clearInterval(id);
  }, [playing, step, last]);

  return {
    currentFrame,
    playing,
    play: () => { if (currentFrame >= last) setFrame(0); setPlaying(true); },
    pause: () => setPlaying(false),
    toggle: () => setPlaying((p) => !p),
    replay: () => { setFrame(0); setPlaying(true); },
    seek: (frame: number) => { setPlaying(false); setFrame(Math.max(0, Math.min(last, frame))); },
  };
}
