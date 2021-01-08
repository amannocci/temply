from click.testing import CliRunner
from path import Path

from temply.temply import main


def test_template():
    runner = CliRunner()
    result = runner.invoke(main, input='Hello {{ name }} !', env={'name': 'world'})
    assert result.exit_code == 0
    assert result.output == 'Hello world !\n'


def test_missing_env():
    runner = CliRunner()
    result = runner.invoke(main, input='Hello {{ name }} !', env={})
    assert result.exit_code == 1


def test_output_file():
    runner = CliRunner()
    result = runner.invoke(main, input='Hello {{ name }} !', args=['-o', '/tmp/output'], env={'name': 'world'})
    assert result.exit_code == 0
    assert result.output == ''
    assert Path('/tmp/output').read_text() == 'Hello world !'
    Path('/tmp/output').remove()
