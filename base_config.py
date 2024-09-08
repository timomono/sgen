from abc import ABC, abstractmethod
from importlib.machinery import ModuleSpec
import importlib.util
from pathlib import Path
import importlib

from base_middleware import BaseMiddleware


class LocalizationConfig(ABC):
    @property
    def LOCALE_DIR(self) -> Path:
        return config().BASE_DIR / "locale"

    @property
    def DEFAULT_LANG(self) -> str:
        return "en"


class BaseConfig(ABC):
    """Base config class.

    Create a config.py in the project root
    and create a Config class that extends from BaseConfig.
    """

    @property
    @abstractmethod
    def DEBUG(self) -> bool:
        """Debug mode.

        Set it to False when deploying.
        """
        pass

    @property
    @abstractmethod
    def BASE_DIR(self) -> Path:
        """Project base directory."""
        pass

    @property
    def SRC_DIR(self) -> Path:
        """Source directory.

        Write html template in this folder.
        """
        return self.BASE_DIR / "src"

    @property
    def IGNORE_FILES(self) -> list[Path]:
        """Files that will not be included in the build.

        Note that extends, includes etc. is possible.

        Folders with the language name used in
        t_include are automatically ignored.
        """
        return []

    @property
    def MIDDLEWARE(self) -> list[BaseMiddleware]:
        """
        List of middleware. These are executed at build time.
        """
        return []

    @property
    def LOCALE_CONFIG(self) -> None | LocalizationConfig:
        """Localization configuration.

        Set none to turn off localization.

        Example

        ```python
        class Config(BaseConfig):
            BASE_DIR = Path(__file__).resolve().parent
            LOCALE_CONFIG = LocalizationConfig()
        ```
        """
        return None


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
