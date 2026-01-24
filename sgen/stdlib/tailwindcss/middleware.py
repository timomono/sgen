from pathlib import Path
import re
from sgen.base_middleware import BaseMiddleware
from sgen.components.override_decorator import override

cdn = b'<script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"></script>'


class TailwindcssMiddleware(BaseMiddleware):
    @override
    def do(self, build_path: Path):
        for file in build_path.glob("**/*.html"):
            with open(file, "rb") as frb:
                body = frb.read()
            body = re.sub(
                rb"(<head[\s\S]*?>)",
                rb"\1" + cdn,
                body,
            )
            with open(file, "wb") as fwb:
                fwb.write(body)
