from pathlib import Path
from time import sleep
from typing import Generator

from base_config import config
from logging import getLogger

from build import build  # type:ignore

logger = getLogger(__name__)


def listenChange():
    mTimes: dict[Path, float] = {}
    logger.warn("Change listening...")
    try:
        build()
        while True:
            listen_files: Generator[Path, None, None] = Path(
                config().BASE_DIR
            ).glob("**/*")
            for filepath in listen_files:
                if str(filepath.resolve()).startswith(
                    str((config().BASE_DIR / "build").resolve())
                ):
                    continue
                old_time = mTimes.get(filepath)
                mtime = filepath.stat().st_mtime
                mTimes[filepath] = mtime
                if old_time is None:
                    continue
                elif mtime > old_time:
                    logger.warn(f"{filepath} changed, rebuilding. ")
                    build()
            sleep(0.3)
    except KeyboardInterrupt:
        return
