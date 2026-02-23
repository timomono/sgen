from logging import getLogger
from pathlib import Path
import re
import shutil
from sgen.base_middleware import BaseMiddleware
from sgen.components.override_decorator import override
from subprocess import run, PIPE
from uuid import uuid4

cdn = b'<script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"></script>'
logger = getLogger(__name__)


class TailwindcssMiddleware(BaseMiddleware):
    @override
    def __init__(self, use_cdn=False, minify=True) -> None:
        self.use_cdn = use_cdn
        self.minify = minify
        super().__init__()

    @override
    def do(self, build_path: Path):
        if self.use_cdn:
            # Use CDN
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
        else:
            temp_path = build_path / "temp"
            temp_path.mkdir()
            for file in build_path.glob("**/*.css"):
                temp_file = temp_path / (uuid4().hex + ".css")
                try:
                    logger.debug(f"Processing {file} with tailwindcss...")
                    logger.debug(
                        f"Running command: npx -y @tailwindcss/cli -i {file} -o {temp_file} {'--minify' if self.minify else ''}"
                    )
                    result = run(
                        [
                            f"npx",
                            "-y",
                            "@tailwindcss/cli",
                            "-i",
                            file.absolute(),
                            "-o",
                            temp_file.absolute(),
                            *(["--minify"] if self.minify else []),
                        ],
                        stdout=PIPE,
                        stderr=PIPE,
                    )
                    if result.stdout != b"":
                        logger.info("stdout of tailwindcss:")
                        logger.info(result.stdout.decode())
                    if "Done in" not in result.stderr.decode():
                        logger.warning(
                            f"stderr of tailwindcss (during processing {file}):"
                        )
                        logger.warning(result.stderr.decode())
                    file.unlink()
                    shutil.copy(temp_file, file)
                    temp_file.unlink()
                except Exception as e:
                    logger.warning("Error while running tailwindcss:")
                    logger.warning(e)
