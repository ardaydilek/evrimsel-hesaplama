"""ContainerRunner — runs an untrusted submission in Docker. The production engine.

Two phases (build added in Task 12):
  run: toolchain image, --network none, strict caps; stdout captured for the scorer.

Hardening is effective under macOS runc and stronger under gVisor at deploy via
ARENA_DOCKER_RUNTIME (default "runc").
"""
from __future__ import annotations

import os
import shutil
import tempfile
import uuid
from contextlib import nullcontext

from .docker_cli import DockerCli, DockerOutcome, SubprocessDockerCli
from .presets import Preset, effective_build_cmd, effective_run_cmd, get_preset
from .run_spec import ResourceLimits, RunSpec
from .runner import RunResult
from .workdir import write_files, make_world_readable, make_dirs_writable

RUN_LIMITS = ResourceLimits(memory_mb=512, cpus=1.0, wall_s=10, pids=128, output_bytes=1_000_000)
BUILD_LIMITS = ResourceLimits(memory_mb=1024, cpus=2.0, wall_s=120, pids=512, output_bytes=256_000)

# Open-file-descriptor ceiling. --pids-limit already caps processes/threads (the
# right cgroup-based mechanism), but it does not bound file descriptors; a single
# process can still exhaust the host's fd table. Cap nofile per container as a
# standard DoS defense for untrusted workloads. Generous enough for normal toolchains.
NOFILE_LIMIT = 4096

# The fixed Dantzig42 problem data, auto-copied into every submission's workdir so a
# solver can read it by name (e.g. a GA reading the distance matrix). A submitter who
# uploads a same-named file overrides it.
_DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
_PROBLEM_FILES = ("cityData.txt", "intercityDistance.txt")


def copy_problem_data(work: str, skip: set[str]) -> None:
    for fn in _PROBLEM_FILES:
        if fn in skip:
            continue
        src = os.path.join(_DATA_DIR, fn)
        if os.path.exists(src):
            shutil.copy(src, os.path.join(work, fn))


