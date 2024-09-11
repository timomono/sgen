from abc import ABC, abstractmethod
from pathlib import Path
from base_middleware import BaseMiddleware


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
    def BUILD_DIR(self) -> Path:
        """Built output directory."""
        return self.BASE_DIR / "build"

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
