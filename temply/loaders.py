import os
from abc import ABC, abstractmethod
from typing import Dict, Optional

import click
from path import Path


class Loader(ABC):
    """Abstract loader"""

    @abstractmethod
    def load(self, ref: Optional[Dict] = None) -> Dict:
        """
        Load environments variables into ref dict.
        :param ref: ref dict context.
        """
        return ref or dict()


class EnvLoader(Loader):
    """Environment loader implementation"""

    def load(self, ref: Optional[Dict] = None) -> Dict:
        ctx = ref if ref else dict()
        for k, v in os.environ.items():
            ctx[k] = v
        return ctx


class EnvdirLoader(Loader):
    """Environment directory loader implementation"""

    def __init__(self, path: str):
        self.__path = path

    def load(self, ref: Optional[Dict] = None) -> Dict:
        ctx = ref if ref else dict()
        for root, dirs, files in os.walk(self.__path, followlinks=False):
            for file in files:
                with open(os.path.join(root, file), 'r') as f:
                    value = f.read().strip("\n\t ").replace("\x00", "\n")
                    if len(value) > 0:
                        ctx[file] = value
                    else:
                        del ctx[file]
        return ctx


class DotenvLoader(Loader):
    """Environment file loader implementation"""

    def __init__(self, path: str):
        self.__path = path

    def load(self, ref: Optional[Dict] = None) -> Dict:
        ctx = ref if ref else dict()

        # Check dotfile is a regular file
        dotfile_path = Path(self.__path)
        if not dotfile_path.isfile():
            raise click.FileError(dotfile_path.abspath(), 'Must be a regular file')

        # Process
        try:
            value = dotfile_path.read_text()
            lines = value.splitlines()
            for line in lines:
                key, value = line.split('=', 1)
                ctx[key] = value
        except OSError as err:
            raise click.FileError(dotfile_path.abspath(), err.__str__())

        return ctx
