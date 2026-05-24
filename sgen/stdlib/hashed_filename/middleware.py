import hashlib
import os
from pathlib import Path
import re

from sgen.base_middleware import BaseMiddleware
from sgen.components.base_num import encode_bytes_to_base_n
from sgen.components.override_decorator import override

from logging import getLogger

logger = getLogger(__name__)


class HashedFilenameMiddleware(BaseMiddleware):
    script_and_style = re.compile(
        rb'(?P<prefix_script><(script)\s+[^>]*\bsrc=["\'])(?P<path_script>[^"\']+)(?P<suffix_script>["\'][^>]*>)|'
        rb'(?P<prefix_link><(link)\s+[^>]*\brel=["\']stylesheet["\'][^>]*\bhref=["\'])(?P<path_link>[^"\']+)(?P<suffix_link>["\'][^>]*>)'
    )

    @override
    def __init__(self) -> None:
        self.hash_map = {}

    @override
    def do(self, build_path: Path):
        for file in build_path.glob("**/*"):
            if not file.is_file():
                continue
            if file.suffix in (".css", ".js"):
                with open(file, "rb") as frb:
                    file_hash = encode_bytes_to_base_n(
                        hashlib.file_digest(frb, "sha256").digest(),
                        36,
                        "0123456789abcdefghijklmnopqrstuvwxyz",
                    )
                hash_path = file.parent / ((file_hash[:8]) + file.suffix)
                self.hash_map[file.relative_to(build_path)] = (
                    hash_path.relative_to(build_path)
                )
                file.rename(hash_path)

    @override
    def after(self, build_path: Path) -> None:
        from sgen.get_config import sgen_config

        for file in build_path.glob("**/*"):
            if not file.is_file():
                continue
            if file.suffix == ".html":

                def repl(match: re.Match):
                    prefix: bytes = match.group(
                        "prefix_script"
                    ) or match.group("prefix_link")
                    path: bytes = match.group("path_script") or match.group(
                        "path_link"
                    )
                    suffix: bytes = match.group(
                        "suffix_script"
                    ) or match.group("suffix_link")
                    if path.startswith(b"//") or path.startswith(b"http"):
                        return prefix + path + suffix

                    path_str = path.decode("utf-8")

                    html_dir = file.parent.relative_to(build_path)
                    if path_str.startswith("/"):
                        absolute_path = sgen_config.BUILD_DIR / path_str[1:]
                    else:
                        absolute_path = (html_dir / path_str).resolve()
                    print(absolute_path)
                    try:
                        relative_to_build = absolute_path.relative_to(
                            build_path.resolve()
                        )
                    except ValueError:
                        raise

                    if relative_to_build in self.hash_map:
                        hashed_path = self.hash_map[relative_to_build]

                        html_dir_abs = file.parent.resolve()
                        hashed_abs = (
                            build_path.resolve() / hashed_path
                        ).resolve()

                        rel = os.path.relpath(
                            hashed_abs, html_dir_abs
                        ).replace("\\", "/")

                        return prefix + rel.encode("utf-8") + suffix
                    else:
                        raise ValueError(
                            str(relative_to_build)
                            + str(self.hash_map)
                            + "File name is not changed: "
                            + path.decode(),
                        )

                file.write_bytes(
                    self.script_and_style.sub(repl, file.read_bytes())
                )
