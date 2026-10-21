from pathlib import Path

import pytest
from click.testing import CliRunner

from temply.cli import main


def render(
    runner: CliRunner,
    template: Path,
    *args: str,
    env: dict[str, str] | None = None,
):
    return runner.invoke(
        main, args=["--keep-template", *args, template.as_posix()], env=env
    )


def test_wrong_file_template(runner: CliRunner) -> None:
    result = runner.invoke(main, args=["unknown"])
    assert result.exit_code == 2
    assert "does not exist" in result.stderr


def test_missing_env(runner: CliRunner, fixtures: Path) -> None:
    result = render(runner, fixtures / "simple.tpl")
    assert result.exit_code == 1
    assert "'simple' is undefined" in result.stderr
    assert "Traceback" not in result.output


def test_allow_missing_env(runner: CliRunner, fixtures: Path) -> None:
    result = render(runner, fixtures / "simple.tpl", "--allow-missing")
    assert result.exit_code == 0
    assert result.output == "Hello world: "


def test_template_removed_by_default(runner: CliRunner, tmp_path: Path) -> None:
    template = tmp_path / "template.tpl"
    template.write_text("Hello {{ name }} !")

    result = runner.invoke(main, args=[template.as_posix()], env={"name": "world"})
    assert result.exit_code == 0
    assert result.output == "Hello world !"
    assert not template.exists()


def test_keep_template(runner: CliRunner, tmp_path: Path) -> None:
    template = tmp_path / "template.tpl"
    template.write_text("Hello {{ name }} !")

    result = render(runner, template, env={"name": "world"})
    assert result.exit_code == 0
    assert template.exists()


def test_template_kept_on_render_error(runner: CliRunner, tmp_path: Path) -> None:
    template = tmp_path / "template.tpl"
    template.write_text("Hello {{ name }} !")

    result = runner.invoke(main, args=[template.as_posix()])
    assert result.exit_code == 1
    assert template.exists()


def test_template_kept_on_output_error(runner: CliRunner, tmp_path: Path) -> None:
    template = tmp_path / "template.tpl"
    template.write_text("Hello {{ name }} !")
    output = tmp_path / "missing" / "output"

    result = runner.invoke(
        main, args=["-o", output.as_posix(), template.as_posix()], env={"name": "w"}
    )
    assert result.exit_code == 1
    assert template.exists()
    assert not output.exists()


def test_output_file(runner: CliRunner, fixtures: Path, tmp_path: Path) -> None:
    output = tmp_path / "output"
    result = render(
        runner, fixtures / "simple.tpl", "-o", output.as_posix(), env={"simple": "1"}
    )
    assert result.exit_code == 0
    assert result.output == ""
    assert output.read_text() == "Hello world: 1"


def test_stdout_preserves_trailing_newline(runner: CliRunner, tmp_path: Path) -> None:
    template = tmp_path / "template.tpl"
    template.write_text("a\n")
    result = render(runner, template)
    assert result.exit_code == 0
    assert result.output == "a\n"


@pytest.mark.parametrize("name", ["simple.tpl", "include.tpl"])
def test_simple_template(runner: CliRunner, fixtures: Path, name: str) -> None:
    result = render(runner, fixtures / name, env={"simple": "1"})
    assert result.exit_code == 0
    assert result.output == "Hello world: 1"


def test_advanced_template(runner: CliRunner, fixtures: Path) -> None:
    result = render(runner, fixtures / "advanced.tpl", env={"simple": "1", "foo": "b"})
    assert result.exit_code == 0
    assert result.output == "1\nfoobar\ndefined\n"


def test_doc_template(runner: CliRunner, fixtures: Path) -> None:
    result = render(
        runner,
        fixtures / "doc.tpl",
        env={"variable": "foo", "another_one": "bar"},
    )
    assert result.exit_code == 0
    assert (
        result.output
        == "variable = 'foo'\nanother_one = 'bar'\ndefault_var = 'default'\n"
    )


def test_json_template(runner: CliRunner, fixtures: Path) -> None:
    result = render(
        runner, fixtures / "json.tpl", env={"json_var": '{"a": ["é", 1, true]}'}
    )
    assert result.exit_code == 0
    assert result.output == '{"a": ["é", 1, true]}\n{"a": ["é", 1, true]}\n'


def test_invalid_json_value(runner: CliRunner, fixtures: Path) -> None:
    result = render(runner, fixtures / "json.tpl", env={"json_var": "{"})
    assert result.exit_code == 1
    assert "Unable to render template" in result.stderr


def test_yaml_template(runner: CliRunner, fixtures: Path) -> None:
    yaml_var = """
    obj:
      key-one: "val"
      key-two: "é"
    arr:
      - "str"
    """
    result = render(runner, fixtures / "yaml.tpl", env={"yaml_var": yaml_var})
    assert result.exit_code == 0
    expected = "arr:\n- str\nobj:\n  key-one: val\n  key-two: é\n"
    assert result.output == expected * 2


@pytest.mark.parametrize(
    ("value", "expected"),
    [("foo", "foo"), ("42", "42"), ("true", "true")],
)
def test_yaml_scalar(
    runner: CliRunner, tmp_path: Path, value: str, expected: str
) -> None:
    template = tmp_path / "template.tpl"
    template.write_text("{{ foo | from_yaml | to_yaml }}")
    result = render(runner, template, env={"foo": value})
    assert result.exit_code == 0
    assert result.output == expected


