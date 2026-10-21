import os
import sys
from pathlib import Path

from scripts.utils import (
    Constants,
    container_backend,
    normalized_arch,
    project_version,
)

NFPM_IMAGE = "docker.io/goreleaser/nfpm:v2.48.0"


def build_package(pkg: str) -> None:
    arch = normalized_arch()
    version = project_version()
    print(f"Building {pkg} {arch} package...")

    backend, cmd, env = container_backend()
    args = ["run", "--rm", "-v", f"{Path.cwd()}:/src", "-w", "/src"]
    # Rootless podman already maps the container root to the current user
    if backend == "docker":
        args.extend(["--user", f"{os.getuid()}:{os.getgid()}"])
    args.extend(["-e", f"ARCH={arch}", "-e", f"VERSION={version}"])
    args.extend(
        [
            NFPM_IMAGE,
            "package",
            "--config",
            Constants.NFPM_CONFIG_PATH.as_posix(),
            "--target",
            Constants.DIST_PATH.as_posix(),
            "--packager",
            pkg,
        ]
    )
    cmd(*args, _out=sys.stdout, _err=sys.stderr, _env=env)


def deb() -> None:
    build_package("deb")


def rpm() -> None:
    build_package("rpm")
