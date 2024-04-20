import os
import sys
from pathlib import Path
from typing import Any, Dict, Final, NoReturn

import toml
from dotty_dict import dotty
from sh import Command, CommandNotFound
from toml import TomlDecodeError


class Constants:
    """All constants"""

    # pylint: disable=R0903
    ENCODING_UTF_8: Final[str] = "utf-8"
    PROJECT_PATH: Final[Path] = Path("pyproject.toml")
    PYRIGHTCONFIG_PATH: Final[Path] = Path("pyrightconfig.json")
    REGISTRY_URL: str = os.getenv("REGISTRY_URL", "local.dev")


def fatal(msg: str, err: Exception | None = None) -> NoReturn:
    """Print error message on stderr and die."""
    print(msg, file=sys.stderr)
    if err:
        print(err, file=sys.stderr)
    sys.exit(1)


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


def detect_poetry() -> Command:
    """
    Try to detect poetry.
    Returns:
        a command if poetry is detected.
    """
    try:
        return Command("poetry")
    except CommandNotFound:
        fatal("`poetry` isn't detected")


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
