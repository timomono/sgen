from pathlib import Path
from typing import override
from sgen.base_config import BaseConfig


class Config(BaseConfig):
    @property
    @override
    def DEBUG(self):
        return False

    @property
    @override
    def BASE_DIR(self):
        return Path(__file__).resolve().parent

    @property
    @override
    def IGNORE_FILES(self):
        return [
            self.SRC_DIR / "base.html",
        ]

    @property
    @override
    def MIDDLEWARE(self):
        return []
