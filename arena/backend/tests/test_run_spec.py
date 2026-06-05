from arena_core.run_spec import RunSpec, ResourceLimits


def test_runspec_minimal_defaults():
    spec = RunSpec(preset="python", files={"main.py": "print('hi')"})
    assert spec.mode == "preset"
    assert spec.build_cmd is None
    assert spec.run_cmd is None
    assert spec.stdin == ""


def test_runspec_carries_files_and_overrides():
    spec = RunSpec(
        preset="cpp",
        files={"main.cpp": "int main(){}", "Makefile": "all:\n\tg++ main.cpp -o solver"},
        build_cmd="make", run_cmd="./solver", stdin="data",
    )
    assert "Makefile" in spec.files
    assert spec.build_cmd == "make"
    assert spec.run_cmd == "./solver"
    assert spec.stdin == "data"


def test_resource_limits_fields():
    lim = ResourceLimits(memory_mb=512, cpus=1.0, wall_s=10, pids=128, output_bytes=1_000_000)
    assert lim.memory_mb == 512
    assert lim.cpus == 1.0
    assert lim.wall_s == 10
    assert lim.pids == 128
    assert lim.output_bytes == 1_000_000
