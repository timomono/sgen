from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import re
from typing import ClassVar, List
from sgen.cli import running_command
from sgen.base_middleware import BaseMiddleware
from sgen.cmds import ListenChange
from threading import Thread
from queue import Queue
from logging import getLogger

from sgen.components.override_decorator import override

logger = getLogger(__name__)


class SSEHandler(BaseHTTPRequestHandler):
    clients: ClassVar[List[Queue[str]]] = []

    def do_GET(self) -> None:
        if self.path != "/events":
            self.send_response(404)
            self.end_headers()
            return

        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Connection", "keep-alive")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

        q: Queue[str] = Queue()
        self.clients.append(q)

        try:
            while True:
                # Wait for event
                message = q.get()
                data = f"data: {message}\n\n".encode()
                self.wfile.write(data)
                self.wfile.flush()
        except (BrokenPipeError, ConnectionResetError):
            pass
        finally:
            self.clients.remove(q)

    @classmethod
    def broadcast(cls, message: str) -> None:
        for q in cls.clients:
            q.put(message)


SCRIPT = b"""
    const origin = `${location.protocol}//${location.hostname}:8572`;

    console.log(origin);
    const evtSource = new EventSource(origin + "/events");
    evtSource.onmessage = function(event) {
        if (event.data === "reload") {
            location.reload();
        }
    };
"""


class AutoReloadMiddleware(BaseMiddleware):
    """A middleware to automatically reload the page when a file changes.
    This is useful for development mode.
    """

    isServerRunning = False

    @override
    def __init__(self) -> None:
        super().__init__()

    @override
    def before(self, build_path: Path) -> None:
        # if not already running, start the SSE server
        if not AutoReloadMiddleware.isServerRunning:
            logger.info("starting SSE server for auto reloading")
            Thread(
                target=ThreadingHTTPServer(
                    ("0.0.0.0", 8572), SSEHandler
                ).serve_forever,
                daemon=True,
            ).start()
            AutoReloadMiddleware.isServerRunning = True
        return super().before(build_path)

    @override
    def do(self, build_path: Path):
        is_debug = isinstance(running_command, ListenChange)
        if not is_debug:
            return

        # add a script to the page to listen for SSE events
        for html_file in build_path.rglob("*.html"):
            content = html_file.read_bytes()
            content = re.sub(
                rb"</body *>",
                rb"<script>" + SCRIPT + rb"</script></body>",
                content,
            )
            html_file.write_bytes(content)

    @override
    def after(self, build_path: Path) -> None:
        SSEHandler.broadcast("reload")
