import platform
import sys

from scripts.utils import (
    container_backend,
)


def build_package(pkg: str) -> None:
    # Build and package
    arch = platform.machine().lower()
    arch = "amd64" if arch == "x86_64" else arch
    arch = "arm64" if arch == "aarch64" else arch
    print(f"Building {arch} package...")
    cmd, env = container_backend()
    cmd(
        "run",
        "--rm",
        "-v",
        ".:/tmp",
        "-w",
        "/tmp",
        "goreleaser/nfpm",
        "package",
        "--config",
        f"distributions/packages/nfpm.{arch}.yaml",
        "--target",
        "/tmp/dist",
        "--packager",
        pkg,
        _out=sys.stdout,
        _err=sys.stderr,
        _env=env,
    )


def deb() -> None:
    build_package("deb")


def rpm() -> None:
    build_package("rpm")
