from pathlib import Path
from sgen.components.timeout import timeout
from sgen.get_config import sgen_config
from wsgiref.simple_server import make_server
from logging import getLogger
from wsgiref.types import StartResponse, WSGIEnvironment
from mimetypes import guess_type

logger = getLogger(__name__)


@timeout(3)
def development_server(env: WSGIEnvironment, start_response: StartResponse):
    info: str = env["PATH_INFO"][1:]

    root: Path = sgen_config.BUILD_DIR
    path: Path = root.joinpath(info).resolve()
    content_type: str

    if path.exists() and (
        path.is_file() or (path.is_dir() and (path / "index.html").exists())
    ):
        if path.is_dir():
            path = path / "index.html"
        status = "200 OK"
        content_type = guess_type(path)[0] or "text/plain"

        headers = [
            ("Content-Type", content_type),
            ("Content-Length", str(path.stat().st_size)),
            ("Server", "Sgen development server"),
        ]
        start_response(status, headers)
        with open(path, "rb") as f:
            while byte := f.read(5 * 1024):
                yield byte
    else:
        # Find 404.html
        for parent in path.parents:
            if parent < root:
                # Default 404
                body = b"404 Not Found"
                status = "404 Not Found"
                content_type = "text/plain"

                headers = [
                    ("Content-Type", content_type),
                    ("Content-Length", str(len(body))),
                    ("Server", "Sgen development server"),
                ]
                start_response(status, headers)
                return [body]

            if (parent / "404.html").exists():
                path = parent / "404.html"
                status = "404 Not Found"
                body = path.read_bytes()
                content_type = guess_type(path)[0] or "text/plain"

                headers = [
                    ("Content-Type", content_type),
                    ("Content-Length", str(path.stat().st_size)),
                    ("Server", "Sgen development server"),
                ]
                start_response(status, headers)
                with open(path, "rb") as f:
                    while byte := f.read(5 * 1024):
                        yield byte
        # find_404_path = path.parent
        # while True:
        #     if find_404_path in root.parents:
        #         # Default 404
        #         body = b"404 Not Found"
        #         status = "404 Not Found"
        #         content_type = "text/plain"
        #         break
        #     if (find_404_path / "404.html").exists():
        #         path = find_404_path / "404.html"
        #         status = "200 OK"
        #         body = path.read_bytes()
        #         content_type = guess_type(path)[0] or "text/plain"
        #         break
        #     find_404_path = path.parent


def runserver(host: str = "localhost", port: int = 8282):
    server = make_server(host, port, development_server)
    logger.warning(f"serving at http://{host}:{port}")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        return
    finally:
        server.server_close()


if __name__ == "__main__":
    host = "localhost"
    port = 8282

    runserver(host, port)
