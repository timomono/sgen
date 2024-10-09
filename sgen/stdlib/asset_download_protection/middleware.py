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
# main.js minified version
SCRIPT_STR = """async function decodeImages(){var a=[];for(var c of document.querySelectorAll("*[data-prot-src-id]")){const d=a[c.dataset.protSrcId];var e=await (await fetch(d)).blob();e=e.slice(1,e.size,e.type);let b=URL.createObjectURL(e);b=d.includes("#")?b+"#"+d.split("#").slice(-1)[0]:b;c.addEventListener("load",()=>URL.revokeObjectURL(b));void 0!==c.src?c.src=b:void 0!==c.getAttribute("xlink:href")&&c.setAttribute("xlink:href",b)}for(const d of document.querySelectorAll("img"))d.addEventListener("contextmenu",b=>b.preventDefault()),d.addEventListener("mousedown",b=>b.preventDefault()),d.style["pointer-events"]="none",a=document.createElement("img"),a.src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAAtJREFUGFdjYAACAAAFAAGq1chRAAAAAElFTkSuQmCC",c=document.createElement("div"),c.style.display=d.style.display,c.style.position="relative",a.style.position="absolute",a.style.width="100%",a.style.height="100%",a.style.top="0",a.style.bottom="0",a.style.left="0",a.style.right="0",a.alt="Dummy image",a.addEventListener("contextmenu",b=>b.preventDefault()),a.addEventListener("mousedown",b=>b.preventDefault()),d.parentNode.insertBefore(c,d),c.append(d),c.append(a)}"loading"===document.readyState?document.addEventListener("DOMContentLoaded",a=>decodeImages()):decodeImages();"""  # noqa:E501

SCRIPT_STR = SCRIPT_STR.replace("{", "{{")
SCRIPT_STR = SCRIPT_STR.replace("}", "}}")
SCRIPT_STR = SCRIPT_STR.replace("[]", "{list_str}")


class AssetDownloadProtectionMiddleware(BaseMiddleware):
    """Middleware that protects against asset downloads.
    Please note that this package cannot completely suppress asset downloads.
    """

    def __init__(self, except_debug: bool = True) -> None:
        self.except_debug = except_debug
        super().__init__()

    def do(self, build_path: Path) -> None:
        from sgen.get_config import sgen_config

        if self.except_debug and sgen_config.DEBUG:
            return
        EXCLUDE_SUFFIXES = (
            ".html",
            ".htm",
            ".css",
            ".js",
            ".svg",
            ".htaccess",
            ".toml",
            ".yaml",
        )
        EXCLUDE_FILENAMES = (
            "sitemap.xml",
            "robots.txt",
            ".htaccess",
        )
        with open(build_path / ".htaccess", "w") as f:
            f.write(HTACCESS_STR)
        for file in (
            path
            for path in build_path.glob("**/*")
            if path.suffix not in EXCLUDE_SUFFIXES
            and path.name not in EXCLUDE_FILENAMES
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
                if (
                    urlparse(value).hostname is not None
                    or "." + value.split(".")[-1] in EXCLUDE_SUFFIXES
                ):
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
                # src|xlink:href
                replace_src,
                body,
            )
            list_string = SCRIPT_STR.format(
                list_str=obfScript(
                    "["
                    + ",".join(map(lambda v: '"' + v[1] + '"', sources))
                    + "]",
                    debugger=False,
                    iter=0,
                    format=False,
                ),
            )
            filename = ".".join(file.name.split(".")[:-1])
            decode_img_js: Path = file.parent / (filename + "-decode-img.js")
            with open(decode_img_js, "w") as f:
                f.write(list_string)
            result = re.sub(
                r"(< */ *head *>)",
                rf"<script async "
                rf'src="{decode_img_js.relative_to(file.parent)}">'
                rf"</script>\1",
                result,
            )
            with open(file, "w") as f:
                f.write(result)


# URL.createObjectURL(await (await fetch("/img/logo/icon.svg")).blob())
# URL.revokeObjectURL("blob:http://localhost:8282/3db748e1-775b-4067-9e3e-43802fb2cfa9")