class ContainerRunner:
    def __init__(self, docker: DockerCli | None = None, *, build_network_provider=None,
                 runtime: str | None = None,
                 run_limits: ResourceLimits = RUN_LIMITS,
                 build_limits: ResourceLimits = BUILD_LIMITS,
                 work_dir: str | None = None):
        self.docker = docker or SubprocessDockerCli()
        # build_network_provider() -> context manager yielding (network_name|None, proxy_env dict)
        self._build_network_provider = build_network_provider
        self.runtime = runtime or os.environ.get("ARENA_DOCKER_RUNTIME", "runc")
        self.run_limits = run_limits
        self.build_limits = build_limits
        # Base dir for per-submission workdirs. Under DooD (worker in a container,
        # submissions run by the host daemon) this MUST be a host path that is
        # bind-mounted into the worker at the SAME path, so the `-v {work}:/work`
        # source resolves on the host. None => system temp (local/dev/test).
        self.work_dir = work_dir or os.environ.get("ARENA_WORK_DIR") or None

    def run(self, spec: RunSpec) -> RunResult:
        try:
            preset = get_preset(spec.preset)
        except ValueError as exc:
            return RunResult("error", "", str(exc), None, 0)

        with tempfile.TemporaryDirectory(dir=self.work_dir) as work:
            try:
                write_files(work, spec.files)
            except ValueError as exc:
                return RunResult("error", "", str(exc), None, 0)
            # Drop the fixed problem data in (unless the submitter uploaded same-named files).
            copy_problem_data(work, set(spec.files))
            # tempfile makes the workdir 0700; the run phase executes as uid 65534
            # (nobody) and on a real Linux/gVisor host can't traverse/read it otherwise.
            make_world_readable(work)

            build_cmd = effective_build_cmd(spec)
            if build_cmd:
                # The build phase mounts /work rw and runs as the image-default user,
                # which under gVisor can't write into the 0755 worker-owned dir — widen
                # dirs so the linker can emit artifacts (the run phase remounts /work ro).
                make_dirs_writable(work)
                res = self._build(preset, work, build_cmd)
                if res.status != "ok":
                    return res

            return self._run_phase(preset, work, effective_run_cmd(spec), spec.stdin)

    def _run_phase(self, preset: Preset, work: str, run_cmd: str, stdin: str) -> RunResult:
        name = "arena-run-" + uuid.uuid4().hex[:12]
        args = self._common_args(name, work, self.run_limits, writable_work=False)
        args += ["--network", "none"]
        if stdin:
            args += ["--interactive"]
        args += [preset.run_image, "sh", "-c", run_cmd]
        outcome = self.docker.run(args, timeout_s=self.run_limits.wall_s, stdin=stdin, kill_name=name)
        return self._to_result(outcome, self.run_limits, build_phase=False)

    def _build(self, preset: Preset, work: str, build_cmd: str) -> RunResult:
        name = "arena-build-" + uuid.uuid4().hex[:12]
        if preset.build_needs_network:
            provider = self._build_network_provider or _default_build_network
            net_ctx = provider()
        else:
            net_ctx = nullcontext((None, {}))
        with net_ctx as (network, proxy_env):
            args = self._common_args(name, work, self.build_limits,
                                     writable_work=True, tmpfs_exec=True,
                                     tmpfs_size_mb=512)
            if network:
                args += ["--network", network]
                for key, value in proxy_env.items():
                    args += ["--env", f"{key}={value}"]
            else:
                args += ["--network", "none"]
            args += [preset.build_image, "sh", "-c", build_cmd]
            outcome = self.docker.run(args, timeout_s=self.build_limits.wall_s, kill_name=name)
        return self._to_result(outcome, self.build_limits, build_phase=True)

    def _common_args(self, name: str, work: str, limits: ResourceLimits, *,
                     writable_work: bool, tmpfs_exec: bool = False,
                     tmpfs_size_mb: int = 64) -> list[str]:
        mount = f"{work}:/work" + ("" if writable_work else ":ro")
        # /tmp is the only writable surface for untrusted RUN code. Mount it noexec
        # so a submission cannot drop+execute a payload there (which would partially
        # defeat --read-only + /work:ro). The build phase (Task 12) opts into exec
        # because some toolchains exec helper scripts from temp, and gets a larger
        # size (Task 21) so real dependency caches (Maven plugins, cargo/go caches) fit.
        tmpfs_opt = f"/tmp:rw,size={tmpfs_size_mb}m," + ("exec" if tmpfs_exec else "noexec")
        args = [
            "run", "--rm", "--name", name,
            "--runtime", self.runtime,
            "--memory", f"{limits.memory_mb}m", "--memory-swap", f"{limits.memory_mb}m",
            "--cpus", str(limits.cpus),
            "--pids-limit", str(limits.pids),
            "--ulimit", f"nofile={NOFILE_LIMIT}:{NOFILE_LIMIT}",
            "--cgroupns", "private",
            "--read-only",
            "--tmpfs", tmpfs_opt,
            "--cap-drop", "ALL",
            "--security-opt", "no-new-privileges",
            "--workdir", "/work",
            "--volume", mount,
        ]
        # Run phase drops to an unprivileged user; the build phase (Task 12) keeps the
        # image-default user so it can write artifacts into the bind-mounted workdir.
        if not writable_work:
            args += ["--user", "65534:65534"]
        return args

    def _to_result(self, outcome: DockerOutcome, limits: ResourceLimits, *,
                   build_phase: bool) -> RunResult:
        stdout = _truncate_bytes(outcome.stdout, limits.output_bytes)
        stderr = _truncate_bytes(outcome.stderr, limits.output_bytes)
        if outcome.timed_out:
            return RunResult("timeout", stdout, stderr, None, outcome.duration_ms)
        if outcome.exit_code != 0:
            reason = stderr.strip() or stdout.strip() or ("build failed" if build_phase else "run failed")
            return RunResult("error", stdout, reason, outcome.exit_code, outcome.duration_ms)
        return RunResult("ok", stdout, stderr, outcome.exit_code, outcome.duration_ms)


def _truncate_bytes(text: str, max_bytes: int) -> str:
    encoded = text.encode("utf-8")
    if len(encoded) <= max_bytes:
        return text
    return encoded[:max_bytes].decode("utf-8", errors="ignore")


def _default_build_network():
    # Imported lazily so unit tests never touch real Docker provisioning.
    from .build_network import build_network
    return build_network()
