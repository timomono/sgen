from pathlib import Path

from sgen.base_middleware import BaseMiddleware
from sgen.components.override_decorator import override


class PathMiddleware(BaseMiddleware):
    @override
    def after(self, build_path: Path) -> None:
        from sgen.get_config import sgen_config

        for file in build_path.glob("**/*"):
            if not file.is_file():
                continue
            body = file.read_bytes()
            body = body.replace(
                b"[[path here]]",
                str(file.relative_to(sgen_config.BUILD_DIR)).encode(),
            )
            if body.find(b"path here") != -1:
                print(body.decode(errors="replace"))
            with open(file, "wb") as f:
                f.write(body)
