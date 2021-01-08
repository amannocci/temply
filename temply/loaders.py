import os
from abc import ABC, abstractmethod
from typing import Dict, Optional


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
