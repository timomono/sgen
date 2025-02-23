from pathlib import Path
from random import randint
import re
from urllib.parse import urlparse

from urllib.parse import urljoin
from sgen.base_middleware import BaseMiddleware
from sgen.stdlib.asset_download_protection.image_division import divide_image
from sgen.components.obfuscation.text_obf import obfScript
from sgen.components.random_str import (
    random_path,
    random_path_to_url,
)

# <Files ~ "^(?!.*((\.(html|htm))|/)$).*">

# TODO: Add comment "Generated by sgen asset_download_protection"
HTACCESS_STR = (
    ""
    r"""<Files ~ "\.(gif|jpg|jpeg|png|svg|mp4|m4a|mp3|avi|webm|weba|webp)$">
SetEnvIf Referer "^http://localhost/" samesite
order deny,allow
deny from all
allow from env=samesite
</Files>
"""
)

# main.js minified version
SCRIPT_STR = """async function l(){try{const h=[],m={};for(var f of document.querySelectorAll("*[data-prot-src-id]:not(img)")){const a=h[f.dataset.protSrcId],b=await (await fetch(a)).blob();let d=URL.createObjectURL(b.slice(1,b.size,b.type));d=a.includes("#")?d+"#"+a.split("#").slice(-1)[0]:d;f.addEventListener("load",()=>URL.revokeObjectURL(d));void 0!==f.src?f.src=d:void 0!==f.getAttribute("xlink:href")&&f.setAttribute("xlink:href",d)}for(const a of document.querySelectorAll("img[data-prot-src-id]")){a.addEventListener("contextmenu",
c=>c.preventDefault());a.addEventListener("mousedown",c=>c.preventDefault());a.style["pointer-events"]="none";const b=document.createElement("img");b.src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAAtJREFUGFdjYAACAAAFAAGq1chRAAAAAElFTkSuQmCC";const d=document.createElement("div");for(const c of getComputedStyle(a))d.style[c]=a.style[c];for(const c of a.classList)d.classList.add(c);d.style.position="relative";b.style.position="absolute";b.style.width="100%";
b.style.height="100%";b.style.top="0";b.style.bottom="0";b.style.left="0";b.style.right="0";b.alt="Dummy image";b.addEventListener("contextmenu",c=>c.preventDefault());b.addEventListener("mousedown",c=>c.preventDefault());a.parentNode.insertBefore(d,a);for(const c of m[h[a.dataset.protSrcId]]){const e=document.createElement("img");f=c;const k=await (await fetch(f)).blob();let g=URL.createObjectURL(k.slice(1,k.size,k.type));g=f.includes("#")?g+"#"+f.split("#").slice(-1)[0]:g;e.addEventListener("load",
()=>URL.revokeObjectURL(g));void 0!==e.src?e.src=g:void 0!==a.getAttribute("xlink:href")&&a.setAttribute("xlink:href",g);e.style.position="absolute";e.style.width="100%";e.style.height="100%";e.style.top="0";e.style.bottom="0";e.style.left="0";e.style.right="0";e.alt=a.alt;d.append(e)}a.remove();d.append(b)}}catch(h){console.error(h)}}"loading"===document.readyState?document.addEventListener("DOMContentLoaded",()=>l()):l();"""  # noqa:E501

SCRIPT_STR = SCRIPT_STR.replace("{", "{{")
SCRIPT_STR = SCRIPT_STR.replace("}", "}}")
SCRIPT_STR = SCRIPT_STR.replace("[]", "{list_str}")
SCRIPT_STR = SCRIPT_STR.replace("{{}}", "{dict_str}")


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
            "_redirects",
            "_headers",
            "favicon.ico",
            "favicon.png",
        )
        with open(build_path / ".htaccess", "w") as f:
            f.write(HTACCESS_STR)

        new_paths: dict[Path, set[Path]] = {}
        for file in [
            p
            for p in build_path.glob("**/*")
            if p.suffix in (".jpg", ".jpeg", ".png", ".bmp", ".webp")
        ]:
            new_paths[file] = set()

            def get_path(_):
                rand = random_path(file.parent, file.suffix)
                new_paths[file].add(rand)
                return rand

            divide_image(file, get_path, randint(3, 7))
            file.unlink()

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
                sources.append(
                    (
                        attr_name,
                        random_path_to_url(
                            build_path
                            / Path(
                                urljoin(
                                    "/" + str(file.relative_to(build_path)),
                                    value,
                                )[1:]
                            ),
                            file,
                            build_path,
                            is_absolute=True,
                        ),
                    )
                )
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
                ),
                dict_str=obfScript(
                    "({"
                    + ",".join(
                        (
                            (
                                '"'
                                + str(
                                    random_path_to_url(
                                        k, file, build_path, is_absolute=True
                                    )
                                )
                                + '"'
                                + ":["
                                + ",".join(
                                    map(
                                        lambda p: '"'
                                        + random_path_to_url(
                                            p, file, build_path
                                        )
                                        + '"',
                                        v,
                                    )
                                )
                                + "]"
                            )
                            for k, v in new_paths.items()
                        )
                    )
                    + "})",
                ),
            )
            decode_img_js: Path = random_path(build_path, ".js")
            with open(decode_img_js, "w") as f:
                f.write(list_string)
            src_path = random_path_to_url(decode_img_js, file, build_path)
            result = re.sub(
                r"(< */ *head *>)",
                rf"<script async " rf'src="{src_path}">' rf"</script>\1",
                result,
            )
            with open(file, "w") as f:
                f.write(result)


# URL.createObjectURL(await (await fetch("/img/logo/icon.svg")).blob())
# URL.revokeObjectURL("blob:http://localhost:8282/3db748e1-775b-4067-9e3e-43802fb2cfa9")
