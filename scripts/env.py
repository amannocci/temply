import json
import sys
from pathlib import Path

from sh import Command, CommandNotFound, RunningCommand

from scripts.utils import Constants, detect_poetry


def configure() -> None:
    poetry = detect_poetry()

    # Generate pyright config
    process: RunningCommand = poetry("env", "info", "-p", _err=sys.stderr, _return_cmd=True)  # type: ignore[no-untyped-def]
    project_venv_path = Path(process.stdout.decode(Constants.ENCODING_UTF_8).strip())
    project_venv_name = project_venv_path.name
    venv_path = project_venv_path.parents[0].as_posix()
    if not Constants.PYRIGHTCONFIG_PATH.exists():
        Constants.PYRIGHTCONFIG_PATH.write_text(json.dumps({"venv": project_venv_name, "venvPath": venv_path}))

    try:
        pre_commit = Command("pre-commit")
        pre_commit("install", _out=sys.stdout, _err=sys.stderr)
    except (CommandNotFound, ImportError):
        print("pre-commit isn't installed")
