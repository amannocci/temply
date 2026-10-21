# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Temply** is a command-line tool that renders Jinja2 templates with variables from the environment and files.
It's shipped as a standalone binary built with PyInstaller, so it runs without a Python runtime (e.g. in containers).

- **CLI**: Click
- **Templating**: Jinja2
- **Data sources**: environment variables, envdir directory, dotenv file, JSON file
- **Delivery**: tarballs for Linux and macOS (amd64, arm64), `deb` and `rpm` packages for Linux
- **Python**: see `requires-python` in `pyproject.toml`
- **License**: Apache-2.0

Versions and dependency ranges live in `pyproject.toml` and `src/temply/__init__.py`; don't duplicate them here.

## Directory Layout

```
temply/
├── src/temply/                  # Package (src-layout, built with uv_build)
│   ├── __init__.py             # __version__
│   ├── cli.py                  # Click command: options, Jinja2 environment, rendering
│   ├── loaders.py              # Data loaders (env, envdir, dotenv, json)
│   ├── filters.py              # Jinja2 filters and the environment() global
│   └── io.py                   # Atomic file write helper
├── tests/
│   ├── conftest.py             # PROJECT_ROOT_DIR, PROJECT_TESTS_FIXTURES_DIR
│   ├── e2e/conftest.py         # runner, clean_env (autouse), fixtures (tmp copy)
│   ├── e2e/*_test.py           # End-to-end tests through Click's CliRunner
│   └── fixtures/               # Template, envdir, dotenv and json fixtures
├── scripts/                    # Build, package and release automation (poe tasks)
├── distributions/
│   ├── tarball/temply.spec     # PyInstaller spec (all platforms)
│   └── packages/nfpm.yaml      # nfpm config, ARCH/VERSION from env vars
├── bin/temply                  # PyInstaller entry point
└── .github/workflows/          # CI, pre-release and release workflows
```

## Core Behaviour

### CLI (`src/temply/cli.py`)

1. Read the template from `INPUT_FILE`, or from stdin when omitted.
   - File: `FileSystemLoader` on the template's directory.
   - Stdin: `DictLoader` for the template, then `FileSystemLoader` on the current directory for includes.
2. Build the Jinja2 `Environment` (`StrictUndefined` unless `--allow-missing`, `trim_blocks`, `lstrip_blocks`,
   `keep_trailing_newline`) and register filters and the `environment` global.
3. Load variables with a `ChainLoader`.
4. Render. Jinja2, `ValueError`, `TypeError` and YAML errors become a `click.ClickException` (exit 1, no traceback).
5. Write the output: atomically to `-o` via `temply.io.write_atomically`, or to stdout with `nl=False`.
6. Only then delete the template, unless `--keep-template` is set (the default deletes it).

### Loaders (`src/temply/loaders.py`)

- `ChainLoader` merges loaders in order; later loaders override earlier ones.
  A `None` value unsets the key from what earlier loaders produced.
- Precedence is fixed, whatever the option order: `EnvLoader` < `EnvdirLoader` < `DotenvLoader` < `JsonFileLoader`.
- All files are read as `utf-8-sig` (a leading BOM is dropped). Read and parse errors raise `click.FileError`.
- `EnvdirLoader`: one file per variable, top level only, hidden files and names with `=` skipped.
  The value is right-stripped of spaces, tabs and newlines, and `NUL` becomes a newline. An empty file unsets the variable.
- `DotenvLoader`: `KEY=VALUE` lines; blank lines, `#` comments and an `export ` prefix are allowed; spaces around key
  and value are stripped, and so are matching quotes. No escapes, interpolation or multiline values.
  A line without `=` raises an error with its line number.
- `JsonFileLoader`: a JSON object, or a list of `{"key": ..., "value": ...}` objects. Values keep their JSON type.

### Filters (`src/temply/filters.py`)

