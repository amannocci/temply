import os
import re
import sys
from pathlib import Path
from typing import Final, NoReturn

from sh import Command, CommandNotFound


class Constants:
    """All constants"""

    DIST_PATH: Final[Path] = Path("dist")
    DISTRIBUTIONS_TARBALL_PATH: Final[Path] = Path("distributions") / "tarball"
    DISTRIBUTIONS_TARBALL_LINUX_SPEC_PATH: Final[Path] = (
        DISTRIBUTIONS_TARBALL_PATH / "temply.linux.spec"
    )
    DISTRIBUTIONS_TARBALL_MACOS_SPEC_PATH: Final[Path] = (
        DISTRIBUTIONS_TARBALL_PATH / "temply.macOS.spec"
    )
    ENCODING_UTF_8: Final[str] = "utf-8"
    PYINSTALLER_SPEC_PATH: Final[Path] = Path("temply.spec")
    PYPROJECT_PATH: Final[Path] = Path("pyproject.toml")
    PYRIGHTCONFIG_PATH: Final[Path] = Path("pyrightconfig.json")
    REGISTRY_URL: str = os.getenv("REGISTRY_URL", "local.dev")
    TEMPLY_INIT_PATH: Final[Path] = Path("temply") / "__init__.py"


def fatal(msg: str, err: Exception | None = None) -> NoReturn:
    """Print error message on stderr and die."""
    print(msg, file=sys.stderr)
    if err:
        print(err, file=sys.stderr)
    sys.exit(1)


def detect_uv() -> Command:
    """
    Try to detect uv.
    Returns:
        a command if uv is detected.
    """
    try:
        return Command("uv")
    except CommandNotFound:
        fatal("`uv` isn't detected")


def detect_gh() -> Command:
    """
    Try to detect gh.
    Returns:
        a command if gh is detected.
    """
    try:
        return Command("gh")
    except CommandNotFound:
        fatal("`gh` isn't installed")


def detect_git() -> Command:
    """
    Try to detect git.
    Returns:
        a command if git is detected.
    """
    try:
        return Command("git")
    except CommandNotFound:
        fatal("`git` isn't installed")


def detect_pyinstaller() -> Command:
    """
    Try to detect pyinstaller.
    Returns:
        a command if pyinstaller is detected.
    """
    try:
        return Command("pyinstaller")
    except CommandNotFound:
        fatal("`pyinstaller` isn't installed")


def project_version() -> str:
    """
    Returns:
        current project version.
    """
    uv = detect_uv()
    details = uv("pip", "show", "temply", _err=sys.stderr)
    version = re.search(r"Version: (.*)", details).group(1)
    return version.replace(".dev0", "-dev").strip()


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
