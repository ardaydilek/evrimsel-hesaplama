"""Judge0Runner — production execution via a self-hosted Judge0 instance.

Judge0 runs each submission in a hardened sandbox (isolate: cgroups + namespaces,
no network, CPU/memory/time limits). This class holds the orchestration logic
(build submission -> poll -> map status to RunResult). HTTP is injected via the
Judge0Client protocol, so the logic is unit-tested without a live Judge0; the
concrete HTTP client + live integration are wired on the Linux host (M3/deploy).

Judge0 status ids: 1 In Queue, 2 Processing (non-terminal); 3 Accepted;
5 Time Limit Exceeded; 6 Compilation Error; 7-12 runtime errors.
"""
from __future__ import annotations

import time
from typing import Protocol

from .runner import RunResult

_STATUS_ACCEPTED = 3
_STATUS_TLE = 5


class Judge0Client(Protocol):
    def create_submission(self, payload: dict) -> str:
        """POST a submission; return its token."""
        ...

    def get_submission(self, token: str) -> dict:
        """GET a submission result by token (Judge0's JSON as a dict)."""
        ...


class Judge0Runner:
    def __init__(self, client: Judge0Client, language_ids: dict[str, int],
                 poll_interval_s: float = 0.5, max_polls: int = 60):
        self.client = client
        self.language_ids = language_ids
        self.poll_interval_s = poll_interval_s
        self.max_polls = max_polls

    def run(self, language: str, source: str, stdin: str = "") -> RunResult:
        lang = language.lower()
        if lang not in self.language_ids:
            return RunResult("error", "", f"unsupported language: {language}", None, 0)

        token = self.client.create_submission({
            "language_id": self.language_ids[lang],
            "source_code": source,
            "stdin": stdin,
        })

        for attempt in range(self.max_polls):
            result = self.client.get_submission(token)
            if self._status_id(result) >= _STATUS_ACCEPTED:
                return self._to_run_result(result)
            if attempt < self.max_polls - 1:    # don't sleep after the final poll
                time.sleep(self.poll_interval_s)

        return RunResult("error", "", "judge0 polling timed out", None, 0)

    @staticmethod
    def _status_id(result: dict) -> int:
        return (result.get("status") or {}).get("id", 0)

    @classmethod
    def _to_run_result(cls, result: dict) -> RunResult:
        status_id = cls._status_id(result)
        stdout = result.get("stdout") or ""
        stderr = result.get("stderr") or ""
        compile_output = result.get("compile_output") or ""
        raw_time = result.get("time")
        time_ms = int(float(raw_time) * 1000) if raw_time is not None else 0

        if status_id == _STATUS_ACCEPTED:
            status = "ok"
        elif status_id == _STATUS_TLE:
            status = "timeout"
        else:
            status = "error"
            if compile_output and not stderr:
                stderr = compile_output

        return RunResult(status, stdout, stderr, None, time_ms)
