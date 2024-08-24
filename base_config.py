from abc import ABC, abstractmethod
from pathlib import Path


class BaseConfig(ABC):
    @property
    @abstractmethod
    def BASE_DIR(self) -> Path: pass
