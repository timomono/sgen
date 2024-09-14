from enum import Enum
import math
from pathlib import Path
from time import sleep
from typing import Iterable

from logging import getLogger

from sgen.build import build  # type:ignore
import shutil
import atexit
from sgen.get_config import sgen_config

logger = getLogger(__name__)


def listenChange():
    IGNORE_LIST = (
        "build",
        "env",
        "venv",
        ".env",
        ".venv",
        ".mypy_cache",
        ".DS_Store",
        "__pycache__",
    )
    mTimes: dict[Path, float] = {}
    logger.warning("Change listening...")
    try:
        build()
        while True:
            listen_files: Iterable[Path] = Path(sgen_config.BASE_DIR).glob(
                "**/"
                # "[!build]"
                # "[!env]"
                # "[!venv]"
                # "[!.env]"
                # "[!.venv]"
                # "[!.mypy_cache]"
                # "[!.DS_Store]"
                # "[!__pycache__]"
                "*"
            )
            # Ignore
            listen_files = [
                f
                for f in listen_files
                if not any(map(lambda n: n in str(f).split("/"), IGNORE_LIST))
            ]
            for filepath in listen_files:
                old_time = mTimes.get(filepath)
                mtime = filepath.stat().st_mtime
                mTimes[filepath] = mtime
                if old_time is None:
                    continue
                elif mtime > old_time:
                    # print(mtime, old_time)
                    fPrint(
                        f"{filepath} changed, rebuilding. ",
                        color=ConsoleColor.YELLOW,
                    )
                    try:
                        # Prevent multiple builds when multiple files are
                        # changed at once
                        # for filepath in listen_files:
                        #     old_time = mTimes.get(filepath)
                        #     mtime = filepath.stat().st_mtime
                        #     mTimes[filepath] = mtime
                        build()
                        fPrint(
                            f"{filepath} changed, built. ",
                            color=ConsoleColor.GREEN,
                        )
                    except Exception as e:
                        fPrint(
                            f"Error while building: {e}",
                            color=ConsoleColor.RED,
                        )
                        # logger.warn("Error while building: ")
                        # logger.exception(e)

                sleep(0.3)
    except KeyboardInterrupt:
        clean()
        return


class ConsoleColor(Enum):
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"


def fPrint(s, color: ConsoleColor | None = None):
    if color:
        colorStr = color.value + s + "\033[0m"
    else:
        colorStr = s
    terminal_size = shutil.get_terminal_size()
    if len(s) > terminal_size.columns:
        print("\r" + colorStr)
    spaceSize = (terminal_size.columns - len(s)) / 2
    # print("\r" + "-" * terminal_size.columns, end="")
    print("\r", end="")
    for i in range(terminal_size.columns):
        print("-", end="", flush=True)
        sleep(0.003)
    sleep(0.2)
    print(
        "\r"
        + "=" * math.ceil(spaceSize)
        + colorStr
        + "=" * math.floor(spaceSize),
        end="",
    )


def clean():
    terminal_size = shutil.get_terminal_size()
    print("\r", end="", flush=True)
    print(" " * terminal_size.columns, end="", flush=True)


atexit.register(clean)
