from click.testing import CliRunner
from path import Path

from temply.temply import main


def test_no_template():
    runner = CliRunner()
    result = runner.invoke(main)
    assert result.exit_code == 2
    assert 'Missing argument' in result.stdout


def test_wrong_template():
    runner = CliRunner()
    result = runner.invoke(main, args=['unknown'])
    assert result.exit_code == 1
    assert 'Must be a regular file' in result.stdout


def test_missing_env():
    runner = CliRunner()
    result = runner.invoke(main, args=['tests/fixtures/simple.tpl'], env={})
    assert result.exit_code == 1


def test_missing_env_allowed():
    runner = CliRunner()
    result = runner.invoke(main, args=['--allow-missing', 'tests/fixtures/simple.tpl'], env={})
    assert result.exit_code == 0
    assert result.output == 'Hello world: \n'


def test_simple_template():
    runner = CliRunner()
    result = runner.invoke(main, args=['tests/fixtures/simple.tpl'], env={'simple': '1'})
    assert result.exit_code == 0
    assert result.output == 'Hello world: 1\n'


def test_include_template():
    runner = CliRunner()
    result = runner.invoke(main, args=['tests/fixtures/include.tpl'], env={'simple': '1'})
    assert result.exit_code == 0
    assert result.output == 'Hello world: 1\n'


def test_advanced_template():
    runner = CliRunner()
    result = runner.invoke(main, args=['tests/fixtures/advanced.tpl'], env={'simple': '1', 'foo': 'bar'})
    assert result.exit_code == 0
    assert result.output == '1\nfoobar\ndefined\n\n'


def test_doc_template():
    runner = CliRunner()
    result = runner.invoke(main, args=['tests/fixtures/doc.tpl'], env={'variable': 'foo', 'another_one': 'bar'})
    assert result.exit_code == 0
    assert result.output == "variable = 'foo'\nanother_one = 'bar'\ndefault_var = 'default'\n"


def test_json_template():
    runner = CliRunner()
    result = runner.invoke(main, args=['tests/fixtures/json.tpl'], env={'json_var': '[]'})
    assert result.exit_code == 0
    assert result.output == "[]\n[]\n"


def test_envs_template():
    runner = CliRunner()
    result = runner.invoke(main, args=['tests/fixtures/envs.tpl'], env={'MY_FOO': 'foo', 'MY_BAR': 'bar'})
    assert result.exit_code == 0
    assert result.output == "BAR = bar\nFOO = foo\n\n"


def test_output_file():
    runner = CliRunner()
    result = runner.invoke(main, args=['-o', '/tmp/output', 'tests/fixtures/simple.tpl'], env={'simple': '1'})
    assert result.exit_code == 0
    assert result.output == ''
    assert Path('/tmp/output').read_text() == 'Hello world: 1'
    Path('/tmp/output').remove()
