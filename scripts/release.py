import os
import re
import sys
from pathlib import Path

from sh import ErrorReturnCode

from scripts.utils import Constants, detect_gh, detect_git, fatal, project_version


def __update_file_version(file_path: Path, version: str, pattern: str) -> None:
    try:
        data = file_path.read_text()
    except Exception as err:
        fatal(f"The `{file_path.as_posix()}` can't be read", err)

    replacement = (
        f'version: "{version}"'
        if pattern.startswith("version:")
        else f'version = "{version}"'
    )
    data = re.sub(pattern, replacement, data, count=1)
    try:
        file_path.write_text(data)
    except Exception as err:
        fatal(f"The `{file_path.as_posix()}` file can't be written", err)


def __set_version(version: str) -> None:
    # Update app version
    try:
        Constants.TEMPLY_INIT_PATH.write_text(f"""__version__ = \"{version}\"\n""")
    except Exception as err:
        fatal(
            f"The `{Constants.TEMPLY_INIT_PATH.as_posix()}` file can't be written", err
        )

    # Update project version
    __update_file_version(Constants.PYPROJECT_PATH, version, r"version = \"(.+)\"")

    # Update NFPM versions
    __update_file_version(
        Constants.DISTRIBUTIONS_NFPM_AMD64_PATH, version, r"version: \"(.+)\""
    )
    __update_file_version(
        Constants.DISTRIBUTIONS_NFPM_ARM64_PATH, version, r"version: \"(.+)\""
    )


def pre() -> None:
    # Ensure we have inputs
    release_version = os.getenv("RELEASE_VERSION")
    if not release_version:
        fatal("You must define `RELEASE_VERSION` environment variable.")
    if not re.match(r"(\d){1,2}\.(\d){1,2}\.(\d){1,2}", release_version):
        fatal("The `RELEASE_VERSION` should match semver format.")

    # Create a new branch
    branch_name = f"release/v{release_version}"
    git = detect_git()
    git("checkout", "-b", branch_name, _out=sys.stdout, _err=sys.stderr)

    # Update all files
    __set_version(release_version)

    # Push release branch
    git("add", "--all", _out=sys.stdout, _err=sys.stderr)
    git(
        "commit",
        "-m",
        f"release: temply v{release_version}",
        "--no-verify",
        _out=sys.stdout,
        _err=sys.stderr,
    )
    git("push", "origin", branch_name, _out=sys.stdout, _err=sys.stderr)

    # Create a PR
    gh = detect_gh()
    gh(
        "pr",
        "create",
        "--fill",
        "--base=main",
        f"--head={branch_name}",
        _out=sys.stdout,
        _err=sys.stderr,
    )


def run() -> None:
    # Read the project version
    release_version = project_version()

    # Create the release tag
    git = detect_git()
    try:
        git("tag", release_version, _out=sys.stdout, _err=sys.stderr)
        git("push", "origin", release_version, _out=sys.stdout, _err=sys.stderr)
    except ErrorReturnCode:
        fatal(f"The release `v{release_version}` already exists.")

    # Create the release
    args = [
        "release",
        "create",
        "--generate-notes",
        "--latest",
        f"--title=temply v{release_version}",
        release_version,
    ]
    binaries = [
        file.absolute().as_posix()
        for file in Path("dist").glob("./temply*")
        if file.is_file()
    ]
    args.extend(binaries)
    gh = detect_gh()
    gh(args, _out=sys.stdout, _err=sys.stderr)


def post() -> None:
    # Ensure we have inputs
    next_version = os.getenv("NEXT_VERSION")
    if not next_version:
        fatal("You must define `NEXT_VERSION` environment variable")
    if not re.match(r"(\d){1,2}\.(\d){1,2}\.(\d){1,2}-dev", next_version):
        fatal("The `NEXT_VERSION` should match semver format.")

    # Create a new branch
    branch_name = f"feat/post-release-v{next_version}"
    git = detect_git()
    git("checkout", "-b", branch_name, _out=sys.stdout, _err=sys.stderr)

    # Update all files
    __set_version(next_version)

    # Push changes
    git("add", "--all", _out=sys.stdout, _err=sys.stderr)
    git(
        "commit",
        "-m",
        "chore: prepare for next iteration",
        "--no-verify",
        _out=sys.stdout,
        _err=sys.stderr,
    )
    git("push", "origin", branch_name, _out=sys.stdout, _err=sys.stderr)

    # Create a PR
    gh = detect_gh()
    gh(
        "pr",
        "create",
        "--fill",
        "--base=main",
        f"--head={branch_name}",
        _out=sys.stdout,
        _err=sys.stderr,
    )
