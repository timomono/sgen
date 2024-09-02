from abc import ABC, abstractmethod
from logging import getLogger
from pathlib import Path
from typing import Iterable

from base_config import config

logger = getLogger(__name__)


class Command(ABC):
    @property
    @abstractmethod
    def name(self):
        pass

    @abstractmethod
    def run(self, param: list):
        pass


class Build(Command):
    # pass
    name = "build"

    def run(self, param: list):
        from build import build  # type: ignore

        if len(param) != 0:
            raise TypeError(
                f"Too many or too few arguments "
                f"(got {len(param)}, excepted 0)"
            )

        build()
        logger.warn("Successfully built!")


class ListenChange(Command):
    name = "listen"

    def run(self, param: list):
        from detect_change import listenChange

        if len(param) != 0:
            raise TypeError(
                f"Too many or too few arguments "
                f"(got {len(param)}, excepted 0)"
            )
        listenChange()


class HttpServer(Command):
    name = "runserver"

    def run(self, param: list):
        if len(param) >= 1:
            raise TypeError(
                f"Too many or too few arguments "
                f"(got {len(param)}, excepted 0 to 1)"
            )
        if len(param) == 1:
            runserver(param[0])
        else:
            runserver()


def runserver(port: int = 8282):
    import http.server
    import socketserver

    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(
                *args, directory=str(config().BASE_DIR / "build"), **kwargs
            )

    with socketserver.TCPServer(("", port), Handler) as httpd:
        logger.warn(
            f"serving at port {port} http://localhost:{port}",
        )
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            return


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

    def run(self, param: list):
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
        examplePath = Path(__file__).parent / "example" / param[0]
        projPath = Path(param[1])

        if not examplePath.exists():
            raise ExampleNotFoundError(
                f'Example "{exampleName} not implemented. '
            )

        if projPath.exists():
            try:
                prompt = input(
                    f"{projPath} is already exists. override? (y/n): "
                )
            except KeyboardInterrupt:
                logger.warn("Cancelled by user. ")
                return
            if not (prompt.lower() == "y" or prompt.lower() == "yes"):
                logger.warn("Cancelled by user. ")
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
            with open(file, "r") as f:
                body = f.read()
                body = body.replace(
                    "{{project_name}}", projPath.resolve().name
                )
            with open(file, "w") as f:
                f.write(body)


commands: list[Command] = [
    Build(),
    CreateProject(),
    ListenChange(),
    HttpServer(),
    CreateExampleProj(),
]
