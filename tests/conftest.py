from pathlib import Path
from typing import Final

PROJECT_ROOT_DIR: Final[Path] = Path(__file__).parent.parent.absolute().resolve()
PROJECT_TESTS_FIXTURES_DIR: Final[Path] = PROJECT_ROOT_DIR / "tests" / "fixtures"
