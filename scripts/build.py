import os
import sys

from sh import Command

from scripts.utils import Constants, fatal, normalized_arch, project_version, require

SMOKE_TEMPLATE = (
    "{{ (JSON_VAR | from_json).a | to_json }}\n"
    "{{ (YAML_VAR | from_yaml).b | to_yaml }}\n"
    "{% for key, value in environment('SMOKE_') %}{{ key }}={{ value }}{% endfor %}\n"
)
SMOKE_ENV = {"JSON_VAR": '{"a": [1, "é"]}', "YAML_VAR": "b: c", "SMOKE_D": "e"}
# The newline after the last block tag is removed by trim_blocks
SMOKE_EXPECTED = '[1, "é"]\nc\nD=e'


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

    # Check temply bundle is working, including modules only loaded when rendering
    bundle_path = Constants.DIST_PATH / "temply"
    temply = Command(bundle_path / "temply")
    temply("--version", _out=sys.stdout, _err=sys.stderr)
    rendering = temply(
        _in=SMOKE_TEMPLATE,
        _env={"PATH": os.environ.get("PATH", ""), **SMOKE_ENV},
        _err=sys.stderr,
    )
    if rendering != SMOKE_EXPECTED:
        fatal(
            f"Bundle rendering mismatch:\nexpected: {SMOKE_EXPECTED!r}\n"
            f"got: {rendering!r}"
        )

    # Create a tarball
    tarball_path = (
        Constants.DIST_PATH / f"temply-{version}-{sys.platform}-{arch}.tar.gz"
    )
    require("tar")("-C", bundle_path, "-czf", tarball_path, "./")
    print(f"Created {tarball_path}")
