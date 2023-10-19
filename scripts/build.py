import platform
import sys
from pathlib import Path
from time import time

from sh import git, podman

from scripts.utils import Constants, container_backend, read_project_conf


def run() -> None:
    conf = read_project_conf()
    commit_hash_short = git("rev-parse", "--short", "HEAD").strip()
    current_time_epoch = int(time())
    version = conf.get("tool.poetry.version")
    python_version = platform.python_version()

    image_id = f"{version}-{current_time_epoch}-{commit_hash_short}"

    # Create dist dir
    local_dist_path = Path("dist")
    local_dist_path.mkdir(parents=True, exist_ok=False)
    local_dist_path = local_dist_path.absolute().as_posix()

    cmd = container_backend()
    for platform_arch in ["linux/amd64", "linux/arm64"]:
        platform_arch_slug = platform_arch.replace("/", "-")
        cmd(
            "buildx",
            "build",
            "--platform",
            platform_arch,
            "-v",
            f"{local_dist_path}:/opt/temply/dist",
            "--build-arg",
            f"base_image_version={python_version}",
            "--build-arg",
            f"platform_arch={platform_arch_slug}",
            "--build-arg",
            f"app_version={version}",
            "-t",
            f"{Constants.REGISTRY_URL}/temply:{image_id}",
            "-f",
            "Containerfile",
            ".",
            _out=sys.stdout,
            _err=sys.stderr,
        )
