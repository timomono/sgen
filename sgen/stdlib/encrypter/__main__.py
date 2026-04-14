from pathlib import Path
from sgen.components.timeout import timeout
from wsgiref.simple_server import make_server
from logging import getLogger
from wsgiref.types import StartResponse, WSGIEnvironment
from mimetypes import guess_type
from json import loads

logger = getLogger(__name__)


def development_server(env: WSGIEnvironment, start_response: StartResponse):
    info: str = env["PATH_INFO"][1:]

    root: Path = Path(__file__).parent
    content_type: str

    match info:
        case "":
            path = root / "fingerprint.html"
            content_type = "text/html"

            headers = [
                ("Content-Type", content_type),
                ("Content-Length", str(path.stat().st_size)),
                ("Server", "Sgen Encrypter"),
            ]
            start_response("200 OK", headers)
            yield path.read_bytes()
            return
        case "fingerprint.js":
            path = root / info
            content_type = "application/javascript"

            headers = [
                ("Content-Type", content_type),
                ("Content-Length", str(path.stat().st_size)),
                ("Server", "Sgen Encrypter"),
            ]
            start_response("200 OK", headers)
            yield path.read_bytes()
            return
        case "fingerprint.css":
            path = root / info
            content_type = "text/css"

            headers = [
                ("Content-Type", content_type),
                ("Content-Length", str(path.stat().st_size)),
                ("Server", "Sgen Encrypter"),
            ]
            start_response("200 OK", headers)
            yield path.read_bytes()
            return
        case "save_browser":
            try:
                request_body_size = int(env.get("CONTENT_LENGTH", 0))
                request_body = env["wsgi.input"].read(request_body_size)
                fingerprint = loads(request_body)["fingerprint"]
                print(f"Received browser fingerprint: {fingerprint}")

                headers = [
                    ("Content-Type", "application/json"),
                    ("Content-Length", str(len(b'{"status": "success"}'))),
                    ("Server", "Sgen Encrypter"),
                ]
                start_response("200 OK", headers)
                yield b'{"status": "success"}'
                return
            except Exception as e:
                logger.error(f"Error processing save_browser request: {e}")
                body = (
                    b'{"status": "error", "message": "'
                    + str(e).encode()
                    + b'"}'
                )
                headers = [
                    ("Content-Type", "application/json"),
                    (
                        "Content-Length",
                        str(len(body)),
                    ),
                    ("Server", "Sgen Encrypter"),
                ]
                start_response("500 Internal Server Error", headers)
                yield body
                return
        case _:
            headers = [
                ("Content-Type", "text/plain"),
                ("Content-Length", str(len(b"404 Not Found"))),
                ("Server", "Sgen Encrypter"),
            ]
            start_response("404 Not Found", headers)
            return [b"404 Not Found"]


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
    host = "0.0.0.0"
    port = 8767

    runserver(host, port)
