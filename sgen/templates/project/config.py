from pathlib import Path
from typing import override
from sgen.base_config import BaseConfig
from sgen.cli import running_command
from sgen.cmds import ListenChange
from sgen.stdlib.smini.middleware import SminiMiddleware
from sgen.stdlib.xmlsitemap.middleware import XMLSitemapMiddleware


class Config(BaseConfig):
    @property
    @override
    def DEBUG(self):
        return isinstance(running_command, ListenChange)

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
        return [
            XMLSitemapMiddleware(),
            SminiMiddleware(),
        ]
