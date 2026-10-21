import sys

from sh import Command

from scripts.utils import Constants, normalized_arch, project_version, require


def run() -> None:
    version = project_version()
    arch = normalized_arch()

    # Build standalone bundle
    pyinstaller = require("pyinstaller")
    pyinstaller(
        "--noconfirm",
        Constants.PYINSTALLER_SPEC_PATH.as_posix(),
        _out=sys.stdout,
        _err=sys.stderr,
    )

    # Check temply bundle is working
    bundle_path = Constants.DIST_PATH / "temply"
    Command(bundle_path / "temply")("--version", _out=sys.stdout, _err=sys.stderr)

    # Create a tarball
    tarball_path = (
        Constants.DIST_PATH / f"temply-{version}-{sys.platform}-{arch}.tar.gz"
    )
    require("tar")("-C", bundle_path, "-czf", tarball_path, "./")
    print(f"Created {tarball_path}")
