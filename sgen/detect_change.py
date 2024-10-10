from enum import Enum
import math
import os
from pathlib import Path

from time import sleep
from typing import Iterable

from logging import getLogger, Handler, INFO, root

from sgen.build import build  # type:ignore
import shutil
from sgen.components.override_decorator import OverrideStrict
from sgen.get_config import sgen_config

logger = getLogger(__name__)
root.setLevel(INFO)


def listenChange():
    IGNORE_LIST = (
        "build",
        "sitemap.xml",
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
                    clean_log()
                    # print(mtime, old_time)
                    logger.warning(
                        f"{filepath} changed, rebuilding. ",
                    )
                    build()
                    # Prevent multiple builds when multiple files are
                    # changed at once
                    # sleep(1)
                    new_listen_files: Iterable[Path] = Path(
                        sgen_config.BASE_DIR
                    ).glob("*")
                    new_listen_files = [
                        f
                        for f in listen_files
                        if not any(
                            map(lambda n: n in str(f).split("/"), IGNORE_LIST)
                        )
                    ]
                    for update_path in new_listen_files:
                        mtime = update_path.stat().st_mtime
                        mTimes[update_path] = mtime
                    logger.info(
                        f"{filepath} changed, built. ",
                    )
                    # logger.exception(e)
                    # msg = (
                    #     e.args[0]  # type:ignore
                    #     if len(e.args) == 0
                    #     else e.args  # type:ignore
                    # )
                    # e.with_traceback()
                    # logger.error(f"{msg}")
                    # logger.error(f"{e.with_traceback()}")
                    # logger.warn("Error while building: ")
                    # logger.exception(e)

            sleep(0.3)
    except Exception:
        logger.exception("An error occurred during build")
    except KeyboardInterrupt:
        clean_log()
        return


class ConsoleColor(Enum):
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"


class ConsoleOutput(OverrideStrict):
    color: ConsoleColor | None
    body: str

    def __init__(
        self,
        body: str,
        color: ConsoleColor | None = None,
    ) -> None:
        self.color = color
        self.body = body

    def getColorString(self):

        if self.color:
            return self.color.value + self.body + "\033[0m"
        else:
            return self.body


console_outputs: list[ConsoleOutput] = []

# MAX_OUTPUT_CONSOLE = 5


def fPrint(s: str, color: ConsoleColor | None = None):
    terminal_size = shutil.get_terminal_size()
    # max_output_console = terminal_size.lines
    # if len(console_outputs) > max_output_console:
    #     console_outputs.pop()
    console_outputs.append(ConsoleOutput(s, color))
    clean_screen()
    for console_output in console_outputs:
        colorStr = console_output.getColorString()
        terminal_size = shutil.get_terminal_size()
        if len(s) > terminal_size.columns:
            print(colorStr)
            continue
        spaceSize = (terminal_size.columns - len(console_output.body)) / 2
        print(
            "\r"
            + "=" * math.ceil(spaceSize)
            + colorStr
            + "=" * math.floor(spaceSize),
        )


class FPrintHandler(Handler):
    def __init__(self):
        super().__init__()

    def emit(self, record):
        log_entry = self.format(record)
        if record.levelname == "INFO":
            fPrint(log_entry, color=ConsoleColor.GREEN)
        elif record.levelname == "WARNING":
            fPrint(log_entry, color=ConsoleColor.YELLOW)
        elif record.levelname == "ERROR":
            fPrint(log_entry, color=ConsoleColor.RED)
        else:
            fPrint(log_entry)


# logger.addHandler(FPrintHandler())
# Add to root logger
root.addHandler(FPrintHandler())


def clean_log():
    global console_outputs
    clean_screen()
    console_outputs = []


def clean_screen():
    os.system("cls" if os.name == "nt" else "clear")


clean_log()

# atexit.register(clean)
