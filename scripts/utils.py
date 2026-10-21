import os
import platform
import sys
import tomllib
from pathlib import Path
from typing import Final, NoReturn

from sh import Command, CommandNotFound


class Constants:
    """All constants"""

    DIST_PATH: Final[Path] = Path("dist")
    PYINSTALLER_SPEC_PATH: Final[Path] = Path("distributions/tarball/temply.spec")
    NFPM_CONFIG_PATH: Final[Path] = Path("distributions/packages/nfpm.yaml")
    PYPROJECT_PATH: Final[Path] = Path("pyproject.toml")
    TEMPLY_INIT_PATH: Final[Path] = Path("src/temply/__init__.py")
    UV_LOCK_PATH: Final[Path] = Path("uv.lock")
    SUPPORTED_ARCHS: Final[frozenset[str]] = frozenset({"amd64", "arm64"})


def fatal(msg: str, err: Exception | None = None) -> NoReturn:
    """Print error message on stderr and die."""
    print(msg, file=sys.stderr)
    if err:
        print(err, file=sys.stderr)
    sys.exit(1)


def require(name: str) -> Command:
    """
    Resolve a command or die.
    Args:
        name: command name.

    Returns:
        the resolved command.
    """
    try:
        return Command(name)
    except CommandNotFound:
        fatal(f"`{name}` isn't installed")


def project_version() -> str:
    """
    Returns:
        current project version (e.g. `1.2.3` or `1.2.4-dev`).
    """
    try:
        with Constants.PYPROJECT_PATH.open("rb") as pyproject:
            return tomllib.load(pyproject)["project"]["version"]
    except (OSError, tomllib.TOMLDecodeError, KeyError) as err:
        fatal(f"Unable to read version from `{Constants.PYPROJECT_PATH}`", err)


def normalized_arch() -> str:
    """
    Returns:
        current machine architecture using debian naming (amd64, arm64).
    """
    arch = platform.machine().lower()
    arch = {"x86_64": "amd64", "aarch64": "arm64"}.get(arch, arch)
    if arch not in Constants.SUPPORTED_ARCHS:
        fatal(f"Unsupported architecture `{arch}`")
    return arch


def container_backend() -> tuple[str, Command, dict[str, str]]:
    """
    Detect a container backend, either docker or podman.

    Returns:
        the backend name, its command and the environment to use.
    """
    env = os.environ.copy()
    for backend in ("docker", "podman"):
        try:
            cmd = Command(backend)
        except CommandNotFound:
            continue
        if backend == "podman":
            env["BUILDAH_FORMAT"] = "docker"
        return backend, cmd, env
    fatal("Unable to find a suitable container backend: docker or podman")
