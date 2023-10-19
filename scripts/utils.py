import os
import sys
from pathlib import Path
from typing import Any, Dict, Final

import toml
from dotty_dict import dotty
from sh import Command, CommandNotFound
from toml import TomlDecodeError


class Constants:
    """All constants"""

    # pylint: disable=R0903
    ENCODING_UTF_8: Final[str] = "utf-8"
    PROJECT_PATH: Final[Path] = Path("pyproject.toml")
    REGISTRY_URL: str = os.getenv("REGISTRY_URL", "local.dev")


def read_project_conf() -> Dict[str, Any]:
    """
    Read project configuration and returns a dict configuration.
    Returns:
        dict configuration.
    Raises:
        TomlDecodeError: if the `pyproject.toml` isn't valid.
    """
    try:
        return dotty(toml.load(Path("pyproject.toml").absolute().as_posix()))
    except TomlDecodeError as err:
        print("The `pyproject.toml` file isn't valid", file=sys.stderr)
        raise err


def container_backend() -> Command:
    """
    Try to detect a container backend.
    Either podman or docker.

    Returns:
        a command if a backend is detected.
    Raises:
        CommandNotFound: if a suitable backend can't be found.
    """
    cmd = None
    for backend in ["docker", "podman"]:
        try:
            cmd = Command(backend)
            continue
        except CommandNotFound:
            pass

    if not cmd:
        raise CommandNotFound("Unable to find a suitable backend: docker or podman")
    return cmd
