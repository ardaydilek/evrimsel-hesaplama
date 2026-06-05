import pytest

from arena_core.presets import PRESETS, get_preset, effective_build_cmd, effective_run_cmd
from arena_core.run_spec import RunSpec


def test_six_presets_registered():
    assert set(PRESETS) == {"python", "cpp", "go", "rust", "node", "java"}


def test_get_unknown_preset_raises():
    with pytest.raises(ValueError, match="unknown preset"):
        get_preset("brainfuck")


def test_effective_commands_use_defaults_when_none():
    spec = RunSpec(preset="cpp", files={"main.cpp": ""})
    assert effective_build_cmd(spec) == "make"
    assert effective_run_cmd(spec) == "./solver"


def test_effective_commands_honor_overrides():
    spec = RunSpec(preset="cpp", files={"main.cpp": ""},
                   build_cmd="g++ main.cpp -o solver", run_cmd="./solver --fast")
    assert effective_build_cmd(spec) == "g++ main.cpp -o solver"
    assert effective_run_cmd(spec) == "./solver --fast"


def test_python_has_no_default_build():
    assert effective_build_cmd(RunSpec(preset="python", files={"main.py": ""})) is None


def test_networked_build_flag():
    assert get_preset("go").build_needs_network is True
    assert get_preset("cpp").build_needs_network is False
