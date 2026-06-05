"""LocalRunner — runs a submission's entrypoint as a host subprocess. DEV / TEST ONLY.

NOT a sandbox: runs with the host's privileges and no isolation. Never use for
untrusted submissions in production — that is ContainerRunner's job. It exists so the
pipeline runs end-to-end on a dev machine without Docker. It materializes the files
map to a temp dir and runs the effective build (if any) then run command there. Only
the python preset is meaningfully supported locally.
"""
from __future__ import annotations

import subprocess
import tempfile
import time

from .presets import effective_build_cmd, effective_run_cmd
from .run_spec import RunSpec
from .runner import RunResult
from .workdir import write_files


class LocalRunner:
    def __init__(self, timeout_s: float = 5.0):
        self.timeout_s = timeout_s

    def run(self, spec: RunSpec) -> RunResult:
        with tempfile.TemporaryDirectory() as tmp:
            try:
                write_files(tmp, spec.files)
            except ValueError as exc:
                return RunResult("error", "", str(exc), None, 0)

            build = effective_build_cmd(spec)
            if build:
                res = self._exec(build, tmp, spec.stdin)
                if res.status != "ok":
                    return res

            return self._exec(effective_run_cmd(spec), tmp, spec.stdin)

    def _exec(self, cmd: str, cwd: str, stdin: str) -> RunResult:
        start = time.monotonic()
        try:
            proc = subprocess.run(cmd, shell=True, cwd=cwd, input=stdin,
                                  capture_output=True, text=True, timeout=self.timeout_s)
        except subprocess.TimeoutExpired as exc:
            elapsed = int((time.monotonic() - start) * 1000)
            return RunResult("timeout", _s(exc.stdout), _s(exc.stderr), None, elapsed)
        elapsed = int((time.monotonic() - start) * 1000)
        status = "ok" if proc.returncode == 0 else "error"
        return RunResult(status, proc.stdout, proc.stderr, proc.returncode, elapsed)


def _s(v) -> str:
    if v is None:
        return ""
    return v.decode(errors="replace") if isinstance(v, (bytes, bytearray)) else v