@pytest.mark.parametrize(
    ("args", "env", "expected"),
    [
        ([], {"MY_FOO": "foo", "MY_BAR": "bar"}, "BAR = bar\nFOO = foo\n"),
        (
            ["--envdir", "envdir"],
            {"MY_FOO": "foo", "MY_BAR": "bar"},
            "BAR = bar\nFOO =     bar\n",
        ),
        (
            ["--dotenv", "dotenv"],
            {"MY_FOO": "foo", "MY_BAR": "bar"},
            "BAR = foobar\nFOO = foo\n",
        ),
        (["--json-file", "envs.json"], {}, "key.secret = value-of-secret\n"),
    ],
)
def test_loaders(
    runner: CliRunner,
    fixtures: Path,
    args: list[str],
    env: dict[str, str],
    expected: str,
) -> None:
    args = [
        arg if arg.startswith("--") else (fixtures / arg).as_posix() for arg in args
    ]
    result = render(runner, fixtures / "envs.tpl", *args, env=env)
    assert result.exit_code == 0, result.output
    assert result.output == expected


def test_loaders_precedence(runner: CliRunner, fixtures: Path, tmp_path: Path) -> None:
    envdir = tmp_path / "envdir"
    envdir.mkdir()
    (envdir / "MY_A").write_text("envdir")
    (envdir / "MY_B").write_text("envdir")
    (envdir / "MY_C").write_text("envdir")
    dotenv = tmp_path / "dotenv"
    dotenv.write_text("MY_B=dotenv\nMY_C=dotenv\n")
    json_file = tmp_path / "envs.json"
    json_file.write_text('{"MY_C": "json"}')

    result = render(
        runner,
        fixtures / "envs.tpl",
        "--json-file",
        json_file.as_posix(),
        "--dotenv",
        dotenv.as_posix(),
        "--envdir",
        envdir.as_posix(),
        env={"MY_A": "env", "MY_D": "env"},
    )
    assert result.exit_code == 0, result.output
    assert result.output == "A = envdir\nB = dotenv\nC = json\nD = env\n"


def test_envdir_edge_cases(runner: CliRunner, fixtures: Path, tmp_path: Path) -> None:
    envdir = tmp_path / "envdir"
    envdir.mkdir()
    (envdir / "MY_UNSET").write_text("")
    (envdir / "MY_MULTI").write_text("a\x00b\n\n")
    (envdir / ".hidden").write_bytes(b"\xff\xfe")
    (envdir / "sub").mkdir()
    (envdir / "sub" / "MY_NESTED").write_text("nested")

    result = render(
        runner,
        fixtures / "envs.tpl",
        "--envdir",
        envdir.as_posix(),
        env={"MY_UNSET": "from-env"},
    )
    assert result.exit_code == 0, result.output
    assert result.output == "MULTI = a\nb\n"


def test_dotenv_edge_cases(runner: CliRunner, fixtures: Path, tmp_path: Path) -> None:
    dotenv = tmp_path / "dotenv"
    dotenv.write_text(
        "﻿# comment\n"
        "\n"
        "MY_A=plain\n"
        "export MY_B=exported\n"
        'MY_C="double quoted"\n'
        "MY_D='single quoted'\n"
        "MY_E = spaced \n"
        "MY_F=with=equals\n"
        "MY_G=\r\n",
        encoding="utf-8",
    )
    result = render(runner, fixtures / "envs.tpl", "--dotenv", dotenv.as_posix())
    assert result.exit_code == 0, result.output
    assert result.output == (
        "A = plain\nB = exported\nC = double quoted\nD = single quoted\n"
        "E = spaced\nF = with=equals\nG = \n"
    )


def test_wrong_dotenv_line(runner: CliRunner, fixtures: Path, tmp_path: Path) -> None:
    dotenv = tmp_path / "dotenv"
    dotenv.write_text("MY_A=a\nINVALID\n")
    result = render(runner, fixtures / "envs.tpl", "--dotenv", dotenv.as_posix())
    assert result.exit_code == 1
    assert "line 2" in result.stderr


def test_wrong_dotenv_template(runner: CliRunner, fixtures: Path) -> None:
    result = render(
        runner, fixtures / "envs.tpl", "--dotenv", (fixtures / "missing").as_posix()
    )
    assert result.exit_code == 2
    assert "does not exist" in result.stderr


@pytest.mark.parametrize("content", ["{", "[1, 2]", '"str"'])
def test_wrong_json_file(
    runner: CliRunner, fixtures: Path, tmp_path: Path, content: str
) -> None:
    json_file = tmp_path / "envs.json"
    json_file.write_text(content)
    result = render(runner, fixtures / "envs.tpl", "--json-file", json_file.as_posix())
    assert result.exit_code == 1
    assert "Traceback" not in result.output


def test_envdir_with_bom(runner: CliRunner, fixtures: Path, tmp_path: Path) -> None:
    envdir = tmp_path / "envdir"
    envdir.mkdir()
    (envdir / "MY_A").write_text("﻿value", encoding="utf-8")
    result = render(runner, fixtures / "envs.tpl", "--envdir", envdir.as_posix())
    assert result.exit_code == 0, result.output
    assert result.output == "A = value\n"


def test_json_file_with_bom(runner: CliRunner, fixtures: Path, tmp_path: Path) -> None:
    json_file = tmp_path / "envs.json"
    json_file.write_text('﻿{"MY_A": "value"}', encoding="utf-8")
    result = render(runner, fixtures / "envs.tpl", "--json-file", json_file.as_posix())
    assert result.exit_code == 0, result.output
    assert result.output == "A = value\n"
