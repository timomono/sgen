from abc import ABC
from pathlib import Path
from sgen.components.override_decorator import override
from sgen.base_middleware import BaseMiddleware
from sgen.stdlib.smini.smini import MINIFY_EXTS, minify


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
    def __init__(
        self,
        js_delete_br=False,
        except_debug=True,
    ) -> None:
        self.js_delete_br = js_delete_br
        self.except_debug = except_debug
        super().__init__()

    @override
    def do(self, build_path: Path):
        from sgen.get_config import sgen_config

        if self.except_debug and sgen_config.DEBUG:
            return
        for filePath in (
            p for p in build_path.glob("**/*") if p.suffix in MINIFY_EXTS
        ):
            with open(filePath, "r") as f:
                result = minify(
                    f.read(),
                    filePath.suffix,
                    self.js_delete_br,
                )
            with open(filePath, "w") as f:
                f.write(result)
