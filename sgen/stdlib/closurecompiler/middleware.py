from logging import getLogger
import os
from pathlib import Path
import re
import shutil
from sgen.components.override_decorator import override
from urllib.parse import urlparse
import uuid
from sgen.base_middleware import BaseMiddleware
from sgen.stdlib.closurecompiler.compile import (
    CompileLevel,
    compileByFilenames,
)

logger = getLogger(__name__)


class ClosureCompilerMiddleware(BaseMiddleware):
    @override
    def __init__(
        self,
        output_js_filename: Path | None = None,
        except_debug: bool = True,
        compile_level: CompileLevel = CompileLevel.SIMPLE_OPTIMIZATIONS,
        script_tag: bool = False,
        options: list[str] = [],
    ) -> None:
        from sgen.get_config import sgen_config

        self.except_debug = except_debug
        self.compile_level = compile_level
        self.script_tag = script_tag
        if output_js_filename is None:
            self.output_js_filename = sgen_config.BUILD_DIR / "main.js"
        else:
            self.output_js_filename = output_js_filename
        self.options = options
        super().__init__()

    @override
    def do(self, build_path: Path):
        from sgen.get_config import sgen_config

        if self.except_debug and sgen_config.DEBUG:
            return
        scripts_in_html: set[str] = set()
        temp_script_tags = build_path / "temp_script_tags"
        temp_script_tags.mkdir()
        # Apply script tag in html
        if self.script_tag:
            for html_file in build_path.glob("**/*.html"):
                with open(html_file, "r") as f:
                    html_body = f.read()
                relative_out_js_file = os.path.relpath(
                    self.output_js_filename,
                    start=html_file.parent,
                )
                matches = re.finditer(
                    r"<head[^>]*>[\s\S]*"
                    r"< *script *[^>]*(src=[\"\']?[^>\"' ]*[\"\']?)?"
                    r"[^>]*>"
                    r"(?P<body>[\s\S]*)< */ *script *>"
                    r"[\s\S]*< */ *head *>",
                    # r"(?P<prefix><head[^>]*>[\s\S]"
                    # r"< *script +[^>]*src=)[\"\']?(?P<url>[^>\"' ]*)[\"\']?"
                    # r"(?P<tag_suffix> *[^>]*>)"
                    # r"(?P<body>[\s\S])(?P<suffix>< */ *script *>"
                    # r"[\s\S]< */ *head *>)",
                    # lambda m: (
                    #     rf'{m.group("prefix")}'
                    #     rf'"{relative_out_js_file}"'
                    #     rf'{m.group("tag_suffix")}'
                    #     rf'{m.group("body")}'
                    #     if urlparse(m.group(2)).hostname is None
                    #     else m.string
                    # ),
                    html_body,
                )
                for match in matches:
                    body = match.group("body")
                    scripts_in_html.add(body)
                    with open(
                        temp_script_tags
                        / f"script-tag-{html_file.name}-{uuid.uuid4()}.js",
                        "w",
                    ) as f:
                        f.write(body)
        if list(build_path.glob("**/*.js")) != []:
            logger.warning("Compiling javascript with Closure compiler...")
            is_protected = False
            for file in build_path.glob("**/*.js"):
                with open(file, "rb") as f:
                    if f.read(1) == b"\xff":
                        temp_file_path = file.parent / (file.name + ".tmp")
                        with open(file, "rb") as original_file, open(
                            temp_file_path, "wb"
                        ) as temp_file:
                            original_file.seek(1)
                            while chunk := original_file.read(4096):
                                temp_file.write(chunk)
                        file.unlink()
                        temp_file_path.rename(file)
                        is_protected = True
            compileByFilenames(
                build_path.glob("**/*.js"),
                self.output_js_filename,
                self.compile_level,
                self.options,
            )
            if is_protected:
                for file in build_path.glob("**/*.js"):
                    temp_file_path = file.parent / (file.name + ".tmp")
                    with open(file, "rb") as original_file, open(
                        temp_file_path, "wb"
                    ) as temp_file:
                        temp_file.write(b"\xff")
                        while chunk := original_file.read(4096):
                            temp_file.write(chunk)
                        file.unlink()
                        temp_file_path.rename(file)
            logger.warning("Compiled. ")
            if temp_script_tags.exists():
                shutil.rmtree(temp_script_tags)
            # Remove duplicate files in main.js
            for js_file in build_path.glob("**/*.js"):
                # Except main.js
                if js_file.resolve() == self.output_js_filename.resolve():
                    continue
                js_file.unlink()

            # Update script tag in HTML
            # TODO: Add .htm
            for html_file in build_path.glob("**/*.html"):
                with open(html_file, "r") as f:
                    html_body = f.read()
                relative_out_js_file = os.path.relpath(
                    self.output_js_filename,
                    start=html_file.parent,
                )
                script_match = re.match(
                    r"[\s\S]*[\s\S]*"
                    r"< *script[^>]*>"
                    r"[\s\S]*</script *>[\s\S]*[\s\S]*",
                    html_body,
                )
                if script_match is not None:
                    # print(f"Removing on {html_file}")
                    # Remove script tags
                    html_body = re.sub(
                        r"(<head[^>]*>)([\s\S]*?)(</head *>)",
                        lambda hm: hm.group(1)
                        + re.sub(
                            r"(<script(?![^>]*\bsrc\b)[^>]*>[\s\S]*?"
                            r"</script *>)",
                            lambda m: ("" if self.script_tag else m.group(0)),
                            hm.group(2),
                        )
                        + hm.group(3),
                        html_body,
                    )
                    # print(html_body)
                    # Remove tag with src
                    html_body = re.sub(
                        r"(< *script(?:[^>]*?"
                        r"src=[\"']?([^\"']+)[\"']?[^>]*?)[^>]*>"
                        r"[\s\S]*?</script *>)",
                        lambda m: (
                            ""
                            if urlparse(m.group(2)).hostname is None
                            else m.group(1)
                        ),
                        html_body,
                    )
                    # Add main.js
                    html_body = re.sub(
                        "</head *>",
                        f"<script src='{relative_out_js_file}' async></script>"
                        "</head>",
                        html_body,
                    )
                    # Remove it
                    # html_body = re.sub(
                    #     r"(<head[^>]*>[\s\S]*?)< *script(?:[^>]*?"
                    #     r"src=[\"']?([^\"']+)[\"']?[^>]*?)?[^>]*>"
                    #     r"[\s\S]*?</script *>([\s\S]*</head>)",
                    #     lambda m: (
                    #         rf"{m.group(1)}{m.group(3)}"
                    #         # if urlparse(m.group(2)).hostname is None
                    #         # else m.string
                    #     ),
                    #     html_body,
                    # )
                with open(html_file, "w") as f:
                    f.write(html_body)
