# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Temply** is a standalone command-line tool that renders Jinja2 templates without requiring a Python runtime. It's delivered as a compiled binary (via PyInstaller) that can run independently in containerized environments.

Key characteristics:
- **Purpose**: Template rendering with environment variable injection
- **Delivery**: Standalone executables for Linux and macOS (compiled with PyInstaller)
- **CLI Interface**: Click-based command-line application
- **Templating Engine**: Jinja2
- **Data Sources**: Environment variables, files (.env, .envdir, JSON), stdin
- **License**: Apache-2.0
- **Python Version**: 3.12+

## Architecture & Structure

### Directory Layout
```
temply/
├── src/temply/              # Main package (src-layout convention)
│   ├── cli.py              # Click command-line interface
│   ├── loaders.py          # Data loaders (env, files, JSON, YAML)
│   ├── filters.py          # Jinja2 custom filters
│   └── __init__.py         # Version info
├── tests/e2e/              # End-to-end tests (pytest)
├── scripts/                # Build and release automation scripts
├── distributions/          # PyInstaller spec files for Linux/macOS
└── bin/                    # Development entry point
```

### Core Components

1. **CLI Module** (`src/temply/cli.py`)
   - Entry point for the command-line application
   - Handles options: `--allow-missing`, `--keep-template`, `--envdir`, `--dotenv`, `--json-file`, `-o/--output-file`
   - Stdin support for template input
   - File input/output handling

2. **Loaders** (`src/temply/loaders.py`)
   - Abstract `Loader` base class with `load()` method returning dict
   - `ChainLoader`: Composites multiple loaders
   - `EnvLoader`: Loads from environment variables
   - `EnvdirLoader`: Loads from directory of env files
   - `DotenvLoader`: Loads from .env files
   - `JsonFileLoader`: Loads from JSON files
   - Data merging: Later loaders override earlier ones

3. **Filters** (`src/temply/filters.py`)
   - Custom Jinja2 filters for template processing
   - Functions: `from_json()`, `to_json()`, `from_yaml()`, `to_yaml()`, `get_environment()`

### Build & Release Pipeline

**Build Process** (`scripts/build.py`):
- Uses PyInstaller to create standalone binaries
- Generates separate specs for Linux and macOS
- Creates distributable tarballs with version info

**Release Process** (`scripts/release.py`):
- Updates version numbers
- Creates GitHub releases with artifacts
- Manages release notes

**Distribution Scripts** (`scripts/package.py`):
- Debian package generation (.deb) on Linux
- RPM package generation (.rpm) on Linux

## Development Commands

### Setup
```bash
# Clone and install
git clone https://github.com/techcode-io/temply
cd temply
uv sync                    # Install dependencies and set up environment
uv run poe env:configure   # Configure environment
```

### Common Tasks
```bash
uv run poe lint            # Run ruff linter on src/temply
uv run poe fmt             # Format with ruff (imports + formatting)
uv run poe test            # Run all pytest tests (19 total)
uv run poe build           # Build standalone binary
uv run poe project:upgrade # Upgrade dependencies and pre-commit hooks
```

### Running Specific Tests
```bash
# Single test file
uv run pytest tests/e2e/temply_file_test.py -v

# Single test
uv run pytest tests/e2e/temply_file_test.py::test_simple_template -v

# With output
uv run pytest tests/e2e/ -v -s
```

### Direct Usage
```bash
# Use the CLI directly (after uv sync)
temply --version
temply template.j2 -o output.txt
echo "Hello {{ name }}" | temply
```

## Build System & Dependencies

**Build Backend**: `uv_build>=0.10.0,<0.12.0`
- Modern Python build standard
- No hatch-specific configuration needed
- Automatically discovers package in `src/temply`

**Runtime Dependencies**:
- `click>=8.1.7` - CLI framework
- `jinja2>=3.1.4` - Template engine
- `PyYAML>=6.0.2` - YAML support

**Dev Dependencies** (via uv):
- `poethepoet` - Task runner (poe)
- `pyinstaller` - Binary compilation
- `pytest` - Testing framework
- `ruff` - Linter & formatter
- `sh` - Shell command execution (for scripts)

