"""RunSpec — the generalized input to a Runner.

Supersedes the old (language, source, stdin) trio. A submission is a multi-file
project for a language *preset*, with optional build/run command overrides.
ResourceLimits are platform-owned (set by the runner), never supplied by submitters.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal


@dataclass(frozen=True, slots=True)
class ResourceLimits:
    memory_mb: int
    cpus: float
    wall_s: float
    pids: int
    output_bytes: int


@dataclass(slots=True)
class RunSpec:
    preset: str
    files: dict[str, str] = field(default_factory=dict)
    build_cmd: str | None = None
    run_cmd: str | None = None
    stdin: str = ""
    mode: Literal["preset", "byoi"] = "preset"
