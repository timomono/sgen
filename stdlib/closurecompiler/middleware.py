from pathlib import Path
from typing import override
from get_config import sgen_config
from base_middleware import BaseMiddleware
from stdlib.closurecompiler.compile import CompileLevel, compileByFilenames


class ClosureCompilerMiddleware(BaseMiddleware):
    @override
    def __init__(
        self,
        except_debug=True,
        compile_level: CompileLevel = CompileLevel.SIMPLE_OPTIMIZATIONS,
        output_js_filename: Path = sgen_config.BUILD_DIR / "main.js",
        options: list[str] = [],
    ) -> None:
        self.except_debug = except_debug
        self.compile_level = compile_level
        self.output_js_filename = output_js_filename
        self.options = options
        super().__init__()

    @override
    def do(self, build_path: Path):
        if self.except_debug and sgen_config.DEBUG:
            return
        # for file_path in build_path.glob("**/*.js"):
        compileByFilenames(
            build_path.glob("**/*.js"),
            self.output_js_filename,
            self.compile_level,
            self.options,
        )
