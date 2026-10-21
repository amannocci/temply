import os
import re
import sys
from pathlib import Path

from sh import ErrorReturnCode

from scripts.utils import Constants, fatal, project_version, require

RELEASE_VERSION_PATTERN = r"\d+\.\d+\.\d+"
NEXT_VERSION_PATTERN = r"\d+\.\d+\.\d+-dev"


def __update_file_version(file_path: Path, version: str) -> None:
    try:
        data = file_path.read_text(encoding="utf-8")
    except OSError as err:
        fatal(f"The `{file_path.as_posix()}` file can't be read", err)

    data, count = re.subn(
        r'^(version\s*=\s*)"[^"]*"',
        rf'\g<1>"{version}"',
        data,
        count=1,
        flags=re.MULTILINE,
    )
    if count == 0:
        fatal(f"Unable to find version in `{file_path.as_posix()}`")

    try:
        file_path.write_text(data, encoding="utf-8")
    except OSError as err:
        fatal(f"The `{file_path.as_posix()}` file can't be written", err)


def __set_version(version: str) -> list[Path]:
    """Bump version in all project files and return the updated files."""
    try:
        Constants.TEMPLY_INIT_PATH.write_text(
            f'__version__ = "{version}"\n', encoding="utf-8"
        )
    except OSError as err:
        fatal(
            f"The `{Constants.TEMPLY_INIT_PATH.as_posix()}` file can't be written", err
        )
    __update_file_version(Constants.PYPROJECT_PATH, version)

    # Refresh the lockfile which embeds the project version
    env = {k: v for k, v in os.environ.items() if k not in ("UV_FROZEN", "UV_LOCKED")}
    require("uv")("lock", _env=env, _out=sys.stdout, _err=sys.stderr)

    return [
        Constants.TEMPLY_INIT_PATH,
        Constants.PYPROJECT_PATH,
        Constants.UV_LOCK_PATH,
    ]


def __read_version(env_var: str, pattern: str, example: str) -> str:
    version = os.getenv(env_var)
    if not version:
        fatal(f"You must define `{env_var}` environment variable.")
    if not re.fullmatch(pattern, version):
        fatal(f"The `{env_var}` should match the `{example}` format, got `{version}`.")
    return version


def __bump_and_open_pr(version: str, branch_name: str, message: str) -> None:
    git = require("git")
    git("checkout", "-b", branch_name, _out=sys.stdout, _err=sys.stderr)

    files = __set_version(version)

    git("add", *files, _out=sys.stdout, _err=sys.stderr)
    git("commit", "-m", message, "--no-verify", _out=sys.stdout, _err=sys.stderr)
    git("push", "origin", branch_name, _out=sys.stdout, _err=sys.stderr)

    require("gh")(
        "pr",
        "create",
        "--fill",
        "--base=main",
        f"--head={branch_name}",
        _out=sys.stdout,
        _err=sys.stderr,
    )


def pre() -> None:
    release_version = __read_version(
        "RELEASE_VERSION", RELEASE_VERSION_PATTERN, "1.2.3"
    )
    __bump_and_open_pr(
        release_version,
        f"release/v{release_version}",
        f"release: temply v{release_version}",
    )


def run() -> None:
    release_version = project_version()
    if not re.fullmatch(RELEASE_VERSION_PATTERN, release_version):
        fatal(
            f"The project version `{release_version}` isn't a release version. "
            "Merge the pre-release PR first."
        )

    # Create the release tag
    git = require("git")
    try:
        git("tag", release_version, _out=sys.stdout, _err=sys.stderr)
    except ErrorReturnCode as err:
        fatal(f"Unable to create the tag `{release_version}`.", err)
    try:
        git("push", "origin", release_version, _out=sys.stdout, _err=sys.stderr)
    except ErrorReturnCode as err:
        git("tag", "-d", release_version, _out=sys.stdout, _err=sys.stderr)
        fatal(f"Unable to push the tag `{release_version}`.", err)

    # Create the release
    assets = sorted(
        file.absolute().as_posix()
        for file in Constants.DIST_PATH.glob("temply*")
        if file.is_file()
    )
    if not assets:
        fatal(f"No release assets found in `{Constants.DIST_PATH}`.")
    require("gh")(
        "release",
        "create",
        "--generate-notes",
        "--latest",
        f"--title=temply v{release_version}",
        release_version,
        *assets,
        _out=sys.stdout,
        _err=sys.stderr,
    )


def post() -> None:
    next_version = __read_version("NEXT_VERSION", NEXT_VERSION_PATTERN, "1.2.3-dev")
    __bump_and_open_pr(
        next_version,
        f"feat/post-release-v{next_version}",
        "chore: prepare for next iteration",
    )
