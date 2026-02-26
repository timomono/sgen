from abc import ABC, abstractmethod
from functools import lru_cache
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
    def run(self, param: list[str]):
        pass


class Build(Command):
    # pass
    name = "build"

    def run(self, param):
        from sgen.build import build

        if len(param) != 0:
            raise TypeError(
                f"Too many or too few arguments "
                f"(got {len(param)}, excepted 0)"
            )

        build()
        logger.info("Successfully built!")


class ListenChange(Command):
    name = "listen"

    def run(self, param):
        from sgen.detect_change import listenChange

        if len(param) != 0:
            raise TypeError(
                f"Too many or too few arguments "
                f"(got {len(param)}, excepted 0)"
            )
        listenChange()


class HttpServer(Command):
    name = "runserver"

    def run(self, param: list[str]):
        from sgen.server import runserver

        if len(param) > 1:
            raise TypeError(
                f"Too many or too few arguments "
                f"(got {len(param)}, excepted 0 to 1)"
            )
        if len(param) == 1:
            if ":" in param[0]:
                host, _port_str = param[0].split(":")
                port = int(_port_str)
            else:
                host, port = "localhost", int(param[0])
            runserver(host, port)
        else:
            runserver()


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
            Path(__file__).parent / "templates" / "project",
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


class ExampleNotFoundError(NotImplementedError):
    pass


def did_you_mean(list_: list, text: str, max_similarity: int = 7) -> list[str]:
    return [t for t in list_ if similarity(t, text) < max_similarity]


@lru_cache(maxsize=100)
def similarity(text1: str, text2: str) -> int:
    if text1 == "":
        return len(text2)
    if text2 == "":
        return len(text1)
    if text1[0] == text2[0]:
        return similarity(text1[1:], text2[1:])
    l1 = similarity(text1, text2[1:])
    l2 = similarity(text1[1:], text2)
    l3 = similarity(text1[1:], text2[1:])
    return 1 + min(l1, l2, l3)


class CreateExampleProj(Command):
    name = "example"

    def run(self, param: list):
        from shutil import copytree

        if len(param) != 2:
            raise TypeError(
                f"Too many or too few arguments "
                f"(got {len(param)}, excepted 1)"
            )

        exampleName: str = param[0]
        if "/" in exampleName or "\\" in exampleName:
            raise ExampleNotFoundError(
                "Example name include slash or backslash."
            )
        examplesFolder = Path(__file__).parent / "example"
        examplePath: Path = Path(__file__).parent / "example" / param[0]
        projPath = Path(param[1])
        ignoreNameList = [".DS_Store", "__pycache__"]
        exampleNames = [
            n
            for n in map(lambda p: str(p.name), examplesFolder.glob("*"))
            if n not in ignoreNameList
        ]

        if (not examplePath.exists()) or exampleName in ignoreNameList:
            did_you_mean_result = did_you_mean(exampleNames, exampleName)
            raise ExampleNotFoundError(
                f'Example "{exampleName}" not implemented. '
                + ("Did you mean: " if did_you_mean_result != [] else "")
                + f'{" or ".join(did_you_mean_result)}'
                # f'Excepted: ({", ".join(exampleNames)})'
            )

        if projPath.exists():
            try:
                prompt = input(
                    f"{projPath} is already exists. override? (y/n): "
                )
            except KeyboardInterrupt:
                logger.warning("Cancelled by user. ")
                return
            if not (prompt.lower() == "y" or prompt.lower() == "yes"):
                logger.warning("Cancelled by user. ")
                return

        copytree(
            examplePath,
            projPath,
            dirs_exist_ok=True,
            ignore=createProjIgnoreTree,
        )

        for file in projPath.glob("**/*"):
            if file.is_dir():
                continue
            with open(file, "rb") as f:
                body = f.read()
                body = body.replace(
                    b"{{project_name}}",
                    projPath.resolve().name.encode("utf-8"),
                )
            with open(file, "wb") as f:
                f.write(body)


commands: list[Command] = [
    Build(),
    CreateProject(),
    ListenChange(),
    HttpServer(),
    CreateExampleProj(),
]
