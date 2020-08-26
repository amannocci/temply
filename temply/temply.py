import json
import os

import click
import jinja2
from jinja2 import Environment, FileSystemLoader
from path import Path

from . import __version__


@click.command('temply')
@click.option('--allow-missing', help='Allow missing variables.', is_flag=True)
@click.option('-o', '--output-file', help='Output file path.', type=click.Path())
@click.version_option(f'{__version__}')
@click.argument('input_file')
def main(allow_missing, output_file, input_file):
    """Render jinja2 templates on the command line with environment variables."""

    # Check template path is a regular file
    template_path = Path(input_file)
    if not template_path.isfile():
        raise click.FileError(template_path.abspath(), 'Must be a regular file')

    # Define undefine behaviour
    if allow_missing:
        undefine_behaviour = jinja2.Undefined
    else:
        undefine_behaviour = jinja2.StrictUndefined

    # Setup env
    env = Environment(
        loader=FileSystemLoader(template_path.parent.abspath()),
        undefined=undefine_behaviour
    )
    env.filters['from_json'] = _from_json
    env.filters['fromjson'] = _from_json

    # Render template
    template = env.get_template(str(template_path.name))
    rendering = template.render(**os.environ)

    # Stdout or file
    if output_file:
        Path(output_file).write_text(rendering)
    else:
        click.echo(rendering)


@jinja2.evalcontextfilter
def _from_json(ctx, value):
    return json.loads(value)
