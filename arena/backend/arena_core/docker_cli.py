"""Thin, injectable wrapper around the `docker` CLI.

ContainerRunner builds full `docker run ...` argument lists and hands them here.
Keeping this layer tiny + injectable means ContainerRunner is unit-tested with a fake
(asserting the argv it builds and scripting outcomes), while production uses the real
CLI. No docker SDK dependency.
"""
from __future__ import annotations

import subprocess
import time
from dataclasses import dataclass
from shutil import which
from typing import Protocol


@dataclass
class DockerOutcome:
    stdout: str
    stderr: str
    exit_code: int | None    # None when the container was killed (timeout)
    timed_out: bool
    duration_ms: int


class DockerCli(Protocol):
    def run(self, args: list[str], *, timeout_s: float, stdin: str = "",
            kill_name: str | None = None) -> DockerOutcome:
        ...


class SubprocessDockerCli:
    def run(self, args, *, timeout_s, stdin="", kill_name=None) -> DockerOutcome:
        start = time.monotonic()
        try:
            proc = subprocess.run(["docker", *args], input=stdin, capture_output=True,
                                  text=True, timeout=timeout_s)
        except subprocess.TimeoutExpired as exc:
            if kill_name:
                subprocess.run(["docker", "kill", kill_name], capture_output=True, text=True)
            ms = int((time.monotonic() - start) * 1000)
            return DockerOutcome(_s(exc.stdout), _s(exc.stderr), None, True, ms)
        ms = int((time.monotonic() - start) * 1000)
        return DockerOutcome(proc.stdout, proc.stderr, proc.returncode, False, ms)


def docker_available() -> bool:
    return which("docker") is not None


def _s(v) -> str:
    if v is None:
        return ""
    return v.decode(errors="replace") if isinstance(v, (bytes, bytearray)) else v
