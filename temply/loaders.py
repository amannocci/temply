import json
import os
from abc import ABC, abstractmethod
from pathlib import Path

import click


# pylint: disable=R0903
class Loader(ABC):
    """Abstract loader"""

    @abstractmethod
    def load(self, ref: dict | None = None) -> dict:
        """
        Load environments variables into ref dict.
        :param ref: ref dict context.
        """
        return ref or {}


class EnvLoader(Loader):
    """Environment loader implementation"""

    def load(self, ref: dict | None = None) -> dict:
        ctx = ref if ref else {}
        for key, value in os.environ.items():
            ctx[key] = value
        return ctx


class EnvdirLoader(Loader):
    """Environment directory loader implementation"""

    def __init__(self, path: str) -> None:
        """Init envdir loader."""
        self.__path = path

    def load(self, ref: dict | None = None) -> dict:
        ctx = ref if ref else {}
        for root, _, files in os.walk(self.__path, followlinks=False):
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

    def __init__(self, path: str) -> None:
        """Init dotenv loader."""
        self.__path = path

    def load(self, ref: dict | None = None) -> dict:
        ctx = ref if ref else {}

        # Check dotfile is a regular file
        dotfile_path = Path(self.__path)
        if not dotfile_path.is_file():
            raise click.FileError(str(dotfile_path.absolute()), "Must be a regular file")

        # Process
        try:
            value = dotfile_path.read_text(encoding="utf-8")
            lines = value.splitlines()
            for line in lines:
                key, value = line.split("=", 1)
                ctx[key] = value
        except OSError as err:
            raise click.FileError(str(dotfile_path.absolute()), str(err))

        return ctx


class JsonFileLoader(Loader):
    """Environment json file loader implementation"""

    def __init__(self, path: str) -> None:
        """Init json file loader."""
        self.__path = path

    def load(self, ref: dict | None = None) -> dict:
        ctx = ref if ref else {}

        # Check json file is a regular file
        json_file_path = Path(self.__path)
        if not json_file_path.is_file():
            raise click.FileError(str(json_file_path.absolute()), "Must be a regular file")

        # Process
        try:
            values = json.loads(json_file_path.read_text(encoding="utf-8"))
            for val in values:
                if val.get("key"):
                    ctx[val.get("key")] = val.get("value")
        except OSError as err:
            raise click.FileError(str(json_file_path.absolute()), str(err))

        return ctx
