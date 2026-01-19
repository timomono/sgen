from enum import Enum
from io import BufferedReader, BufferedWriter, BytesIO
from pathlib import Path
from pprint import pprint
from typing import Any, BinaryIO, Generator
from sgen.base_renderer import BaseRenderer
import re
import html

from sgen.stdlib.pyrender.avoid_escape import AvoidEscape
from sgen.stdlib.pyrender.tokenizer import TokenType, processTags, tokenize

# py_exec = re.compile(
#     rb"{%\s*([\s\S]*?)%}", re.DOTALL
# )  # \s* = zero or more spaces
# py_eval = re.compile(rb"{{\s*([\s\S]*?)}}", re.DOTALL)

PERMITTED_MODULES = [
    "random",
    "math",
    "datetime",
    "sgen.stdlib.pyrender.avoid_escape",
    "sgen.stdlib.pyrender.template",
]


class PyRenderer(BaseRenderer):
    def render(
        self,
        render_from: BufferedReader | BinaryIO,
        render_to: BufferedWriter | BinaryIO,
        path: Path,
        **kwargs: dict,
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
                    if name in PERMITTED_MODULES
                    else (_ for _ in ()).throw(
                        PermissionError(f"Module {name} not permitted")
                    )
                ),
            },
        }
        exec_locals: dict[str, Any] = {
            **kwargs,
        }
        render_from.seek(0)
        self.sandboxing()
        try:

            def include_in_template(rel_path: str, **kwargs):
                from sgen.get_config import sgen_config

                bio = BytesIO(b"")
                renderer = PyRenderer()
                renderer.render(
                    open(sgen_config.SRC_DIR / path.parent / rel_path, "rb"),
                    bio,
                    path / rel_path,
                    **kwargs,
                )
                return AvoidEscape(bio.getvalue().decode())

            exec_locals["include"] = include_in_template

            # pprint(list(map(str, tokenize(from_, to))))

            processTags(
                render_from,
                render_to,
                lambda code: eval(
                    code.strip(),
                    exec_globals,
                    exec_locals,
                ),
                lambda code: exec(
                    code.strip(),
                    exec_globals,
                    exec_locals,
                ),
            )

            # content = py_exec.sub(
            #     process_exec,
            #     content,
            # )
            # content = py_eval.sub(
            #     process_eval,
            #     content,
            # )
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
