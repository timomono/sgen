from pathlib import Path
import re
from urllib.parse import urlparse
from sgen.base_middleware import BaseMiddleware
from sgen.stdlib.asset_download_protection.obf import obfScript

# <Files ~ "^(?!.*((\.(html|htm))|/)$).*">

HTACCESS_STR = (
    r""""""
    r"""<Files ~ "\.(gif|jpg|jpeg|png|svg|mp4|m4a|mp3|avi|webm|weba|webp)$">
SetEnvIf Referer "^http://localhost/" samesite
order deny,allow
deny from all
allow from env=samesite
</Files>
"""
)

with open(Path(__file__).parent / "minified.js") as f:
    SCRIPT_STR = f.read()

SCRIPT_STR = SCRIPT_STR.replace("{", "{{")
SCRIPT_STR = SCRIPT_STR.replace("}", "}}")
SCRIPT_STR = SCRIPT_STR.replace("[]", "{list_str}")


class AssetDownloadProtectionMiddleware(BaseMiddleware):
    """Middleware that protects against asset downloads.
    Please note that this package cannot completely suppress asset downloads.
    """

    def do(self, build_path: Path) -> None:
        with open(build_path / ".htaccess", "w") as f:
            f.write(HTACCESS_STR)
        for file in (
            path
            for path in build_path.glob("**/*")
            if path.suffix not in (".html", ".htm", ".css", ".js")
            and path.is_file()
        ):
            temp_file_path = file.parent / (file.name + ".tmp")
            with open(file, "rb") as original_file, open(
                temp_file_path, "wb"
            ) as temp_file:
                temp_file.write(b"\xff")
                while chunk := original_file.read(4096):
                    temp_file.write(chunk)
                file.unlink()
                temp_file_path.rename(file)
            # with open(file, "ab") as bf:
            #     bf.write(b"\x01")
            # with open(file, "rb") as brf:
            #     b = brf.read()
            # with open(file, "wb") as bwf:
            #     bwf.write(b"\x01" + b)

        for file in build_path.glob("**/*.html"):
            sources: list[tuple[str, str]] = []

            def replace_src(match: re.Match) -> str:
                attr_name: str = match.group(2)
                value: str = match.group(3)
                if urlparse(value).hostname is not None:
                    return (
                        match.group(1)
                        + attr_name
                        + "="
                        + '"'
                        + value
                        + '"'
                        + match.group(4)
                    )
                sources.append((attr_name, value))
                attr_name = "data-prot-src-id"
                value = str(len(sources) - 1)
                return (
                    match.group(1)
                    + attr_name
                    + "="
                    + '"'
                    + value
                    + '"'
                    + match.group(4)
                )

            with open(file, "r") as f:
                body = f.read()
            result: str = re.sub(
                r"(<(?!script)[a-zA-Z0-9]+ +[^>]*)"
                r"""(src) *= *["']?([^>"' ]*)["']?( *[^>]*>)""",
                replace_src,
                body,
            )
            list_string = SCRIPT_STR.format(
                list_str=obfScript(
                    "["
                    + ",".join(map(lambda v: '"' + v[1] + '"', sources))
                    + "]",
                    debugger=False,
                    iter=2,
                ),
            )

            result = re.sub(
                r"(< */ *head *>)",
                r"<script>"
                + list_string.replace("\\", "\\\\")
                + r"</script>\1",
                result,
            )
            with open(file, "w") as f:
                f.write(result)


# URL.createObjectURL(await (await fetch("/img/logo/icon.svg")).blob())
# URL.revokeObjectURL("blob:http://localhost:8282/3db748e1-775b-4067-9e3e-43802fb2cfa9")
