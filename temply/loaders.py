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