- `from_json`/`fromjson`, `to_json`/`tojson` (replaces Jinja2's built-in `tojson`; no HTML escaping, unicode kept).
- `from_yaml`/`fromyaml` (`safe_load`), `to_yaml`/`toyaml` (`safe_dump`, unicode kept, no `...` end marker).
- `environment(prefix="")` global: sorted `(key, value)` pairs of non-callable context entries starting with `prefix`,
  with the prefix removed.

## Development Commands

```bash
uv sync                    # Install dependencies
uv run poe env:configure   # Install pre-commit hooks
uv run poe fmt             # Sort imports and format (ruff)
uv run poe lint            # ruff check src tests scripts + ruff format --check
uv run poe test            # pytest
uv run poe build           # PyInstaller bundle in dist/temply + dist/temply-<version>-<os>-<arch>.tar.gz
uv run poe package:deb     # Linux only, nfpm in a docker/podman container
uv run poe package:rpm     # Linux only, nfpm in a docker/podman container
uv run poe project:upgrade # Upgrade dependencies and pre-commit hooks
```

Running specific tests:

```bash
uv run pytest tests/e2e/temply_file_test.py -v
uv run pytest tests -k dotenv -v
```

Release tasks (`release:pre`, `release`, `release:post`) are meant to run from the GitHub workflows, see below.

## Code Conventions

- Use absolute package imports (`from temply.loaders import ...`); relative imports are banned by ruff (`TID252`).
- Ruff uses its default rules plus `TID252` (see `[tool.ruff.lint]` in `pyproject.toml`).
- Type hints on public functions; `Loader.load()` returns `dict[str, Any]`.
- Pre-commit runs ruff check, ruff format, LF line endings and gitlint. Commit titles must start with
  `build|ci|docs|feat|fix|perf|refactor|test|chore|release` and stay within 80 characters (see `.gitlint`).

## Testing

- Tests are end-to-end through Click's `CliRunner`. Test files are named `*_test.py`.
- The autouse `clean_env` fixture removes test variables (`MY_*`, `simple`, `name`, ...) from the host environment.
  Add new variable names there if a test relies on them being unset.
- Use the `fixtures` fixture (a copy of `tests/fixtures` in `tmp_path`) and `tmp_path` for outputs.
  Never render tracked fixtures in place or write to `/tmp`.
- `render(runner, template, *args, env=...)` in `temply_file_test.py` passes `--keep-template` for you.

## Build & Release

- **Build** (`scripts/build.py`): runs PyInstaller on `distributions/tarball/temply.spec`, checks `--version`, then
  creates the tarball. Linux binaries are built on an old Ubuntu runner for `glibc` compatibility.
- **Package** (`scripts/package.py`): runs a pinned `goreleaser/nfpm` image with `ARCH` and `VERSION` env vars.
- **Version format**: `X.Y.Z` for releases, `X.Y.Z-dev` between releases. `scripts.utils.project_version()` reads it
  from `pyproject.toml`. Tags have no `v` prefix (e.g. `0.8.2`).
- **Release flow** (GitHub workflows, `main` only):
  1. *Pre release* (`release:pre`): bumps `pyproject.toml`, `src/temply/__init__.py` and `uv.lock` to `X.Y.Z` and
     opens a PR.
  2. *Release* (`release`): after CI, tags and publishes a GitHub release with tarballs and packages. It refuses
     `-dev` versions.
  3. *Post release* (`release:post`): bumps to the next `X.Y.Z-dev` and opens a PR.
- CI (`.github/workflows/ci.yml`): lint, build on 4 targets, test, package deb/rpm, and install checks for tarballs
  and debs.

## Sandbox Notes

- `uv run` and the venv's Python live under `~/.cache/uv` and `~/.local/share/uv`, which the Claude Code sandbox blocks.
  Run `.venv/bin/poe`, `.venv/bin/pytest` or `.venv/bin/ruff` outside the sandbox, or adjust it with `/sandbox`.
- Git commits run the pre-commit hooks, which need the same access.
