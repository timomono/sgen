from enum import StrEnum, auto
import hashlib
from logging import getLogger
import os
from pathlib import Path
import re
import shutil
from sgen.base_middleware import BaseMiddleware
from sgen.components.download import download
from sgen.components.override_decorator import override
from subprocess import run, PIPE
from uuid import uuid4

from sgen.components.platform_cache import get_cache_dir
from sgen.components.process import is_process_running
from sgen.stdlib.tailwindcss.select_binary import get_tailwind_binary_url
from sys import stdout

cdn = b'<script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"></script>'
logger = getLogger(__name__)


def convert_to_cache_name(file: Path) -> str:
    from sgen.get_config import sgen_config

    return (
        str(file.relative_to(sgen_config.BASE_DIR))
        .replace("/", "__")
        .replace("\\", "__")
    )


class TailwindcssMode(StrEnum):
    CDN = auto()
    NPX = auto()
    STANDALONE = auto()


class TailwindcssMiddleware(BaseMiddleware):
    """A middleware to process CSS files with Tailwind CSS.
    Attributes:
        minify (bool): Whether to minify the output CSS. Default is True.
        mode (TailwindcssMode): The mode to use for processing Tailwind CSS. Default is TailwindcssMode.STANDALONE.
        version (str): The version of Tailwind. ONLY AVAILABLE IN STANDALONE MODE. Default is 4.2.1.
    """

    @override
    def __init__(
        self,
        minify=True,
        mode: TailwindcssMode = TailwindcssMode.STANDALONE,
        version="4.2.1",
    ) -> None:
        self.minify = minify
        self.mode = mode
        self.version = version
        super().__init__()

    @override
    def do(self, build_path: Path):
        from sgen.get_config import sgen_config

        match self.mode:
            case TailwindcssMode.CDN:
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
            case TailwindcssMode.NPX | TailwindcssMode.STANDALONE:
                temp_path = build_path / "temp"
                temp_path.mkdir()
                files_num = len(list(build_path.glob("**/*.css")))
                is_progress_shown = False
                for i, file in enumerate(list(build_path.glob("**/*.css"))):
                    # check if the cache is available
                    with open(file, "rb") as frb:
                        file_hash = hashlib.file_digest(frb, "sha256").digest()
                    cached_hash = (
                        sgen_config.BASE_DIR
                        / ".cache"
                        / "tailwindcss"
                        / (convert_to_cache_name(file) + ".hash")
                    )
                    if (
                        cached_hash.exists() and cached_hash.is_file()
                    ) and cached_hash.read_bytes() == file_hash:
                        logger.debug(
                            f"Cache hit for {file}, skipping tailwindcss processing..."
                        )
                        shutil.copy(file, temp_path / file.name)
                        continue

                    stdout.write(
                        f"\033[KCompiling Tailwind CSS: "
                        + f"{i + 1: 2}"
                        + f"/{files_num: 2} "
                        + f"({i / files_num * 100: 5.1f}%) "
                        + str(file.relative_to(build_path))
                        + "\r"
                    )
                    is_progress_shown = True

                    temp_file = temp_path / (uuid4().hex + ".css")
                    try:
                        logger.debug(f"Processing {file} with tailwindcss...")
                        logger.debug(
                            f"Running command: tailwindcss -i {file} -o {temp_file} {'--minify' if self.minify else ''}"
                        )
                        match self.mode:
                            case TailwindcssMode.NPX:
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
                            case TailwindcssMode.STANDALONE:
                                cache_path = (
                                    get_cache_dir()
                                    / "tailwindcss"
                                    / "standalone"
                                    / self.version
                                )
                                cache_path.mkdir(parents=True, exist_ok=True)
                                binary_path = cache_path / "tailwindcss"

                                downloading_flag = cache_path / ".downloading"

                                if (
                                    not binary_path.exists()
                                    or not binary_path.is_file()
                                    or Path(
                                        downloading_flag
                                    ).exists()  # Avoid using broken cache when crash happens during downloading
                                ):
                                    # check if is another process downloading the binary or crashed
                                    if Path(
                                        downloading_flag
                                    ).exists() and is_process_running(
                                        int(Path(downloading_flag).read_text())
                                    ):
                                        raise RuntimeError(
                                            f"Another process (pid {Path(downloading_flag).read_text()}) is downloading tailwindcss standalone binary. Please wait until it's done."
                                        )

                                    url = get_tailwind_binary_url(self.version)
                                    logger.info(
                                        f"Downloading tailwindcss standalone binary from {url}..."
                                    )
                                    Path(downloading_flag).write_text(
                                        str(os.getpid())
                                    )
                                    download(url, binary_path)
                                    Path(downloading_flag).unlink()
                                    binary_path.chmod(0o755)
                                result = run(
                                    [
                                        binary_path.absolute(),
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

                        # write hash of original file to reduce unnecessary re-compiling
                        with open(file, "rb") as frb:
                            original_hash = hashlib.file_digest(frb, "sha256")
                        cache_file = (
                            sgen_config.BASE_DIR
                            / ".cache"
                            / "tailwindcss"
                            / (convert_to_cache_name(file))
                        )
                        hash_file = cache_file.with_suffix(
                            cache_file.suffix + ".hash"
                        )
                        hash_file.parent.mkdir(parents=True, exist_ok=True)

                        hash_file.write_bytes(original_hash.digest())
                        shutil.copy(
                            temp_file, cache_file
                        )  # Cache the compiled css

                        # replace original file with the compiled file
                        file.unlink()
                        shutil.copy(temp_file, file)
                        temp_file.unlink()
                    except Exception as e:
                        logger.warning("Error while running tailwindcss:")
                        logger.warning(e)
                if is_progress_shown:
                    stdout.write(
                        "\033[KTailwind - done\n"
                    )  # to clear the progress
