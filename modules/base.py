# modules/base.py
from abc import ABC, abstractmethod


class BaseModule(ABC):
    @abstractmethod
    def execute(self, *args, **kwargs):
        """Executes the module's feature action and returns results."""
        pass
