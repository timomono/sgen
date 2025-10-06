from io import BufferedReader, BufferedWriter
from pathlib import Path
from sgen.base_renderer import BaseRenderer
import re
import html

from sgen.stdlib.pyrender.avoid_escape import AvoidEscape

py_exec = re.compile(rb"{%(.*?)%}")
py_eval = re.compile(rb"{{(.*?)}}")


class PyRenderer(BaseRenderer):
    def render(
        self,
        render_from: BufferedReader,
        render_to: BufferedWriter,
        path: Path,
    ) -> None:
        exec_globals = {
            "__builtins__": {
                "print": print,
                "range": range,
                "len": len,
                "int": int,
                "str": str,
                "float": float,
                "bool": bool,
                "list": list,
                "dict": dict,
                "set": set,
                "tuple": tuple,
                "sum": sum,
                "__import__": lambda name, *args: (
                    __import__(name, *args)
                    if name
                    in [
                        "random",
                        "math",
                        "datetime",
                        "sgen.stdlib.pyrender.avoid_escape",
                    ]
                    else (_ for _ in ()).throw(
                        PermissionError(f"Module {name} not permitted")
                    )
                ),
            },
        }
        render_from.seek(0)
        self.sandboxing()
        try:

            def process_exec(match):
                exec(match.group(1).lstrip(), exec_globals)
                return b""

            def process_eval(match):
                result = eval(match.group(1).lstrip(), exec_globals)
                if isinstance(result, AvoidEscape):
                    return str(result.value).encode()
                return html.escape(str(result)).encode()

            for line in render_from:
                line = py_exec.sub(
                    process_exec,
                    line,
                )
                line = py_eval.sub(
                    process_eval,
                    line,
                )
                render_to.write(line)
        finally:
            self.SANDBOXING = False
        return super().render(render_from, render_to, path)

    def sandboxing(self):
        from sys import addaudithook

        self.SANDBOXING = True

        def handle(event, args):
            if not self.SANDBOXING:
                return
            # Sandboxed to prevent accidental impact
            # if event == "open":
            #     print(args[0])
            #     raise PermissionError("Operation forbidden: open.")
            if event.split(".")[0] in [
                "subprocess",
                "os",
                "shutil",
                "winreg",
                "sys",
                "gc",
            ]:
                raise PermissionError(
                    f"Operation forbidden: {event.split(".")[0]}."
                )
            if event == "module.__getattribute__" and args[0] in [
                "subprocess",
                "os",
                "shutil",
                "winreg",
                "sys",
                "gc",
            ]:
                raise PermissionError(f"Operation forbidden: {args[0]}")
            if event == "import" and args[0] == "os":
                raise ImportError("Usage of 'os' module is prohibited!")

        addaudithook(handle)
