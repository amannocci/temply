import platform
import shutil
import stat
import sys
from pathlib import Path

from sh import Command, tar

from scripts.utils import (
    Constants,
    detect_pyinstaller,
    project_version,
)


def run() -> None:
    version = project_version()

    # Create dist dir
    shutil.rmtree(Constants.DIST_PATH, ignore_errors=True)
    Constants.DIST_PATH.mkdir(parents=True, exist_ok=False)

    system = sys.platform
    pyinstaller = detect_pyinstaller()
    try:
        shutil.copyfile(
            Constants.DISTRIBUTIONS_TARBALL_MACOS_SPEC_PATH
            if system == "darwin"
            else Constants.DISTRIBUTIONS_TARBALL_LINUX_SPEC_PATH,
            Constants.PYINSTALLER_SPEC_PATH,
        )
        pyinstaller(
            Constants.PYINSTALLER_SPEC_PATH.as_posix(),
            _out=sys.stdout,
            _err=sys.stderr,
        )
    finally:
        Constants.PYINSTALLER_SPEC_PATH.unlink(missing_ok=True)

    # Make ensemble executable
    ensemble_exec = Path("./dist/temply/temply")
    ensemble_exec.chmod(ensemble_exec.stat().st_mode | stat.S_IEXEC)

    # Check ensemble bundle is working
    Command(ensemble_exec)("--version", _out=sys.stdout, _err=sys.stderr)

    # Create a tarball for macOS
    if system == "darwin":
        arch = platform.machine()
        arch = "amd64" if arch == "x86_64" else arch
        tar(
            "-C",
            "dist/temply",
            "-czf",
            f"./dist/temply-{version}-{system}-{arch}.tar.gz",
            "./",
        )
