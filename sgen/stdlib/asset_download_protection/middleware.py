from pathlib import Path
import re
from urllib.parse import urlparse
from sgen.base_middleware import BaseMiddleware

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

SCRIPT_STR = """document.addEventListener("DOMContentLoaded",async()=>{const f=[];for(const b of document.querySelectorAll("*[data-prot-src-id]")){b.addEventListener("contextmenu",c=>c.preventDefault());b.addEventListener("mousedown",c=>c.preventDefault());const e=URL.createObjectURL(await (await fetch(f[b.dataset.protSrcId])).blob());b.src=e;b.addEventListener("load",()=>URL.revokeObjectURL(e));const g=b.parentElement,a=document.createElement("img");a.src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAAtJREFUGFdjYAACAAAFAAGq1chRAAAAAElFTkSuQmCC";const d=document.createElement("div");d.style.position="relative";a.style.position="absolute";a.style.width="100%";a.style.height="100%";a.style.top="0";a.style.bottom="0";a.style.left="0";a.style.right="0";a.addEventListener("contextmenu",c=>c.preventDefault());a.addEventListener("mousedown",c=>c.preventDefault());g.append(d);d.append(b);d.append(a)}});"""  # noqa:E501

SCRIPT_STR = SCRIPT_STR.replace("{", "{{")
SCRIPT_STR = SCRIPT_STR.replace("}", "}}")
SCRIPT_STR = SCRIPT_STR.replace("[]", "[{list_str}]")


class AssetDownloadProtectionMiddleware(BaseMiddleware):
    """Middleware that protects against asset downloads.
    Please note that this package cannot completely suppress asset downloads.
    """

    def do(self, build_path: Path) -> None:
        with open(build_path / ".htaccess", "w") as f:
            f.write(HTACCESS_STR)
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
            result = re.sub(
                r"(<[a-zA-Z0-9]+ +[^>]*)"
                r"""(src) *= *["']?([^>"' ]*)["']?( *[^>]*>)""",
                replace_src,
                body,
            )
            list_string = SCRIPT_STR.format(
                list_str=",".join(map(lambda v: '"' + v[1] + '"', sources))
            )

            result = re.sub(
                r"(< */ *head *>)",
                rf"<script>{list_string}</script>\1",
                result,
            )
            with open(file, "w") as f:
                f.write(result)


# URL.createObjectURL(await (await fetch("/img/logo/icon.svg")).blob())
# URL.revokeObjectURL("blob:http://localhost:8282/3db748e1-775b-4067-9e3e-43802fb2cfa9")