**Tool Integration**:
- Task runner: Poe (defined in `pyproject.toml` under `[tool.poe.tasks]`)
- Linter: Ruff (checks `src/` directory)
- Type checking: Pyright (configured in `pyproject.toml`)
- Pre-commit hooks: Enforces linting and formatting before commits
- Pytest: Configured with `pythonpath = ["."]` for import resolution

## Testing

**Test Framework**: pytest with Click's CliRunner for CLI testing

**Test Structure**:
- `tests/__init__.py` - Defines `PROJECT_TESTS_FIXTURES_DIR` and `PROJECT_ROOT_DIR`
- `tests/e2e/temply_file_test.py` - File-based template tests (14 tests)
- `tests/e2e/temply_stdin_test.py` - Stdin-based template tests (5 tests)
- `tests/fixtures/` - Template fixture files used by tests

**Test Patterns**:
```python
# CLI tests use CliRunner from Click
def test_example(runner: CliRunner) -> None:
    result = runner.invoke(main, args=["template.tpl", "-o", "output"])
    assert result.exit_code == 0
```

**Running Tests**:
```bash
uv run poe test           # All tests
uv run pytest tests -v    # Verbose output
uv run pytest tests -k "simple"  # Filter by name
```

## Key Development Patterns

### Entry Point
- CLI entry point defined in `pyproject.toml`: `temply = "temply.cli:main"`
- The `main()` function is a Click command that orchestrates loaders and Jinja2 rendering

### Data Flow
1. Parse CLI arguments (input file, output file, flags)
2. Build `ChainLoader` with appropriate loaders based on options
3. Load environment context from loaders
4. Create Jinja2 `Environment` with custom filters
5. Render template with context
6. Write output (file or stdout)

### Loader Composition
- Use `ChainLoader([env_loader, dotenv_loader, json_loader])` to merge data sources
- Later loaders override earlier ones
- All loaders return dicts that get merged

## Recent Changes (March 2027)

### Src-Layout Refactoring
- **Changed**: Moved package from root `temply/` to `src/temply/`
- **Reason**: Modern Python packaging convention with better namespace isolation
- **Files Modified**:
  - Moved 4 files: `__init__.py`, `cli.py`, `filters.py`, `loaders.py`
  - Updated `scripts/utils.py` - `TEMPLY_INIT_PATH` now points to `src/temply`
  - Updated `pyproject.toml` - pyright, ruff paths updated to `src/`

### Build System Migration
- **Changed**: From `hatchling` to `uv_build` backend
- **Reason**: Simpler, uv-native, removes hatch-specific configuration
- **Configuration**: Removed `[tool.hatch.*]` sections; uv_build auto-discovers packages
- **Version Constraint**: `uv_build>=0.10.0,<0.12.0` for reproducible builds

### Impact
- All 19 tests pass with new structure
- CLI functionality unchanged
- Development workflow unchanged (still use `uv sync` and `poe` tasks)
- Package building works seamlessly with PyInstaller

## Workflow Tips

### Before Committing
1. `uv run poe fmt` - Format code
2. `uv run poe lint` - Check for issues
3. `uv run poe test` - Verify tests pass
4. Pre-commit hooks will validate automatically on git commit

### Adding New Features
1. Add code to `src/temply/` (appropriate module)
2. Add/update tests in `tests/e2e/`
3. Consider adding custom Jinja2 filters if template-related
4. Test with: `uv run poe test` and manual `temply --help` checks

### Debugging
- Use `temply --version` to verify CLI works
- Use `echo "template" | temply` for stdin testing
- Add print statements and run via `uv run pytest -s` for detailed output
- Check `pytest` output for test fixture paths

## Entry Points & Commands

**CLI Entry Point**: `temply` (defined as `temply.cli:main` in pyproject.toml)

**Version**: `0.7.5-dev` (defined in `src/temply/__init__.py`)

**Poe Task Aliases**:
- `env:configure` - Setup environment
- `env:wipe` - Clean build artifacts
- `project:upgrade` - Update dependencies
- `generate` - Generate config files
- `lint` - Run ruff checks
- `fmt` - Format code
- `build` - Compile binary
- `test` - Run tests
- `package:deb` - Build Debian package (Linux only)
- `package:rpm` - Build RPM package (Linux only)
- `release:pre` - Create release PR
- `release` - Create release
- `release:post` - Prepare next iteration