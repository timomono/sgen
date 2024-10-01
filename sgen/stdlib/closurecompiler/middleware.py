import os
from pathlib import Path
import re
import shutil
from typing import override
from urllib.parse import urlparse
import uuid
from sgen.base_middleware import BaseMiddleware
from sgen.stdlib.closurecompiler.compile import (
    CompileLevel,
    compileByFilenames,
)


class ClosureCompilerMiddleware(BaseMiddleware):
    @override
    def __init__(
        self,
        output_js_filename: Path | None = None,
        except_debug: bool = True,
        compile_level: CompileLevel = CompileLevel.SIMPLE_OPTIMIZATIONS,
        options: list[str] = [],
    ) -> None:
        from sgen.get_config import sgen_config

        self.except_debug = except_debug
        self.compile_level = compile_level
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
        for html_file in build_path.glob("**/*.html"):
            with open(html_file, "r") as f:
                html_body = f.read()
            relative_out_js_file = os.path.relpath(
                self.output_js_filename,
                start=html_file.parent,
            )
            matches = re.finditer(
                r"<head[^>]*>[\s\S]"
                r"< *script +[^>]*src=[\"\']?[^>\"' ]*[\"\']?"
                r" *[^>]*>"
                r"(?P<body>[\s\S])< */ *script *>"
                r"[\s\S]< */ *head *>",
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
                    / f"script-tag-{html_file.name}-{uuid.uuid4()}.js"
                ) as f:
                    f.write(body)
        compileByFilenames(
            build_path.glob("**/*.js"),
            self.output_js_filename,
            self.compile_level,
            self.options,
        )
        # shutil.rmtree(temp_script_tags)
        # Remove duplicate files in main.js
        for js_file in build_path.glob("**/*.js"):
            # Except main.js
            if js_file.resolve() == self.output_js_filename.resolve():
                continue
            js_file.unlink()

        # Update script tag in HTML
        for html_file in build_path.glob("**/*.html"):
            with open(html_file, "r") as f:
                html_body = f.read()
            relative_out_js_file = os.path.relpath(
                self.output_js_filename,
                start=html_file.parent,
            )
            # TODO: It should won't delete closing tag!
            html_body = re.sub(
                r"(<head[^>]*>[\s\S]"
                r"< *script +[^>]*src=)[\"\']?([^>\"' ]*)[\"\']?( *[^>]*>"
                r"[\s\S]< */ *head *>)",
                lambda m: (
                    rf'{m.group(1)}"{relative_out_js_file}"{m.group(3)}'
                    if urlparse(m.group(2)).hostname is None
                    else m.string
                ),
                html_body,
            )
            with open(html_file, "w") as f:
                f.write(html_body)
