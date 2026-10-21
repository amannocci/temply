import json
import os
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

import click


class Loader(ABC):
    """Abstract loader"""

    @abstractmethod
    def load(self) -> dict[str, Any]:
        """
        Load from data source.
        A `None` value means the key must be unset from previously loaded values.
        """
        ...


class ChainLoader(Loader):
    """Chain loader implementation"""

    def __init__(self, loaders: list[Loader]) -> None:
        """Init chain loader."""
        self.__loaders = loaders

    def load(self) -> dict[str, Any]:
        ctx: dict[str, Any] = {}
        for loader in self.__loaders:
            for key, value in loader.load().items():
                if value is None:
                    ctx.pop(key, None)
                else:
                    ctx[key] = value
        return ctx


class EnvLoader(Loader):
    """Environment loader implementation"""

    def load(self) -> dict[str, Any]:
        return dict(os.environ)


class EnvdirLoader(Loader):
    """Environment directory loader implementation"""

    def __init__(self, path: Path) -> None:
        """Init envdir loader."""
        self.__path = path

    def load(self) -> dict[str, Any]:
        ctx: dict[str, Any] = {}
        for file in self.__path.iterdir():
            if file.name.startswith(".") or "=" in file.name or not file.is_file():
                continue
            try:
                value = file.read_text(encoding="utf-8-sig")
            except (OSError, ValueError) as err:
                raise click.FileError(str(file.absolute()), str(err)) from err

            # An empty file means the variable must be unset
            value = value.rstrip("\n\t ").replace("\x00", "\n")
            ctx[file.name] = value if value else None
        return ctx


class DotenvLoader(Loader):
    """Environment file loader implementation"""

    def __init__(self, path: Path) -> None:
        """Init dotenv loader."""
        self.__path = path

    def load(self) -> dict[str, Any]:
        try:
            content = self.__path.read_text(encoding="utf-8-sig")
        except (OSError, ValueError) as err:
            raise click.FileError(str(self.__path.absolute()), str(err)) from err

        ctx: dict[str, Any] = {}
        for lineno, raw_line in enumerate(content.splitlines(), start=1):
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            line = line.removeprefix("export ").lstrip()
            key, sep, value = line.partition("=")
            key, value = key.strip(), value.strip()
            if not sep or not key:
                raise click.FileError(
                    str(self.__path.absolute()), f"line {lineno}: expected KEY=VALUE"
                )
            if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
                value = value[1:-1]
            ctx[key] = value
        return ctx


class JsonFileLoader(Loader):
    """Environment json file loader implementation"""

    def __init__(self, path: Path) -> None:
        """Init json file loader."""
        self.__path = path

    def load(self) -> dict[str, Any]:
        try:
            values = json.loads(self.__path.read_text(encoding="utf-8-sig"))
        except (OSError, ValueError) as err:
            raise click.FileError(str(self.__path.absolute()), str(err)) from err

        # Plain object: {"KEY": "value"}
        if isinstance(values, dict):
            return values

        # List of entries: [{"key": "KEY", "value": "value"}]
        if isinstance(values, list) and all(isinstance(val, dict) for val in values):
            return {val["key"]: val.get("value") for val in values if val.get("key")}

        raise click.FileError(
            str(self.__path.absolute()),
            'Expected a JSON object or a list of {"key": ..., "value": ...} objects',
        )
