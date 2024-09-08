from pathlib import Path
from base_config import BaseConfig, LocalizationConfig


class Config(BaseConfig):
    @property
    def DEBUG(self):
        return False

    @property
    def BASE_DIR(self):
        return Path(__file__).resolve().parent

    @property
    def LOCALE_CONFIG(self):
        return LocalizationConfig()

    @property
    def IGNORE_FILES(self):
        return [
            self.SRC_DIR / "base.html",
        ]

    @property
    def MIDDLEWARE(self):
        return []
