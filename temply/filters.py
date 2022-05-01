import json

import yaml
from jinja2 import pass_eval_context, pass_context


@pass_eval_context
def from_json(ctx, value):
    return json.loads(value)


@pass_eval_context
def to_json(ctx, value):
    return json.dumps(value).strip()


@pass_eval_context
def from_yaml(ctx, value):
    return yaml.safe_load(value)


@pass_eval_context
def to_yaml(ctx, value):
    return yaml.safe_dump(value).strip()


@pass_context
def get_environment(ctx, prefix=''):
    for key, value in sorted(ctx.items()):
        if not callable(value) and key.startswith(prefix):
            yield key[len(prefix):], value
