import sys

from sh import Command, CommandNotFound


def configure() -> None:
    try:
        pre_commit = Command("pre-commit")
        pre_commit("install", _out=sys.stdout, _err=sys.stderr)
    except (CommandNotFound, ImportError):
        print("pre-commit isn't installed")
