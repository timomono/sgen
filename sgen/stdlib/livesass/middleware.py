from logging import getLogger
from sgen.base_middleware import BaseMiddleware
import subprocess
from pathlib import Path
from sgen.components.override_decorator import override

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
        # TODO: Only build on update saas
        # (Add optional "change_file" parameter?)
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
            stdout=subprocess.PIPE,
        )
        if res.stderr != "":
            logger.warning("[SASS STDERR]\n" + res.stderr)
        if res.stdout != "":
            logger.warning("[SASS STDOUT]\n" + res.stdout)
        logger.info("Compiled")
