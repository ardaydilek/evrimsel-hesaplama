"""Safely materialize a submission's files into a working directory, and validate
the files map against the upload contract.

Submission paths are untrusted: every path must be relative with no '..' segment and
not absolute, else a submission could escape its sandbox workdir (path traversal /
Zip-Slip). Used by LocalRunner, ContainerRunner (materialize) and the API
(validate-before-store).

Defense in depth (string checks + a resolved-path containment backstop), per current
guidance for preventing Zip-Slip in Python:
  1. reject empty / NUL-containing paths,
  2. reject absolute paths and leading separators (POSIX '/' and Windows '\\'),
  3. normalize and reject any '..' segment (backslash treated as a separator too, so a
     Windows-style traversal can't slip through on a POSIX host and be reinterpreted
     downstream),
  4. when writing, verify the realpath of the destination is contained within the
     realpath of the root before creating anything (catches anything the string
     checks might ever miss, including symlink games).
"""
from __future__ import annotations

import os

MAX_FILES = 64
MAX_TOTAL_BYTES = 256 * 1024


def _safe_relpath(relpath: str) -> str:
    """Return a normalized, sandbox-safe relative path, or raise ValueError.

    The error message contains either "relative" (path is absolute / not relative)
    or "traversal" (path escapes via '..'); callers and tests rely on this.
    """
    if not relpath:
        raise ValueError("file path must be relative: ''")
    if "\x00" in relpath:
        # A NUL byte can truncate the path at the OS layer; reject outright rather
        # than let open() raise an opaque error.
        raise ValueError(f"file path contains NUL byte: {relpath!r}")
    if relpath.startswith("/") or relpath.startswith("\\"):
        raise ValueError(f"file path must be relative: {relpath!r}")

    # Treat backslash as a separator regardless of host OS so a Windows-style
    # traversal ("..\\x") cannot pass on POSIX and be reinterpreted elsewhere.
    unified = relpath.replace("\\", "/")
    norm = os.path.normpath(unified)
    # os.path.normpath on POSIX keeps '/' as the separator; split on both to be safe.
    segments = norm.replace("\\", "/").split("/")
    if (
        os.path.isabs(norm)
        or norm == ".."
        or norm.startswith("../")
        or ".." in segments
    ):
        raise ValueError(f"unsafe file path (traversal): {relpath!r}")
    if norm == ".":
        # e.g. "foo/.." or ".": normalizes to the root dir itself, which is not a
        # valid file destination (open(root, "w") would be an opaque IsADirectoryError).
        raise ValueError(f"file path resolves to the directory itself: {relpath!r}")
    return norm


def write_files(root: str, files: dict[str, str]) -> None:
    """Write each (relpath -> content) under ``root``, creating parent dirs.

    Every path is validated with ``_safe_relpath`` and, as a backstop, the resolved
    destination is confirmed to live inside the resolved ``root`` before any write.
    Raises ValueError on any unsafe path; nothing is written for that entry.
    """
    root_real = os.path.realpath(root)
    for relpath, content in files.items():
        safe = _safe_relpath(relpath)
        dest = os.path.join(root, safe)
        # Containment backstop: the resolved dest must be root itself or under it.
        dest_real = os.path.realpath(dest)
        if dest_real != root_real and os.path.commonpath([root_real, dest_real]) != root_real:
            raise ValueError(f"unsafe file path (traversal): {relpath!r}")
        os.makedirs(os.path.dirname(dest) or root, exist_ok=True)
        with open(dest, "w") as f:
            f.write(content)


def make_world_readable(root: str) -> None:
    """Make ``root`` and everything under it traversable/readable by the unprivileged
    run user (uid 65534).

    ``tempfile`` creates the workdir as mode 0700 and the process umask may restrict
    the written files; the run-phase container executes as uid 65534 (nobody) for
    hardening, and on a real Linux host (esp. under gVisor) it genuinely cannot
    traverse a 0700 dir or read 0600 files. Docker Desktop's file sharing is permissive
    enough to hide this, so it only surfaces on the deployed host. Safe to widen: the
    workdir is per-submission, ephemeral, and the run container is *supposed* to read it.
    """
    os.chmod(root, 0o755)
    for dirpath, dirnames, filenames in os.walk(root):
        for name in dirnames:
            os.chmod(os.path.join(dirpath, name), 0o755)
        for name in filenames:
            os.chmod(os.path.join(dirpath, name), 0o644)


def make_dirs_writable(root: str) -> None:
    """Make ``root`` and every directory under it writable by any uid, so the build
    container can create artifacts (object files, the output binary) in the workdir.

    The build phase mounts ``/work`` read-write but runs as the build image's *default*
    user (root), while the workdir is owned by the worker's uid (10001). The build
    container runs with ``--cap-drop ALL``, so its root has **no CAP_DAC_OVERRIDE** and
    cannot bypass file permissions: against a 0755 dir owned by another uid it is denied
    write, and the linker fails with ``cannot open output file solver: Permission
    denied``. Docker Desktop's permissive file sharing hides this locally; it only
    surfaces on the deployed host (gVisor enforces it) — the same way the run-phase read
    bug did (see :func:`make_world_readable`).

    Only directories are widened to 0777; existing source files keep their mode (the
    build creates *new* files in the now-writable dirs rather than rewriting inputs). The
    run phase remounts ``/work`` read-only, so this is invisible there, and the workdir
    is per-submission and ephemeral.
    """
    os.chmod(root, 0o777)
    for dirpath, dirnames, _ in os.walk(root):
        for name in dirnames:
            os.chmod(os.path.join(dirpath, name), 0o777)


def check_files(files: dict[str, str], *, max_files: int = MAX_FILES,
                max_total_bytes: int = MAX_TOTAL_BYTES) -> None:
    """Validate the upload contract; raise ValueError with a submitter-facing message."""
    if not files:
        raise ValueError("at least one file is required")
    if len(files) > max_files:
        raise ValueError(f"too many files: {len(files)} > {max_files}")
    total = sum(len(c.encode("utf-8")) for c in files.values())
    if total > max_total_bytes:
        raise ValueError(f"upload too large: {total} bytes > {max_total_bytes}")
    for relpath in files:
        _safe_relpath(relpath)
