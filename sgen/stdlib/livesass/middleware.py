from logging import getLogger
from sgen.base_middleware import BaseMiddleware
import subprocess
from pathlib import Path
from typing import override

logger = getLogger(__name__)


class LiveSassMiddleware(BaseMiddleware):
    @override
    def __init__(
        self,
        sass_cli: str = "sass",
        out_filename: Path = Path("./cs"),
        options: tuple[str] | None = None,
    ) -> None:
        from sgen.get_config import sgen_config

        self.sass_cli = sass_cli
        self.out_filename = out_filename
        if options is None:
            self.options = (
                ("--style", "compressed", "--no-source-map")
                if sgen_config.DEBUG
                else ()
            )
        else:
            self.options = options
        super().__init__()

    @override
    def do(self, build_dir: Path):
        from sgen.get_config import sgen_config

        logger.info("Compiling sass...")
        res = subprocess.run(
            (
                self.sass_cli,
                f"{sgen_config.SRC_DIR}:{build_dir/self.out_filename}",
            )
            + self.options,
            encoding="utf-8",
            stderr=subprocess.PIPE,
        )
        logger.info("Compiled")
        if res.stderr != "":
            logger.warning("[SASS STDERR]\n" + res.stderr)
        logger.warning(f"{sgen_config.SRC_DIR}:{build_dir/self.out_filename}")
