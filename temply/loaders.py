import json
import os
from abc import ABC, abstractmethod
from pathlib import Path

import click


# pylint: disable=R0903
class Loader(ABC):
    """Abstract loader"""

    @abstractmethod
    def load(self) -> dict:
        """
        Load from data source.
        """
        return {}


class ChainLoader(Loader):
    """Chain loader implementation"""

    def __init__(self, loaders: list[Loader]) -> None:
        """Init chain loader."""
        self.__loaders = loaders

    def load(self) -> dict:
        ctx = {}
        for loader in self.__loaders:
            ctx = {**ctx, **loader.load()}
        return ctx


class EnvLoader(Loader):
    """Environment loader implementation"""

    def load(self) -> dict:
        ctx = {}
        for key, value in os.environ.items():
            ctx[key] = value
        return ctx


class EnvdirLoader(Loader):
    """Environment directory loader implementation"""

    def __init__(self, path: Path) -> None:
        """Init envdir loader."""
        self.__path = path

    def load(self) -> dict:
        ctx = {}
        for root, _, files in os.walk(self.__path.as_posix(), followlinks=False):
            for file in files:
                with open(os.path.join(root, file), "r", encoding="utf-8") as file_descriptor:
                    value = file_descriptor.read().strip("\n\t ").replace("\x00", "\n")
                    if len(value) > 0:
                        ctx[file] = value
                    else:
                        del ctx[file]
        return ctx


class DotenvLoader(Loader):
    """Environment file loader implementation"""

    def __init__(self, path: Path) -> None:
        """Init dotenv loader."""
        self.__path = path

    def load(self) -> dict:
        ctx = {}

        # Check dotfile is a regular file
        if not self.__path.is_file():
            raise click.FileError(str(self.__path.absolute()), "Must be a regular file")

        # Process
        try:
            value = self.__path.read_text(encoding="utf-8")
            lines = value.splitlines()
            for line in lines:
                key, value = line.split("=", 1)
                ctx[key] = value
        except OSError as err:
            raise click.FileError(str(self.__path.absolute()), str(err))

        return ctx


class JsonFileLoader(Loader):
    """Environment json file loader implementation"""

    def __init__(self, path: Path) -> None:
        """Init json file loader."""
        self.__path = path

    def load(self) -> dict:
        ctx = {}

        # Check json file is a regular file
        if not self.__path.is_file():
            raise click.FileError(str(self.__path.absolute()), "Must be a regular file")

        # Process
        try:
            values = json.loads(self.__path.read_text(encoding="utf-8"))
            for val in values:
                if val.get("key"):
                    ctx[val.get("key")] = val.get("value")
        except OSError as err:
            raise click.FileError(str(self.__path.absolute()), str(err))

        return ctx
