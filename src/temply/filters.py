import json
from collections.abc import Iterator
from typing import Any

import yaml
from jinja2 import pass_context
from jinja2.runtime import Context


def from_json(value: str) -> Any:
    """
    Parse json value.
    Args:
        value: value to parse.

    Returns:
        parsed value.
    """
    return json.loads(value)


def to_json(value: Any) -> str:
    """
    Convert any value to json.
    Args:
        value: value to convert.

    Returns:
        converted value.
    """
    return json.dumps(value, ensure_ascii=False)


def from_yaml(value: str) -> Any:
    """
    Parse yaml value.
    Args:
        value: value to parse.

    Returns:
        parsed value.
    """
    return yaml.safe_load(value)


def to_yaml(value: Any) -> str:
    """
    Convert any value to yaml.
    Args:
        value: value to convert.

    Returns:
        converted value.
    """
    # Scalars are dumped with a document end marker (`...`) that we don't want
    dump = yaml.safe_dump(value, allow_unicode=True)
    return dump.removesuffix("...\n").rstrip("\n")


@pass_context
def get_environment(ctx: Context, prefix: str = "") -> Iterator[tuple[str, Any]]:
    """
    Filter environment variables with a prefix.
    Args:
        ctx: context.
        prefix: environment variable prefix.

    Returns:
        generator with all environment variables with a prefix.
    """
    # Skip callables to hide jinja globals (range, lipsum, ...)
    for key, value in sorted(ctx.items()):
        if not callable(value) and key.startswith(prefix):
            yield key[len(prefix) :], value
