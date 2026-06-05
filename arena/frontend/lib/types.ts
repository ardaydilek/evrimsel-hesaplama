export type Status = "queued" | "running" | "scored" | "failed";

export interface Preset {
  name: string;
  default_build_cmd: string | null;
  default_run_cmd: string;
}

export interface LeaderboardRow {
  id: string;
  handle: string;
  preset: string;
  length: number;
  gap: number;
  runtime_ms: number;
}

export interface Problem {
  num_cities: number;
  optimal: number;
  matrix: number[][];
  coordinates: [number, number][];
}

export interface SubmissionInput {
  handle: string;
  preset: string;
  files: Record<string, string>;
  build_cmd?: string | null;
  run_cmd?: string | null;
}

export interface Submission {
  id: string;
  handle: string;
  preset: string;
  status: Status;
  fail_reason: string | null;
  length?: number;
  runtime_ms?: number;
  tour?: number[];
  gen_log?: [number, number, number][] | null;
}
