import json

import click
import jinja2
from jinja2 import Environment, FileSystemLoader, DictLoader
from path import Path

from . import __version__
from .loaders import EnvLoader, EnvdirLoader, DotenvLoader, JsonFileLoader


@click.command('temply')
@click.option('--allow-missing', help='Allow missing variables.', is_flag=True)
@click.option('--keep-template', help='Keep original template file.', is_flag=True)
@click.option('--envdir', help='Load environment variables from directory', type=click.Path())
@click.option('--dotenv', help='Load environment variables from dotenv file', type=click.Path())
@click.option('--json-file', help='Load environment variables from json file', type=click.Path())
@click.option('-o', '--output-file', help='Output file path.', type=click.Path())
@click.version_option(f'{__version__}')
@click.argument('input_file', required=False)
def main(allow_missing, keep_template, envdir, dotenv, json_file, output_file, input_file):
    """Render jinja2 templates on the command line with environment variables."""

    # Define undefine behaviour
    if allow_missing:
        undefine_behaviour = jinja2.Undefined
    else:
        undefine_behaviour = jinja2.StrictUndefined

    # Decide if we use stdin or regular file
    if input_file:
        # Check template path is a regular file
        template_path = Path(input_file)
        if not template_path.isfile():
            raise click.FileError(template_path.abspath(), 'Must be a regular file')

        # Template name
        template_name = str(template_path.name)

        # Set loader
        loader = FileSystemLoader(template_path.parent.abspath())
    else:
        # Template name
        template_name = 'stdin_template'

        # Set loader
        loader = DictLoader({template_name: click.get_text_stream('stdin').read()})

    # Setup environment
    env = Environment(loader=loader, undefined=undefine_behaviour)

    # Setup env
    env.filters['from_json'] = _from_json
    env.filters['fromjson'] = _from_json
    env.filters['to_json'] = _to_json
    env.filters['tojson'] = _to_json

    # Render template
    template = env.get_template(template_name)
    template.globals['environment'] = _get_environment

    # Compute env
    envs = EnvLoader().load()
    envs = EnvdirLoader(envdir).load(envs) if envdir else envs
    envs = DotenvLoader(dotenv).load(envs) if dotenv else envs
    envs = JsonFileLoader(json_file).load(envs) if json_file else envs
    try:
        rendering = template.render(**envs)
    except jinja2.UndefinedError as e:
        raise Exception(e)

    # Remove template
    if input_file and not keep_template:
        Path(input_file).remove()

    # Stdout or file
    if output_file:
        Path(output_file).write_text(rendering)
    else:
        click.echo(rendering)


@jinja2.evalcontextfilter
def _from_json(ctx, value):
    return json.loads(value)


@jinja2.evalcontextfilter
def _to_json(ctx, value):
    return json.dumps(value)


@jinja2.contextfunction
def _get_environment(ctx, prefix=''):
    for key, value in sorted(ctx.items()):
        if not callable(value) and key.startswith(prefix):
            yield key[len(prefix):], value
