import sys

from scripts.utils import require


def configure() -> None:
    pre_commit = require("pre-commit")
    pre_commit("install", _out=sys.stdout, _err=sys.stderr)
