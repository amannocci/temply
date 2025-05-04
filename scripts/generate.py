import sys

from scripts.utils import Constants, detect_pyinstaller


def run() -> None:
    for os in ("macOS", "linux"):
        args = ["-n", "temply", "--onedir", "--optimize=1", "--noconfirm"]
        exclude_modules = ()
        for exclude_module in exclude_modules:
            args.extend(["--exclude-module", exclude_module])

        hidden_imports = ()
        for hidden_import in hidden_imports:
            args.extend(["--hidden-import", hidden_import])

        args.extend(
            [
                "./bin/temply",
            ]
        )
        pyinstaller = detect_pyinstaller()
        pyinstaller(args, _out=sys.stdout, _err=sys.stderr)
        if os == "macOS":
            Constants.PYINSTALLER_SPEC_PATH.rename(
                Constants.DISTRIBUTIONS_TARBALL_MACOS_SPEC_PATH
            )
        elif os == "linux":
            Constants.PYINSTALLER_SPEC_PATH.rename(
                Constants.DISTRIBUTIONS_TARBALL_LINUX_SPEC_PATH
            )
