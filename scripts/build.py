import platform
import sys
from pathlib import Path
from time import time

from sh import Command

from scripts.utils import (
    Constants,
    container_backend,
    detect_git,
    detect_pyinstaller,
    fatal,
    project_version,
)


def run() -> None:
    git = detect_git()
    commit_hash_short = git("rev-parse", "--short", "HEAD").strip()
    current_time_epoch = int(time())
    version = project_version()
    python_version = platform.python_version()

    image_id = f"{version}-{current_time_epoch}-{commit_hash_short}"

    # Create dist dir
    local_dist_path = Path("dist")
    local_dist_path.mkdir(parents=True, exist_ok=False)
    local_dist_path = local_dist_path.absolute()

    system = platform.system().lower()
    if system == "darwin":
        pyinstaller = detect_pyinstaller()
        pyinstaller("temply.spec", _out=sys.stdout, _err=sys.stderr)
        arch = platform.machine()
        arch = "amd64" if arch == "x86_64" else arch
        Path("./dist/temply").replace(Path(f"./dist/temply-{version}-{system}-{arch}"))
        Command(f"./dist/temply-{version}-{system}-{arch}")("--version", _out=sys.stdout, _err=sys.stderr)
    elif system == "linux":
        # Use cross-build to build both amd64 and arm64 versions.
        cmd, env = container_backend()
        for arch in ["amd64", "arm64"]:
            platform_arch = f"linux/{arch}"
            cmd(
                "buildx",
                "build",
                "--load",
                "--platform",
                platform_arch,
                "--build-arg",
                f"base_image_version={python_version}",
                "-t",
                f"{Constants.REGISTRY_URL}/temply:{image_id}",
                "-f",
                "Containerfile",
                ".",
                _out=sys.stdout,
                _err=sys.stderr,
                _env=env,
            )
            container_id = cmd(
                "run",
                "-d",
                "--platform",
                platform_arch,
                "--entrypoint=cat",
                f"{Constants.REGISTRY_URL}/temply:{image_id}",
                _err=sys.stderr,
                _env=env,
            ).strip()
            cmd(
                "cp",
                f"{container_id}:/opt/temply/dist/temply",
                (local_dist_path / f"temply-{version}-linux-{arch}").as_posix(),
                _out=sys.stdout,
                _err=sys.stderr,
                _env=env,
            )
            cmd(
                "rm",
                "-f",
                container_id,
                _out=sys.stdout,
                _err=sys.stderr,
                _env=env,
            )
            Command(f"./dist/temply-{version}-linux-{arch}")("--version", _out=sys.stdout, _err=sys.stderr)
    else:
        fatal(f"Unsupported system: {system}")
