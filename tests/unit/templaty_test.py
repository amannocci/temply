from click.testing import CliRunner

from templaty.templaty import main


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
