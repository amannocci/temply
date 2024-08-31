import sys

from scripts.utils import detect_pyinstaller


def run() -> None:
    args = ["-n", "temply", "--onefile", "--noconfirm"]
    exclude_modules = (
        "setuptools",
        "setuptools._vendor",
        "setuptools._vendor.importlib_metadata",
    )
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
