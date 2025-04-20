from io import BufferedReader, BufferedWriter
from pathlib import Path
from sgen.base_renderer import BaseRenderer
import re

py_exec = re.compile(r"{%(.*?)%}")
py_eval = re.compile(r"{{(.*?)}}")


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
                    if name in ["random"]
                    else (_ for _ in ()).throw(
                        PermissionError(f"Module {name} not permitted")
                    )
                ),
            },
        }
        render_from.seek(0)
        self.sandboxing()
        for line in render_from:
            line = py_exec.sub(
                lambda m: exec(m.group(1).lstrip(), exec_globals),
                line,
            )
            line = py_eval.sub(
                lambda m: str(eval(m.group(1).lstrip(), exec_globals)),
                line,
            )
            render_to.write(line)
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
