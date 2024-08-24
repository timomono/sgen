from abc import ABC, abstractmethod
from importlib.machinery import ModuleSpec
import importlib.util
from pathlib import Path
import importlib


class BaseConfig(ABC):
    @property
    @abstractmethod
    def BASE_DIR(self) -> Path:
        pass

    @property
    def SRC_DIR(self) -> Path:
        return self.BASE_DIR / "src"

    @property
    def IGNORE_FILES(self) -> list[Path]:
        return [
            self.SRC_DIR / "base.html",
        ]


# class Config:
#     def __getattribute__(self, name: str) -> Any:
#         configFile = Path("./config.py")
#         # importlib.util.spec_from_file_location(name, configFile)
#         spec: ModuleSpec = importlib.util.spec_from_file_location(
#             "config", configFile
#         )  # type: ignore
#         module = importlib.util.module_from_spec(spec)
#         spec.loader.exec_module(module)  # type: ignore
#         return getattr(module.Config, name)


# config = Config()


def config() -> BaseConfig:
    configFile = Path("./config.py")
    # importlib.util.spec_from_file_location(name, configFile)
    spec: ModuleSpec = importlib.util.spec_from_file_location(
        "config", configFile
    )  # type: ignore
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore
    return module.Config()
