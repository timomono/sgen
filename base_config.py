from abc import ABC, abstractmethod
from importlib.machinery import ModuleSpec
import importlib.util
from pathlib import Path
import importlib


class LocalizationConfig(ABC):
    @property
    def LOCALE_DIR(self) -> Path:
        return config().BASE_DIR / "locale"

    @property
    def DEFAULT_LANG(self) -> str:
        return "en"


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

    LOCALE_CONFIG: None | LocalizationConfig = None


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
