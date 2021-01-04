import json
import os

import click
import jinja2
from jinja2 import Environment, FileSystemLoader, DictLoader
from path import Path

from . import __version__


@click.command('temply')
@click.option('--allow-missing', help='Allow missing variables.', is_flag=True)
@click.option('--keep-template', help='Keep original template file.', is_flag=True)
@click.option('-o', '--output-file', help='Output file path.', type=click.Path())
@click.version_option(f'{__version__}')
@click.argument('input_file', required=False)
def main(allow_missing, keep_template, output_file, input_file):
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

    # Render template
    template = env.get_template(template_name)
    template.globals['environment'] = _get_environment
    try:
        rendering = template.render(**os.environ)
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


@jinja2.contextfunction
def _get_environment(ctx, prefix=''):
    for key, value in sorted(ctx.items()):
        if not callable(value) and key.startswith(prefix):
            yield key[len(prefix):], value
