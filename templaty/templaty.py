import os

import click
from jinja2 import Environment, FileSystemLoader
from path import Path


@click.command('templaty')
@click.argument('input_file')
def main(input_file):
    # Check template path is a regular file
    template_path = Path(input_file)
    if not template_path.isfile():
        raise click.FileError(template_path.abspath(), 'Must be a regular file')

    env = Environment(
        loader=FileSystemLoader(template_path.parent.abspath()),
    )
    template = env.get_template(str(template_path.name))
    click.echo(template.render(**os.environ))
