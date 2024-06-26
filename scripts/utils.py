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
    PYPROJECT_PATH: Final[Path] = Path("pyproject.toml")
    PYRIGHTCONFIG_PATH: Final[Path] = Path("pyrightconfig.json")
    REGISTRY_URL: str = os.getenv("REGISTRY_URL", "local.dev")
    TEMPLY_INIT_PATH: Final[Path] = Path("./temply/__init__.py")


def fatal(msg: str, err: Exception | None = None) -> NoReturn:
    """Print error message on stderr and die."""
    print(msg, file=sys.stderr)
    if err:
        print(err, file=sys.stderr)
    sys.exit(1)


def read_project_conf() -> dict[str, Any]:
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
        fatal("The `pyproject.toml` file isn't valid", err)


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


def detect_gh() -> Command:
    try:
        return Command("gh")
    except CommandNotFound:
        fatal("`gh` isn't installed")


def detect_git() -> Command:
    try:
        return Command("git")
    except CommandNotFound:
        fatal("`git` isn't installed")


def container_backend() -> tuple[Command, dict[str, str]]:
    """
    Try to detect a container backend.
    Either podman or docker.

    Returns:
        a command if a backend is detected.
    Raises:
        CommandNotFound: if a suitable backend can't be found.
    """
    cmd = None
    env = os.environ.copy()
    for backend in ["docker", "podman"]:
        try:
            cmd = Command(backend)
        except CommandNotFound:
            continue
        if "podman" == backend:
            env["BUILDAH_FORMAT"] = "docker"
        break

    if not cmd:
        raise CommandNotFound("Unable to find a suitable backend: docker or podman")
    return cmd, env
