from abc import ABC, abstractmethod
from logging import getLogger
from pathlib import Path
from typing import Iterable

logger = getLogger(__name__)


class Command(ABC):
    @property
    @abstractmethod
    def name(self):
        pass

    @abstractmethod
    def run(self, param: dict):
        pass


class Build(Command):
    # pass
    name = "build"

    def run(self, param: dict):
        from build import build  # type: ignore

        if len(param) != 0:
            raise TypeError(
                f"Too many or too few arguments "
                f"(got {len(param)}, excepted 0)"
            )

        build()


class ListenChange(Command):
    name = "listen"

    def run(self, param: dict):
        from detect_change import listenChange

        if len(param) != 0:
            raise TypeError(
                f"Too many or too few arguments "
                f"(got {len(param)}, excepted 0)"
            )
        listenChange()


def createProjIgnoreTree(dir: str, filenames: list[str]) -> Iterable[str]:
    ignores = set()
    for filename in filenames:
        path = Path(dir) / filename
        if any(
            substring in str(path.resolve())
            for substring in ["__pycache__", "build", ".DS_Store"]
        ):
            ignores.add(filename)
    return ignores


class CreateProject(Command):
    name = "create"

    def run(self, param):
        from shutil import copytree

        if len(param) != 1:
            raise TypeError(
                f"Too many or too few arguments "
                f"(got {len(param)}, excepted 1)"
            )

        projPath = Path(param[0])

        if projPath.exists():
            try:
                prompt = input(
                    f"{param[0]} is already exists. override? (y/n): "
                )
            except KeyboardInterrupt:
                logger.warn("Cancelled by user. ")
                return
            if not (prompt.lower() == "y" or prompt.lower() == "yes"):
                logger.warn("Cancelled by user. ")
                return

        copytree(
            Path(__file__).parent / "example",
            param[0],
            dirs_exist_ok=True,
            ignore=createProjIgnoreTree,
        )

        for file in projPath.glob("**/*"):
            if file.is_dir():
                continue
            with open(file, "r") as f:
                body = f.read()
                body = body.replace(
                    "{{project_name}}", projPath.resolve().name
                )
            with open(file, "w") as f:
                f.write(body)


commands: list[Command] = [Build(), CreateProject(), ListenChange()]
