from abc import ABC, abstractmethod
from importlib.machinery import ModuleSpec
import importlib.util
from pathlib import Path
from typing import Any
import importlib


class BaseConfig(ABC):
    @property
    @abstractmethod
    def BASE_DIR(self) -> Path:
        pass

    @property
    def SRC_DIR(self):
        return self.BASE_DIR / "src"


class Config:
    def __getattribute__(self, name: str) -> Any:
        configFile = Path("./config.py")
        # importlib.util.spec_from_file_location(name, configFile)
        spec: ModuleSpec = importlib.util.spec_from_file_location(
            "config", configFile
        )  # type: ignore
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)  # type: ignore
        return getattr(module.Config, name)


config = Config()
