from pathlib import Path

import click
import jinja2
import yaml
from jinja2 import ChoiceLoader, DictLoader, Environment, FileSystemLoader

from temply import __version__
from temply.filters import from_json, from_yaml, get_environment, to_json, to_yaml
from temply.io import write_atomically
from temply.loaders import (
    ChainLoader,
    DotenvLoader,
    EnvdirLoader,
    EnvLoader,
    JsonFileLoader,
    Loader,
)


@click.command("temply")
@click.option("--allow-missing", help="Allow missing variables.", is_flag=True)
@click.option(
    "--keep-template",
    help="Keep original template file (it is deleted after rendering by default).",
    is_flag=True,
)
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
    "input_file",
    required=False,
    type=click.Path(exists=True, readable=True, dir_okay=False, path_type=Path),
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
    # Decide if we use stdin or regular file
    loader: jinja2.BaseLoader
    if input_file:
        template_name = input_file.name
        loader = FileSystemLoader(input_file.parent.absolute())
    else:
        template_name = "stdin_template"
        with click.open_file("-") as stdin:
            source = stdin.read()
        # Allow stdin templates to include files relative to current directory
        loader = ChoiceLoader(
            [DictLoader({template_name: source}), FileSystemLoader(Path.cwd())]
        )

    # Setup environment
    env = Environment(
        loader=loader,
        undefined=jinja2.Undefined if allow_missing else jinja2.StrictUndefined,
        trim_blocks=True,
        lstrip_blocks=True,
        keep_trailing_newline=True,
    )
    env.filters.update(
        {
            "from_json": from_json,
            "fromjson": from_json,
            "to_json": to_json,
            "tojson": to_json,
            "from_yaml": from_yaml,
            "fromyaml": from_yaml,
            "to_yaml": to_yaml,
            "toyaml": to_yaml,
        }
    )
    env.globals["environment"] = get_environment

    # Compute env (later loaders override earlier ones)
    loaders: list[Loader] = [EnvLoader()]
    if envdir:
        loaders.append(EnvdirLoader(envdir))
    if dotenv:
        loaders.append(DotenvLoader(dotenv))
    if json_file:
        loaders.append(JsonFileLoader(json_file))
    envs = ChainLoader(loaders).load()

    # Render template
    try:
        rendering = env.get_template(template_name).render(envs)
    except (jinja2.TemplateError, ValueError, TypeError, yaml.YAMLError) as err:
        raise click.ClickException(f"Unable to render template: {err}") from err

    # Stdout or file
    if output_file:
        try:
            write_atomically(output_file, rendering)
        except OSError as err:
            raise click.FileError(str(output_file), err.strerror or str(err)) from err
    else:
        click.echo(rendering, nl=False)

    # Remove template only once output is safely written
    if input_file and not keep_template:
        input_file.unlink()
