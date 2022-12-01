import os
import re
import sys
from pathlib import Path

from sh import git


def __set_version(version: str) -> None:
    # Update app version
    try:
        (Path("temply") / "__init__.py").write_text(f"""__version__ = \"{version}\"\n""")
    except Exception as err:
        print("The `temply/__init__.py` file can't be written", file=sys.stderr)
        raise err

    # Update project version
    try:
        data = Path("pyproject.toml").read_text()
    except Exception as err:
        print("The `pyproject.toml` can't be read", file=sys.stderr)
        raise err

    data = re.sub(r"version = \"(.+)\"", f'version = "{version}"', data, count=1)
    try:
        Path("pyproject.toml").write_text(data)
    except Exception as err:
        print("The `pyproject.toml` file can't be written", file=sys.stderr)
        raise err


def run() -> None:
    # Ensure we have inputs
    release_version = os.getenv("RELEASE_VERSION")
    next_version = os.getenv("NEXT_VERSION")
    if not release_version:
        return print("You must define `RELEASE_VERSION` environment variable", file=sys.stderr)
    if not next_version:
        return print("You must define `NEXT_VERSION` environment variable", file=sys.stderr)

    # Switch to main branch
    git("checkout", "main", _out=sys.stdout, _err=sys.stderr)

    # Update all files
    __set_version(release_version)

    # Push changes
    git("add", "--all", _out=sys.stdout, _err=sys.stderr)
    git("commit", "-s", "-m", f"[Released] temply {release_version}", "--no-verify", _out=sys.stdout, _err=sys.stderr)
    git("tag", release_version, _out=sys.stdout, _err=sys.stderr)

    # Update all files
    __set_version(next_version)
    git("add", "--all", _out=sys.stdout, _err=sys.stderr)
    git("commit", "-s", "-m", "[Updated] Prepare for next iteration", "--no-verify", _out=sys.stdout, _err=sys.stderr)
    git("push", _out=sys.stdout, _err=sys.stderr)
    git("push", "--tags", _out=sys.stdout, _err=sys.stderr)
