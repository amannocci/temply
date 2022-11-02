from pathlib import Path

from click.testing import CliRunner

from temply.temply import main
from tests import PROJECT_ROOT_DIR

runner: CliRunner = CliRunner()


def setup_function():
    global runner
    runner = CliRunner()


def test_wrong_file_template():
    result = runner.invoke(main, args=["unknown"])
    assert result.exit_code == 1
    assert "Must be a regular file" in result.stdout


def test_missing_env():
    path = (PROJECT_ROOT_DIR / "tests" / "fixtures" / "simple.tpl").as_posix()
    result = runner.invoke(main, args=["--keep-template", path], env={})
    assert result.exit_code == 1


def test_allow_missing_env():
    path = (PROJECT_ROOT_DIR / "tests" / "fixtures" / "simple.tpl").as_posix()
    result = runner.invoke(main, args=["--keep-template", "--allow-missing", path], env={})
    assert result.exit_code == 0
    assert result.output == "Hello world: \n"


def test_keep_template():
    Path("/tmp/output.tpl").write_text("Hello {{ name }} !")

    result = runner.invoke(main, args=["/tmp/output.tpl"], env={"name": "world"})
    assert result.exit_code == 0
    assert result.output == "Hello world !\n"
    assert not Path("/tmp/output.tpl").exists()


def test_output_file():
    path = (PROJECT_ROOT_DIR / "tests" / "fixtures" / "simple.tpl").as_posix()
    result = runner.invoke(main, args=["--keep-template", "-o", "/tmp/output", path], env={"simple": "1"})
    assert result.exit_code == 0
    assert result.output == ""
    assert Path("/tmp/output").read_text() == "Hello world: 1"
    Path("/tmp/output").unlink()


def test_simple_template():
    path = (PROJECT_ROOT_DIR / "tests" / "fixtures" / "simple.tpl").as_posix()
    result = runner.invoke(main, args=["--keep-template", path], env={"simple": "1"})
    assert result.exit_code == 0
    assert result.output == "Hello world: 1\n"


def test_include_template():
    path = (PROJECT_ROOT_DIR / "tests" / "fixtures" / "include.tpl").as_posix()
    result = runner.invoke(main, args=["--keep-template", path], env={"simple": "1"})
    assert result.exit_code == 0
    assert result.output == "Hello world: 1\n"


def test_advanced_template():
    path = (PROJECT_ROOT_DIR / "tests" / "fixtures" / "advanced.tpl").as_posix()
    result = runner.invoke(main, args=["--keep-template", path], env={"simple": "1", "foo": "bar"})
    assert result.exit_code == 0
    assert result.output == "1\nfoobar\ndefined\n\n"


def test_doc_template():
    path = (PROJECT_ROOT_DIR / "tests" / "fixtures" / "doc.tpl").as_posix()
    result = runner.invoke(main, args=["--keep-template", path], env={"variable": "foo", "another_one": "bar"})
    assert result.exit_code == 0
    assert result.output == "variable = 'foo'\nanother_one = 'bar'\ndefault_var = 'default'\n\n"


def test_json_template():
    path = (PROJECT_ROOT_DIR / "tests" / "fixtures" / "json.tpl").as_posix()
    result = runner.invoke(main, args=["--keep-template", path], env={"json_var": "[]"})
    assert result.exit_code == 0
    assert result.output == "[]\n[]\n\n"


def test_yaml_template():
    path = (PROJECT_ROOT_DIR / "tests" / "fixtures" / "yaml.tpl").as_posix()
    result = runner.invoke(
        main,
        args=["--keep-template", path],
        env={
            "yaml_var": """
    obj:
      key-one: "val"
      key-two: "val"
    arr:
      - "str"
    """
        },
    )
    assert result.exit_code == 0
    assert (
        result.output
        == "arr:\n- str\nobj:\n  key-one: val\n  key-two: val\narr:\n- str\nobj:\n  key-one: val\n  key-two: val\n\n"
    )


def test_envs_template():
    path = (PROJECT_ROOT_DIR / "tests" / "fixtures" / "envs.tpl").as_posix()
    result = runner.invoke(main, args=["--keep-template", path], env={"MY_FOO": "foo", "MY_BAR": "bar"})
    assert result.exit_code == 0
    assert result.output == "BAR = bar\nFOO = foo\n\n"


def test_envdir_template():
    path = (PROJECT_ROOT_DIR / "tests" / "fixtures" / "envs.tpl").as_posix()
    envdir_path = (PROJECT_ROOT_DIR / "tests" / "fixtures" / "envdir").as_posix()
    result = runner.invoke(
        main, args=["--keep-template", "--envdir", envdir_path, path], env={"MY_FOO": "foo", "MY_BAR": "bar"}
    )
    assert result.output == "BAR = bar\nFOO = bar\n\n"
    assert result.exit_code == 0


def test_dotenv_template():
    path = (PROJECT_ROOT_DIR / "tests" / "fixtures" / "envs.tpl").as_posix()
    dotenv_path = (PROJECT_ROOT_DIR / "tests" / "fixtures" / "dotenv").as_posix()
    result = runner.invoke(
        main, args=["--keep-template", "--dotenv", dotenv_path, path], env={"MY_FOO": "foo", "MY_BAR": "bar"}
    )
    assert result.output == "BAR = foobar\nFOO = foo\n\n"
    assert result.exit_code == 0


def test_json_file_template():
    path = (PROJECT_ROOT_DIR / "tests" / "fixtures" / "envs.tpl").as_posix()
    json_path = (PROJECT_ROOT_DIR / "tests" / "fixtures" / "envs.json").as_posix()
    result = runner.invoke(main, args=["--keep-template", "--json-file", json_path, path])
    assert result.output == "key.secret = value-of-secret\n\n"
    assert result.exit_code == 0


def test_wrong_dotenv_template():
    path = (PROJECT_ROOT_DIR / "tests" / "fixtures" / "envs.tpl").as_posix()
    wrong_dotenv_path = (PROJECT_ROOT_DIR / "tests" / "fixtures" / "wrong_dotenv").as_posix()
    result = runner.invoke(
        main, args=["--keep-template", "--dotenv", wrong_dotenv_path, path], env={"MY_FOO": "foo", "MY_BAR": "bar"}
    )
    assert "Must be a regular file" in result.output
    assert result.exit_code == 1
