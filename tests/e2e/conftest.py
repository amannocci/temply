import os
import shutil
from pathlib import Path

import pytest
from click.testing import CliRunner

from tests.conftest import PROJECT_TESTS_FIXTURES_DIR


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture(autouse=True)
def clean_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Ensure variables used by tests don't leak from the host environment."""
    for key in list(os.environ):
        if key.startswith("MY_") or key in {
            "simple",
            "name",
            "foo",
            "variable",
            "another_one",
            "json_var",
            "yaml_var",
        }:
            monkeypatch.delenv(key)


@pytest.fixture
def fixtures(tmp_path: Path) -> Path:
    """Copy of fixtures directory to avoid touching tracked files."""
    target = tmp_path / "fixtures"
    shutil.copytree(PROJECT_TESTS_FIXTURES_DIR, target)
    return target
