from abc import ABC
from pathlib import Path
from typing import override
from get_config import sgen_config
from base_middleware import BaseMiddleware
from stdlib.smini.smini import minify


class BaseSminiConfig(ABC):
    """Minify option.
    Automatic minification at build time.
    """

    JSRemoveBr = False
    """Remove break line for JS.

    Note that a missing semicolon will result in an error.
    """

    HTMLRemoveBr = False
    """Remove break line for HTML.

    Note that a missing semicolon will result in an error in script tag.
    """

    except_debug = True


class SminiMiddleware(BaseMiddleware):
    @override
    def __init__(self, config: BaseSminiConfig) -> None:
        self.config = config
        super().__init__()

    @override
    def do(self, build_path: Path):
        if self.config.except_debug and sgen_config.DEBUG:
            return
        for filePath in build_path.glob("**/*.js"):
            with open(filePath, "r") as f:
                result = minify(
                    f.read(),
                    filePath.suffix,
                    self.config.HTMLRemoveBr,
                    self.config.JSRemoveBr,
                )
            with open(filePath, "w") as f:
                f.write(result)
