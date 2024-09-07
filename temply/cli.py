from pathlib import Path

import click
import jinja2
from jinja2 import DictLoader, Environment, FileSystemLoader

from . import __version__
from .filters import from_json, from_yaml, get_environment, to_json, to_yaml
from .loaders import ChainLoader, DotenvLoader, EnvdirLoader, EnvLoader, JsonFileLoader


# pylint: disable=R0913,R0914
@click.command("temply")
@click.option("--allow-missing", help="Allow missing variables.", is_flag=True)
@click.option("--keep-template", help="Keep original template file.", is_flag=True)
@click.option(
    "--envdir",
    help="Load environment variables from directory",
    type=click.Path(exists=True, readable=True, file_okay=False, path_type=Path),
)
@click.option(
    "--dotenv",
    help="Load environment variables from dotenv file",
    type=click.Path(exists=True, readable=True, dir_okay=False, path_type=Path),
)
@click.option(
    "--json-file",
    help="Load environment variables from json file",
    type=click.Path(exists=True, readable=True, dir_okay=False, path_type=Path),
)
@click.option(
    "-o",
    "--output-file",
    help="Output file path.",
    type=click.Path(writable=True, dir_okay=False, path_type=Path),
)
@click.version_option(__version__)
@click.argument(
    "input_file", required=False, type=click.Path(exists=True, readable=True, dir_okay=False, path_type=Path)
)
def main(
    allow_missing: bool,
    keep_template: bool,
    envdir: Path | None,
    dotenv: Path | None,
    json_file: Path | None,
    output_file: Path | None,
    input_file: Path | None,
) -> None:
    """Render jinja2 templates on the command line with environment variables."""
    # Define undefined behaviour
    if allow_missing:
        undefined_behaviour = jinja2.Undefined
    else:
        undefined_behaviour = jinja2.StrictUndefined

    # Decide if we use stdin or regular file
    if input_file:
        # Template name
        template_name = str(input_file.name)

        # Set loader
        loader = FileSystemLoader(input_file.parent.absolute())
    else:
        # Template name
        template_name = "stdin_template"

        # Set loader
        loader = DictLoader({template_name: click.get_text_stream("stdin").read()})

    # Setup environment
    env = Environment(
        loader=loader, undefined=undefined_behaviour, trim_blocks=True, lstrip_blocks=True, keep_trailing_newline=True
    )

    # Setup env
    env.filters["from_json"] = from_json
    env.filters["fromjson"] = from_json
    env.filters["to_json"] = to_json
    env.filters["tojson"] = to_json
    env.filters["from_yaml"] = from_yaml
    env.filters["fromyaml"] = from_yaml
    env.filters["to_yaml"] = to_yaml
    env.filters["toyaml"] = to_yaml

    # Render template
    template = env.get_template(template_name)
    template.globals["environment"] = get_environment

    # Compute env
    loaders = [EnvLoader()]
    if envdir:
        loaders.append(EnvdirLoader(envdir))
    if dotenv:
        loaders.append(DotenvLoader(dotenv))
    if json_file:
        loaders.append(JsonFileLoader(json_file))
    envs = ChainLoader(loaders).load()

    try:
        rendering = template.render(**envs)
    except jinja2.UndefinedError as err:
        # pylint: disable=W0719
        raise Exception(err) from err

    # Remove template
    if input_file and not keep_template:
        Path(input_file).unlink()

    # Stdout or file
    if output_file:
        Path(output_file).write_text(rendering, encoding="utf-8")
    else:
        click.echo(rendering)
