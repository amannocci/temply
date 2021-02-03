from click.testing import CliRunner
from path import Path

from temply.temply import main


def test_wrong_file_template():
    runner = CliRunner()
    result = runner.invoke(main, args=['unknown'])
    assert result.exit_code == 1
    assert 'Must be a regular file' in result.stdout


def test_missing_env():
    runner = CliRunner()
    result = runner.invoke(main, args=['--keep-template', 'tests/fixtures/simple.tpl'], env={})
    assert result.exit_code == 1


def test_allow_missing_env():
    runner = CliRunner()
    result = runner.invoke(main, args=['--keep-template', '--allow-missing', 'tests/fixtures/simple.tpl'], env={})
    assert result.exit_code == 0
    assert result.output == 'Hello world: \n'


def test_keep_template():
    Path('/tmp/output.tpl').write_text('Hello {{ name }} !')

    runner = CliRunner()
    result = runner.invoke(main, args=['/tmp/output.tpl'],
                           env={'name': 'world'})
    assert result.exit_code == 0
    assert result.output == "Hello world !\n"
    assert not Path('/tmp/output.tpl').exists()


def test_output_file():
    runner = CliRunner()
    result = runner.invoke(main, args=['--keep-template', '-o', '/tmp/output', 'tests/fixtures/simple.tpl'],
                           env={'simple': '1'})
    assert result.exit_code == 0
    assert result.output == ''
    assert Path('/tmp/output').read_text() == 'Hello world: 1'
    Path('/tmp/output').remove()


def test_simple_template():
    runner = CliRunner()
    result = runner.invoke(main, args=['--keep-template', 'tests/fixtures/simple.tpl'], env={'simple': '1'})
    assert result.exit_code == 0
    assert result.output == 'Hello world: 1\n'


def test_include_template():
    runner = CliRunner()
    result = runner.invoke(main, args=['--keep-template', 'tests/fixtures/include.tpl'], env={'simple': '1'})
    assert result.exit_code == 0
    assert result.output == 'Hello world: 1\n'


def test_advanced_template():
    runner = CliRunner()
    result = runner.invoke(main, args=['--keep-template', 'tests/fixtures/advanced.tpl'],
                           env={'simple': '1', 'foo': 'bar'})
    assert result.exit_code == 0
    assert result.output == '1\nfoobar\ndefined\n\n'


def test_doc_template():
    runner = CliRunner()
    result = runner.invoke(main, args=['--keep-template', 'tests/fixtures/doc.tpl'],
                           env={'variable': 'foo', 'another_one': 'bar'})
    assert result.exit_code == 0
    assert result.output == "variable = 'foo'\nanother_one = 'bar'\ndefault_var = 'default'\n"


def test_json_template():
    runner = CliRunner()
    result = runner.invoke(main, args=['--keep-template', 'tests/fixtures/json.tpl'], env={'json_var': '[]'})
    assert result.exit_code == 0
    assert result.output == "[]\n[]\n"


def test_envs_template():
    runner = CliRunner()
    result = runner.invoke(main, args=['--keep-template', 'tests/fixtures/envs.tpl'],
                           env={'MY_FOO': 'foo', 'MY_BAR': 'bar'})
    assert result.exit_code == 0
    assert result.output == "BAR = bar\nFOO = foo\n\n"


def test_envdir_template():
    runner = CliRunner()
    result = runner.invoke(main, args=['--keep-template', '--envdir', 'tests/fixtures/envdir', 'tests/fixtures/envs.tpl'],
                           env={'MY_FOO': 'foo', 'MY_BAR': 'bar'})
    assert result.output == "BAR = bar\nFOO = bar\n\n"
    assert result.exit_code == 0


def test_dotenv_template():
    runner = CliRunner()
    result = runner.invoke(main, args=['--keep-template', '--dotenv', 'tests/fixtures/dotenv', 'tests/fixtures/envs.tpl'],
                           env={'MY_FOO': 'foo', 'MY_BAR': 'bar'})
    assert result.output == "BAR = foobar\nFOO = foo\n\n"
    assert result.exit_code == 0


def test_wrong_dotenv_template():
    runner = CliRunner()
    result = runner.invoke(main, args=['--keep-template', '--dotenv', 'tests/fixtures/wrong_dotenv', 'tests/fixtures/envs.tpl'],
                           env={'MY_FOO': 'foo', 'MY_BAR': 'bar'})
    assert "Must be a regular file" in result.output
    assert result.exit_code == 1
