import sys

from sh import Command, CommandNotFound

from scripts.utils import fatal


def configure() -> None:
    try:
        pre_commit = Command("pre-commit")
        pre_commit("install", _out=sys.stdout, _err=sys.stderr)
    except (CommandNotFound, ImportError):
        fatal("pre-commit isn't installed")
