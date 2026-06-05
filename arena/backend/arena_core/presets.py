"""The preset registry: language preset -> toolchain image + default build/run commands.

Adding a language is a data change here, not new runner code. Submitters may override
build_cmd/run_cmd per submission; None means "use the preset default". Image tags are
the local names produced by docker/build-presets.sh.
"""
from __future__ import annotations

from dataclasses import dataclass

from .run_spec import RunSpec


@dataclass(frozen=True, slots=True)
class Preset:
    name: str
    build_image: str
    run_image: str
    default_build_cmd: str | None
    default_run_cmd: str
    build_needs_network: bool


PRESETS: dict[str, Preset] = {
    "python": Preset("python", "arena/python:1", "arena/python:1", None, "python3 main.py", False),
    "cpp":    Preset("cpp", "arena/cpp:1", "arena/cpp:1", "make", "./solver", False),
    "go":     Preset("go", "arena/go:1", "arena/go:1", "go build -o solver ./...", "./solver", True),
    "rust":   Preset("rust", "arena/rust:1", "arena/rust:1", "cargo build --release",
                     "./target/release/solver", True),
    "node":   Preset("node", "arena/node:1", "arena/node:1", "npm ci", "node main.js", True),
    "java":   Preset("java", "arena/java:1", "arena/java:1", "mvn -q package",
                     "java -jar target/app.jar", True),
}


def get_preset(name: str) -> Preset:
    try:
        return PRESETS[name]
    except KeyError:
        raise ValueError(f"unknown preset: {name}") from None


def effective_build_cmd(spec: RunSpec) -> str | None:
    p = get_preset(spec.preset)
    return spec.build_cmd if spec.build_cmd is not None else p.default_build_cmd


def effective_run_cmd(spec: RunSpec) -> str:
    p = get_preset(spec.preset)
    return spec.run_cmd if spec.run_cmd is not None else p.default_run_cmd
