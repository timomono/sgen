from sgen.base_middleware import BaseMiddleware
from pathlib import Path
from base64 import b64encode
import re

script_tag_regexp = re.compile(
    rb"<script [^>]*type *= *[\"']?(?:text/x-python|py|python)[\"']?[^>]>"
    rb"(?P<script>[\s\S]*)"
    rb"(?P<suffix></script *>)"
)
head_tag_regexp = re.compile(rb"(<head[^>]*>)")

pyodide_cdn = (
    b'<script src="https://cdn.jsdelivr.net/pyodide/v0.29.3/full/pyodide.js">'
    + b"</script>"
)


class PyodideMiddleware(BaseMiddleware):
    def __init__(self) -> None:
        super().__init__()

    def do(self, build_path: Path):
        for file in build_path.iterdir():
            if file.suffix == ".py":
                with open(file, "rb") as f:
                    body = f.read()
                with open(file, "wb") as f:
                    f.write(PyodideMiddleware.template(body))
                file.rename(file.with_suffix(".js"))
            elif file.suffix in [".html", ".htm"]:
                with open(file, "rb") as f:
                    body = f.read()
                with open(file, "wb") as f:
                    replaced = script_tag_regexp.sub(
                        lambda m: b"<script>"
                        + PyodideMiddleware.template(
                            m.group("script"),
                        )
                        + m.group("suffix"),
                        body,
                    )
                    # add the script tag if necessary
                    # if body != replaced:
                    replaced = head_tag_regexp.sub(
                        lambda m: m.group(1) + pyodide_cdn, replaced
                    )
                    f.write(replaced)

    @staticmethod
    def template(script: bytes):
        return (
            b"""// ATTENTION: DO NOT USE THE BASE64 FOR SECURITY REASONS
(async () => {
    const loading_status = {
        unloaded: 0,
        loading: 1,
        loaded: 2,
    }
    const decoded_utf8str = atob("%s");
    const decoded_array = new Uint8Array(Array.prototype.map.call(decoded_utf8str, c => c.charCodeAt()));
    const decoded = new TextDecoder().decode(decoded_array);

    const run = () => __pyodide_obj.runPython(decoded);

    switch (window.__pyodide_loading_status) {
        case loading_status.unloaded:
        case undefined:
            window.__pyodide_obj ||= await loadPyodide();
            run()
            window.dispatchEvent(new Event("pyodideload"))
            break;

        case loading_status.loading:
            window.addEventListener("pyodideload", run)
            break;

        case loading_status.loaded:
            run()
            break;
    }
})()
"""
            # % json.dumps(bytes(script)).encode()
            % b64encode(script)
        )
