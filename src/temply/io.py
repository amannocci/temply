import os
import tempfile
from pathlib import Path


def write_atomically(path: Path, content: str) -> None:
    """Write content to path through a temporary file to avoid partial writes."""
    fd, tmp_path = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as tmp_file:
            tmp_file.write(content)
        os.replace(tmp_path, path)
    except BaseException:
        Path(tmp_path).unlink(missing_ok=True)
        raise
