from pathlib import Path

import pytest
from click.testing import CliRunner

from temply.cli import main


def test_template(runner: CliRunner) -> None:
    result = runner.invoke(main, input="Hello {{ name }} !", env={"name": "world"})
    assert result.exit_code == 0
    assert result.output == "Hello world !"


def test_missing_env(runner: CliRunner) -> None:
    result = runner.invoke(main, input="Hello {{ name }} !")
    assert result.exit_code == 1
    assert "'name' is undefined" in result.stderr


def test_allow_missing_env(runner: CliRunner) -> None:
    result = runner.invoke(main, args=["--allow-missing"], input="Hello {{ name }} !")
    assert result.exit_code == 0
    assert result.output == "Hello  !"


def test_output_file(runner: CliRunner, tmp_path: Path) -> None:
    output = tmp_path / "output"
    result = runner.invoke(
        main,
        input="Hello {{ name }} !",
        args=["-o", output.as_posix()],
        env={"name": "world"},
    )
    assert result.exit_code == 0
    assert result.output == ""
    assert output.read_text() == "Hello world !"


def test_include(
    runner: CliRunner, fixtures: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(fixtures)
    result = runner.invoke(
        main, input='{% include "simple.tpl" %}', env={"simple": "1"}
    )
    assert result.exit_code == 0
    assert result.output == "Hello world: 1"
