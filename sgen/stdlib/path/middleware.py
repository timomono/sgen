from pathlib import Path

from sgen.base_middleware import BaseMiddleware
from sgen.components.override_decorator import override
from typing import Callable


class PathMiddleware(BaseMiddleware):
    @override
    def __init__(
        self, path_replacer: Callable[[str], str] = lambda x: x
    ) -> None:
        self.path_replacer = path_replacer
        super().__init__()

    @override
    def after(self, build_path: Path) -> None:
        from sgen.get_config import sgen_config

        for file in build_path.glob("**/*"):
            if not file.is_file():
                continue
            body = file.read_bytes()
            body = body.replace(
                b"[[path here]]",
                self.path_replacer(
                    str(file.relative_to(sgen_config.BUILD_DIR))
                ).encode(),
            )
            if body.find(b"path here") != -1:
                print(body.decode(errors="replace"))
            with open(file, "wb") as f:
                f.write(body)
