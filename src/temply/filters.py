import json

import yaml
from jinja2 import pass_context, pass_eval_context


@pass_eval_context
def from_json(_, value):
    """
    Parse json value.
    Args:
        _: any.
        value: value to parse.

    Returns:
        parsed value.
    """
    return json.loads(value)


@pass_eval_context
def to_json(_, value):
    """
    Convert any value to json.
    Args:
        _: any.
        value: value to convert.

    Returns:
        converted value.
    """
    return json.dumps(value).strip()


@pass_eval_context
def from_yaml(_, value):
    """
    Parse yaml value.
    Args:
        _: any.
        value: value to parse.

    Returns:
        parsed value.
    """
    return yaml.safe_load(value)


@pass_eval_context
def to_yaml(_, value):
    """
    Convert any value to yaml.
    Args:
        _: any.
        value: value to convert.

    Returns:
        converted value.
    """
    return yaml.safe_dump(value).strip()


@pass_context
def get_environment(ctx, prefix=""):
    """
    Filter environment variables with a prefix.
    Args:
        ctx: context.
        prefix: environment variable prefix.

    Returns:
        generator with all environment variables with a prefix.
    """
    for key, value in sorted(ctx.items()):
        if not callable(value) and key.startswith(prefix):
            yield key[len(prefix) :], value
