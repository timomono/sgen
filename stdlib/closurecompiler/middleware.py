from pathlib import Path
from typing import override
from base_config import config
from base_middleware import BaseMiddleware
from stdlib.closurecompiler.compile import CompileLevel, compile


class ClosureCompilerMiddleware(BaseMiddleware):
    @override
    def __init__(
        self,
        except_debug=True,
        compile_level: CompileLevel = CompileLevel.SIMPLE_OPTIMIZATIONS,
        options: list[str] = [],
    ) -> None:
        self.except_debug = except_debug
        self.compile_level = compile_level
        self.options = options
        super().__init__()

    @override
    def do(self, build_path: Path):
        if self.except_debug and config().DEBUG:
            return
        for filePath in build_path.glob("**/*.js"):
            with open(filePath, "r") as f:
                result = compile(f.read(), self.compile_level, self.options)
            with open(filePath, "w") as f:
                f.write(result)
