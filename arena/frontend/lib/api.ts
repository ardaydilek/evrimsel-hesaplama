import type {
  LeaderboardRow, Preset, Problem, Submission, SubmissionInput,
} from "./types";

export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = "ApiError";
  }
}

async function detailOf(res: Response): Promise<string> {
  try {
    const body = await res.json();
    return body?.detail ?? res.statusText;
  } catch {
    return res.statusText;
  }
}

async function getJSON<T>(url: string): Promise<T> {
  const res = await fetch(url);
  if (!res.ok) throw new ApiError(res.status, await detailOf(res));
  return (await res.json()) as T;
}

export const getLeaderboard = () => getJSON<LeaderboardRow[]>("/api/leaderboard");
export const getProblem = () => getJSON<Problem>("/api/problem");
export const getPresets = () => getJSON<Preset[]>("/api/presets");
export const getSubmission = (id: number | string) =>
  getJSON<Submission>(`/api/submissions/${id}`);

export async function createSubmission(
  input: SubmissionInput,
): Promise<{ id: string; status: string }> {
  const res = await fetch("/api/submissions", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(input),
  });
  if (!res.ok) throw new ApiError(res.status, await detailOf(res));
  return res.json();
}
