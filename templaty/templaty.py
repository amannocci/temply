import os

import click
import jinja2
from jinja2 import Environment, FileSystemLoader
from path import Path


@click.command('templaty')
@click.option('--allow-missing', help='Allow missing variables.', is_flag=True)
@click.argument('input_file')
def main(allow_missing, input_file):
    # Check template path is a regular file
    template_path = Path(input_file)
    if not template_path.isfile():
        raise click.FileError(template_path.abspath(), 'Must be a regular file')

    # Define undefine behaviour
    if allow_missing:
        undefine_behaviour = jinja2.Undefined
    else:
        undefine_behaviour = jinja2.StrictUndefined

    # Render template
    env = Environment(
        loader=FileSystemLoader(template_path.parent.abspath()),
        undefined=undefine_behaviour
    )
    template = env.get_template(str(template_path.name))
    click.echo(template.render(**os.environ))
