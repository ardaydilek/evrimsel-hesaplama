"""The Runner interface: how the platform executes a submission.

A Runner takes a RunSpec (a multi-file project for a language preset, with optional
build/run commands) and returns a RunResult capturing what the program printed and
how it terminated. Concrete runners: ContainerRunner (production, real Docker sandbox)
and LocalRunner (dev/test, NOT sandboxed). The rest of the system depends only on this
interface, so the execution backend is swappable.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Protocol, runtime_checkable

from .run_spec import RunSpec

RunStatus = Literal["ok", "timeout", "error"]


@dataclass
class RunResult:
    status: RunStatus          # ok = ran to completion; timeout; error = crash / build fail / bad request
    stdout: str
    stderr: str
    exit_code: int | None      # process exit code (None when killed / timed out / not applicable)
    time_ms: int               # wall-clock runtime


@runtime_checkable
class Runner(Protocol):
    def run(self, spec: RunSpec) -> RunResult:
        ...
