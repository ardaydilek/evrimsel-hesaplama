import os

import pytest

from arena_core.workdir import (
    write_files, check_files, make_world_readable, make_dirs_writable,
)


def test_writes_nested_files(tmp_path):
    write_files(str(tmp_path), {"a.py": "x=1", "pkg/b.py": "y=2"})
    assert (tmp_path / "a.py").read_text() == "x=1"
    assert (tmp_path / "pkg" / "b.py").read_text() == "y=2"


def test_make_world_readable_sets_traversable_perms(tmp_path):
    # The run container is uid 65534 (nobody); a 0700 workdir / 0600 files block it on
    # real Linux. make_world_readable must widen the dir tree to 0755 + files to 0644.
    root = tmp_path / "wd"
    root.mkdir(mode=0o700)
    write_files(str(root), {"main.py": "print(1)", "sub/util.py": "x=1"})
    os.chmod(root / "main.py", 0o600)  # simulate a restrictive umask
    make_world_readable(str(root))
    assert os.stat(root).st_mode & 0o777 == 0o755
    assert os.stat(root / "sub").st_mode & 0o777 == 0o755
    assert os.stat(root / "main.py").st_mode & 0o777 == 0o644
    assert os.stat(root / "sub" / "util.py").st_mode & 0o777 == 0o644


def test_make_dirs_writable_widens_dirs_keeps_files(tmp_path):
    # The build container runs as the image-default user and can't write into the
    # 0755 worker-owned workdir under gVisor. make_dirs_writable opens the dir tree
    # to 0777 so the linker can emit artifacts, while leaving source files untouched.
    root = tmp_path / "wd"
    root.mkdir(mode=0o755)
    write_files(str(root), {"main.cpp": "x", "sub/util.cpp": "y"})
    os.chmod(root / "main.cpp", 0o644)
    make_dirs_writable(str(root))
    assert os.stat(root).st_mode & 0o777 == 0o777
    assert os.stat(root / "sub").st_mode & 0o777 == 0o777
    assert os.stat(root / "main.cpp").st_mode & 0o002 == 0  # files not widened


def test_write_rejects_absolute_path(tmp_path):
    with pytest.raises(ValueError, match="relative"):
        write_files(str(tmp_path), {"/etc/passwd": "bad"})


def test_write_rejects_parent_traversal(tmp_path):
    with pytest.raises(ValueError, match="traversal"):
        write_files(str(tmp_path), {"../escape.py": "bad"})


def test_check_files_rejects_empty():
    with pytest.raises(ValueError, match="at least one file"):
        check_files({})


def test_check_files_rejects_too_many():
    with pytest.raises(ValueError, match="too many files"):
        check_files({f"f{i}.py": "" for i in range(65)}, max_files=64)


def test_check_files_rejects_too_large():
    with pytest.raises(ValueError, match="too large"):
        check_files({"big.txt": "x" * 1001}, max_total_bytes=1000)


def test_check_files_rejects_traversal():
    with pytest.raises(ValueError, match="traversal"):
        check_files({"../x": "y"})


def test_check_files_accepts_valid():
    check_files({"main.py": "print(1)", "pkg/util.py": "x=1"})  # no raise


# --- Hardening tests (traversal-defense edge cases) ---------------------------
# These guard against bypasses of the string-level checks. See workdir.py for the
# rationale; the security boundary must hold against every one of these.

@pytest.mark.parametrize(
    "bad",
    [
        "a/../../b",      # escapes after normalization
        "./../x",         # leading ./ then parent
        "sub/../../x",    # escapes via nested ..
        "..",             # bare parent
        "../../etc/passwd",
        "foo/../../bar",
    ],
)
def test_check_files_rejects_traversal_variants(bad):
    with pytest.raises(ValueError, match="traversal"):
        check_files({bad: "x"})


@pytest.mark.parametrize("bad", ["/abs", "/etc/passwd", "//double", "/"])
def test_check_files_rejects_absolute_variants(bad):
    with pytest.raises(ValueError, match="relative"):
        check_files({bad: "x"})


@pytest.mark.parametrize("bad", ["..\\x", "..\\..\\x", "pkg\\..\\..\\x", "\\abs"])
def test_check_files_rejects_backslash_traversal(bad):
    # Backslash must be treated as a separator regardless of host OS, so a
    # Windows-style traversal cannot slip through on a POSIX runner and then be
    # reinterpreted elsewhere. Leading backslash is rejected as non-relative.
    with pytest.raises(ValueError):
        check_files({bad: "x"})


@pytest.mark.parametrize("bad", ["\x00abc", "a/\x00/b", "ok.py\x00.txt"])
def test_check_files_rejects_null_byte(bad):
    with pytest.raises(ValueError):
        check_files({bad: "x"})


def test_write_rejects_backslash_traversal_on_posix(tmp_path):
    # Even though "..\\x" is a single literal filename on POSIX, treating
    # backslash as a separator is the safe, portable choice.
    with pytest.raises(ValueError):
        write_files(str(tmp_path), {"pkg\\..\\..\\x": "bad"})


def test_write_does_not_escape_root(tmp_path):
    # Belt-and-suspenders: nothing accepted by write_files lands outside root.
    root = tmp_path / "root"
    root.mkdir()
    sentinel = tmp_path / "escape.txt"
    write_files(str(root), {"deep/nested/ok.py": "safe"})
    assert (root / "deep" / "nested" / "ok.py").read_text() == "safe"
    assert not sentinel.exists()


@pytest.mark.parametrize("bad", [".", "foo/..", "a/b/../.."])
def test_check_files_rejects_paths_resolving_to_root(bad):
    # A path that normalizes to the directory itself is not a valid file target.
    with pytest.raises(ValueError):
        check_files({bad: "x"})


def test_check_files_accepts_dotted_names():
    # A leading dot in a *filename* (not a path segment) is fine.
    check_files({".gitignore": "*.pyc", "pkg/.keep": "", "a.b.c.py": "x=1"})
